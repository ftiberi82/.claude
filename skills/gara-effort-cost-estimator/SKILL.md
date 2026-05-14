---
name: gara-effort-cost-estimator
description: >
  Fase 3 del processo di risposta a una RFP: produce il Cost Model commerciale completo
  (stima effort, costi, ricavi, margine, sensitivity pricing, risk register) a partire dal
  workbook Excel `rfp_handoff.xlsx` prodotto in Fase 1 da `gara-rfp-handoff` e aggiornato
  manualmente in Fase 2 con le risposte ricevute dal cliente.
  PRE-STEP OBBLIGATORIO: prima di costruire la stima, la skill aggiorna IN-PLACE il Sheet 10
  (Nota di Handoff) dell'Excel di input rileggendo Sheet 8 (Input Cost Model) e Sheet 9
  (Registro Chiarimenti) nello stato attuale. Nessun altro sheet dell'input viene modificato.
  TRIGGER quando: l'utente fornisce un file `rfp_handoff.xlsx` (o equivalente con i 10 sheet
  del template `gara-rfp-handoff`) e chiede di produrre la stima effort, il cost model, il
  modello economico, la sensitivity di pricing, il risk register della stima, l'offerta
  economica preliminare, oppure cita la "Fase 3" del processo di gara.
  OUTPUT: file `[nome_gara]_CostModel_v1.xlsx` ottenuto copiando e popolando il template
  predefinito `assets/template_cost_model.xlsx` con 4 sheet: Stima Effort, Cost Model,
  Sensitivity Pricing, Risk Register Stima.
  COMPORTAMENTO INTERATTIVO OBBLIGATORIO: prima di popolare il template di output, la skill
  elenca esplicitamente in chat tutte le scelte interpretative di stima (certo / assunzione
  operativa / benchmark con fonte / bloccante) e si ferma in attesa di approvazione. Le
  assunzioni operative e i benchmark di settore richiedono conferma esplicita prima di
  procedere. Questo è comportamento intenzionale, non un errore — non riprendere
  automaticamente.
  AUTONOMIA: skill end-to-end. Richiede esclusivamente l'Excel handoff in input. Non
  richiede l'esistenza di output di altre skill.
  NON USARE se l'utente fornisce un file `requisiti_estratti.json` invece dell'Excel
  handoff: in quel caso usa la skill `gara-bid-estimator` che fa parte di un percorso di
  stima parallelo. Questa skill (`gara-effort-cost-estimator`) si attiva solo con un
  workbook handoff a 10 sheet.
  SKIP se: il file di input non è un workbook handoff valido (mancano sheet 8, 9 o 10);
  l'Excel handoff è ancora nella forma originale post-Fase 1 senza alcun aggiornamento di
  Fase 2 (in quel caso la stima si baserà solo sui dati del Capitolato senza incorporare
  le risposte ai chiarimenti — avvisa l'utente prima di procedere).
---

# Gara Effort & Cost Model Estimator (Fase 3)

Produce il modello economico completo della gara a partire dal workbook Excel di handoff
prodotto in Fase 1 (`gara-rfp-handoff`) e aggiornato manualmente in Fase 2 con le risposte
ai chiarimenti del cliente. L'output è un file Excel separato `[nome_gara]_CostModel_v1.xlsx`
con 4 sheet — Stima Effort, Cost Model, Sensitivity Pricing, Risk Register Stima — generato
copiando e popolando un template ufficiale.

**Vincolo operativo non negoziabile (da `prompt_2.txt`):** prima di procedere con stime,
calcoli o interpretazioni non esplicitamente supportati dagli input, fermati e chiedi
conferma. Non introdurre ipotesi senza dichiararle. Se un dato è assente o ambiguo,
classificalo come "assunzione operativa" e documenta valore, razionale, impatto. Non usare
benchmark di settore senza indicarne la fonte e chiedere validazione.

## Posizionamento nel processo (4 step)

```
Fase 1 — Valutazione caratteristiche commerciali e tecniche
   └─ skill: gara-rfp-handoff
   └─ output: rfp_handoff.xlsx (10 sheet operativi + _Esempi)

Step 2 — Brainstorming delivery/bid (primo deliverable executive)
   └─ skill: gara-rfp-deck
   └─ output: executive_summary.pptx (10 slide pre-formattate)
   └─ utilizzato per allineamento interno PRIMA dei chiarimenti al cliente

Fase 2 — Aggiornamento post-chiarimenti (MANUALE)
   └─ il bid manager invia le domande Sheet 9 al cliente
   └─ riceve risposte, aggiorna Stato/Data/Sintesi nel Sheet 9
   └─ valorizza eventuali parametri "DA ASSUMERE" del Sheet 8 con i nuovi dati

Fase 3 — Stima Effort & Cost Model  ◄── QUESTA SKILL
   └─ skill: gara-effort-cost-estimator
   └─ pre-step: aggiorna Sheet 10 dell'Excel input
   └─ output: [nome_gara]_CostModel_v1.xlsx (4 sheet)
```

**`gara-rfp-deck` è Step 2 del processo**, non skill ausiliaria. Va invocata
immediatamente dopo `gara-rfp-handoff` (Fase 1) per produrre il deck di brainstorming
delivery/bid prima della Fase 2 manuale dei chiarimenti.

## Distinzione vs `gara-bid-estimator`

`gara-bid-estimator` esiste già ma fa parte di un **percorso di stima parallelo e
indipendente** (catena `gara-rfp-analyzer` → `gara-req-extractor` → `gara-bid-estimator`
con input `requisiti_estratti.json`). Le due skill non vanno mai mescolate.

| | `gara-bid-estimator` | `gara-effort-cost-estimator` (questa) |
|---|---|---|
| **Input** | `requisiti_estratti.json` (output di `gara-req-extractor`) | `rfp_handoff.xlsx` (output di `gara-rfp-handoff`) |
| **Catena** | analyzer → req-extractor → bid-estimator | rfp-handoff → fase 2 manuale → effort-cost-estimator |
| **Focus** | Stima solution design (effort di sviluppo per requisito) | Cost model commerciale completo: effort + costi + ricavi + margine + sensitivity + risk register |
| **Output** | Template Excel "Stima Solution Design" | `[nome_gara]_CostModel_v1.xlsx` con 4 sheet |

**In caso di dubbio sul trigger**: l'input è discriminante.
- Input = `requisiti_estratti.json` → `gara-bid-estimator`
- Input = `rfp_handoff.xlsx` → questa skill

## Input richiesti

- File `.xlsx` prodotto da `gara-rfp-handoff` con i 10 sheet operativi:
  `1. Info Sintetiche RFP`, `2. Mappatura Capability`, `3. Driver di Stima`,
  `4. Gap Analysis`, `5. Domande Chiarimento`, `6. Assunzioni`,
  `7. Matrice Profili x Capability`, `8. Input Cost Model`,
  `9. Registro Chiarimenti`, `10. Nota di Handoff`.

Se il file è privo dei sheet 8, 9 o 10, la skill non può procedere — termina con messaggio
di errore.

Se il Sheet 9 ha tutte le righe in stato `Non inviato`, avvisa l'utente che la Fase 2 non è
stata svolta e proponi due opzioni: (a) procedere con la stima basata solo sui dati del
Capitolato di Fase 1 (più rischiosa, molti gap aperti); (b) sospendere e completare prima
la Fase 2.

## Comportamento interattivo (regola assoluta)

Prima di costruire i 4 sheet di output, la skill DEVE eseguire il seguente ciclo:

### Step A — Lettura stato attuale dell'input

Legge:
- **Sheet 1**: nome cliente, durata contrattuale, modello commerciale, tariffe T&M,
  GG/U totali T&M annui, sede.
- **Sheet 2**: mappatura capability L1/L2/L3, profili coinvolti per capability.
- **Sheet 6**: tutte le assunzioni con relativo Rischio (ALTO/MEDIO/BASSO).
- **Sheet 7**: matrice profili × capability (chi fa cosa, in che volume).
- **Sheet 8**: parametri **certi** (verdi), **da assumere** (gialli — verifica se sono
  stati valorizzati durante la Fase 2), **bloccanti** (rossi — verifica se sono stati
  risolti).
- **Sheet 9**: stato di ciascun chiarimento (`Non inviato` / `Inviato` / `Risposta
  ricevuta`) + sintesi risposta + flag bloccante.

### Step B — Classificazione di ogni dato di stima

Per ogni dato che entrerà nei 4 sheet di output, classifica la fonte:

- `certo` — estratto direttamente dal Capitolato di gara o dalle risposte ai chiarimenti
  (Sheet 9 stato = `Risposta ricevuta`). Cita riferimento.
- `assunzione operativa` — assente nei documenti e dalle risposte. Documenta valore,
  razionale, impatto sul risultato.
- `benchmark` — proposto sulla base di benchmark di settore. **Cita SEMPRE la fonte**
  (es. "Gartner IT Outsourcing 2024", "ISBSG benchmark", "internal rate card 2024",
  "data dal Sheet 6 di una gara similare"). Senza fonte non è ammesso.
- `bloccante` — dato necessario ma assente sia dai documenti sia dalle risposte; non
  ammette assunzione perché impatto troppo grande senza chiarimento.

### Step C — Registro scelte interpretative

Presenta in chat all'utente, in formato Markdown strutturato:

1. **Scelte di stima certe** — tabella numerata: cosa, valore, fonte, riferimento.
2. **Assunzioni operative proposte** — tabella numerata: cosa, valore assunto, razionale,
   impatto se errata, rischio (ALTO/MEDIO/BASSO).
3. **Benchmark di settore proposti** — tabella numerata: cosa, valore, fonte
   (citazione completa), razionale, impatto se errato.
4. **Bloccanti residui** — lista delle voci che restano in sezione ROSSA del Sheet 8 anche
   dopo la Fase 2; per queste la skill propone uno scenario worst-case da tracciare nel
   Risk Register, ma non valorizza il Cost Model.

### Step D — Attesa approvazione

Termina il messaggio con domanda esplicita:

> "Confermi tutte le scelte di stima, le assunzioni operative e i benchmark elencati?
> (sì / modifica N / no)"

**FERMATI qui.** Non popolare il template finché non c'è approvazione esplicita.

### Step E — Pre-step OBBLIGATORIO: aggiornamento Sheet 10 dell'input

Solo dopo approvazione, **prima** di generare il file di output:

1. Apri il file `rfp_handoff.xlsx` in modalità scrittura.
2. Riscrivi le 3 sezioni del Sheet 10 (`COSA È CONFERMATO`, `COSA È APERTO`,
   `DECISION POINT CRITICI`) sulla base dello stato attuale di Sheet 8 e Sheet 9:
   - **`COSA È CONFERMATO`**: include tutte le voci verdi del Sheet 8 + tutti i
     chiarimenti del Sheet 9 con `Stato = Risposta ricevuta` + sintesi della risposta.
   - **`COSA È APERTO`**: include tutte le voci gialle del Sheet 8 con prefisso
     `DA ASSUMERE — ...` + tutti i chiarimenti `Inviato` o `Non inviato` con prefisso
     `BLOCCANTE — ...` o `IN ATTESA — ...` (in funzione del flag `Bloccante per stima`).
   - **`DECISION POINT CRITICI`**: include i parametri rossi del Sheet 8 ancora
     irrisolti + i chiarimenti `Bloccante per stima = SI` ancora `Inviato` (in attesa di
     risposta).
3. Salva il file. **Non toccare nessun altro sheet** — vincolo da `prompt_2.txt`.

### Step F — Generazione del file di output

1. Estrai il **nome gara** dal Sheet 1, riga 4 colonna B (label "Stazione appaltante"),
   prendendo il primo token significativo (es. "RAI", "Comune di Milano", "Poste Italiane").
2. Copia `assets/template_cost_model.xlsx` come `[nome_gara]_CostModel_v1.xlsx` nella
   working directory dell'utente.
3. Popola le 4 sheet del template applicando le regole di formattazione (verde / giallo /
   rosso / blu / nero) cella per cella.
4. Inserisci formule Excel per ogni calcolo. **Mai valori calcolati in Python e poi
   incollati come hardcoded.**

### Step G — Riepilogo finale

Presenta il riepilogo dell'output (vedi sezione "Workflow > Step 8" sotto).

## Le 5 sheet del file di output (struttura del template)

Il template `assets/template_cost_model.xlsx` è organizzato in **5 sheet operativi
+ 1 sheet `_Esempi`**. La filosofia del template è:

> **Lo Sheet 0 è l'unico punto di INPUT.** Tutti gli altri sheet (A, B, C) sono interamente
> formula-driven con riferimenti tipo `='0. Parametri'!$D$N`. Una volta valorizzato Sheet 0,
> Stima Effort / Cost Model / Sensitivity si ricalcolano automaticamente. Solo lo Sheet D
> (Risk Register) richiede compilazione manuale perché elenca rischi qualitativi.

### `0. Parametri` — Input centralizzato (57 parametri in 10 sezioni)

L'unico sheet realmente da popolare. Colonne: `#`, `Categoria`, `Parametro`, `Valore`,
`Unità`, `Fonte / Origine`, `Note`.

Sezioni (titoli merged):
1. **ECONOMICS DI GARA — Valori contrattuali (€)** (rows 6-12): Startup, Canone base 36m,
   Plafond T&M 36m, Canone proroga 24m, Plafond T&M proroga 24m, Oneri sicurezza.
2. **TARIFFE T&M — Base d'asta** (rows 13-17): tariffe Architetto, TL/Analista funzionale,
   Analista Programmatore, Programmatore (€/GG).
3. **VOLUMI T&M — Capitolato p.36** (rows 18-22): GG/U/anno per i 4 profili T&M.
4. **COMPOSIZIONE TEAM CANONE** (rows 23-28): n. risorse per ruolo (SM, TL d'area, Tech
   Leader, Analista Programmatore, Programmatore).
5. **COSTI INTERNI — Costo giornaliero pieno aziendale** (rows 29-35): €/GG per ciascun
   profilo + Architetto T&M (top seniority).
6. **DRIVER OPERATIVI MAC** (rows 36-46): ticket totali/anno, distribuzione % P1/P2/P3/P4,
   effort medio P1/P2/P3/P4 in ore, ore lavorative/GG.
7. **DRIVER OPERATIVI ALTRI SERVIZI CANONE** (rows 47-58): chiamate REP/mese, durata
   intervento REP, eventi speciali, profili dedicati eventi, attività GES/GST/anno con
   relativi effort, conferimenti CON sui 39 mesi.
8. **CAPACITY / DURATA** (rows 59-64): GG lavorativi/anno per risorsa, mesi startup,
   mesi periodo operativo, mesi proroga, % capacity in fase startup.
9. **STRATEGIA RIBASSO** (rows 65-68): % ribasso canone, % ribasso T&M, tasso utilizzo plafond.
10. **OVERHEAD / CONTINGENCY / INFLAZIONE** (rows 69-72): % overhead PM, % contingency,
    tasso inflazione costo lavoro/anno.

**Color coding del Sheet 0**:
- **Verde (#DCFCE7)** sezioni 1-4 + alcuni driver operativi: parametri certi (Disciplinare,
  Capitolato, risposte cliente).
- **Giallo (#FEF9C3)** sezioni 5, 8 (alcune righe), 9, 10: assunzioni operative del
  cost modeler.
- **Rosso (#FEE2E2)** sezione 3 (Volumi T&M): bloccanti irrisolti — il template adotta
  un valore di default (Capitolato p.36) per far girare il modello, ma la cella resta
  marcata rossa.

### `A. Stima Effort` — Effort calcolato (sola formula, no input)

Tre sotto-sezioni:
- **A.1 SERVIZI CANONE — Effort operativo necessario** (rows 5-11): per MAC/REP/GES/GST/CON
  calcola `GG/U Anno`, `GG/U Startup (3m)`, `GG/U Periodo Base 36m`, `GG/U Totale 39m`
  da driver Sheet 0 sezioni 6-7. Subtotale row 11.
- **A.2 SERVIZI CANONE — Capacity team presidio fisso** (rows 13-19): per ciascun profilo
  Canone (SM, TL, Tech Leader, AP, Prog) calcola la capacity totale come `n risorse × 220
  GG/U/anno`. Totale row 19. Una nota riga 20 segnala che capacity ≥ effort operativo.
- **A.3 SERVIZI T&M — Volumi Capitolato** (rows 22-27): per i 4 profili T&M legge i
  GG/U/anno dal Sheet 0 sezione 3, calcola GG/U startup (=0) e periodo base. Totale row 27.

Colonne: `Servizio`, `Capability / Profilo`, `Driver di calcolo`, `Formula / Volume`,
`GG/U Anno`, `GG/U Startup (3m)`, `GG/U Periodo Base 36m`, `GG/U Totale 39m`,
`Metodo / Fonte` (l'unica col da popolare con il riferimento alla fonte).

### `B. Cost Model` — Ricavi, Costi, Margine (sola formula, no input)

Cinque sotto-sezioni:
- **B.1 RICAVI** (rows 4-11): Ricavo Startup, Canone post ribasso, T&M Capitolato post
  ribasso, Plafond residuo (info), Oneri sicurezza, Totale ricavi 39 mesi.
- **B.2 COSTI DIRETTI** (rows 13-18): costo team Canone Startup (60% capacity), Canone
  periodo operativo (100%), T&M periodo operativo, Totale costi diretti.
- **B.3 COSTI INDIRETTI** (rows 20-26): overhead PM, contingency, inflazione cumulata,
  totale indiretti.
- **B.4 MARGINE TOTALE** (rows 27-31): Totale ricavi, totale costi (diretti+indiretti),
  margine €, margine %.
- **B.5 MARGINE PER SERVIZIO** (rows 32-37): canone solo, T&M solo, startup, ricavi vs costi
  per linea di servizio.

Colonne tipiche: `Voce`, `Calcolo`, `Lordo (pre ribasso)`, `% Ribasso`, `Netto (post
ribasso)`, `Riferimento`, `Note`. Le colonne F (Riferimento) e G (Note) sono libere e
vanno popolate con i riferimenti alla fonte.

### `C. Sensitivity Pricing` — Scenari e matrice di sensitività (sola formula)

Due sotto-sezioni:
- **C.1 SCENARI PREDEFINITI** (rows 4-10): 5 scenari pre-impostati nel template:
  `Conservativo` (ribasso 5/5/70%), `Base` (10/8/100%), `Aggressivo` (15/12/100%),
  `Disciplinare-Plafond Conservativo` (5/5/70%, basato su plafond invece di volumi
  Capitolato), `Disciplinare-Plafond Base` (10/8/100%). Per ognuno: % ribasso canone,
  % ribasso T&M, % utilizzo plafond, volumi T&M (Capitolato/Plafond), ricavi/costi/margine.
- **C.2 MATRICE SENSITIVITY** (rows 12-18): griglia 5×5 che incrocia % ribasso canone
  (0/5/10/15/20%) × % ribasso T&M (0/5/8/10/15%), mostrando margine % atteso.

Le colonne A-K sono interamente formula-driven. La colonna L (Note) è libera e va popolata
con commenti specifici dello scenario.

### `D. Risk Register Stima` — Rischi associati alla stima (input manuale)

Unico sheet senza formule. Una riga per ogni:
- assunzione operativa marcata GIALLA in Sheet 0 → un rischio che documenta cosa succede
  se l'assunzione è errata
- bloccante irrisolto marcato ROSSO in Sheet 0 → un rischio CRITICO con impatto economico
- chiarimento aperto/non inviato dal Sheet 9 dell'input
- rischi strutturali emersi durante l'analisi (es. margine canone negativo, team somma a
  42 invece di 41 dichiarati)

Colonne: `#`, `Rischio`, `Origine (Sheet 8/9)`, `Impatto stimato €`, `Probabilità` (drop-down
`A`/`M`/`B`), `Severity` (drop-down `CRITICA`/`ALTA`/`MEDIA`/`BASSA`), `Mitigazione`,
`Owner`.

Ordina per Severity decrescente, poi per Probabilità decrescente.

### `_Esempi` — Riferimento di compilazione

Ultimo sheet del workbook. Contiene esempi reali estratti dalla gara RAI per ogni sheet
operativo (parametro verde/giallo/rosso del Sheet 0, riga MAC e Architetto T&M del Sheet
A, ricavo canone e costo team del Sheet B, scenario Base e Plafond del Sheet C, due
rischi tipici del Sheet D). Le formule sono mostrate come testo illustrativo prefissato
con `↳ ` per non essere valutate da Excel.

**OBBLIGATORIO**: leggi `_Esempi` prima di compilare ogni sheet.

## Regole di formattazione (vincolo non negoziabile da `prompt_2.txt`)

- **Sfondo verde** (es. `#C6EFCE`): cella con valore certo (estratto da documento
  o risposta a chiarimento). Cell comment opzionale con riferimento.
- **Sfondo giallo** (es. `#FFEB9C`): cella con valore assunto (assunzione operativa o
  benchmark). **Cell comment OBBLIGATORIO** con razionale; per i benchmark, prefisso
  `[BENCHMARK: <fonte>]`.
- **Sfondo rosso** (es. `#FFC7CE`): cella con valore bloccante non risolto. Cell comment
  OBBLIGATORIO con descrizione del blocco.
- **Testo blu** (`#0070C0`): input hardcoded (rate card, % ribasso, costi interni, GG/U
  base d'asta).
- **Testo nero**: formule e celle calcolate.
- **Font**: Arial o Calibri (allineato al template, da definire in Fase B).
- **Zero errori formula**: nessun `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`. Usa
  `IFERROR(...)` dove appropriato.

## Workflow

### Step 1 — Validazione input
Verifica che il file `.xlsx` di input esista, sia leggibile, contenga tutti i 10 sheet
attesi del template `gara-rfp-handoff`. Errore se mancano sheet 8, 9, 10.

### Step 2 — Lettura stato attuale
Esegui Step A della sezione "Comportamento interattivo".

### Step 3 — Costruzione bozza interna
Costruisci internamente la mappatura dei **57 parametri del Sheet 0** del template a
partire dai dati dell'Excel handoff (Sheet 1, 6, 7, 8, 9). Marca ogni parametro come
`certo` / `assunzione` / `benchmark` / `bloccante`.

In aggiunta, costruisci la lista delle voci da inserire in **Sheet D (Risk Register)**:
una riga per ogni assunzione gialla del Sheet 0, ogni bloccante rosso, ogni chiarimento
aperto/non inviato del Sheet 9 dell'input, ogni rischio strutturale emerso dall'analisi.

Per le colonne fonte/nota dei Sheet A, B, C (col I per A, F+G per B, L per C): prepara
il testo specifico della gara (es. "Risposta RAI #1,2 + assunzione distribuzione",
"Bloccante #1 non risolto").

**Non scrivere ancora il file di output e non toccare ancora il file di input.**

I sheet A, B, C **non richiedono dati**: si calcolano via formule a partire dal Sheet 0
una volta che il template è copiato e popolato.

### Step 4 — Presentazione registro scelte interpretative
Esegui Step C della sezione "Comportamento interattivo".

### Step 5 — Attesa approvazione
**FERMATI.** Non procedere finché l'utente non risponde.

### Step 6 — Applicazione modifiche (se richieste)
Se l'utente chiede modifiche, applicale e ripresenta il registro aggiornato.

### Step 7 — Aggiornamento Sheet 10 dell'input + popolamento template di output

1. Esegui Step E (pre-step Sheet 10 dell'input).
2. Estrai il **nome gara** dal Sheet 1 dell'input (riga 4 col B, primo token).
3. Copia `assets/template_cost_model.xlsx` come `[nome_gara]_CostModel_v1.xlsx` nella
   working directory dell'utente.
4. **Popola il Sheet 0 (Parametri)**:
   - colonna `D` (Valore) con i 57 valori approvati nel registro
   - colonna `F` (Fonte / Origine) con la citazione esatta (es. "Disciplinare p.11-12",
     "Risposta RAI #1", "Capitolato p.36", "Cost Modeler", "Bid manager",
     "[BENCHMARK: <fonte>]")
   - colonna `G` (Note) per i casi che richiedono spiegazione (es. valori bloccanti
     irrisolti adottati come default, scelte tra alternative)
5. **Popola le colonne fonte/nota dei Sheet A, B, C** (l'unica parte di questi sheet
   che richiede compilazione): col I in A, col F e G in B, col L in C. Tutto il resto si
   calcola da solo.
6. **Popola il Sheet D (Risk Register)**: una riga per ogni voce della bozza interna,
   ordinata per Severity DESC poi per Probabilità DESC.
7. Verifica che le formule di A, B, C non producano errori (`#REF!`, `#DIV/0!`, ecc.).
8. Salva il file.

**Vincoli**:
- **Mai modificare le formule di A, B, C**: sono parte del template. Se servono nuovi
  calcoli, comunica all'utente che la struttura è bloccata.
- **Mai sostituire formule con valori hardcoded**: se una formula del template puntasse
  a una cella vuota, non sostituirla con il numero risultante — lascia la formula e
  popola la cella sorgente in Sheet 0.
- **Color coding cella per cella**: il template ha già il color coding di default per
  Sheet 0 (verde/giallo/rosso per sezione). Se un parametro cambia categoria rispetto al
  default (es. una sezione Verde diventa Gialla perché la fonte ufficiale manca), aggiorna
  il fill della cella.

### Step 8 — Riepilogo finale
Presenta in chat:

> **Cost Model generato — [Nome gara]**
>
> File prodotto: `[nome_gara]_CostModel_v1.xlsx`
> File di input aggiornato (solo Sheet 10): `rfp_handoff.xlsx`
>
> **Sheet 0 (Parametri)**: 57 parametri valorizzati — Verdi: N | Gialli: N | Rossi: N
> **Sheet A (Stima Effort)**: ricalcolato — Effort canone N GG/U | Capacity presidio N GG/U | T&M N GG/U
> **Sheet B (Cost Model)**: ricavo netto €..., costo totale €..., margine lordo €... (XX%)
> **Sheet C (Sensitivity)**: 5 scenari — Conservativo: Y%, Base: Y%, Aggressivo: Y%, +2 plafond
> **Sheet D (Risk Register)**: N rischi (CRITICA: N, ALTA: N, MEDIA: N, BASSA: N)
>
> **Distribuzione fonte dati Sheet 0**: certo N | assunzione operativa N | benchmark N | bloccante N
>
> **Prossimo passo**: revisione cost modeler / commercial review per definire strategia di
> ribasso e finalizzare offerta economica.

## Tracciabilità

Per ogni dato nel workbook di output, classifica la certezza (estensione vs
`gara-rfp-handoff` per coprire i benchmark):

- `certo` — Sheet 8 verde dell'input + risposte cliente Sheet 9 = `Risposta ricevuta`.
- `assunzione operativa` — assente nei documenti e nelle risposte; valore proposto.
- `benchmark` — basato su fonte esterna esplicitamente citata e validata dall'utente.
- `bloccante` — assente sia da documenti sia da risposte; non ammette assunzione per via
  dell'impatto economico. Tracciato in Sheet D, non nel Cost Model.

Le assunzioni del Sheet 6 dell'input sono già tracciate; non duplicarle nel registro
scelte interpretative — citale per riferimento.

## Regole operative

- **Comportamento interattivo non negoziabile**: la skill SI FERMA dopo lo Step 4
  (registro scelte) e attende approvazione. Non modificare mai il Sheet 10 dell'input
  prima dell'approvazione.
- **Modifica Sheet 10 dell'input solo dopo approvazione**: la modifica è IN-PLACE ma
  vincolata al solo Sheet 10. Tutti gli altri sheet dell'input restano invariati
  (verifica byte-level pre/post).
- **Mai valori calcolati in Python e incollati come hardcoded**: tutti i calcoli del
  Cost Model devono essere formule Excel.
- **Benchmark sempre con fonte**: se proponi un valore basato su benchmark, cita la fonte
  e il prefisso `[BENCHMARK: <fonte>]` nella nota cella. Senza fonte non è ammesso.
- **Bloccanti non si valorizzano**: se un dato è classificato `bloccante`, non
  inventare un valore di compromesso. Vai nello scenario worst-case e tracciare nel
  Risk Register.
- **Naming output**: `[nome_gara]_CostModel_v1.xlsx`, dove `[nome_gara]` è il primo token
  significativo della Stazione appaltante (Sheet 1 B4). Es: "RAI", "PosteItaliane",
  "ComuneMilano".
- **Lingua**: italiano, salvo che l'Excel handoff non sia in altra lingua.
- **Formule**: zero errori. Verifica con `scripts/recalc.py` della skill `xlsx` se
  disponibile.

## Self-check pre-output (obbligatorio dopo Step 7)

Prima di presentare il riepilogo finale all'utente (Step 8), eseguire i seguenti controlli
di sanità sulle formule del Sheet A. Se uno qualsiasi fallisce, segnalarlo come anomalia
strutturale del template nel Risk Register Sheet D (Severity CRITICA) e comunicarlo
all'utente:

1. **Capacity team presidio Sheet A righe 14-18** — ogni formula in col E deve essere del
   tipo `='0. Parametri'!$D$<N>*'0. Parametri'!$D$60` dove `<N>` è la riga del Sheet 0 che
   contiene il **numero di risorse** (non il costo €/GG):
   - Row 14 Service Manager → deve puntare a `$D$24` (n. SM), non `$D$30` (costo SM)
   - Row 15 Team Leader d'area → `$D$25` (n. TL)
   - Row 16 Technical Leader → `$D$26` (n. TechL)
   - Row 17 Analista Programmatore → `$D$27` (n. AP)
   - Row 18 Programmatore → `$D$28` (n. Prog)

   Verifica programmatica: per ogni riga 14-18, leggere la formula col E e verificare che
   contenga il numero di riga corretto del Sheet 0 (24/25/26/27/28). Se trova un riferimento
   diverso (es. 30/31/32/33/34 che sono i costi interni), è un **bug del template**.

2. **Totale capacity ≈ totale risorse × GG/anno** — la formula `=SUM(E14:E18)` in row 19
   deve risultare circa `(n_SM + n_TL + n_TechL + n_AP + n_Prog) × GG_lav_anno`. Per il
   caso RAI standard: `(1+4+11+12+14) × 220 = 9.240`. Se il valore differisce di un ordine
   di grandezza, è probabile bug del template.

3. **Formule sezione T&M (rows 23-26)** — devono puntare a `$D$19-$D$22` (volumi T&M
   GG/U/anno).

**Azione in caso di failure**: NON modificare le formule del template dall'output
generato (vincolo "Mai modificare le formule di A, B, C"). Invece: (a) inserire una voce
CRITICA nel Risk Register Sheet D che descriva il bug e il workaround manuale, (b)
comunicare all'utente nel riepilogo finale che il template ha anomalie strutturali da
correggere alla sorgente (`assets/template_cost_model.xlsx`).

## Asset

- `assets/template_cost_model.xlsx` — template ufficiale del workbook Cost Model. Contiene
  6 sheet: `0. Parametri` (57 input slot in 10 sezioni), `A. Stima Effort` (formule),
  `B. Cost Model` (formule), `C. Sensitivity Pricing` (formule + matrice 5×5),
  `D. Risk Register Stima` (input manuale con drop-down `A/M/B` e `CRITICA/ALTA/MEDIA/BASSA`),
  `_Esempi` (esempi di compilazione tratti dalla gara RAI).
- 161 formule pre-impostate nei Sheet A/B/C che pescano dal Sheet 0. **Non modificarle.**
- 2 data validation pre-impostate nel Sheet D (colonne E e F).

**Non modificare il template in place**: copialo nella working directory dell'utente come
`[nome_gara]_CostModel_v1.xlsx` e popolalo lì.
