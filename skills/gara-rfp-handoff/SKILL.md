---
name: gara-rfp-handoff
description: >
  Analizza la documentazione commerciale e tecnica di una RFP e produce un workbook Excel di
  handoff per il team che dovrà stimare. Si basa su un template predefinito (`assets/template_rfp_handoff.xlsx`)
  con 10 sheet operativi numerati + 1 sheet Requisiti + 1 sheet di esempi: Info Sintetiche RFP,
  Mappatura Capability, Requisiti, Driver di Stima, Gap Analysis, Domande Chiarimento,
  Assunzioni, Matrice Profili x Capability, Input Cost Model, Registro Chiarimenti, Nota di Handoff.
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
  PREREQUISITO OBBLIGATORIO: la skill richiede in input `requisiti_estratti.json` prodotto da
  `gara-req-extractor` (schema v2.0). Se il file non è nella working directory, la skill si
  ferma e indirizza l'utente a `gara-req-extractor` prima di proseguire. Opzionalmente, se è
  presente `rfp_analysis.json` prodotto da `gara-rfp-analyzer`, viene usato come contesto.
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

## Posizionamento nel workflow `gara-*`

Questa è la **Step 4 della Fase 1** del workflow gara end-to-end orchestrato da
`gara-workflow`. Sequenza completa: `gara-workflow` → `gara-rfp-analyzer` →
`gara-req-extractor` → **`gara-rfp-handoff` (qui)** → `gara-rfp-deck` → [Fase 2 manuale] →
`gara-effort-cost-estimator` (sempre) + `gara-bid-estimator` (condizionale).

La skill resta richiamabile **standalone** se serve solo l'handoff verso il team di stima
(richiede comunque `requisiti_estratti.json` come prerequisito obbligatorio già introdotto).

---

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

- **Obbligatorio**: `requisiti_estratti.json` prodotto da `gara-req-extractor` (schema v2.0)
  presente nella working directory. Se manca, la skill **si ferma** e indirizza l'utente a
  `gara-req-extractor` prima di proseguire (vedi Workflow → Step 1bis).
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

Il file `assets/template_rfp_handoff.xlsx` contiene 12 sheet (ordine esatto):
`1. Info Sintetiche RFP`, `2. Mappatura Capability`, `Requisiti`, `3. Driver di Stima`,
`4. Gap Analysis`, `5. Domande Chiarimento`, `6. Assunzioni`, `7. Matrice Profili x Capability`,
`8. Input Cost Model`, `9. Registro Chiarimenti`, `10. Nota di Handoff`, `_Esempi`.

Lo sheet `Requisiti` è inserito in posizione fisica 3 (subito dopo `2. Mappatura Capability`)
ma **non porta prefisso numerico**: i sheet numerati 3-10 mantengono i loro numeri originali
per non rompere le skill a valle (`gara-rfp-deck`, `gara-effort-cost-estimator`) che li
referenziano per nome.

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

### `Requisiti` — elenco requisiti scope (popolato da `gara-req-extractor`)

Sheet **read-only dalla sorgente JSON**. Una riga per ogni elemento dell'array `requisiti`
del file `requisiti_estratti.json` (schema v2.0). 16 colonne, mappa 1:1 con il JSON:

