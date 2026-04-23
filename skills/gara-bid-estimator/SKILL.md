---
name: gara-bid-estimator
description: >
  Analizza documenti di gara IT o documenti funzionali per produrre una stima di solution design compilando un template Excel ufficiale.
  TRIGGER quando: il documento e un capitolato, bando di gara, CSA, RFP, disciplinare tecnico, documento di offerta, analisi funzionale, specifiche funzionali, SRS, documento di analisi dei requisiti, user story mapping, backlog di prodotto, documento tecnico di progetto; l'utente chiede di analizzare requisiti (di gara o funzionali), stimare l'effort, preparare un'offerta tecnica, classificare requisiti per area funzionale, valutare la complessita di un progetto, estrarre requisiti da un documento; il file si chiama "capitolato", "bando", "CSA", "RFP", "analisi", "specifiche", "SRS", "requisiti" o simili anche in formato PDF o DOCX.
  PRIORITA su skill pdf, docx e xlsx: questa skill governa il workflow end-to-end quando il documento contiene requisiti funzionali o tecnici da stimare; le skill di formato sono usate come helper per leggere/scrivere file, non per guidare l'analisi.
  SKIP se il documento e un contratto esecutivo, verbale di riunione, fattura, collaudo, piano di test o documento privo di requisiti stimabili.
---

# Gara Bid Estimator

Usa questa skill quando devi leggere un documento di gara o un documento funzionale e trasformarlo in una stima strutturata in Excel.

## Input richiesti

- Documento di gara o documento funzionale in `pdf`, `docx`, `xlsx` o `csv`
- Template Excel ufficiale da compilare
- Eventuali allegati tecnici di supporto

Se il template ufficiale non e disponibile, fermati e richiedilo: la skill deve popolare il file fornito, senza modificarne la struttura.
Il template di riferimento incluso come asset e `assets/Stima_SolutionDesign_Template.xlsx`.

## Uso delle skill di formato

Questa e una skill di dominio: governa classificazione, stima e compilazione del template. Le skill di formato sono helper per leggere/scrivere file.

- Se la skill `pdf` e installata, usala come helper per leggere il contenuto del file `.pdf`; l'analisi e la stima restano di competenza di questa skill.
- Se la skill `docx` e installata, usala come helper per leggere e scrivere file `.docx`.
- Se la skill `xlsx` e installata, usala come helper per creare e aggiornare il file `.xlsx` di output.
- In caso di conflitto di routing con `pdf` o `docx`, questa skill ha priorita quando il documento e un capitolato, bando o RFP.

## Workflow

1. Leggi il documento, identifica il tipo e annota i dati di contesto:
   - **Documento di gara** (capitolato, CSA, RFP, bando): nome gara, codice, cliente/stazione appaltante, scadenza offerta, budget stimato, durata contratto, tipologia appalto.
   - **Documento funzionale** (analisi funzionale, SRS, specifiche, backlog): nome progetto/sistema, versione documento, cliente, fase progettuale (analisi / design / sviluppo), release o sprint target, ambito del documento (moduli coperti).
   Il tipo di documento non cambia il workflow di decomposizione e stima, ma determina il livello di dettaglio atteso: i documenti funzionali forniscono di norma schermate, API ed entita gia nominate — usale direttamente senza inferire, riservando `[stimato]` solo ai casi in cui il dettaglio e effettivamente assente.
