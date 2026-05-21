---
name: gara-workflow
description: >
  Orchestratore end-to-end del processo di risposta a una gara/RFP. Guida l'utente
  attraverso tutte le fasi richiamando le 6 skill `gara-*` esistenti nei punti giusti,
  gestendo la pausa per la Fase 2 manuale (chiarimenti cliente), classificando
  automaticamente il tipo di gara dai JSON prodotti a monte e decidendo il branching
  della Fase 3 (solo Cost Model vs Cost Model + Stima Soluzione).
  TRIGGER Fase 1+2 (avvio): l'utente carica i documenti di una gara (capitolato,
  disciplinare, CSA, bando, RFP) e chiede "rispondi alla gara X", "voglio fare l'offerta",
  "guidami nella risposta", "esegui il workflow completo della gara", "fammi il pacchetto
  bid completo", "lancia il flusso gara end-to-end", oppure cita "workflow gara" o
  "orchestratore gara".
  TRIGGER Fase 3 (ripresa): l'utente ha già un `rfp_handoff.xlsx` con il Sheet 9
  (Registro Chiarimenti) aggiornato dalle risposte cliente e chiede "completa la gara",
  "ho ricevuto i chiarimenti, vai con la stima", "lancia Fase 3", "ho aggiornato Sheet 9
  prosegui", o "siamo pronti per cost model e stima soluzione".
  OUTPUT progressivi del ciclo: `rfp_analysis.json`, `requisiti_estratti.json`,
  `rfp_handoff.xlsx`, `executive_summary.pptx`, `[gara]_CostModel_v1.xlsx` e
  (condizionale) `Stima_SolutionDesign_*.xlsx`.
  COMPORTAMENTO INTERATTIVO OBBLIGATORIO: la skill si ferma in 5 punti naturali
  (domande bloccanti extractor, Step B handoff, Fase 2 manuale, conferma classificazione
  tipo gara, Step C cost-estimator). Non prosegue mai senza input esplicito dell'utente.
  La pausa Fase 2 è SEMPRE attiva (eccezione: l'utente dichiara esplicitamente "il
  cliente non risponderà, procedi senza chiarimenti").
  COMPORTAMENTO NON AUTOMATICO: la skill NON esegue le altre `gara-*` skill da sola.
  Le invoca via Skill tool una alla volta, attendendo che ciascuna abbia chiuso il
  proprio workflow prima di passare alla successiva.
  SKIP se l'utente chiede esplicitamente UNA SOLA delle 6 skill atomiche (es. "solo
  l'extractor", "solo il deck", "solo il cost model") — in tal caso reindirizza alla
  skill specifica e termina; non avviare il workflow completo. SKIP se i documenti
  forniti non sono di una gara (contratto esecutivo, verbale, fattura, collaudo).
---

# Gara Workflow — orchestratore end-to-end

Skill orchestratore che codifica l'intero processo di risposta a una gara/RFP, dalle
prime letture dei documenti fino alla stima finale (Cost Model commerciale ed
eventualmente Stima di Solution Design).

**Non sostituisce** le 6 skill atomiche (`gara-rfp-analyzer`, `gara-req-extractor`,
`gara-rfp-handoff`, `gara-rfp-deck`, `gara-effort-cost-estimator`, `gara-bid-estimator`):
le richiama nei punti corretti del flusso. Chi vuole può sempre invocare le singole skill
direttamente — questa è l'opzione "guidata".

## Mappa delle 6 skill `gara-*` e I/O

| Skill | Input | Output | Interattività |
|---|---|---|---|
| `gara-rfp-analyzer` | doc gara | `rfp_analysis.json` | Zero domande |
| `gara-req-extractor` | doc gara + (`rfp_analysis.json` opt) | `requisiti_estratti.json` | Solo se bloccanti |
| `gara-rfp-handoff` | doc gara + `requisiti_estratti.json` (obbl.) | `rfp_handoff.xlsx` (12 sheet) | Step B approvazione |
| `gara-rfp-deck` | `rfp_handoff.xlsx` | `executive_summary.pptx` | Zero domande |
| `gara-effort-cost-estimator` | `rfp_handoff.xlsx` con Sheet 9 aggiornato | `[gara]_CostModel_v1.xlsx` + Sheet 10 dell'handoff riscritto in-place | Step C approvazione |
| `gara-bid-estimator` | `requisiti_estratti.json` (+ `rfp_analysis.json` opt) | `Stima_SolutionDesign_*.xlsx` | Solo se bloccanti residui |

## Due punti di ingresso

La skill ha due modalità a seconda di cosa esiste già nella working directory:

### Ingresso A — Fase 1+2 (partenza da zero, ci sono solo i documenti di gara)

Esegue dallo Step 1 allo Step 6. Termina con una pausa esplicita: l'utente deve
completare la **Fase 2 manuale** (invio domande al cliente, raccolta risposte,
aggiornamento Sheet 9 e Sheet 10 dell'handoff) e poi rilanciare la skill. **Sheet 8
NON è materiale del bid manager**: i parametri V/G/R di Sheet 8 saranno valorizzati
dal cost modeler in Fase 3 leggendo le sintesi delle risposte cliente da Sheet 9.

### Ingresso B — Fase 3 (ripresa dopo i chiarimenti cliente)

Esegue dallo Step 7 allo Step 10. Richiede `rfp_handoff.xlsx` con almeno una riga
del Sheet 9 in stato `Risposta ricevuta`.

## Workflow

### Step 1 — Routing del punto di ingresso

Verifica i file presenti in working directory:

```
ESISTE rfp_handoff.xlsx con Sheet 9 contenente righe "Risposta ricevuta"?
├── SÌ → vai a Step 7 (Ingresso B — Fase 3)
└── NO → ESISTE rfp_handoff.xlsx (anche senza risposte)?
         ├── SÌ → chiedi conferma all'utente: "Trovo rfp_handoff.xlsx ma Sheet 9
         │       non ha risposte ricevute. Vuoi (a) proseguire da Fase 2 manuale
         │       /completa Sheet 9 prima, oppure (b) re-eseguire da zero?"
         └── NO → vai a Step 2 (Ingresso A — Fase 1)
```

### Step 2 — Invoca `gara-rfp-analyzer`

Output atteso: `rfp_analysis.json` nella working directory.

La skill è non interattiva: parte e finisce in autonomia. Al termine, verifica che il
file sia stato prodotto correttamente.

### Step 3 — Invoca `gara-req-extractor`

Output atteso: `requisiti_estratti.json` (schema v2.0).

**Comportamento bloccante**: la skill può sospendersi al termine dell'estrazione per
presentare `domande_bloccanti` di scope-critical. Se questo accade:
- Trasmetti le domande all'utente esattamente come la skill le ha presentate.
- **FERMATI**. Non proseguire il workflow finché l'utente non ha risposto.
- Quando l'utente risponde, la skill extractor produrrà il JSON e potrai procedere.

### Step 4 — Invoca `gara-rfp-handoff`

Input: i documenti di gara + `requisiti_estratti.json` (prerequisito già introdotto
nella skill handoff). Output atteso: `rfp_handoff.xlsx` (12 sheet: 10 numerati +
Requisiti + _Esempi).

**Comportamento bloccante**: la skill si ferma allo Step B per chiedere approvazione
del "Registro scelte interpretative" (estratto/inferito/assunto). Trasmetti il registro
all'utente esattamente come la skill lo presenta, **FERMATI**, attendi l'approvazione.
Solo dopo, la skill produrrà il file e potrai procedere.

### Step 5 — Invoca `gara-rfp-deck`

Input: `rfp_handoff.xlsx`. Output: `executive_summary.pptx` (10 slide).
Non interattiva: parte e finisce in autonomia.

### Step 6 — STOP per Fase 2 manuale (bid manager)

Presenta in chat all'utente questo messaggio strutturato:

```markdown
## ✅ Fase 1 completata — deliverable prodotti

- `rfp_analysis.json` — analisi strategica della gara
- `requisiti_estratti.json` — N requisiti (di cui A padre, B figlio, C singoli)
- `rfp_handoff.xlsx` — workbook 12 sheet per il team di stima
- `executive_summary.pptx` — deck 10 slide per brainstorming delivery/bid

## 🟡 Fase 2 — Manuale (a carico del bid manager)

Azioni richieste prima di lanciare Fase 3:

1. **Estrarre dal Sheet 9 (Registro Chiarimenti)** le N domande in stato
   `Non inviato`, in particolare quelle con `Bloccante per stima = SI`.
2. **Inviare le domande al cliente** (mail, portale gare, riunione di chiarimento).
3. **Aggiornare Sheet 9** mano a mano che arrivano le risposte:
   - colonna `Stato`: da `Non inviato` → `Inviato` → `Risposta ricevuta`
   - colonna `Data Risposta`: data effettiva
   - colonna `Sintesi Risposta`: 1-2 frasi che catturano la risposta (testo della risposta cliente, non valori numerici)
   - colonna `Bloccante per stima`: aggiornare a `NO` se la risposta scioglie il blocco
4. **Aggiornare Sheet 10 (Nota di Handoff)**: riclassificare le voci della sezione 2
   `COSA È APERTO` man mano che le risposte arrivano — spostare in sezione 1
   `COSA È CONFERMATO` le voci BLOCCANTE/DA ASSUMERE che hanno avuto risposta cliente.
5. **NON toccare il Sheet 8** (Input Cost Model). I parametri V/G/R di Sheet 8 sono
   materiale del **cost modeler in Fase 3**, non del bid manager. Il cost modeler
   in Fase 3 leggerà le sintesi delle risposte di Sheet 9 e tradurrà i testi del
   bid manager in parametri numerici (es. "volume MAC 1.500/anno split 8/12/35/45")
   spostando le voci dalla sezione GIALLO/ROSSO a VERDE.
6. **Salvare** il file aggiornato come `rfp_handoff.xlsx` nella stessa working directory.

## ⏭ Quando hai finito

Rilancia questa skill con una frase tipo:
- "Fase 2 completata, procedi con Fase 3"
- "Ho aggiornato il Sheet 9, prosegui"
- "Vai con cost model e stima soluzione"
```

**TERMINA QUI il primo lancio.** La skill NON prosegue automaticamente alla Fase 3.

**Eccezione**: se l'utente dichiara esplicitamente "il cliente non risponderà" o
"procedi senza chiarimenti", chiedi conferma una volta ("Confermi che vuoi saltare la
Fase 2 manuale? In tal caso i parametri GIALLI del Sheet 8 resteranno tali e il Cost
Model includerà un risk register più aggressivo"), e se l'utente conferma vai
direttamente a Step 7 senza pausa.

### Step 7 — Pre-flight Fase 3

Verifica esistenza dei 3 file:
- `rfp_handoff.xlsx` con almeno una riga del Sheet 9 in stato `Risposta ricevuta`
  (a meno dell'eccezione "il cliente non risponderà")
- `requisiti_estratti.json`
- `rfp_analysis.json`

Se uno manca, segnala l'errore con il path mancante e termina senza procedere.

### Step 8 — Classificazione automatica del tipo gara

Leggi i due JSON e applica il decision tree gerarchico (prima regola che matcha vince).

#### Decision tree

```
1. AM (Application Management) — Fase 3 = solo cost-estimator
   Tutte le seguenti condizioni devono essere vere:
   a) rfp_analysis.formato_risposta.modalita_prezzi ∈
      {time_and_material, tariffa_giornaliera, misto-TM-dominante}
   b) rfp_analysis.valore_economico.durata_contratto_mesi ≥ 24
   c) rfp_analysis.summary_tecnico.tipo_progetto ∈ {evolutiva, misto}
      OPPURE (requisiti.categoria_scope == custom_software > 70%
              AND area_funzionale dominante ∈ {PMO e Governance, Integrazione Sistemi Legacy})

2. SI_brownfield (System Integration brownfield) — Fase 3 = cost-estimator + bid-estimator
   Tutte le seguenti:
   a) rfp_analysis.summary_tecnico.tipo_progetto ∈ {brownfield, evolutiva, migrazione}
   b) rfp_analysis.stack_asis.applicable == true
   c) requisiti.categoria_scope == custom_software ≥ 50%

3. greenfield_prodotti (Greenfield a forte componente COTS) — Fase 3 = solo cost-estimator
   Tutte le seguenti:
   a) rfp_analysis.summary_tecnico.tipo_progetto == nuovo_sviluppo
   b) (requisiti.categoria_scope == cots_product
       + requisiti.categoria_scope == service_external) ≥ 50%

4. greenfield_custom (Greenfield sviluppo custom) — Fase 3 = cost-estimator + bid-estimator
   Tutte le seguenti:
   a) rfp_analysis.summary_tecnico.tipo_progetto == nuovo_sviluppo
   b) requisiti.categoria_scope == custom_software > 50%

5. Fallback — Fase 3 = chiedi all'utente
   Nessuna regola precedente matcha O JSON parziali O incoerenze tra i due:
   → tipo_gara = indeterminato
```

#### Presentazione all'utente

Indipendentemente dal risultato, presenta sempre questo messaggio:

```markdown
## Classificazione automatica del tipo gara

**tipo_gara**: <valore>

**Rationale**:
- 1 frase che spiega la regola che ha matchato (o perché si è caduti nel fallback)

**Fonti**:
- `rfp_analysis.summary_tecnico.tipo_progetto` = <valore>
- `rfp_analysis.formato_risposta.modalita_prezzi` = <valore>
- `rfp_analysis.valore_economico.durata_contratto_mesi` = <valore>
- `rfp_analysis.stack_asis.applicable` = <valore>
- `requisiti.categoria_scope` distribuzione:
  - custom_software: N% (M requisiti su totale)
  - cots_product: N%
  - service_external: N%
  - out_of_scope: N%
- `area_funzionale` dominante: <nome> (N requisiti)

**Conseguenza branching Fase 3**:
- AM o greenfield_prodotti → SOLO `gara-effort-cost-estimator`
- SI_brownfield o greenfield_custom → `gara-effort-cost-estimator` + `gara-bid-estimator`
- indeterminato → ti chiedo di scegliere esplicitamente

**Confermi questa classificazione?**
(rispondi "sì" / "modifica → <tipo corretto>" / per indeterminato: scegli tra AM, SI_brownfield, greenfield_custom, greenfield_prodotti)
```

**FERMATI.** Se l'utente conferma, usa la classificazione automatica. Se l'utente
sovrascrive, usa il suo valore. Solo dopo questa conferma procedi a Step 9.

### Step 8bis — Refresh Sheet 10 dell'handoff (PRE-STIMA, OBBLIGATORIO)

Prima di lanciare la stima vera e propria, aggiorna **in-place** il `Sheet 10 (Nota di
Handoff)` dell'`rfp_handoff.xlsx` rileggendo `Sheet 8 (Input Cost Model)` e
`Sheet 9 (Registro Chiarimenti)` nello stato attuale (post-Fase 2). Riscrivi le 3
sezioni di Sheet 10:

- **`1. COSA È CONFERMATO`**: include tutte le voci VERDI del Sheet 8 + tutte le righe
  del Sheet 9 con `Stato = Risposta ricevuta` e relativa sintesi della risposta cliente.
  Una voce per riga: label breve in colonna A, contenuto disteso in colonna B (es.
  `Volumi MAC` | `1.500 ticket/anno confermati da risposta cliente del 18/05`).
- **`2. COSA È APERTO`**: include tutte le voci GIALLE del Sheet 8 con prefisso
  `DA ASSUMERE — …` (sono ancora da valorizzare in Fase 3 dal cost modeler), tutte le
  voci ROSSE con prefisso `BLOCCANTE — …` (ancora non sciolte), e le voci del Sheet 9
  con `Stato ≠ Risposta ricevuta` e `Bloccante = SI`.
- **`3. DECISION POINT CRITICI`**: parametri ROSSI del Sheet 8 ancora aperti +
  trade-off emersi dalle risposte cliente che richiedono una decisione del cost modeler
  (es. assunzione operativa vs benchmark, scelta di scenario commerciale).

**Regola di coerenza** (NON NEGOZIABILE): ogni voce con prefisso `BLOCCANTE — …` nella
sezione 2 di Sheet 10 deve corrispondere 1:1 a una riga della sezione ROSSO di Sheet 8.
Ogni voce `DA ASSUMERE — …` deve corrispondere a una o più voci GIALLO di Sheet 8 della
stessa categoria.

**Output di questo step**: l'`rfp_handoff.xlsx` viene modificato in-place — solo Sheet 10
cambia, tutti gli altri sheet restano invariati. Nessun nuovo file prodotto.

**Idempotenza**: la skill `gara-effort-cost-estimator` allo Step 9a esegue comunque il
proprio Step E (pre-step Sheet 10) come safety net — se Step 8bis è stato eseguito
correttamente, lo Step E della cost-estimator produrrà lo stesso output (no-op). Il
doppio passaggio non è duplicazione: rende lo Step 8bis un punto di controllo esplicito
del workflow e visibile all'utente prima del lancio della stima.

Al termine, presenta in chat all'utente un breve sommario dell'aggiornamento:

```markdown
## ✅ Sheet 10 aggiornato — pronto per Fase 3 stima

- Voci CONFERMATE: N (di cui K nuove da risposte cliente)
- Voci APERTE: M (BLOCCANTI: A, DA ASSUMERE: B)
- DECISION POINT CRITICI: D

Procedo ora con la stima (cost-estimator + eventuale bid-estimator).
```

Senza fermarsi, prosegui automaticamente a Step 9a.

### Step 9a — Invoca `gara-effort-cost-estimator` (sempre)

Input: `rfp_handoff.xlsx` con Sheet 8/9 aggiornati dalla Fase 2 manuale.
Output: `[gara]_CostModel_v1.xlsx` + Sheet 10 dell'handoff riscritto in-place.

**Comportamento bloccante**: la skill si ferma allo Step C per chiedere approvazione
del registro scelte di stima (certo / assunzione operativa / benchmark con fonte /
bloccante). Trasmetti il registro all'utente, **FERMATI**, attendi la conferma.
Solo dopo, la skill produrrà il Cost Model e potrai procedere.

### Step 9b — Invoca `gara-bid-estimator` (CONDIZIONALE)

**Skip se** `tipo_gara ∈ {AM, greenfield_prodotti}`.
**Esegui se** `tipo_gara ∈ {SI_brownfield, greenfield_custom}`.

Input: `requisiti_estratti.json` (+ `rfp_analysis.json` come contesto opzionale).
Output: `Stima_SolutionDesign_*.xlsx`.

Se la skill bid-estimator presenta domande bloccanti residue, gestiscile come allo
Step 3 (trasmetti, fermati, attendi risposta, riprendi).

### Step 10 — Riepilogo finale

Presenta in chat all'utente la chiusura del workflow:

```markdown
## ✅ Workflow gara completato

### Tipo gara
**<tipo_gara>** (confermato dall'utente)

### Deliverable prodotti

| File | Skill | Contenuto |
|---|---|---|
| `rfp_analysis.json` | gara-rfp-analyzer | Analisi strategica gara |
| `requisiti_estratti.json` | gara-req-extractor | N requisiti scope (schema v2.0) |
| `rfp_handoff.xlsx` | gara-rfp-handoff + Fase 2 manuale | Workbook di handoff (12 sheet, Sheet 9 aggiornato, Sheet 10 riscritto in Fase 3) |
| `executive_summary.pptx` | gara-rfp-deck | Deck executive 10 slide |
| `[gara]_CostModel_v1.xlsx` | gara-effort-cost-estimator | Cost Model commerciale completo |
| `Stima_SolutionDesign_*.xlsx` (solo se SI_brownfield o greenfield_custom) | gara-bid-estimator | Stima effort per requisito |

### Next step suggerito
- Revisione commerciale del Cost Model con il bid manager
- Stesura della proposta tecnica finale partendo dal deck + stima soluzione (se prodotta)
- Verifica margine target con la direzione delivery
```

## Regole assolute

- **Una skill alla volta**: invocare `gara-*` skill sempre singolarmente, mai in parallelo
  nello stesso turno conversazionale.
- **Mai saltare gli stop**: la skill rispetta tutti i punti di pausa delle skill chiamate
  (extractor bloccanti, handoff Step B, cost-estimator Step C) e i propri (Fase 2 manuale,
  conferma classificazione).
- **Mai forzare la classificazione**: il fallback "indeterminato" è un esito legittimo —
  in quel caso si chiede all'utente, non si tira a indovinare.
- **Mai modificare i file**: l'orchestratore non scrive nessun file direttamente. Tutti
  gli output sono prodotti dalle skill chiamate. Singola eccezione: lo Step 10 può
  stampare solo testo in chat.
- **Idempotenza degli step**: se `rfp_analysis.json` esiste già e l'utente non chiede
  esplicitamente di ri-eseguirlo, NON ri-invocare `gara-rfp-analyzer`. Idem per ogni
  output successivo. Riusa quello che c'è.
- **Output in italiano** salvo richiesta esplicita diversa.

## Casistiche di skip

NON avviare il workflow completo (reindirizza alla skill specifica e termina):

| Richiesta utente | Skill da invocare al posto |
|---|---|
| "Estrai i requisiti / fai l'analisi requisiti" | `gara-req-extractor` |
| "Fai l'analisi strategica della gara / valore / criteri" | `gara-rfp-analyzer` |
| "Compila l'handoff / capability / domande chiarimento" | `gara-rfp-handoff` |
| "Genera il deck executive / le slide" | `gara-rfp-deck` |
| "Fai il cost model / la stima economica" | `gara-effort-cost-estimator` |
| "Fai la stima di solution design / effort per requisito" | `gara-bid-estimator` |

Solo se l'utente parla di "workflow completo", "pacchetto bid", "guidami nella risposta",
"risposta alla gara end-to-end", attiva questa skill orchestratrice.