| Col | Header | Origine JSON | Drop-down ammessi |
|---|---|---|---|
| A | `ID` | `id` (es. `REQ-001`, `REQ-001.1`) | — |
| B | `Tipo` | `tipo` | `padre`, `figlio`, `singolo` |
| C | `ID Padre` | `padre_id` (vuoto se `tipo` ≠ figlio) | — |
| D | `Area Funzionale` | `area_funzionale` | (12-14 aree predefinite dell'extractor) |
| E | `Testo Bando` | `testo_bando` (verbatim o parafrasi fedele) | — |
| F | `Soluzione Proposta` | `soluzione_proposta` (Schermate / API / Dati / Processi) | — |
| G | `Inferenza` | `inferenza` | `esplicito`, `stimato`, `da_chiarire` |
| H | `Note Inferenza` | `note_inferenza` (vuoto se `inferenza = esplicito`) | — |
| I | `Rationale Requisito` | `rationale_requisito` (1-2 frasi) | — |
| J | `Rationale Soluzione` | `rationale_soluzione` (1-3 frasi) | — |
| K | `Categoria Scope` | `categoria_scope` | `custom_software`, `cots_product`, `service_external`, `out_of_scope` |
| L | `Scope Dettaglio` | `scope_dettaglio` serializzato `nome_prodotto | fornitore | tipo_costo | motivazione` | — |
| M | `Priorità` | `priorita` | `must_have`, `should_have`, `nice_to_have` |
| N | `Certezza` | `certezza` | `estratto`, `inferito`, `assunto` |
| O | `Fonte (Pag/Sez)` | `fonte_pag` | — |
| P | `Fonte Estratto` | `fonte_estratto` (max 20 parole verbatim) | — |

**Regole di popolamento**:
- Una riga per ogni elemento di `requisiti[]`. Ordine = stesso del JSON (già ordinato per area
  e tipo padre/figlio in `gara-req-extractor`).
- Per ogni `tipo = figlio`, il valore di `padre_id` in col C deve corrispondere a un `id`
  presente in col A: verificato dal self-check (check 11).
- Col L (`Scope Dettaglio`) si compila solo se `categoria_scope ≠ custom_software`. Serializza
  l'oggetto `scope_dettaglio` come stringa unica con separatore ` | `: ordine fisso
  `nome_prodotto | fornitore | tipo_costo | motivazione`. Se uno dei campi è null, lascia
  vuoto il segmento ma mantieni i separatori.
- Le `domande_bloccanti` del JSON **NON vanno qui**: confluiscono nel `5. Domande Chiarimento`
  e nel `9. Registro Chiarimenti` (vedi regole specifiche dei due sheet).
- **Non modificare a mano**: lo sheet riflette 1:1 il JSON. Se serve aggiungere/correggere
  un requisito, ri-eseguire `gara-req-extractor` e ri-popolare. Modifiche manuali introducono
  drift con `gara-bid-estimator` che legge dallo stesso JSON.

**Stile differenziato per `tipo` (regola di rendering).** Le righe `padre` rappresentano
visivamente un **contenitore** dei propri figli e devono distinguersi a colpo d'occhio.
Schema obbligatorio:

| Tipo | Fill riga | Font colonne label (A, B, D, E, M) | Font colonne verbose |
|---|---|---|---|
| `padre` | `#E0E7FF` lavanda chiara | `#3730A3` viola scuro **bold** | `#1E1B4B` viola molto scuro regular |
| `figlio` | nessuno | nero `#000000` regular | nero `#000000` regular |
| `singolo` | nessuno | nero `#000000` regular | nero `#000000` regular |

Effetto visivo atteso: scorrendo lo sheet, ogni "blocco gerarchico" è una riga padre
lavanda+bold seguita dalle sue figli regular. Le righe `singolo` (capability non gerarchica)
sono visivamente identiche alle figli — la sola differenza è la colonna B (`Tipo`).

Le colonne `verbose` (col C `ID Padre`, F `Soluzione Proposta`, G-N varie, O-P fonte) ricevono
sul padre il font color più scuro `#1E1B4B` ma non bold, per mantenere leggibilità su
testi lunghi. Le colonne `label` (A `ID`, B `Tipo`, D `Area Funzionale`, E `Testo Bando`, M
`Priorità`) ricevono il font bold viola `#3730A3`.

Allineamento: `left + top + wrap_text` per le colonne testuali, `center` per A/G/K/M/N.

Snippet:
```python
from openpyxl.styles import Font, PatternFill, Alignment
PARENT_FILL = PatternFill('solid', fgColor='E0E7FF')
LABEL_COLS = (1, 2, 4, 5, 13)  # A, B, D, E, M
for r in data_rows:
    tipo = str(ws.cell(row=r, column=2).value or '').strip()
    if tipo == 'padre':
        for c in range(1, 17):
            cell = ws.cell(row=r, column=c)
            cell.fill = PARENT_FILL
            color = '3730A3' if c in LABEL_COLS else '1E1B4B'
            cell.font = Font(name='Calibri', size=10, color=color,
                             bold=(c in LABEL_COLS))
    else:  # figlio o singolo
        for c in range(1, 17):
            cell = ws.cell(row=r, column=c)
            cell.fill = PatternFill(fill_type=None)
            cell.font = Font(name='Calibri', size=10, color='000000')
```

**Why questa scelta cromatica.** La tinta lavanda `#E0E7FF` è deliberatamente fuori dal
palette semaforico già usato negli altri sheet (verde/giallo/rosso/azzurro per criticità in
Sheet 5/8/9/10, verde/giallo/azzurro/viola chiaro per primary/support in Sheet 7) — la
gerarchia padre-figlio non è una scala di criticità ma una **struttura**, quindi richiede una
palette propria. Il viola scuro `#3730A3` mantiene il contrasto WCAG AA sul fill lavanda.

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

**Posizionamento e ciclo di vita.** Lo Sheet 5 è la **baseline statica** delle domande
prodotta a fine Fase 1. Una volta scritto non viene più toccato: serve come catalogo di
riferimento per allegare all'offerta tecnica, per generare il PDF da inviare al portale
chiarimenti del cliente, e come "snapshot iniziale" da confrontare a fine Fase 2 per
capire cosa è cambiato. Lo Sheet 9 è la **vista viva** delle stesse domande con tracciamento
di stato: la stessa lista, ma estesa con campi che evolvono (Stato, Data Risposta, Sintesi,
Bloccante per stima). Il `#` è identico tra i due sheet (regola di coerenza ID) così è
sempre possibile riconciliare. **Regola pratica:** dopo aver compilato Sheet 5, replicare
immediatamente le righe in Sheet 9 con `Stato = Non inviato` — vedi sezione Sheet 9.

Colonne: `#`, `Capability`, `Categoria` (es. Volume/Sizing, Tecnica, Contrattuale, Procedurale),
`Testo Domanda`, `Motivazione / Impatto sulla Stima`, `Prio` (drop-down 1/2/3 — 1=critica).
Le domande devono essere **specifiche e azionabili** — niente domande generiche tipo
"ci può fornire più dettagli?".

**Merge delle `domande_bloccanti` di `requisiti_estratti.json`**: ogni elemento dell'array
`domande_bloccanti` del JSON diventa una riga in questo sheet con:
- `Capability` = `area` del JSON (es. `Autenticazione & IAM`)
- `Categoria` = `Scope/Requisito` (categoria dedicata al merge dal JSON)
- `Testo Domanda` = `[Q-NNN] ` + `domanda` del JSON + ` (opzioni: ` + join di `opzioni` + `)` —
  il prefisso `[Q-NNN]` (con NNN = `id` del JSON, es. `[Q-001]`) è obbligatorio per la
  tracciabilità verso la sorgente.
- `Motivazione / Impatto sulla Stima` = `impatto_stima` del JSON
- `Prio` = `1` (le `domande_bloccanti` sono sempre critiche per definizione)

**Stile semaforico colonna `Prio` (obbligatorio).** Applicare alla cella `F{r}` di ogni
domanda un fill e font color che rispecchino la priorità, in modo che il lettore identifichi
a colpo d'occhio le criticità. Stesso schema da replicare 1:1 nello Sheet 9 (vedi sezione
`9. Registro Chiarimenti` per cross-sheet consistency).

| Prio | Fill | Font | Semantica |
|---|---|---|---|
| `1` | `#FEE2E2` rosso chiaro | `#991B1B` rosso scuro bold | Critica — chiarimento bloccante |
| `2` | `#FED7AA` arancione chiaro | `#9A3412` arancione scuro bold | Alta — sizing/operativa |
| `3` | `#DCFCE7` verde chiaro | `#15803D` verde scuro bold | Bassa — contrattuale generale |

Allineamento centrato. La colorazione tocca solo la cella `Prio` (col F), non l'intera riga
(le righe restano neutre per non saturare visivamente).

Snippet:
```python
from openpyxl.styles import Font, PatternFill, Alignment
PRIO_STYLE = {
    '1': ('FEE2E2', '991B1B'),  # rosso
    '2': ('FED7AA', '9A3412'),  # arancione
    '3': ('DCFCE7', '15803D'),  # verde
}
CENTER = Alignment(horizontal='center', vertical='center')
for r in range(4, last_row + 1):
    cell = ws.cell(row=r, column=6)  # F = Prio
    key = str(cell.value or '').strip()
    if key in PRIO_STYLE:
        fg, fc = PRIO_STYLE[key]
        cell.fill = PatternFill('solid', fgColor=fg)
        cell.font = Font(name='Calibri', size=10, color=fc, bold=True)
        cell.alignment = CENTER
```

**Bug storico (15/05/2026 RAI Sistemi Informativi):** il template aveva Prio 1 in rosso
ma Prio 2 e Prio 3 entrambe in giallo (`#FEF3C7`) — il lettore non distingueva tra "alta"
e "bassa". Sullo Sheet 9 le 3 priorità erano tutte bianche. Fix: template patchato (60
celle Prio reset) + schema fisso codificato nella skill.

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

