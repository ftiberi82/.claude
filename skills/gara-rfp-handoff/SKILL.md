---
name: gara-rfp-handoff
description: >
  Analizza la documentazione commerciale e tecnica di una RFP e produce un workbook Excel di
  handoff per il team che dovrà stimare. Si basa su un template predefinito (`assets/template_rfp_handoff.xlsx`)
  con 10 sheet operativi + 1 sheet di esempi: Info Sintetiche RFP, Mappatura Capability,
  Driver di Stima, Gap Analysis, Domande Chiarimento, Assunzioni, Matrice Profili x Capability,
  Input Cost Model, Registro Chiarimenti, Nota di Handoff.
  TRIGGER quando: l'utente fornisce documenti commerciali e/o tecnici di una RFP, capitolato,
  bando, CSA o disciplinare e chiede di preparare il pacchetto per la stima, l'executive summary
  della gara, la mappatura capability, i driver di stima, la matrice profili, le domande di
  chiarimento al cliente, il registro chiarimenti o la nota di handoff verso il cost modeling.
  OUTPUT: file `rfp_handoff.xlsx` ottenuto copiando e popolando il template
  `assets/template_rfp_handoff.xlsx` mantenendo intestazioni, struttura, formattazione e
  data validation predefinite. Questa skill NON genera deck PowerPoint: lo step
  IMMEDIATAMENTE SUCCESSIVO è invocare `gara-rfp-deck` passandole l'`rfp_handoff.xlsx`
  prodotto per generare l'Executive Summary PPTX (10 slide), primo deliverable di
  brainstorming delivery/bid PRIMA dei chiarimenti al cliente.
  COMPORTAMENTO INTERATTIVO OBBLIGATORIO: prima di popolare il template la skill elenca
  esplicitamente in chat tutte le scelte interpretative (estratto / inferito / assunto) e si
  ferma in attesa di approvazione. Le assunzioni richiedono conferma esplicita prima di
  procedere. Questo è comportamento intenzionale, non un errore — non riprendere automaticamente.
  AUTONOMIA: skill end-to-end. Non richiede output di altre skill `gara-*` come input, ma se
  l'utente fornisce un `rfp_analysis.json` esistente la skill può usarlo come contesto aggiuntivo.
  NON USARE se l'utente vuole solo un'analisi strategica/economica della gara, un file JSON
  di analisi, il valore della gara, i criteri di aggiudicazione o la verifica EOL/LTS dello
  stack — in quel caso usa `gara-rfp-analyzer`. Questa skill (`gara-rfp-handoff`) si attiva
  invece quando l'utente vuole il pacchetto operativo per il team che dovrà stimare:
  workbook con capability, driver di stima, matrice profili x capability, gap analysis,
  registro chiarimenti, nota di handoff.
  SKIP se il documento è un contratto esecutivo, verbale, fattura, collaudo o documento privo
  di scope, capability stimabili o sezioni di valutazione dell'offerta.
---

# Gara RFP Handoff

Prepara il pacchetto di handoff verso la fase di stima a partire dai documenti commerciali e
tecnici di una RFP. L'output è un singolo file Excel — `rfp_handoff.xlsx` — generato copiando
e popolando il template ufficiale `assets/template_rfp_handoff.xlsx` (preserva intestazioni,
formattazione, larghezze colonne, sezioni e data validation).

**Non stimare GG/U.** Questa skill prepara il terreno alla stima, non la produce.

## Distinzione vs `gara-rfp-analyzer`

Le due skill partono dagli stessi documenti ma servono utenti e momenti diversi.

| | `gara-rfp-analyzer` | `gara-rfp-handoff` (questa) |
|---|---|---|
| **A chi serve** | Chi prepara la **risposta** all'offerta (commerciale / sales / bid manager) | Chi organizza il lavoro del **team di stima** (delivery / solution architect / cost modeler) |
| **Output** | `rfp_analysis.json` (un JSON strategico) | `rfp_handoff.xlsx` (workbook operativo) |
| **Scopo** | Capire valore economico, criteri di aggiudicazione, formato risposta atteso, EOL/LTS dello stack as-is | Mappare capability, driver di stima, gap, domande al cliente, matrice profili x capability e produrre l'handoff verso il cost modeler |
| **Comportamento** | Zero domande, scrive il file subito | Interattivo: si ferma per approvazione delle scelte interpretative prima di popolare il template |

**Se l'utente chiede entrambe le cose**: esegui prima `gara-rfp-analyzer` (output JSON), poi
questa skill, che potrà usare il JSON come contesto aggiuntivo. Non duplicare il lavoro.

**In caso di dubbio sul trigger**: guarda l'output che l'utente si aspetta. Se cita "Excel",
"capability", "driver", "matrice profili", "handoff", "pacchetto per la stima" → questa skill.
Se cita "JSON", "valore gara", "criteri di aggiudicazione", "analisi strategica", "EOL/LTS",
"open point QA" → `gara-rfp-analyzer`.
Se cita "deck", "PPT", "executive summary slides", "presentazione", "slide" → `gara-rfp-deck`.
Quest'ultima è una skill **separata**, invocata sull'`rfp_handoff.xlsx` (questa skill
non la chiama mai automaticamente). Se l'utente nel prompt iniziale chiede "pacchetto +
deck" o simili, indica nel riepilogo finale che il deck si genera con `gara-rfp-deck` come
step successivo.

## Input richiesti

- Documenti commerciali della RFP (se presenti): `pdf`, `docx`, `xlsx`, `ppt`, `pptx`.
- Documenti tecnici della RFP: stessi formati.
- Opzionale: `rfp_analysis.json` prodotto da `gara-rfp-analyzer` (usato come contesto se presente).

Se mancano i documenti tecnici, comunica all'utente che il workbook sarà parziale sui punti
tecnici (capability tecniche, profili specialistici, stack) e procedi solo con i dati commerciali.

## Comportamento interattivo (regola assoluta)

**Prima di popolare il template**, la skill DEVE eseguire il seguente ciclo di approvazione:

### Step A — Estrazione e classificazione

Per ogni dato che andrà nel workbook, classifica la fonte:

- `estratto` — presente verbatim nel documento (cita sezione/pagina e max 20 parole originali).
- `inferito` — non esplicito ma ricavabile dal contesto (spiega il ragionamento).
- `assunto` — assente nel documento; assunzione operativa proposta dalla skill.

### Step B — Registro scelte interpretative