2. Per ogni blocco funzionale del bando, decomponilo in unita atomiche stimabili seguendo `references/decomposizione_requisiti.md`:
   - **2a. Individua le unita atomiche**: una riga = una unita atomica (es. un journey utente, una integrazione verso un sistema distinto, un dominio AI). Non stimare aggregati. Se il bando elenca componenti distinte (profili utente, sistemi, sezioni), crea una riga per componente.
   - **2b. Inferisci i dettagli mancanti**: se il bando non fornisce conteggi espliciti (pagine, API, entita), deducili dalla descrizione funzionale. Ogni valore inferito va marcato `[stimato]` nella Colonna D e deve corrispondere a una assunzione nel foglio Assumptions & Risks: _"Si assume che [micro-req] comprenda [N] [unita] — da confermare con il cliente"_.
   - **2c. Stabilisci la gerarchia padre-figlio**: se un blocco funzionale genera ≥ 2 unita atomiche, crea prima una **riga padre** (`REQ-NNN`) che descrive il macro-requisito senza GG/U, poi crea le **righe figlio** (`REQ-NNN.1`, `REQ-NNN.2`, ...) ciascuna con la propria stima. Se il blocco produce una sola unita atomica, usa direttamente `REQ-NNN` con la stima — nessun padre necessario.
   - **2d. Gestisci le ambiguita**: per ogni requisito o componente non riconducibile a una assunzione ragionevole, applica questa sequenza:
     1. Il valore e inferibile dal contesto del bando? → usa `[stimato]` + assunzione in A&R.
     2. L'ambiguita ha impatto significativo sulla stima (>20% variazione GG/U) o blocca la decomposizione padre-figlio? → **fai una domanda mirata all'utente** (vedi formato sotto) e attendi risposta prima di procedere.
     3. L'ambiguita riguarda un dettaglio implementativo di basso impatto? → usa `[DA CHIARIRE]` + assunzione/rischio in A&R e procedi.

     **Formato domande all'utente** — le domande devono essere:
     - Specifiche: citare il testo del bando che genera l'ambiguita
     - Binarie o a scelta multipla quando possibile, con indicazione dell'impatto stimativo per ciascuna opzione
     - Raggruppate: presentare tutte le domande bloccanti in un unico messaggio, non una alla volta
     - Limitate: se sono gia state fatte ≥ 3 domande nell'analisi, preferisci assunzioni documentate per non bloccare il workflow

     Esempio di messaggio domande:
     > **Chiarimento richiesto prima di stimare [Area: Autenticazione & IAM]**
     > Il bando cita: _"autenticazione tramite sistema centralizzato della SA"_
     > 1. Il sistema IAM esiste gia (solo integrazione) o va sviluppato da zero?
     >    - (a) Integrazione con IdP esistente → ~8-10 GG/U
     >    - (b) Sviluppo nuovo IdP → ~18-22 GG/U
     > 2. E richiesta la firma digitale nel flusso di autenticazione? Si / No
3. Classifica ogni micro-requisito usando `references/aree_funzionali.md`.
4. Assegna la complessita con `references/regole_stima.md` e applica eventuali correttivi trasversali da `references/segnali_complessita.md`.
   - **Regola di posizionamento**: parti sempre dal centro del range come default. Scendi al bordo basso solo se tutti i segnali di riduzione sono contemporaneamente presenti. Sali al bordo alto se anche un solo segnale di crescita è presente.
   - **Regola bando**: un bando di gara è per definizione ad alta ambiguità strutturale. In assenza di segnali espliciti di riduzione, il default è centro-alto del range.
5. Se hai dubbi di classificazione, consulta `references/esempi_mapping.md` e scegli l'area prevalente; cita l'area secondaria nelle note.
6. Per le aree con driver di scala, non stimare il blocco come voce unica: usa l'unita di misura indicata nelle reference e separa le componenti significative.
7. **Verifica obbligatoria delle aree trasversali**: prima di compilare il foglio Requirements, controlla che siano presenti righe per le seguenti aree. Se mancano, aggiungile applicando il floor minimo indicato in `references/segnali_complessita.md`:
   - `Sicurezza e Compliance` — floor: Bassa (4-5 GG/U); alzare se GDPR, audit o VAPT presenti
   - `Infrastruttura e DevOps` — floor: Media (8-10 GG/U); sempre per progetti nuovi
   - `Accessibilità` — floor: Bassa (3-4 GG/U); alzare se WCAG/AgID citati esplicitamente
   - `PMO e Governance` — floor: Bassa (3-4 GG/U); alzare se bando PA con SAL formali o più vendor
   Queste voci esistono in ogni progetto IT anche se il bando non le nomina. Non aggiungerle è la causa più frequente di sottostima sistematica.