**Stile semaforico obbligatorio per le celle E:N (regola di rendering).** Le celle valorizzate
con tag devono essere riformattate dopo la scrittura per dare al lettore un heatmap
immediatamente leggibile. Non è opzionale: il fill placeholder del template (`#F8FAFC` con
font `#CBD5E1`) rende i valori illeggibili in Excel e va sempre sovrascritto.

Schema cromatico da applicare a ogni cella E:N popolata:

| Tag | Fill (hex) | Font (hex) | Bold | Semantica visiva |
|---|---|---|---|---|
| `P-DOC` | `#DCFCE7` (verde chiaro) | `#15803D` (verde scuro) | sì | Primario certo → certezza alta |
| `P-IPO` | `#FEF3C7` (giallo chiaro) | `#92400E` (ambra scuro) | sì | Primario ipotizzato → warning, da validare |
| `S-DOC` | `#DBEAFE` (azzurro chiaro) | `#1E40AF` (blu scuro) | sì | Supporto certo |
| `S-IPO` | `#EDE9FE` (viola chiaro) | `#6B21A8` (viola scuro) | sì | Supporto ipotizzato |
| (cella vuota) | nessuno (`fill_type=None`) | nero (`#000000`) | no | N/A — non assegnato |

Snippet Python di riferimento (da applicare a tutte le celle profilo, righe Canone + T&M,
colonne E:N):
```python
from openpyxl.styles import Font, PatternFill, Alignment
SEMAPHORE = {
    'P-DOC': ('DCFCE7', '15803D'),
    'P-IPO': ('FEF3C7', '92400E'),
    'S-DOC': ('DBEAFE', '1E40AF'),
    'S-IPO': ('EDE9FE', '6B21A8'),
}
CENTER = Alignment(horizontal='center', vertical='center')
for r in profile_rows:                       # righe profilo Canone + T&M
    for c in range(5, 15):                   # colonne E-N
        cell = ws.cell(row=r, column=c)
        val = str(cell.value or '').strip()
        if val in SEMAPHORE:
            fg, fc = SEMAPHORE[val]
            cell.fill = PatternFill('solid', fgColor=fg)
            cell.font = Font(name='Calibri', size=10, color=fc, bold=True)
        else:
            cell.fill = PatternFill(fill_type=None)
            cell.font = Font(name='Calibri', size=10, color='000000')
        cell.alignment = CENTER
```

**Legenda riga 4 da riscrivere** per riflettere lo schema cromatico (sovrascrivi il testo
originale "LEGENDA: P = Primario..." che si riferisce alla notazione vecchia P/S):
```
LEGENDA — P-DOC (verde) Primario estratto • P-IPO (giallo) Primario ipotizzato + rationale
in col D • S-DOC (azzurro) Supporto estratto • S-IPO (viola) Supporto ipotizzato •
cella vuota = N/A
```

**Merge fantasma del template (anti-data-loss specifico Sheet 7).** Il template
`assets/template_rfp_handoff.xlsx` ha (versioni precedenti la patch del 15/05/2026)
due `MergedCellRange` residui sulle righe `A23:N23` e `A29:N29` non visibili ma che
intercettano la scrittura: un `safe_set(ws, 23, 2, ...)` viene silenziosamente rifiutato
perché `B23` è MergedCell, e il profilo destinato a quella riga sparisce. Bug osservato
sulla gara RAI Sistemi Informativi: il profilo `Technical Leader / Analista Funzionale T&M`
(5.100+3.400 GG/U, €250/gg) andò perso lasciando solo `A23='T&M'` e B23 vuoto.

Prassi obbligatoria all'inizio del popolamento Sheet 7:
```python
for rng in ['A23:N23', 'A29:N29']:
    if rng in [str(r) for r in ws.merged_cells.ranges]:
        ws.unmerge_cells(rng)
```
Dopodiché il banner `SERVIZI A RICHIESTA T&M` va ricostruito a riga 21 (subito dopo
i 14 profili Canone in righe 6-19) con merge esplicito + stile coerente al banner Canone:
```python
ws.cell(row=21, column=1).value = 'SERVIZI A RICHIESTA T&M - Profili a tariffa giornaliera (...)'
ws.merge_cells('A21:N21')
banner = ws.cell(row=21, column=1)
banner.fill = PatternFill('solid', fgColor='1E3A5F')   # stesso del banner Canone
banner.font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
banner.alignment = Alignment(horizontal='left', vertical='center', indent=1)
```
I 4 profili T&M (Architetto, TL/Analista Funzionale, AP, Prog) seguono nelle righe 22-25.
Eseguire questa unmerge **prima** di popolare la sezione T&M, altrimenti il TL/Analista
Funzionale a riga 23 viene perso senza errore esplicito.

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

**Stile esplicito su ogni riga popolata (regola di rendering anti-leak).** Non
affidarsi al pre-styling che il template potrebbe avere su un sotto-intervallo di righe:
i contenuti delle 3 sezioni hanno lunghezza variabile per ogni RFP (es. la sezione VERDE
può avere 40 voci per una RFP piccola o 90 per una enterprise) e qualunque pre-styling
del template per N righe finirà sempre o sotto-allocato (le ultime righe restano senza
stile) o sovra-allocato con tinte sbagliate (righe verdi che cadono dentro la zona
pre-stilizzata gialla/rossa).

Pertanto: dopo aver scritto i contenuti, **applicare esplicitamente lo stile per gruppo
a tutte e sole le righe effettivamente popolate**, scorrendole una per una. Schema
cromatico fisso (coerente con lo stile semaforico dello Sheet 7):

| Gruppo | Fill riga | Font riga | Fill banner | Font banner |
|---|---|---|---|---|
| VERDE (Parametri Certi) | `#DCFCE7` | `#065F46` | `#15803D` | `#FFFFFF` bold |
| GIALLO (Da Assumere) | `#FEF3C7` | `#92400E` | `#D97706` | `#FFFFFF` bold |
| ROSSO (Bloccanti) | `#FEE2E2` | `#991B1B` | `#B91C1C` | `#FFFFFF` bold |

Per la colonna `#` (col A) di ogni riga di contenuto, applicare bold; le altre colonne
in regular. Banner di sezione: merge `A:F`, font bianco bold 11pt, allineamento sinistro
con indent 1.