Presenta in chat all'utente, in formato Markdown strutturato:

1. **Lista delle scelte interpretative** — ogni scelta numerata con:
   - cosa si sta decidendo (es. "modello commerciale = Misto Canone + T&M")
   - fonte (`estratto` / `inferito` / `assunto`)
   - dove sta nel documento (sezione/pagina) o perché è un'assunzione
   - alternativa scartata (se applicabile)

2. **Lista delle assunzioni operative** — separata, numerata, con motivazione e impatto.

3. **Lista delle incoerenze tra documenti** — se i documenti commerciale e tecnico si
   contraddicono, segnala l'incoerenza come **gap bloccante**: NON tentare di riconciliarla
   autonomamente. Andrà nello sheet `8. Input Cost Model` come parametro **BLOCCANTE**.

### Step C — Attesa approvazione

Termina il messaggio con una domanda esplicita:
> "Confermi tutte le scelte interpretative e le assunzioni elencate sopra? (sì / modifica N / no)"

**FERMATI qui.** Non popolare il template finché l'utente non approva esplicitamente. Se
l'utente chiede modifiche, applicale e ripresenta il registro aggiornato. Se l'utente nega
un'assunzione bloccante, NON sostituirla con un'altra — chiedi il valore corretto o aggiungila
come gap bloccante nello sheet 8.

### Step D — Produzione output

Solo dopo approvazione esplicita: copia il template e popola le celle.

## Lettura documenti

Strategia adattiva (stessa di `gara-rfp-analyzer`):

1. Usa `document-skills` se disponibile in Claude Code.
2. Altrimenti `extract-text` come prima mossa.
3. `python-pptx` come fallback per `.pptx`.
4. Per `xlsx`/`csv` allegati, usa la skill `xlsx`.

Leggi **tutti** i documenti integralmente. Annota mentalmente:
- Sezioni economiche (importi, modello commerciale, durata, opzioni proroga, rate card)
- Sezioni di valutazione (criteri tecnici/economici e pesi, soglie sbarramento)
- Sezioni di scope e capability (servizi, livelli L1/L2/L3, sviluppo, AMS, T&M)
- Driver di stima (volumi, ticket, SLA, KPI, complessità, integrazioni, orari copertura)
- Profili professionali richiesti (con N. risorse e fonte di pagina)
- Vincoli di delivery (on/off-shore, geografici, nominativi, presidio on-site)
- Incoerenze tra documenti (commerciale vs tecnico)

### Checklist di estrazione OBBLIGATORIA

Per ogni RFP, la skill deve attivamente cercare e catturare tutti i seguenti parametri,
perché sono tipicamente determinanti per il cost model. Se il parametro è assente nel
documento, registralo come gap (Sheet 4) o come parametro DA ASSUMERE (Sheet 8 giallo).
**Non considerare il parametro "non rilevante" solo perché non lo si trova al primo passaggio.**

**Parametri economici e contrattuali:**
- Importo per voce: start-up / fase affiancamento, canone mensile, plafond T&M, oneri sicurezza
- Durata base + opzione proroga (durata, condizioni economiche della proroga)
- **Revisione prezzi**: meccanismo di adeguamento automatico durante l'esecuzione
  (soglia di attivazione %, formula di aggiornamento, indice di riferimento es. ISTAT/BtoB)
- Proroga tecnica art.120 c.11 D.lgs.36/2023 (o analoga clausola): condizioni e durata
- Tariffe a base d'asta per profilo (€/giorno o €/ora)
- Volumi GG/U per profilo, **specificando esplicitamente se annuali o totali sul periodo**
- Cauzione provvisoria (% e importo) + contributo ANAC
- Subappalto: limiti, quota minima PMI, divieti
- Avvalimento: ammesso/escluso, premiale o di qualificazione
- Garanzia/giustificazione anomalia offerta
- Penali: per fasce di Livello di Servizio e timing di attivazione (es. dal mese 7)

**Parametri operativi:**
- SLA accettazione e SLA risoluzione per priorità (P1-P4)
- Reperibilità: orari, profili minimi attivi, eventi speciali (Sanremo, Mondiali, elezioni)
- Attività fuori orario standard: ore/anno, modalità di consuntivazione
- Sede di esecuzione: indirizzo + NUTS + modalità (on-site / ibrida / remoto)
- Lingua delle relazioni con il cliente
- Strumenti di lavoro a carico del fornitore (postazioni, VPN, UCC, account aziendale)
- Turn over massimo (% e periodo) + affiancamento minimo (giorni lavorativi)

**Parametri tecnici:**
- Stack tecnologico per dominio (BE, FE, Mobile, SmartTV, DB, messaging, container, ML)
- Parco applicativo (numero app, mix tecnologico, criticità)
- Profili professionali esplicitamente definiti (titolo studio, anzianità, esperienze)

**Parametri di valutazione:**
- Punteggio tecnico (totale + breakdown sub-criteri D / Q / T)
- Punteggio economico + formula di calcolo
- Soglia di sbarramento (esiste? a che livello?)
- Riparametrazione (sì/no, su quanti livelli)
- Soglie quantitative dei punteggi tabellari (N. risorse certificate per ottenere il
  punteggio massimo per ogni voce — se assente è un BLOCCANTE da chiarire)

## Lettura preventiva del template e degli esempi

**OBBLIGATORIO prima di popolare ogni sheet**:

1. Apri il template `assets/template_rfp_handoff.xlsx`.
2. Apri lo sheet `_Esempi` e leggi le righe relative al sheet che stai per compilare.
3. Allinea formato, granularità e tono dei contenuti agli esempi. **Non copiare i valori — copia il PATTERN.**
4. Rispetta i drop-down/data validation impostati: i valori ammessi sono lì per garantire stabilità del cost modeler a valle.

## Struttura del template

Il file `assets/template_rfp_handoff.xlsx` contiene 11 sheet (ordine esatto):

### `1. Info Sintetiche RFP` — form anagrafico
Layout label-valore in colonne A (label) / B (valore). Sezioni:
`DATI IDENTIFICATIVI GARA`, `SCADENZE CHIAVE`, `VALORE APPALTO`, `DURATA CONTRATTO`,
`MODELLO COMMERCIALE`, `CRITERI DI VALUTAZIONE`, `SLA & PENALI CHIAVE`, `SKILL MIX E DELIVERY`,
`REQUISITI DI QUALIFICAZIONE`. **Non rinominare le label** — popola solo la colonna B.
Aggiorna anche le righe titolo 1 e 2 sostituendo i placeholder `<Cliente>`, `<Nome RFP>`, `<CIG>`,
`<Data pubblicazione>`.