8. Compila il foglio `Requirements & Solution Mapping`.
9. Genera assunzioni e rischi coerenti con le ambiguita rilevate e compila `Assumptions & Risks`.
10. Aggrega i GG/U e compila `Summary`. Applica il contingency secondo la seguente regola obbligatoria — non lasciare il campo vuoto o al valore di default del template:
    - **15%** se documento funzionale dettagliato, stack noto, nessuna integrazione legacy
    - **20%** se bando di gara con specifiche incomplete o almeno 1 integrazione
    - **25%** se bando con ≥ 2 segnali di complessità trasversali (legacy + normativa, AI + compliance, ecc.)
    - **30%** se requisiti contraddittori, sistemi legacy non documentati, o aree [DA CHIARIRE] significative
    Documenta nel foglio Summary la motivazione del percentuale scelto in una cella di nota.

## Regole operative

- **Adatta la precisione al tipo di documento**: con un documento funzionale dettagliato (analisi, SRS, specifiche), leggi i dati gia presenti (nomi schermate, endpoint API, entita) e usali direttamente in Colonna D senza marcare `[stimato]`. Riserva `[stimato]` solo ai dettagli ancora assenti. Con un documento di gara, inferisci liberamente dal contesto e documenta ogni inferenza in A&R.
- **Decomponi prima di stimare**: Prima di assegnare GG/U, elenca le unita atomiche del blocco funzionale seguendo `references/decomposizione_requisiti.md`. Se emergono piu unita, crea una riga per ciascuna. Non stimare aggregati.
- **Trasparenza sulle stime inferite**: Ogni valore marcato `[stimato]` in Colonna D deve corrispondere a una assunzione esplicita nel foglio Assumptions & Risks. Ogni `[DA CHIARIRE]` deve generare una assunzione o un rischio.
- Ogni requisito deve avere un solo owner di area funzionale primaria.
- Non assegnare i GG/U partendo solo da `Bassa/Media/Alta`: usa prima la baseline dell'area funzionale, poi posizionati nel range partendo dal **centro come default**. Scendi al bordo basso solo se tutti i driver di riduzione sono presenti; sali al bordo alto se anche un solo driver di crescita è presente.
- Per le aree scalabili come integrazioni, frontend, analytics, documentale e migrazione dati, considera anche la numerosita: numero di integrazioni, schermate, KPI/report, workflow o entita dati.
- Se il driver di scala supera la soglia indicata nelle reference, suddividi la stima in piu righe invece di creare un unico requisito aggregato.
- Ogni requisito `Alta` deve avere una motivazione leggibile nelle note.
- Se una stima dipende da dati mancanti, inserisci `[DA CHIARIRE]` nelle note e crea un'assunzione esplicita.
- Se il requisito menziona integrazioni legacy, normativa stringente, alti volumi o SLA severi, verifica i correttivi trasversali.

## Compilazione Excel