Snippet di riferimento:
```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
GROUP_STYLE = {
    'V': ('DCFCE7', '065F46', '15803D'),  # fill_row, font_row, fill_banner
    'G': ('FEF3C7', '92400E', 'D97706'),
    'R': ('FEE2E2', '991B1B', 'B91C1C'),
}
THIN = Side(border_style='thin', color='E5E7EB')
ROW_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True, indent=1)

# Banner di sezione
for grp, banner_r in banner_rows.items():
    fill_row, font_row, fill_banner = GROUP_STYLE[grp]
    ws.merge_cells(f'A{banner_r}:F{banner_r}')
    cell = ws.cell(row=banner_r, column=1)
    cell.fill = PatternFill('solid', fgColor=fill_banner)
    cell.font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)

# Righe di contenuto - ESPLICITAMENTE su ogni riga popolata, dalla prima all'ultima
for grp, rows in content_groups.items():     # rows = [9,10,...,94] per V, ecc.
    fill_row, font_row, _ = GROUP_STYLE[grp]
    fill = PatternFill('solid', fgColor=fill_row)
    for r in rows:
        for c in range(1, 7):   # A-F
            cell = ws.cell(row=r, column=c)
            cell.fill = fill
            cell.font = Font(name='Calibri', size=10, color=font_row, bold=(c == 1))
            cell.alignment = LEFT
            cell.border = ROW_BORDER
```

**Bug storico evitato (15/05/2026 RAI Sistemi Informativi):** le precedenti generazioni
del workbook avevano l'ultima riga di ogni gruppo senza stile (es. V86 era bianca con
font default mentre V1-V85 erano verdi) perché lo script si affidava al pre-styling del
template anziché applicare lo stile riga per riga. Inoltre, alcune righe verdi cadevano
fisicamente dentro la zona pre-stilizzata gialla/rossa del template, finendo colorate
in modo errato. Il template è ora stato patchato per rimuovere il pre-styling fragile
delle righe di contenuto (le righe 9..120 non hanno più alcun fill di default), così
ogni generazione DEVE applicare esplicitamente lo stile per gruppo come da snippet sopra.

### `9. Registro Chiarimenti`
Estende il Sheet 5 con tracciamento dello stato — è il **diario vivo** della Fase 2 manuale
(invio domande al cliente, raccolta risposte). A fine Fase 1 (output di questa skill) tutte
le righe sono in stato `Non inviato`; durante la Fase 2 il bid manager aggiorna ogni riga
mano a mano che le risposte arrivano dal cliente. La sua evoluzione è ciò che sblocca la
Fase 3 (cost-estimator): quando tutti i `Bloccante per stima = SI` passano a `NO` (o
diventano assunzioni operative documentate), il workbook è pronto per il cost modeling.

Colonne: `#` (stesso del Sheet 5), `Capability`, `Categoria`, `Testo Domanda`,
`Driver che abilita`, `Prio` (drop-down 1/2/3), `Stato` (drop-down Non inviato / Inviato /
Risposta ricevuta), `Data Risposta`, `Sintesi Risposta`, `Impatto se non risolto` (drop-down
ALTO/MEDIO/BASSO), `Bloccante per stima` (drop-down SI/NO).
**Ordina per `Bloccante per stima` decrescente**, poi per `Impatto se non risolto` decrescente.

**Differenza operativa Sheet 5 vs Sheet 9 (riassunto rapido):**

| | Sheet 5 — Domande Chiarimento | Sheet 9 — Registro Chiarimenti |
|---|---|---|
| Scopo | Catalogo **statico** da inviare al cliente / allegare all'offerta | Diario **vivo** dello stato per-domanda |
| Quando si tocca | Solo a fine Fase 1 (questa skill) | A ogni risposta cliente, durante Fase 2 |
| Colonne | 6 (statiche) | 11 (5 statiche + 6 di stato/risposta) |
| Ordinamento | Per `Prio` ascendente | Per `Bloccante` desc, poi `Impatto` desc |
| Cambia nel tempo? | No, baseline immutabile | Sì, evolve fino a Fase 3 |
| Granularità | 1 riga = 1 domanda | idem (allineato col `#` di Sheet 5) |

**Merge simmetrico delle `domande_bloccanti` del JSON**: ogni `domanda_bloccante`
presente nel Sheet 5 con tag `[Q-NNN]` deve essere replicata qui con stesso `#`,
`Bloccante per stima = SI`, `Impatto se non risolto = ALTO`, `Stato = Non inviato`,
`Data Risposta` e `Sintesi Risposta` vuoti. Il `#` resta identico al Sheet 5 (regola
generale di coerenza ID già documentata in "Regole operative").

**Stile semaforico colonna `Prio`**: applica lo **stesso identico schema** dello Sheet 5
(vedi sezione `5. Domande Chiarimento` → "Stile semaforico colonna Prio"). I valori `1/2/3`
significano la stessa cosa e devono essere visivamente identici sui due fogli — il lettore
non deve dover ricordare due codici cromatici diversi per la stessa scala di priorità.

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

**Stile esplicito su ogni riga popolata (regola di rendering, coerente Sheet 8).**
Identico problema strutturale dello Sheet 8: il template ha pre-styling fragile su
righe la cui numerosità dipende dalla RFP (sezione 1 da ~10 a ~25 voci, sezione 2 da
~5 a ~20 voci, sezione 3 da ~3 a ~10 voci). Affidarsi al pre-styling significa avere
l'ultima riga di ogni sezione senza fill, o righe con colore errato perché cadono in
una zona stilizzata per un'altra sezione.

Pertanto applicare esplicitamente lo stile per sezione/sotto-categoria su tutte e sole
le righe popolate. Schema cromatico (allineato a Sheet 8 per coerenza visiva
Sheet 10 ↔ Sheet 8):

| Sezione / Prefisso | Fill riga | Font riga | Fill banner |
|---|---|---|---|
| Sezione 1 — `COSA È CONFERMATO` | `#DCFCE7` verde | `#065F46` | `#15803D` |
| Sezione 2 — `BLOCCANTE — ...` | `#FEE2E2` rosso | `#991B1B` | (banner sezione `#D97706`) |
| Sezione 2 — `DA ASSUMERE — ...` | `#FEF3C7` giallo | `#92400E` | (idem) |
| Sezione 2 — `ERRORE CORRETTO — ...` | `#F3F4F6` grigio | `#374151` | (idem) |
| Sezione 3 — `DECISION POINT CRITICI` | `#DBEAFE` azzurro | `#1E40AF` | `#1E40AF` |