**Regola "team minimo presidio" (campo `Risorse minime presidio`):**
- Conteggia SOLO le figure professionali esplicitamente elencate nella tabella di
  dimensionamento del presidio (di solito un Allegato 1 o paragrafo "Risorse impegnate").
- NON includere nel conteggio i ruoli di responsabilità citati a parte (Service Manager,
  Project Manager, Responsabile Esecutivo del Contratto, ecc.) **a meno che non compaiano
  nella stessa tabella di dimensionamento del presidio**.
- Se il documento cita "Service Manager con presenza stabile" come voce separata dalla
  tabella del presidio, registra in colonna B due valori distinti — esempio:
  `"41 risorse presidio operativo (Capitolato §X, tabella dimensionamento) + 1 Service
  Manager con presenza stabile (Capitolato §Y) → totale fornitura: 42 figure professionali"`.
- In Sheet 8 (verde) usa due voci separate: una per il presidio operativo e una per il SM.

### `2. Mappatura Capability` — gerarchia L1/L2/L3
Colonne: `Livello` (drop-down L1/L2/L3), `Codice`, `Capability / Attività`, `Tipo Contratto`
(drop-down Canone/T&M/Start-up/Misto), `Profili Coinvolti`, `Orario/Copertura`, `SLA Riferimento`,
`Note`. L'indentazione visiva nel campo `Capability / Attività` rispecchia il livello
(L1 = nessun rientro, L2 = 2 spazi, L3 = 6 spazi).

**Regola tracciabilità colonna E `Profili Coinvolti` (OBBLIGATORIA):** ogni profilo
elencato deve essere classificato come **estratto dal documento** o **ipotizzato** (con
rationale esplicito). Usare tag inline:

- **Profili estratti** — citare la fonte tra parentesi quadre: `TL, TechL, AP, Prog [DOC: Cap. §3.1 + Allegato 1]`. Mantenere il riferimento puntuale (sezione/paragrafo/pagina) per ogni gruppo di profili.
- **Profili ipotizzati** — prefisso `[IPOTIZZATO]` + lista profili + `| rationale:` + motivazione breve. Es: `[IPOTIZZATO] DBA Oracle, DevOps Engineer | rationale: stack Oracle/Docker citato in §2.1 e Allegato 2 ma profili non assegnati esplicitamente alla capability`.
- **Misti** (alcuni estratti + alcuni ipotizzati) — separare con `+`: `TL, AP [DOC: §3.1] + [IPOTIZZATO] Cloud Architect | rationale: stack Azure citato in §2.5 senza profilo dedicato`.
- **Cella vuota** = "Nessun profilo associabile né per estrazione né per inferenza ragionevole" (raro; tipicamente capability decorative come START-UP). NON lasciare vuoto se c'è anche un solo profilo ipotizzabile con rationale.

**Why**: la trasparenza sulla provenienza dei profili è critica per il cost modeler in
Fase 3 — un profilo ipotizzato richiede validazione con il cliente o assunzione formale
nel Risk Register; un profilo estratto è già parte del contratto. Senza distinzione esplicita
il cost modeler rischia di trattare gli ipotizzati come dati certi.

### `3. Driver di Stima`
Colonne: `Capability (L2)`, `Driver Disponibile da RFP`, `Valore / Riferimento RFP`,
`Driver Mancante / Gap`, `Impatto sulla Stima` (drop-down ALTO/MEDIO/BASSO),
`Affidabilità Stima` (drop-down ALTA/MEDIA/BASSA).
Pattern di compilazione: per ciascuna capability L2 elenca i driver presenti nelle prime righe
(colonne A, B, C) e i driver mancanti nelle righe successive (colonne D, E, F).

### `4. Gap Analysis`
Colonne: `#`, `Capability`, `Driver Mancante`, `Perché è Necessario`, `Come Colmare il Gap`,
`Priorità` (drop-down ALTA/MEDIA/BASSA), `Azione` (drop-down Chiarimento/Assunzione/Workshop/Decisione interna).
Una riga per ogni gap. **Le incoerenze tra documenti vanno qui con `Priorità=ALTA`** e
replicate nello sheet 8 come parametri BLOCCANTI.

### `5. Domande Chiarimento`
Colonne: `#`, `Capability`, `Categoria` (es. Volume/Sizing, Tecnica, Contrattuale, Procedurale),
`Testo Domanda`, `Motivazione / Impatto sulla Stima`, `Prio` (drop-down 1/2/3 — 1=critica).
Le domande devono essere **specifiche e azionabili** — niente domande generiche tipo
"ci può fornire più dettagli?".

### `6. Assunzioni`
Colonne: `#`, `Capability`, `Assunzione`, `Base / Fonte`, `Valore Adottato`,
`Impatto se Errata`, `Rischio` (drop-down ALTO/MEDIO/BASSO).
Tutte le assunzioni del registro Step B approvate dall'utente confluiscono qui.

**Regola "assunzioni quantificate":** le assunzioni di VOLUME (numero ticket, chiamate,
attività, distribuzione %, ecc.) **devono includere un VALORE NUMERICO PROVVISORIO**
basato su benchmark di settore documentato. Il cost modeler validerà o sovrascriverà;
ma `"Da valorizzare dal cost modeler"` non è un'assunzione, è una richiesta —
in quel caso la voce va nello Sheet 8 GIALLO, non qui.

Esempi corretti (Sheet 6):
- *"Volume MAC stimato: ~1.500 ticket/anno (split 5%/15%/30%/50% per P1-P4) — benchmark
  IT outsourcing portfolio enterprise ~30 app multimediali"*
- *"Distribuzione complessità app: 60% semplice / 30% media / 10% critica — benchmark
  enterprise media&broadcasting"*
- *"Tasso utilizzo plafond T&M: 85% — benchmark contratti AM pubblica amministrazione"*

Esempio errato (Sheet 6):
- *"Numero ticket MAC/anno: Da assumere su benchmark"* → questa è una richiesta al cost
  modeler, va nello Sheet 8 GIALLO con dicitura `"Da valorizzare [N. ticket]"`.

Le assunzioni qualitative (es. modalità di delivery, perimetro tecnologico) non richiedono
valore numerico ma devono comunque indicare la *Base/Fonte* del benchmark o ragionamento.