- Usa sempre il template Excel ufficiale cosi come fornito.
- Non aggiungere, eliminare o rinominare fogli, colonne, sezioni o formule gia presenti nel template.
- Popola solo le celle dati previste dal file originale e preserva la struttura esistente.
- Se servono piu righe di quelle inizialmente presenti, estendi il foglio solo replicando fedelmente la struttura del template gia esistente, senza ridisegnarne il layout.
- Il template reale contiene esattamente 3 fogli: `Summary`, `Requirements & Solution Mapping`, `Assumptions & Risks`.
- Foglio `Requirements & Solution Mapping`
  - Righe intestazione: `1-3`
  - Righe dati iniziali disponibili: `4-20`
  - Riga totale: `21`
  - Colonna A — convenzione ID gerarchica:
    - `REQ-001` = macro-requisito padre (se genera ≥ 2 figli) oppure micro-requisito singolo (se non ha figli)
    - `REQ-001.1`, `REQ-001.2`, ... = figli stimati di REQ-001
    - Numerazione: i padri occupano numeri interi progressivi; i figli estendono il numero del padre con `.N`
  - Colonna B: area funzionale usando i label del template, ad esempio `Autenticazione & IAM`, `Gestione Documenti`, `Cruscotto Analytics`, `Integrazione Sistemi Legacy`, `Notifiche & Comunicazioni`
  - Colonna C: citazione o parafrasi fedele del bando
  - Colonna D: soluzione proposta strutturata — includere le dimensioni applicabili all'area (consulta `references/decomposizione_requisiti.md` per sapere quali sono obbligatorie):
    - `Schermate:` nome e tipo (form/lista/dettaglio/landing/wizard) — obbligatorio per Portale e Frontend, Mobile App
    - `API:` numero e operazione principale (GET/POST/PUT/DELETE + path) — obbligatorio per Portale, Integrazione, API Management, Autenticazione
    - `Dati:` entita e modello dati coinvolto — obbligatorio per Migrazione Dati, AI/ML; facoltativo altrove
    - `Processi:` flussi applicativi, job, workflow, orchestrazioni — obbligatorio per Documentale, Integrazione, Notifiche
    - I valori non esplicitati nel bando ma inferiti dal contesto vanno marcati con suffisso `[stimato]`
  - Colonna E: componente tecnica
  - Colonna F: usa solo il dropdown del template: `Alta`, `Media`, `Bassa`; nelle righe padre lascia vuoto o metti `—`
  - Colonne G/H/I: GG/U per Front End, Back End, Data & AI; nelle righe padre metti `0`
  - Colonna J: senza LibreOffice, sostituisci la formula con il valore intero calcolato (fe+be+data); nelle righe padre metti `0`; riga totale con i totali calcolati
  - Colonna K: usa solo il dropdown del template: `Must Have`, `Should Have`, `Nice to Have`
  - Colonna L: note, assunzioni e punti da chiarire; nelle righe padre scrivi `Macro-requisito — GG/U stimati nei sub-requisiti figli`

  **Righe padre** (REQ-NNN con figli):
  - Colonna D: `— [decomposizione in REQ-NNN.1 → REQ-NNN.N]`
  - Colonna E: `—`
  - Colonna F: `—`
  - Colonne G/H/I/J: `0`
  - Formattazione: sfondo azzurro chiaro (`FFD6E4F0`), font bold — per distinguere visivamente dal padre dai figli
  - Il totale GG/U e' la somma dei soli figli; i padri contribuiscono 0 e non alterano il totale

## Stile e Formattazione

Il file output deve replicare esattamente font, allineamento, bordi e colori del template.

- Foglio `Assumptions & Risks`
  - Sezione Assunzioni: header in righe `1-3`, voci a partire da riga `4`
  - Sezione Rischi: header in righe `13-14`, voci a partire da riga `15`
  - Mantieni gli ID nel formato del template: `A-001`, `R-001`, ...
- Foglio `Summary`
  - Usa le sezioni e le formule gia presenti nel template ufficiale
  - Celle dati progetto da valorizzare nelle sezioni `B5:B10` e `F5:F10` se vuote o da aggiornare
  - La formula `Build` punta a `='Requirements & Solution Mapping'!J21`: preservala
  - Preserva le formule gia presenti in righe `15-27`, inclusi contingency e revenue
  - Le voci `Test Accessibilità`, `Test Sicurezza` e `Test Performance` sono gia previste nel template: valorizzale secondo il bando senza cambiare il layout

## Controlli finali

- Nessuna cella obbligatoria vuota
- Nessuna formula rotta
- Nessuna alterazione strutturale del template originale
- La Build del `Summary` deve coincidere con il totale GG/U dei requisiti o con la logica formula gia presente nel template
- Ogni assunzione rilevante deve avere origine nel documento o in un'ambiguita individuata
- Linguaggio professionale, adatto a un documento di offerta

## Riferimenti da leggere solo quando servono

- Per decomporre in micro-requisiti e valorizzare Colonna D: `references/decomposizione_requisiti.md`
- Per classificare un requisito: `references/aree_funzionali.md`
- Per stimare GG/U e split FE/BE/Data: `references/regole_stima.md`
- Per applicare correttivi trasversali: `references/segnali_complessita.md`
- Per esempi pratici di mapping e decomposizione: `references/esempi_mapping.md`