Per la sezione 2 lo stile della riga deriva dal **prefisso** della colonna A: classificare
`BLOCCANTE` → rosso, `DA ASSUMERE` → giallo, `ERRORE CORRETTO` → grigio. Banner di sezione
ambra (`#D97706`) come "warning generale" copre l'intera sezione 2 mista.

Banner di sezione: merge `A:F`, font bianco bold 12pt. Colonna A delle righe contenuto in
bold (è la label), colonna B in regular.

Snippet:
```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
CONFIRMED = ('DCFCE7', '065F46')
DEC_POINT = ('DBEAFE', '1E40AF')
SUBCATS = {
    'BLOCCANTE':       ('FEE2E2', '991B1B'),
    'DA ASSUMERE':     ('FEF3C7', '92400E'),
    'ERRORE CORRETTO': ('F3F4F6', '374151'),
}
BANNER_FILLS = {1: '15803D', 2: 'D97706', 3: '1E40AF'}
LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True, indent=1)
THIN = Side(border_style='thin', color='E5E7EB')
ROW_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# Banner sezione (per ognuno dei 3 header)
for section_idx, banner_r in banner_rows.items():
    ws.merge_cells(f'A{banner_r}:F{banner_r}')
    cell = ws.cell(row=banner_r, column=1)
    cell.fill = PatternFill('solid', fgColor=BANNER_FILLS[section_idx])
    cell.font = Font(name='Calibri', size=12, bold=True, color='FFFFFF')
    cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)

# Righe contenuto - dispatch per sezione e (sezione 2) per prefisso
def style_row(r, fill_hex, font_hex):
    fill = PatternFill('solid', fgColor=fill_hex)
    for c in range(1, 7):
        cell = ws.cell(row=r, column=c)
        cell.fill = fill
        cell.font = Font(name='Calibri', size=10, color=font_hex, bold=(c == 1))
        cell.alignment = LEFT
        cell.border = ROW_BORDER

for section_idx, rows in section_content.items():
    for r in rows:
        if section_idx == 1:
            style_row(r, *CONFIRMED)
        elif section_idx == 3:
            style_row(r, *DEC_POINT)
        elif section_idx == 2:
            label = str(ws.cell(row=r, column=1).value or '').upper()
            chosen = next((s for p, s in SUBCATS.items() if label.startswith(p)),
                          SUBCATS['DA ASSUMERE'])  # fallback giallo
            style_row(r, *chosen)
```

**Bug storico evitato (15/05/2026 RAI Sistemi Informativi):** lo Sheet 10 generato aveva
- Sezione 1 con r4 grigio chiaro (font illeggibile `#64748B`), r14 verde corretto, r23 in
  ROSSO (completamente errato — è una voce CONFERMATA);
- Sezione 2 quasi tutta senza stile, con una sola riga a metà colorata gialla per caso;
- Sezione 3 interamente senza stile.

Causa: il template aveva pre-styling random `verde/giallo/rosso/bianco` sulle righe
r4-r49 non correlato con le 3 sezioni semantiche. Il template è ora stato patchato per
rimuovere il pre-styling (le righe contenuto sono "neutre"), quindi ogni generazione DEVE
applicare lo stile esplicitamente come da snippet. Effetto: la corrispondenza Sheet 10 ↔
Sheet 8 (regola già documentata) diventa anche **visiva**: una voce BLOCCANTE è rossa in
Sheet 10 come in Sheet 8 ROSSO, una voce DA ASSUMERE è gialla in Sheet 10 come in Sheet 8
GIALLO, una voce CONFERMATO è verde come Sheet 8 VERDE.

### Fase 2 manuale — uso combinato Sheet 9 + Sheet 10 (Sheet 8 NO)

La Fase 2 (a carico del bid manager, fuori dallo scope di esecuzione di questa skill) è il
ponte tra l'output di `gara-rfp-handoff` e l'input di `gara-effort-cost-estimator`. Il bid
manager opera **esclusivamente su due sheet** con granularità diverse:

| Sheet | Granularità | Cosa rappresenta | Aggiornato da |
|---|---|---|---|
| Sheet 9 (Registro Chiarimenti) | 1 riga = 1 domanda | Diario per-domanda con timeline | **Bid manager**, ad ogni risposta cliente |
| Sheet 10 sezione 2 (COSA È APERTO) | 1 riga = 1 tema operativo | Sintesi aggregata di cosa manca per stimare | **Bid manager**, riclassificando voci |
| Sheet 8 (Input Cost Model) | 1 riga = 1 parametro | Stato dei parametri V/G/R | **NON il bid manager** — è competenza del **cost modeler in Fase 3** |

**Separazione di responsabilità — perché il bid manager NON tocca lo Sheet 8.** Il bid
manager è una figura commerciale/contrattuale, non tecnica: il suo ruolo è raccogliere
e documentare le risposte del cliente (Sheet 9) e mantenere allineata la sintesi narrativa
(Sheet 10). L'interpretazione tecnica della risposta — "il cliente ha detto X, quindi il
parametro `Volume MAC` vale Y con split Z" — è una decisione di **cost modeling** che
spetta a chi gira `gara-effort-cost-estimator` in Fase 3. Quella skill ha proprio come
pre-step la rilettura combinata di Sheet 9 + Sheet 8 nel loro stato attuale e l'aggiornamento
in-place del Sheet 10, traducendo i testi delle risposte cliente in valori numerici per il
cost model. Il bid manager fornisce il **materiale grezzo** (testi); il cost modeler fa
**l'interpretazione tecnica** (numeri e split di volumi).

Una voce dello Sheet 10 sezione 2 spesso **aggrega** più righe di Sheet 9. Esempio:
- Voce Sheet 10 `DA ASSUMERE — Volumi storici operativi` → copre 4 righe Sheet 9 (Q-008 MAC, Q-009 REP, Q-010 GES, Q-011 GST).
- Voce Sheet 10 `BLOCCANTE — Volumi T&M` → corrisponde a una riga Sheet 9 (Q-001).

**Workflow tipico per ogni risposta cliente ricevuta (bid manager):**

1. **Sheet 9 — registra la risposta puntuale**:
   - aggiorna riga `Q-NNN`: `Stato` → `Risposta ricevuta`, popola `Data Risposta`, scrivi `Sintesi Risposta` (1-2 frasi che catturano il testo della risposta)
   - se la risposta scioglie il blocco, abbassa `Bloccante per stima` da `SI` a `NO`