### `7. Matrice Profili x Capability`
Righe = profili professionali; colonne capability E:N (intestazioni placeholder dal template
RAI: START-UP, MAC, REP, GES, GST, CON, MAV, MEV, PRJ, SPE).
**REGOLA CRITICA**: prima di popolare le celle, **sostituisci le intestazioni di colonna E:N
con le capability L2 effettive** identificate nello sheet 2 per la specifica RFP.
Sezioni: `SERVIZI A CANONE` (riga 5) e `SERVIZI A RICHIESTA T&M` (riga 23).
Colonna A = Tipo (drop-down Canone/T&M/Misto). Colonna B = Profilo Professionale. Colonna C =
N. Risorse / Volume. Colonna D = Fonte (citazione documento). Celle E:N = drop-down esteso
`P-DOC` / `P-IPO` / `S-DOC` / `S-IPO` / vuoto.

**Tag delle celle E:N (regola tracciabilità OBBLIGATORIA)**:
- `P-DOC` = Primario, **estratto dal documento**: il capitolato/disciplinare assegna
  esplicitamente questo profilo a questa capability. Riportare il riferimento puntuale
  nella colonna D `Fonte` accanto al nome profilo (es. `Capitolato §2.4.2 → REP esplicito BE+FE`).
- `P-IPO` = Primario, **ipotizzato** in base a inferenza ragionevole (stack tecnologico,
  prassi di settore, criticità rilevata). **Rationale obbligatorio** nella colonna D
  `Fonte`: es. `[IPOTIZZATO] stack Oracle/Mongo richiede DBA per GES; Allegato 2 cita
  competenza DBA ma non profilo dedicato`.
- `S-DOC` = Supporto, estratto.
- `S-IPO` = Supporto, ipotizzato + rationale.
- **Cella vuota** = "Né estratto né ragionevolmente ipotizzabile" (es. profilo SmartTV
  per capability REP quando il documento limita REP a BE+FE).

**Why**: la versione precedente della skill consentiva solo `P/S` esplicite + cella vuota,
con il risultato di matrici molto sparse che sottostimavano la copertura reale. L'estensione
`-DOC` / `-IPO` permette di registrare anche le inferenze ragionevoli (utili al cost modeler
per pianificare lo skill mix) mantenendole tracciabili e distinguibili dai dati estratti.

**Regola "profili inventati ammessi solo con tag IPOTIZZATO":** i profili specialistici
non documentati nell'Allegato "Figure Professionali" (DBA, DevOps, QA Engineer, Security
Specialist, ML Engineer, Cloud Architect, Data Engineer, ecc.) possono essere aggiunti
come **righe del Sheet 7 SOLO con tag `P-IPO` / `S-IPO`** e rationale esplicito in col D.
Es: profilo `DBA Oracle` aggiunto perché stack Oracle è centrale ma capitolato non assegna
profilo dedicato → riga con `P-IPO` su capability GES, col D = `[IPOTIZZATO] stack Oracle
in Allegato 2; coperto in pratica da TechL BE ma profilo dedicato realistico per gare
multimedia con DB intensivo`.

Se il documento richiede skill specifiche (es. "esperienza DBA Oracle senior") **e**
indica anche un profilo che copre quella skill, allora la skill va nelle Note del profilo
documentato (col H Sheet 2) — NON creare un profilo ipotizzato duplicato.

**Regola di classificazione P-DOC vs P-IPO (con esempi):**

✅ **`P-DOC` — assegnazione esplicita nel documento**:
> Capitolato §2.4.2 (REP – Reperibilità): *"il servizio dovrà garantire intervento sia in
> ambito Back-end, sia in ambito Front-end"* → `P-DOC` nella colonna `REP` per profili
> BE+FE (TL, TechL, AP, Prog di entrambi gli ambiti) con col D = `Capitolato §2.4.2`.
> Tutti gli altri profili (Mobile, SmartTV) → cella vuota.

✅ **`P-IPO` — inferenza ragionevole con rationale**:
> Profilo `Programmatore BE` (6 risorse) e capability `MAC` (Manutenzione Correttiva).
> Il Capitolato non assegna esplicitamente, ma indica che il presidio MAC è composto
> da N risorse miste BE/FE/Mobile/SmartTV → `P-IPO` con col D = `[IPOTIZZATO] presidio
> MAC esplicitamente miste profili, ragionevole che Programmatore BE copra ticket MAC
> ambito BE per le ~45% applicazioni del parco`.
>
> Differenza chiave dalla versione precedente: prima questa cella sarebbe rimasta
> VUOTA per regola strict-anti-inferenza. Ora viene popolata con `P-IPO` + rationale,
> dando al cost modeler informazione utile per lo skill mix.

✅ **Servizi a Richiesta (T&M)**: se il documento elenca i 4 profili T&M (Architect, TL,
AP, Prog) come unici profili abilitati a coprire MAV/MEV/PRJ/SPE, allora `P-DOC` su tutte
le 4 capability T&M per ognuno dei 4 profili è un'assegnazione esplicita.

### `8. Input Cost Model` — parametri per il cost modeler
Layout a 3 sezioni codificate per colore:
- **VERDE — PARAMETRI CERTI** (riga 8): dati estratti verbatim, utilizzabili direttamente.
- **GIALLO — PARAMETRI DA ASSUMERE** (riga 70): dati non esplicitati, il cost modeler deve valorizzarli.
- **ROSSO — PARAMETRI BLOCCANTI** (riga 89): incoerenze tra documenti o gap critici, richiedono chiarimento formale prima di stimare.

Colonne: `#`, `Categoria` (es. Valore Appalto, Durata, SLA, Tariffe, Volumi MAC, ecc.),
`Parametro`, `Valore / Riferimento`, `Fonte`, `Note per il Cost Modeler`.
**Tutte le incoerenze del Sheet 4 con `Priorità=ALTA` vanno replicate qui come BLOCCANTI**.

**Checklist categorie VERDI da coprire (parametri certi minimi):**
La sezione VERDE deve coprire — quando il dato è presente nel documento — almeno tutte
queste categorie. Se manca una categoria, verificare che non sia stata persa:
- `Valore Appalto` (breakdown per voce: start-up, canone, T&M plafond, oneri, totali)
- `Durata` (start-up, base, opzione proroga, proroga tecnica art.120 c.11)
- `Revisione Prezzi` (meccanismo, soglia, formula, indice di riferimento)
- `Tariffe T&M` (una voce per profilo, € per giorno o ora)
- `Volumi T&M` (una voce per profilo, GG/U specificando il periodo)
- `Team Canone` (una voce per profilo del presidio, con N. risorse minime)
- `SLA` (accettazione + risoluzione P1/P2/P3/P4)
- `Orari` (presidio, reperibilità feriale, reperibilità festiva, eventi speciali)
- `Penali` (timing attivazione, fasce LS A/B/C/D/E)
- `Turn over` (limite % per periodo + giorni affiancamento)
- `Valutazione` (tecnica + economica + soglia sbarramento + riparametrazione)
- `Requisiti partecipazione` (servizi analoghi, fatturato, sub-requisiti)
- `Cauzione` (provvisoria %, importo, riduzioni applicabili) + `ANAC` (contributo)
- `Subappalto` (limiti, quota PMI) + `Avvalimento` (ammesso/escluso)
- `Stack tecnologico` (BE, FE, Mobile, SmartTV, DB, container, AI/ML)
- `Parco applicativo` (numero app, mix tecnologico)
- `Vincoli operativi` (lingua, postazioni, VPN, UCC)

**Tipologie di BLOCCANTI da verificare attivamente** (sezione ROSSO):
Per ogni RFP, scorri questa checklist e verifica che ogni categoria sia stata indagata.
Non considerare la sezione ROSSO completa con 1-2 voci ovvie — è meglio averne 5-7 ben
classificate che ometterne uno reale.

a) **INCOERENZE NUMERICHE TRA DOCUMENTI**
   - Volumi GG/U / volumi ticket / dimensione team: stesso parametro con valori diversi
   - Importi a base d'asta vs valori in Allegati / tabelle riepilogative
   - Date di riferimento (situazione attuale, baseline parco applicativo)

b) **INCOERENZE TERMINOLOGICHE TRA DOCUMENTI**
   - Acronimi/sigle usati con label diverse per lo stesso oggetto (es. MAV vs MAD,
     Manutenzione Adeguativa vs Manutenzione Adeguatrice)
   - Profili professionali con nome diverso ma stessa tariffa o stesso ruolo
   - Servizi descritti con perimetro diverso (Capitolato vs Disciplinare)

c) **DATI ASSENTI CRITICI PER LA STIMA**
   - Volumi storici operativi (ticket per priorità, MTTR, chiamate REP/mese)
   - **Soglie quantitative dei punteggi tabellari** (N. risorse certificate richieste
     per ottenere il punteggio massimo per ogni voce) — se assenti è SEMPRE bloccante
   - % minima on-site se modello "ibrido"
   - Tariffa attività fuori orario / straordinari

d) **AMBIGUITÀ INTERPRETATIVE NON RISOLVIBILI INTERNAMENTE**
   - Definizione di "team minimo" vincolante o derogabile (proposta skill mix alternativo)
   - Perimetro reperibilità (BE+FE soltanto o anche Mobile/TV?)
   - SLA H24 o solo durante orario presidio?
   - Manutenzione modelli AI/ML in produzione vs sviluppo ex-novo

### `9. Registro Chiarimenti`
Estende il Sheet 5 con tracciamento dello stato.
Colonne: `#` (stesso del Sheet 5), `Capability`, `Categoria`, `Testo Domanda`,
`Driver che abilita`, `Prio` (drop-down 1/2/3), `Stato` (drop-down Non inviato / Inviato /
Risposta ricevuta), `Data Risposta`, `Sintesi Risposta`, `Impatto se non risolto` (drop-down
ALTO/MEDIO/BASSO), `Bloccante per stima` (drop-down SI/NO).
**Ordina per `Bloccante per stima` decrescente**, poi per `Impatto se non risolto` decrescente.

### `10. Nota di Handoff` — sintesi narrativa
Tre sezioni con titoli fissi:
- **`1. COSA È CONFERMATO`** (riga 3): voci con label in colonna A e contenuto in colonna B.
  Dati estratti utilizzabili direttamente nel cost model senza ulteriori validazioni.
- **`2. COSA È APERTO`** (riga 16): gap e incoerenze non risolti, prefissati per categoria
  (`BLOCCANTE — ...`, `DA ASSUMERE — ...`, `ERRORE CORRETTO — ...`).
- **`3. DECISION POINT CRITICI`** (riga 27): voci con prefisso `DP-NN (CRITICO/ALTO/MEDIO)` e
  descrizione della decisione che il cost modeler deve prendere.

**Regola di coerenza Sheet 10 ↔ Sheet 8 (NON NEGOZIABILE):**
- Ogni voce con prefisso `BLOCCANTE — ...` nella sezione 2 del Sheet 10 DEVE corrispondere
  1:1 a una riga della sezione ROSSO del Sheet 8 (parametri bloccanti). Se nello Sheet 8
  ROSSO ci sono N voci, nel Sheet 10 sezione "COSA È APERTO" ci devono essere almeno N
  voci `BLOCCANTE`.
- Ogni voce `DA ASSUMERE — ...` DEVE corrispondere a una categoria di voci della sezione
  GIALLO del Sheet 8. Aggregazione ammessa: una voce Sheet 10 può raggruppare più voci
  GIALLO Sheet 8 sotto la stessa categoria (es. "DA ASSUMERE — Volumi storici operativi"
  copre MAC, REP, GES, GST volumi).
- Le voci `ERRORE CORRETTO — ...` sono SOLO per refusi banali nel documento (date
  inconsistenti senza impatto stima, sigle scritte male, ecc.). Se l'errore ha impatto
  sulla stima, va categorizzato come `BLOCCANTE` (NON come ERRORE CORRETTO).
  Esempio: "Capitolato cita giugno 2022 e giugno 2025 per il parco applicativo" →
  se la baseline applicativa è critica per la stima → `BLOCCANTE — Data baseline parco
  applicativo` (anche Sheet 8 ROSSO). Solo se il refuso è palesemente innocuo (es. un
  numero di pagina sbagliato) → `ERRORE CORRETTO`.

### `_Esempi` — riferimento di compilazione
Ultimo sheet del workbook. Contiene esempi reali estratti dalla gara RAI, organizzati per sheet
operativo, con il commento del caso esemplificato. Leggilo PRIMA di compilare ogni sheet.

## Granularità minima per sheet