2. **Sheet 10 — aggiorna la sintesi narrativa**:
   - se tutte le righe Sheet 9 coperte da una voce Sheet 10 sez. 2 hanno avuto risposta, **sposta la voce in sez. 1 `COSA È CONFERMATO`** (o aggiornala con la sintesi della risposta)
   - se solo alcune sono state risposte, riformula la voce sez. 2 per restringere lo scope ancora aperto
   - non toccare la sez. 3 `DECISION POINT CRITICI`: sono decisioni interne, non dipendono dal cliente
   - **non valorizzare parametri Sheet 8** — lascia GIALLI e ROSSI come sono: sarà il cost modeler a tradurli in Fase 3

**Perché il cost modeler usa Sheet 10 e non legge direttamente Sheet 9.** In Fase 3
`gara-effort-cost-estimator` apre il workbook con un obiettivo: capire **se può stimare e
con quali assunzioni**. La granularità per-domanda di Sheet 9 è troppo fine per quella
decisione (28 righe da scorrere e classificare); la sintesi aggregata di Sheet 10 sez. 2
risponde direttamente: "Quanti BLOCCANTI restano aperti? Quante voci DA ASSUMERE devo
modellare con benchmark?". Lo Sheet 8 viene poi valorizzato dal cost modeler stesso
leggendo Sheet 9 (testi puntuali) e Sheet 10 (sintesi) — quindi all'inizio della Fase 3
lo Sheet 8 può ancora avere GIALLI/ROSSI: è normale, non è un errore.

**Trigger di chiusura Fase 2 (criterio di ripresa workflow):**
La Fase 2 si considera completa quando nello Sheet 9 non c'è più nessuna riga con
`Bloccante per stima = SI` E nello Sheet 10 sezione 2 non c'è più nessuna voce con
prefisso `BLOCCANTE — `. **NON è richiesto che Sheet 8 sia tutto VERDE**: la
valorizzazione dei GIALLI è competenza del cost modeler. A trigger soddisfatto si invoca
`gara-effort-cost-estimator` con il workbook aggiornato.

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
| Sheet `Requisiti` | = `len(requisiti)` del JSON (esatto, no soglia) | (idem) | Granularità imposta da `gara-req-extractor`, non da questa skill. Per RFP enterprise tipicamente 40-80 requisiti |

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

### Step 1bis — Lettura `requisiti_estratti.json` (PREREQUISITO OBBLIGATORIO)

Cerca `requisiti_estratti.json` nella working directory dell'utente.

- **Se assente**: presenta in chat un messaggio chiaro e **termina senza popolare il template**:
  > ❌ **Manca `requisiti_estratti.json`** nella working directory.
  > Questa skill richiede l'output di `gara-req-extractor` come input obbligatorio.
  > Esegui prima `gara-req-extractor` sui documenti di gara, poi rilancia `gara-rfp-handoff`.

- **Se presente**:
  1. Valida che `meta.versione_schema == "2.0"`. Se diverso, emetti warning e chiedi
     all'utente se procedere comunque (potrebbero mancare campi del nuovo schema).
  2. Valida che `requisiti` non sia vuoto. Se vuoto, emetti warning: il JSON è stato prodotto
     ma non ha estratto requisiti — chiedi conferma all'utente prima di procedere.
  3. Annota mentalmente: numero requisiti, ripartizione per `area_funzionale`, ripartizione
     `tipo` (padre/figlio/singolo), ripartizione `categoria_scope`, lista `domande_bloccanti`.

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

#### Step 7.0 — Hardening obbligatori (anti-data-loss e anti-mismatch)

Prima di scrivere qualsiasi cella, internalizzare le 4 regole che eliminano le classi
di bug osservate in passato:

1. **Helper `safe_set` / `safe_clear` dalla prima riga, mai accesso diretto a `.value`**.
   Il template contiene merged cells (sheet 1, 7, 8, 10 hanno banner/sezioni con merge);
   un `cell.value = ...` su una `MergedCell` lancia `AttributeError` e interrompe lo
   script lasciando i sheet successivi vuoti. Pattern:
   ```python
   from openpyxl.cell.cell import MergedCell
   def safe_set(ws, r, c, value):
       cell = ws.cell(row=r, column=c)
       if not isinstance(cell, MergedCell):
           cell.value = value
   def safe_clear(ws, from_row, to_row, max_col):
       for r in range(from_row, to_row+1):
           for c in range(1, max_col+1):
               safe_set(ws, r, c, None)
   ```
   Usali sempre, non solo come fix reattivo dopo un crash.

2. **Save per sheet, mai save monolitico in fondo**. Dopo aver popolato ogni sheet,
   chiamare `wb.save(WB_PATH)` immediatamente. Costa pochi millisecondi e impedisce che
   un crash sul sheet N azzeri i sheet 1..N-1 popolati in memoria. Pattern: per ognuno
   dei 12 sheet, blocco `populate → save → log "Sheet X salvato"`.

3. **Label dal template come ground truth, mai "a memoria"**. Per gli sheet a layout
   label-valore (Sheet 1 anagrafica, Sheet 10 nota di handoff), NON costruire mai un
   dizionario `{"Importo a base di gara": ...}` basato su quello che ricordi del
   template. Sempre leggere prima la colonna A del template, raccogliere le label
   esatte presenti, e usarle come chiavi:
   ```python
   label_to_row = {}
   for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=False):
       a = row[0].value
       if a and isinstance(a, str):
           label_to_row[a.strip()] = row[0].row
   # Solo ora costruisci la mappa SHEET1_FILL su queste chiavi reali
   ```
   La regola "Lettura preventiva di `_Esempi`" si estende quindi anche alla **lettura
   della colonna A di ogni sheet a layout label-valore**.

4. **Self-check post-save riaprendo il file**, non solo in-memory. Vedi
   "Validazione pre-output" — il check 0 (nuovo) richiede di chiudere e riaprire il
   workbook e contare le righe popolate per sheet. In-memory un sheet che non è mai
   stato salvato sembra pieno.

#### Step 7.1 — Esecuzione

1. Copia `assets/template_rfp_handoff.xlsx` in `rfp_handoff.xlsx` nella working directory dell'utente.
2. Apri il file copiato (delegando alla skill `xlsx` per le operazioni di scrittura).
3. Per ogni sheet, popola le celle rispettando:
   - intestazioni di colonna esistenti (non rinominarle)
   - drop-down/data validation (usa solo valori ammessi)
   - layout a sezioni (sheet 1, 7, 8, 10): non spostare i titoli di sezione
4. **Sheet `Requisiti`**: trascrivi `requisiti_estratti.json` riga per riga rispettando le 16
   colonne (mapping nella sezione "### Requisiti"). Mantieni `testo_bando` verbatim, non
   riformattare. Per `scope_dettaglio` (oggetto): serializza in stringa col separatore ` | `;
   se l'oggetto è null, lascia la cella vuota. Mantieni l'ordine del JSON.