> **IMPORTANTE — i numeri sotto sono FLOOR, non target.** Una RFP enterprise tipica genera
> un workbook ricco. Per RFP enterprise (>€5M) è atteso che il workbook si attesti al
> **130-170% delle soglie sotto**. Un workbook che si attesta al floor è segnale di
> *under-exploration*: rilanciare con focus su Sheet 3 (driver mancanti), Sheet 4 (gap di
> tipo "dato assente critico"), Sheet 5 (domande Prio 2/3 contrattuali e di sizing).

**Per RFP > €5M (importo complessivo IVA esclusa)**:

| Sheet | Floor minimo | Atteso (1,3-1,7×) | Note |
|---|---|---|---|
| Sheet 2 — Mappatura Capability | ≥30 voci, di cui ≥3-5 L3 per L2 | **45-60 voci** | L3 = sotto-attività operative concrete (es. MAC.01 "Diagnosi", MAC.02 "Risoluzione P1-P2", MAC.03 "P3-P4", MAC.04 "Hotfix", MAC.05 "Validazione", MAC.06 "Escalation") |
| Sheet 3 — Driver di Stima | ≥4-6 driver per L2 | **50-70 driver totali** (con 9 L2) | Vedere "Catalogo driver attesi per capability L2" sotto |
| Sheet 4 — Gap Analysis | ≥15 voci (mix ALTA/MEDIA/BASSA) | **20-25 voci** | Una RFP enterprise ha sempre molti gap |
| Sheet 5 — Domande Chiarimento | ≥20 voci (Prio 1+2+3) | **27-35 voci** | Almeno 7-10 di Prio 1 (BLOCCANTI), 8-12 Prio 2 (sizing/operative), 5-8 Prio 3 (contrattuali generali) |
| Sheet 6 — Assunzioni | ≥10 voci con valore numerico | **14-18 voci** | Vedi regola "assunzioni quantificate" |
| Sheet 7 — Matrice Profili | Tutti i profili documentati × tutte le capability T&M (sezione 2) | (idem) | Sezione Canone: solo P esplicite (può risultare scarsa di P, è OK) |
| Sheet 8 VERDE | ≥40 voci coprenti tutte le categorie | **55-70 voci** | Vedi sopra "Checklist categorie VERDI" |
| Sheet 8 GIALLO | ≥10 voci | **13-18 voci** | Costi interni, overhead, volumi storici, pricing, inflazione |
| Sheet 8 ROSSO | ≥3 voci | **5-8 voci** | Una RFP senza alcun bloccante è altamente sospetta |
| Sheet 9 — Registro Chiarimenti | = Sheet 5 (1:1) | (idem) | Stesso numero, ordinato per Bloccante DESC |
| Sheet 10 — Nota Handoff | ≥10 confermati, ≥6 aperti, ≥3 decision point | **15-20 / 8-12 / 4-6** | Sezioni proporzionate al rischio della RFP |

**Per RFP < €5M:** ridurre proporzionalmente le soglie (×0,6 indicativo), mantenendo
sempre la copertura completa di tutte le capability L2 (no scope coverage debt).

## Catalogo driver attesi per capability L2 (riferimento estrazione)

Per ogni L2 standard, la skill deve valutare attivamente la presenza/assenza dei
seguenti driver e registrarli in Sheet 3. **La lista non è esaustiva — è il floor di
esplorazione**: ogni driver mancante che si scopre durante l'analisi va aggiunto come
voce della colonna "Driver Mancante / Gap".

### MAC — Manutenzione Correttiva
**Driver presenti tipici** (estrarre se in documento): priorità P1-P4, SLA accettazione,
SLA risoluzione, fasce penali, orario copertura, numero applicazioni in perimetro.
**Driver mancanti tipici** (registrare se assenti): volume storico ticket/anno per priorità,
MTTR storico, effort medio per priorità (ore/ticket), % first-call resolution vs escalation,
distribuzione complessità app coinvolte (semplice/media/critica), frequenza hotfix urgenti
fuori ciclo deploy, % esiti workaround vs risoluzione completa, tool monitoring/APM in uso.

### REP — Reperibilità
**Presenti**: orari reperibilità, cap eventi speciali, perimetro tecnologico (BE/FE/Mobile/SmartTV).
**Mancanti**: numero medio chiamate REP/anno per fascia oraria, durata media intervento (ore),
% chiamate che richiedono escalation a presidio canone diurno, calendario eventi live
(Sanremo, Mondiali, elezioni), profili dedicati eventi speciali, ore presidio rinforzato/giorno.

### GES — Gestione Applicativi/DB
**Presenti**: lista esemplificativa attività, fasce dimensione (≤2gg/≤5gg/>5gg), copertura oraria.
**Mancanti**: volume ticket GES/anno per fascia dimensione, mix tipologie (DB ops, upgrade,
ad-hoc, deploy, modifiche massive), N. applicazioni per livello complessità gestionale,
frequenza interventi DB critici (tuning, restore, failover), tool monitoring esistenti,
N. certificati SSL da gestire + frequenza rotazione, stack DB (Oracle/MongoDB/Elastic).

### GST — Gestione Attività Standard
**Presenti**: catalogo attività con effort noto (lista soggetta ad aggiornamento RAI).
**Mancanti**: catalogo concreto con voci/effort/frequenza, volume attività per fascia
effort/anno, frequenza deploy/rilasci per applicazione (release cadence), stack CI/CD
in uso (Jenkins/GitLab CI/ArgoCD/altro), modalità di pubblicazione store enterprise.

### CON — Conferimento
**Presenti**: 3 modalità (presa carico / conferimento / dismissione), esclusioni Variazione.
**Mancanti**: numero atteso nuove app/anno e dismissioni, dimensione media app in
conferimento (righe codice, API, DB), N. dismissioni previste nel periodo
contrattuale, effort onboarding per app, calendario previsto presa in carico.

### MAV — Manutenzione Adeguativa
**Presenti**: 4 profili T&M con tariffe, volumi GG/U Disciplinare.
**Mancanti**: backlog MAV stimato (N. richieste + effort medio), distribuzione MAV
per dominio tecnologico (BE/FE/Mobile/TV/CMS), frequenza aggiornamenti normativi
attesi (ePrivacy, accessibilità), roadmap tecnologica cliente N+1, N+2 (upgrade
pianificati Java, framework, librerie).