5. **Merge delle `domande_bloccanti` del JSON in Sheet 5 e Sheet 9**: per ogni elemento
   dell'array `domande_bloccanti`, aggiungi una riga al Sheet 5 con `Categoria = Scope/Requisito`,
   `Prio = 1`, `Testo Domanda` prefissato `[Q-NNN]` (vedi regole Sheet 5/9). Replica la stessa
   riga in Sheet 9 con stesso `#`, `Bloccante per stima = SI`, `Stato = Non inviato`,
   `Impatto se non risolto = ALTO`.
6. Sheet 7: prima di scrivere i profili, sostituisci le intestazioni E:N con le capability L2
   reali della RFP.
7. Sheet 8: copia in sezione ROSSO tutte le incoerenze tra documenti registrate nel sheet 4.
8. Sheet 9: ordina per `Bloccante per stima` decrescente.
9. Sheet 10: scrivi label brevi in colonna A (es. "Valore appalto", "BLOCCANTE — Volumi T&M",
   "DP-01 (CRITICO)") e contenuto disteso in colonna B.
10. **Save dopo ogni sheet** (vedi Step 7.0 punto 2). NON accumulare 12 popolamenti e poi
    fare un solo `wb.save()` finale: ogni sheet completato deve essere persistito subito.

### Step 8 — Riepilogo finale
Presenta all'utente un riepilogo Markdown:

> **Pacchetto di handoff RFP — [Nome progetto]**
>
> **Cliente:** [...] | **Modello:** [...] | **Durata:** [...] | **Industry:** [...]
>
> **Requisiti caricati:** N (padre: A, figlio: B, singoli: C) | **Aree funzionali:** elenco
> | **Distribuzione scope:** custom N / cots N / service N / out_of_scope N
> | **Domande scope bloccanti mergiate in Sheet 5/9:** N
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
- **Sheet 7 unmerge fantasma all'inizio**: subito dopo aver aperto lo Sheet 7, sciogli i
  merge `A23:N23` e `A29:N29` ereditati dal template (vedi sezione `7. Matrice Profili x
  Capability` → "Merge fantasma del template"). Senza questo step il profilo TL/Analista
  Funzionale T&M va perso silenziosamente.
- **Sheet 7 stile semaforico obbligatorio**: applicare i 4 colori (verde/giallo/azzurro/viola)
  a tutte le celle E:N popolate, sovrascrivendo il fill placeholder grigio chiaro del
  template. La tabella esatta dei colori hex è nella sezione `7. Matrice Profili x
  Capability` → "Stile semaforico obbligatorio".
- **Sheet 8 stile esplicito per gruppo**: dopo aver scritto i contenuti dei 3 gruppi
  (V/G/R), applicare esplicitamente il fill e font color per gruppo su **ogni riga
  popolata**, dalla prima all'ultima. Niente affidamento al pre-styling del template.
  La tabella esatta dei 3 colori (verde/giallo/rosso) + snippet Python sono nella
  sezione `8. Input Cost Model` → "Stile esplicito su ogni riga popolata".
- **Sheet 10 stile esplicito per sezione + sotto-categoria**: stessa logica di Sheet 8,
  con dispatch sulla sezione 2 in base al prefisso della col A (`BLOCCANTE` rosso,
  `DA ASSUMERE` giallo, `ERRORE CORRETTO` grigio). I colori sono identici a Sheet 8 per
  rafforzare la coerenza Sheet 10 ↔ Sheet 8 anche visivamente. Snippet completo nella
  sezione `10. Nota di Handoff` → "Stile esplicito su ogni riga popolata".
- **Sheet 5 + Sheet 9 stile semaforico colonna `Prio`**: applicare alla cella F di ogni
  domanda i tre colori coerenti con la scala di criticità (1 rosso, 2 arancione, 3
  verde). Schema identico sui due sheet. Vedi sezione `5. Domande Chiarimento` →
  "Stile semaforico colonna Prio" per la tabella hex e lo snippet.
- **Sheet `Requisiti` stile padre come contenitore**: ogni riga con `tipo = padre` riceve
  fill lavanda `#E0E7FF` + font bold viola scuro `#3730A3` sulle colonne label, in modo
  che sia visivamente distinguibile come "header del gruppo" rispetto ai propri figli.
  Le righe `figlio` e `singolo` restano neutre (nessun fill, font regular nero). Vedi
  sezione `Requisiti` → "Stile differenziato per tipo" per snippet e razionale cromatico.
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
- **Lettura preventiva delle label di col A** per gli sheet a layout label-valore
  (Sheet 1, Sheet 10): costruire la mappa `label_esatta → row` leggendo il template,
  mai usare un dizionario di label "a memoria" (vedi Step 7.0 punto 3).
- **`safe_set` / `safe_clear` sempre** quando si scrive nel workbook: il template contiene
  merged cells nei banner di sezione (Sheet 1, 7, 8, 10) e un accesso diretto a `.value`
  su `MergedCell` interrompe lo script (vedi Step 7.0 punto 1).
- **Save per sheet, non monolitico**: `wb.save()` dopo ogni sheet popolato, in modo che
  un crash sul sheet N non azzeri i sheet 1..N-1 (vedi Step 7.0 punto 2 + check 0 della
  validazione pre-output).
- **Output sempre in italiano**, salvo richiesta esplicita diversa.
- **Profili professionali ammessi nello Sheet 7**: solo quelli esplicitamente definiti
  nei documenti di gara. NIENTE profili inventati (DBA, DevOps, QA, ML Engineer, ecc.)
  se non sono nominati come profilo a sé stante.
- **Coerenza Sheet 10 ↔ Sheet 8**: ogni `BLOCCANTE — ...` del Sheet 10 sez.2 = una riga
  del Sheet 8 sez. ROSSO. Ogni `DA ASSUMERE — ...` del Sheet 10 sez.2 = uno o più voci
  del Sheet 8 sez. GIALLO della stessa categoria.
- **Assunzioni di volume quantificate**: numero provvisorio basato su benchmark, non
  rinvio al cost modeler (vedi regola Sheet 6).
- **Sheet `Requisiti` read-only dalla sorgente JSON**: lo sheet riflette 1:1
  `requisiti_estratti.json`. NON aggiungere righe non presenti nel JSON; NON omettere righe
  del JSON. Se serve un nuovo requisito, tornare a `gara-req-extractor` e ri-popolare.
  Modifiche manuali introducono drift con `gara-bid-estimator` che legge dallo stesso JSON.