### MEV — Manutenzione Evolutiva
**Presenti**: processo Pacchetto di Lavoro, SLA stima/accettazione, stack tecnologico,
app strategiche evidenziate.
**Mancanti**: backlog MEV per applicazione (N. richieste/anno + effort stimato),
distribuzione MEV per dominio (BE/FE/Mobile/SmartTV/CMS) in %, dimensione media MEV
(GG/U per richiesta) con distribuzione small/medium/large, frequenza richieste urgenti
vs pianificate, governance MEV (chi approva), tool tracciamento (JIRA/Confluence/Azure DevOps).

### PRJ — Progetto (nuovo sviluppo)
**Presenti**: tariffe profili, processo RDE (Richiesta Esecuzione).
**Mancanti**: pipeline progetti prossimi 12-18 mesi (N., natura, complessità, dimensione
media GG/U), durata media progetto (mesi, N. profili), modalità governance progettuale
(PMO interno, tool, ruoli approvazione), criteri di accettazione tipici (Definition of
Done, test coverage, KPI qualità), tariffa attività fuori orario standard (250h/anno).

### SPE — Servizi Specialistici
**Presenti**: categorie menzionate (Security, AI/ML, Cloud, Data, Performance).
**Mancanti**: volume richieste specialistiche per categoria/anno, framework interni
cliente per security assessment, ambito AI/ML (modelli in prod vs sviluppo ex-novo,
infrastruttura MLOps), profili dedicati ammessi vs coperti dai 4 profili tariffari standard.

## Workflow

### Step 1 — Lettura documenti
Leggi tutti i documenti commerciali e tecnici. Se è presente `rfp_analysis.json`, leggilo come
contesto aggiuntivo (non sostituisce la lettura dei documenti).

### Step 2 — Lettura preventiva del template
Apri `assets/template_rfp_handoff.xlsx` e leggi:
- L'ordine e il nome esatto degli sheet.
- Lo sheet `_Esempi` per capire formato, granularità e tono.
- I drop-down/data validation di ogni sheet (per allineare i valori).

### Step 3 — Costruzione bozza interna
Costruisci internamente la mappatura completa di tutti gli sheet, marcando ogni dato come
`estratto` / `inferito` / `assunto`. **Non scrivere ancora il file.**

### Step 4 — Presentazione registro scelte interpretative
Presenta in chat il registro come da Step B della sezione "Comportamento interattivo".

### Step 5 — Attesa approvazione esplicita dell'utente
**FERMATI.** Non procedere finché l'utente non risponde con approvazione esplicita o richieste
di modifica.

### Step 6 — Applicazione modifiche (se richieste)
Se l'utente chiede modifiche, applicale e ripresenta il registro aggiornato. Ripeti lo Step 5
finché non c'è approvazione completa.

### Step 7 — Copia del template e popolamento
1. Copia `assets/template_rfp_handoff.xlsx` in `rfp_handoff.xlsx` nella working directory dell'utente.
2. Apri il file copiato (delegando alla skill `xlsx` per le operazioni di scrittura).
3. Per ogni sheet, popola le celle rispettando:
   - intestazioni di colonna esistenti (non rinominarle)
   - drop-down/data validation (usa solo valori ammessi)
   - layout a sezioni (sheet 1, 7, 8, 10): non spostare i titoli di sezione
4. Sheet 7: prima di scrivere i profili, sostituisci le intestazioni E:N con le capability L2
   reali della RFP.
5. Sheet 8: copia in sezione ROSSO tutte le incoerenze tra documenti registrate nel sheet 4.
6. Sheet 9: ordina per `Bloccante per stima` decrescente.
7. Sheet 10: scrivi label brevi in colonna A (es. "Valore appalto", "BLOCCANTE — Volumi T&M",
   "DP-01 (CRITICO)") e contenuto disteso in colonna B.

### Step 8 — Riepilogo finale
Presenta all'utente un riepilogo Markdown:

> **Pacchetto di handoff RFP — [Nome progetto]**
>
> **Cliente:** [...] | **Modello:** [...] | **Durata:** [...] | **Industry:** [...]
>
> **Capability mappate:** N (L1: A, L2: B, L3: C)
>
> **Driver:** P presenti / M mancanti
>
> **Gap bloccanti:** N | **Incoerenze tra documenti:** N
>
> **Domande al cliente:** N (Prio 1: N, Prio 2: N, Prio 3: N)
>
> **Profili nella matrice:** N | **Celle "Non esplicitato":** N
>
> **Parametri Cost Model:** Verdi N | Gialli N | Rossi N
>
> **Decision point critici:** N
>
> File prodotto: `rfp_handoff.xlsx`
>
> **Prossimo passo immediato:** invoca la skill `gara-rfp-deck` passandole
> `rfp_handoff.xlsx` per produrre l'Executive Summary PPTX. È il **primo deliverable di
> brainstorming** che delivery e bid manager usano per allinearsi prima di muovere i
> chiarimenti al cliente.
>
> **Catena del processo (4 step):**
> - ✅ Fase 1 (questa skill): `rfp_handoff.xlsx` prodotto
> - ⏭ Step 2 (immediato): invoca `gara-rfp-deck` → `executive_summary.pptx` (10 slide)
>   come deliverable di brainstorming delivery/bid PRIMA dei chiarimenti
> - ⏭ Fase 2 (manuale): bid manager invia le domande del Sheet 9 al cliente, riceve
>   risposte, aggiorna Stato/Sintesi nel Sheet 9, valorizza eventuali parametri
>   "DA ASSUMERE" del Sheet 8 con i nuovi dati
> - ⏭ Fase 3: invoca `gara-effort-cost-estimator` passandole il workbook handoff
>   aggiornato per produrre il Cost Model commerciale (Stima Effort, Cost Model,
>   Sensitivity Pricing, Risk Register)

## Tracciabilità

Per ogni dato nel workbook, classifica la certezza:

- `estratto` — presente verbatim nel documento (cita sezione/pagina, max 20 parole verbatim).
- `inferito` — ricavabile dal contesto (motiva il ragionamento).
- `assunto` — assente nel documento; richiede conferma utente nel registro Step B.

Tutti gli `assunto` confluiscono nel sheet `6. Assunzioni`. Tutte le `incoerenze` confluiscono
nel sheet `4. Gap Analysis` e replicate nel sheet `8. Input Cost Model` come BLOCCANTI.

## Regole operative

- **Comportamento interattivo non negoziabile**: la skill SI FERMA dopo lo Step 4 e attende
  approvazione. Non popolare il template prima.
- **Non stimare GG/U**: nessun valore di effort in nessun output. Le tariffe T&M e i volumi
  GG/U citati nei documenti sono dati estratti, non stime.
- **Non riconciliare incoerenze tra documenti**: registrarle come gap bloccanti nel Sheet 4 e
  replicarle nel Sheet 8 sezione ROSSA.
- **Profili x capability solo da fonte esplicita**: le celle E:N del Sheet 7 si compilano
  esclusivamente quando il documento assegna esplicitamente un profilo a una capability. Cella
  vuota = "Non esplicitato nel documento".
- **Sheet 7 intestazioni dinamiche**: prima di popolare, sostituisci le intestazioni di colonna
  E:N con le capability L2 effettive della RFP.
- **Drop-down rispettati**: i valori ammessi nei campi a lista chiusa sono i seguenti:
  - Livello (Sheet 2 col A): `L1`, `L2`, `L3`
  - Tipo Contratto (Sheet 2 col D): `Canone`, `T&M`, `Start-up`, `Misto`
  - Impatto sulla Stima (Sheet 3 col E): `ALTO`, `MEDIO`, `BASSO`
  - Affidabilità Stima (Sheet 3 col F): `ALTA`, `MEDIA`, `BASSA`
  - Priorità (Sheet 4 col F): `ALTA`, `MEDIA`, `BASSA`
  - Azione (Sheet 4 col G): `Chiarimento`, `Assunzione`, `Workshop`, `Decisione interna`
  - Prio (Sheet 5/9 col F): `1`, `2`, `3`
  - Rischio (Sheet 6 col G): `ALTO`, `MEDIO`, `BASSO`
  - Tipo (Sheet 7 col A): `Canone`, `T&M`, `Misto`
  - Assegnazione capability (Sheet 7 col E:N): `P-DOC` (Primario estratto), `P-IPO` (Primario ipotizzato + rationale in col D), `S-DOC` (Supporto estratto), `S-IPO` (Supporto ipotizzato + rationale), oppure vuoto
  - Stato (Sheet 9 col G): `Non inviato`, `Inviato`, `Risposta ricevuta`
  - Impatto se non risolto (Sheet 9 col J): `ALTO`, `MEDIO`, `BASSO`
  - Bloccante per stima (Sheet 9 col K): `SI`, `NO`
- **Coerenza ID**: il `#` del Sheet 5 è lo stesso del Sheet 9 (la stessa domanda).
- **Lettura preventiva di `_Esempi` obbligatoria** prima di popolare ogni sheet.
- **Output sempre in italiano**, salvo richiesta esplicita diversa.
- **Profili professionali ammessi nello Sheet 7**: solo quelli esplicitamente definiti
  nei documenti di gara. NIENTE profili inventati (DBA, DevOps, QA, ML Engineer, ecc.)
  se non sono nominati come profilo a sé stante.
- **Coerenza Sheet 10 ↔ Sheet 8**: ogni `BLOCCANTE — ...` del Sheet 10 sez.2 = una riga
  del Sheet 8 sez. ROSSO. Ogni `DA ASSUMERE — ...` del Sheet 10 sez.2 = uno o più voci
  del Sheet 8 sez. GIALLO della stessa categoria.
- **Assunzioni di volume quantificate**: numero provvisorio basato su benchmark, non
  rinvio al cost modeler (vedi regola Sheet 6).

## Validazione pre-output (self-check obbligatorio prima del Step 8)

Prima di presentare il riepilogo finale all'utente, la skill DEVE eseguire un self-check
sui contenuti scritti nel file e segnalare eventuali violazioni delle regole sopra.

Checklist di validazione (esegui in ordine, ferma all'errore):

1. **Tutte le categorie della "Checklist di estrazione OBBLIGATORIA" sono coperte?**
   In particolare, **revisione prezzi** è presente come voce VERDE Sheet 8 se citata nei
   documenti? (controllo che cattura uno dei più frequenti errori di omissione).

2. **Numero risorse presidio**: il valore in Sheet 1 B61 corrisponde alla somma stretta
   delle figure professionali della tabella di dimensionamento del presidio? Eventuali
   ruoli responsabili (SM, PM, REC) sono separati?

3. **Sheet 7 sezione Canone**: ci sono `P` assegnate per inferenza? Per ogni `P` nella
   sezione Canone, esiste una citazione esplicita nel documento che assegna quel profilo
   a quella capability?

4. **Sheet 7 — profili inventati**: tutti i profili in colonna B sono presenti
   nell'Allegato Figure Professionali del Capitolato? Nessun profilo come "DBA",
   "DevOps", "QA", "ML Engineer" inserito senza presenza esplicita?

5. **Granularità**: la numerosità di ogni sheet rispetta la soglia minima della sezione
   "Granularità minima per sheet" in funzione del valore RFP?

6. **Coerenza Sheet 10 ↔ Sheet 8**: ogni `BLOCCANTE — ...` del Sheet 10 ha un
   corrispondente nello Sheet 8 ROSSO? Nessuna voce in `ERRORE CORRETTO` ha in realtà
   impatto sulla stima (in quel caso va promossa a `BLOCCANTE`)?

7. **Tipologie di bloccanti coperte**: lo Sheet 8 ROSSO copre incoerenze numeriche,
   terminologiche, dati assenti critici e ambiguità interpretative? Nessuna categoria
   è stata trascurata?

8. **Assunzioni quantificate**: le assunzioni di volume nello Sheet 6 hanno un valore
   numerico provvisorio? Le voci "Da valorizzare" stanno nello Sheet 8 GIALLO, non qui?

9. **Tracciabilità profili Sheet 2 col E**: ogni cella `Profili Coinvolti` ha tag
   esplicito `[DOC: <fonte>]` per profili estratti o `[IPOTIZZATO] | rationale: <motivo>`
   per profili ipotizzati? Nessuna lista di profili è priva di classificazione di
   provenienza?

10. **Tracciabilità Sheet 7 celle E:N**: i valori sono `P-DOC` / `P-IPO` / `S-DOC` / `S-IPO`
    (non più `P` / `S` puro)? Ogni `*-IPO` ha rationale in col D `Fonte`? Ogni `*-DOC` ha
    citazione documentale puntuale in col D?

Se uno qualsiasi di questi check fallisce: **correggi il file prima di presentare il
riepilogo all'utente**. Non chiedere conferma per le correzioni di self-check.

## Asset

- `assets/template_rfp_handoff.xlsx` — template ufficiale del workbook di handoff. Non modificarlo
  in place: copialo nella working directory dell'utente come `rfp_handoff.xlsx` e popolalo lì.