- **Tracciabilità domande di scope**: ogni domanda derivata da `domande_bloccanti` del JSON
  presente nel Sheet 5/9 deve mantenere il prefisso `[Q-NNN]` nel testo per consentire il
  raccordo con l'`id` della sorgente JSON.

## Validazione pre-output (self-check obbligatorio prima del Step 8)

Prima di presentare il riepilogo finale all'utente, la skill DEVE eseguire un self-check
sui contenuti scritti nel file e segnalare eventuali violazioni delle regole sopra.

Checklist di validazione (esegui in ordine, ferma all'errore):

0. **Persistenza reale — riapri il file e conta** (PRIMO CHECK, non saltabile). Dopo
   l'ultimo save, chiudi il workbook in memoria e riaprilo da disco con
   `openpyxl.load_workbook(WB_PATH)`. Per ognuno dei 12 sheet, conta le celle non vuote
   da `min_row=4` in poi:
   ```python
   for sn in wb.sheetnames:
       ws = wb[sn]
       filled = sum(1 for row in ws.iter_rows(min_row=4) for c in row
                    if c.value is not None and str(c.value).strip())
       print(f"{sn}: {filled} celle")
   ```
   Se un sheet operativo (1-10 + Requisiti) ha 0 celle popolate, è andato perso in un
   crash: ri-popolare quello sheet e ri-salvare. Se uno sheet è sotto il floor della
   sezione "Granularità minima per sheet", investigare prima di passare al check 1.
   In-memory un sheet che non è mai stato salvato sembra popolato — solo la rilettura
   da disco è autoritativa.

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

10b. **Stile semaforico Sheet 7 applicato**: tutte le celle E:N delle righe profilo
    (Canone 6-19 + T&M 22-25) hanno il fill e font color secondo la tabella semaforica
    (P-DOC verde / P-IPO giallo / S-DOC azzurro / S-IPO viola)? Nessuna cella ha più il
    fill placeholder `#F8FAFC` con font `#CBD5E1` (verifica via `cell.fill.fgColor.rgb`)?
    La legenda riga 4 è stata riscritta con lo schema cromatico?

10c. **Merge fantasma Sheet 7 sciolti**: i range `A23:N23` e `A29:N29` NON sono più in
    `ws.merged_cells.ranges`? Le righe 22-25 contengono i 4 profili T&M completi
    (Architetto, TL/Analista Funzionale, Analista Programmatore, Programmatore) con
    colonna B valorizzata? Il banner T&M a riga 21 ha merge `A21:N21` con stile coerente?

10d. **Stile gruppo coerente Sheet 8**: per ognuno dei 3 gruppi (V/G/R), prima riga e
    **ultima riga del gruppo** hanno lo stesso `fill.fgColor.rgb` e `font.color.rgb`
    (verde `DCFCE7`/`065F46`, giallo `FEF3C7`/`92400E`, rosso `FEE2E2`/`991B1B`)? Nessuna
    riga popolata ha fill `None` o font default? I 3 banner di sezione hanno merge `A:F`
    + fill banner scuro + font bianco bold? Controllo a campione consigliato:
    `assert ws.cell(row=last_row_V, column=1).fill.fgColor.rgb.endswith('DCFCE7')`.

10e. **Stile per sezione/sotto-categoria Sheet 10**: per ognuna delle 3 sezioni, prima e
    ultima riga hanno il fill corretto secondo lo schema (sezione 1 verde `DCFCE7`,
    sezione 3 azzurro `DBEAFE`)? Per la sezione 2 mista, ogni voce è classificata per
    prefisso e ha il fill corretto (BLOCCANTE rosso `FEE2E2`, DA ASSUMERE giallo `FEF3C7`,
    ERRORE CORRETTO grigio `F3F4F6`)? Nessuna voce della sezione 2 è priva di prefisso
    riconosciuto (in tal caso va corretta a monte, non lasciata con fill di default)?
    I 3 banner di sezione hanno merge `A:F` + fill scuro + font bianco bold 12pt?

10f. **Stile semaforico Prio Sheet 5 + Sheet 9**: la colonna F di entrambi gli sheet ha
    per ogni cella valorizzata il fill e font color secondo lo schema (1 rosso
    `FEE2E2`/`991B1B`, 2 arancione `FED7AA`/`9A3412`, 3 verde `DCFCE7`/`15803D`)? Lo
    schema deve essere **identico** sui due sheet (non basta lo stesso colore per Prio 1
    su entrambi: anche 2 e 3 devono coincidere)? Nessuna cella Prio è priva di fill o
    con font default?

11. **Coerenza Sheet `Requisiti` ↔ JSON sorgente**: il numero di righe popolate in
    `Requisiti` è esattamente uguale a `len(requisiti_estratti.json["requisiti"])`? Tutti
    gli `id` del JSON sono presenti in colonna A? Per ogni riga con `tipo = figlio`, il
    `padre_id` (col C) esiste come `id` (col A) in un'altra riga? Per ogni riga con
    `categoria_scope ≠ custom_software`, la col L `Scope Dettaglio` è popolata?

11b. **Stile differenziato `tipo` su Sheet `Requisiti`**: ogni riga con `tipo = padre` ha
    fill `#E0E7FF` lavanda + font bold viola `#3730A3` sulle colonne label (A, B, D, E,
    M)? Le righe `figlio` e `singolo` hanno fill `None` e font nero regular? Controllo a
    campione: `assert ws.cell(row=parent_row, column=1).fill.fgColor.rgb.endswith('E0E7FF')
    and ws.cell(row=parent_row, column=1).font.bold is True`.

12. **Coerenza Sheet 5/9 ↔ `domande_bloccanti` del JSON**: ogni elemento dell'array
    `domande_bloccanti` ha una riga corrispondente nel Sheet 5 con prefisso `[Q-NNN]` nel
    `Testo Domanda`, `Categoria = Scope/Requisito`, `Prio = 1`, e una riga simmetrica nel
    Sheet 9 con stesso `#`, `Bloccante per stima = SI`, `Stato = Non inviato`?

Se uno qualsiasi di questi check fallisce: **correggi il file prima di presentare il
riepilogo all'utente**. Non chiedere conferma per le correzioni di self-check.

## Asset

- `assets/template_rfp_handoff.xlsx` — template ufficiale del workbook di handoff. Non modificarlo
  in place: copialo nella working directory dell'utente come `rfp_handoff.xlsx` e popolalo lì.
