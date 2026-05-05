---
name: gara-bid-estimator-v3
description: >
  Legge il file `requisiti_estratti.json` prodotto da `gara-req-extractor` e compila il template Excel ufficiale con la stima di solution design.
  TRIGGER quando: l'utente fornisce un file `requisiti_estratti.json` già validato e chiede di produrre la stima, compilare il template Excel, generare l'offerta tecnica.
  PREREQUISITO OBBLIGATORIO: il file `requisiti_estratti.json` deve essere stato prodotto e validato tramite la skill `gara-req-extractor`. Non accettare come input il documento di gara originale — rimanda l'utente alla skill di estrazione.
  SKIP se non è disponibile un file JSON validato: in quel caso, indica all'utente di eseguire prima `gara-req-extractor`.
---

# Gara Bid Estimator v3

Legge il file `requisiti_estratti.json` e compila il template Excel ufficiale con la stima completa di solution design.

## Input richiesti

- File `requisiti_estratti.json` prodotto da `gara-req-extractor` (obbligatorio)
- File `rfp_analysis.json` prodotto da `gara-rfp-analyzer` (opzionale ma raccomandato)
- Template Excel da compilare: usa sempre `assets/Stima_SolutionDesign_Template.xlsx` come base, a meno che l'utente non fornisca esplicitamente un template diverso

Se `rfp_analysis.json` è disponibile, leggilo subito dopo aver caricato il template: fornisce
il valore economico della gara (usato per il confronto finale), i metadati di progetto (nome,
cliente, scadenza) e il contesto architetturale che può influenzare le stime.

Se ricevi un documento di gara invece del JSON, **non procedere**: rimanda l'utente a eseguire prima `gara-req-extractor` su quel documento.

## Caricamento del template — operazione obbligatoria prima di qualsiasi altra cosa

**Prima di leggere il JSON e prima di scrivere qualsiasi cella**, carica il template con openpyxl:

```python
from openpyxl import load_workbook
wb = load_workbook('assets/Stima_SolutionDesign_Template.xlsx')
ws_req = wb['Requirements & Solution Mapping']
ws_sum = wb['Summary']
ws_ar  = wb['Assumptions & Risks']
```

**Struttura del template da rispettare:**
- Foglio `RFP Analysis`: dati strategici estratti da `rfp_analysis.json` — compilare le 5 sezioni (valore economico, criteri aggiudicazione, formato risposta, summary tecnico, stack as-is EOL)
- Foglio `QA Open Points`: domande aperte al cliente estratte da `rfp_analysis.open_points_qa` e `domande_bloccanti` del JSON requisiti — colonna "Risposta cliente" in giallo da compilare
- Foglio `Requirements & Solution Mapping`: righe intestazione 1-3, righe dati REQ-001→REQ-016 dalla riga 4 alla riga 19, riga vuota 20, riga TOTALE alla riga 21
- Foglio `Summary`: contiene dati di progetto (righe 5-12, incluse data sottomissione domande riga 11 e data consegna offerta riga 12), riepilogo economico e formula `Build` in `B18` che punta a `='Requirements & Solution Mapping'!J21` — non alterarla. Riga TOTALE in riga 26, Contingency in D27, Totale con contingency in D28, Revenue in D29
- Foglio `Assumptions & Risks`: sezione A (assunzioni) e sezione B (rischi) già strutturate — aggiungi righe in coda a ciascuna sezione

**Regola critica**: non ricreare mai il file da zero. Parti sempre dal template caricato, scrivi solo nelle celle dati e aggiungi righe dove necessario. Font, colori, bordi, formule di aggregazione esistenti devono essere preservati esattamente.

## Uso delle skill di formato

Questa skill governa classificazione, stima e compilazione del template. Le skill di formato Anthropic sono **obbligatorie** — non bypassarle mai.

**Prima di qualsiasi operazione su file**, leggi il file `SKILL.md` della skill corrispondente con il tool `view`:

| Operazione | Skill da leggere (obbligatoria) |
|---|---|
| Creare o modificare file `.xlsx` | `/mnt/skills/public/xlsx/SKILL.md` |
| Leggere un file `.xlsx` o `.xlsm` esistente | `/mnt/skills/public/xlsx/SKILL.md` |
| Creare o modificare file `.docx` (offerta tecnica, relazione) | `/mnt/skills/public/docx/SKILL.md` |
| Creare o modificare file `.pdf` | `/mnt/skills/public/pdf/SKILL.md` |
| Leggere un file `.pdf` allegato | `/mnt/skills/public/pdf-reading/SKILL.md` |
| Leggere un file allegato di tipo sconosciuto | `/mnt/skills/public/file-reading/SKILL.md` |

Segui tutte le istruzioni della skill letta. In caso di conflitto tra questa skill e una skill di formato Anthropic, prevale la skill di formato Anthropic per tutto ciò che riguarda la manipolazione del file; questa skill prevale per classificazione, stima e struttura dei contenuti.

## Workflow

### Step 1 — Leggi e valida il JSON

Il template è già caricato in memoria (vedi sezione precedente). Prima di leggere il JSON, esegui la validazione automatica:

```bash
python3 scripts/validate_json.py requisiti_estratti.json
```

Lo script verifica: campi obbligatori, aree funzionali valide, GG/U non negativi o anomali, duplicati, coerenza gerarchia padre-figlio, certezza e fonte compilate.

- Se `status: errors_found` — **non procedere**: correggi gli errori segnalati o chiedi chiarimenti all'utente
- Se `status: warnings_found` — procedi ma segnala i warning all'utente prima di chiudere il file
- Se `status: success` — procedi normalmente

Carica ora `requisiti_estratti.json`. Verifica che:
- Il campo `meta` sia completo (documento, tipo, cliente).
- Ogni requisito abbia `id`, `area_funzionale`, `soluzione_proposta`, `inferenza`, `priorita`.
- Le aree trasversali obbligatorie siano presenti (Sicurezza e Compliance, Infrastruttura e DevOps).

Se il file è malformato o incompleto, segnala il problema e chiedi all'utente di rieseguire `gara-req-extractor`.

**Regola di fedeltà**: non modificare la struttura dei requisiti ricevuti. Non aggiungere figli a requisiti già marcati come `singolo`. Non unire requisiti separati. Non rinominare aree funzionali. Se ritieni che un requisito sia mal classificato, segnalalo nelle note del foglio Excel senza alterare il JSON.

### Step 2 — Assegna la complessità

Per ogni requisito con `tipo: figlio` o `tipo: singolo`, assegna la complessità (`Alta`, `Media`, `Bassa`) usando `references/regole_stima.md` e i correttivi di `references/segnali_complessita.md`.

**Regola di posizionamento**:
- Parti sempre dal **centro del range** come default.
- Scendi al bordo basso solo se **tutti** i driver di riduzione sono presenti contemporaneamente.
- Sali al bordo alto se **anche uno solo** dei driver di crescita è presente.
- Per bandi di gara: default centro-alto in assenza di segnali espliciti di riduzione.

**Requisiti con `inferenza: da_chiarire`**: assegna il centro del range dell'area come placeholder. Segnala nelle note del foglio Excel con: `[PLACEHOLDER — da_chiarire: rivalutare dopo chiarimento]`.

**Requisiti con `inferenza: stimato`**: assegna la complessità normalmente. Annota nelle note: `[stimato: <nota_inferenza dal JSON>]`.

Per i requisiti `tipo: padre`: lascia la complessità vuota (`—`). I GG/U sono zero.

### Step 3 — Assegna i GG/U e lo split FE/BE/Data

Per ogni requisito `tipo: figlio` o `tipo: singolo`:

1. Identifica il range dell'area da `references/regole_stima.md`.
2. Posizionati nel range in base ai driver (Step 2).
3. Applica lo split FE/BE/Data tipico dell'area.
4. Arrotonda a interi. Il totale J = FE + BE + Data.

Per le aree con driver di scala (Portale, Integrazione, Analytics, Documentale, Migrazione, Mobile, API): considera la numerosità già presente in `soluzione_proposta` (schermate, API, entità). Non riderivare la numerosità — è già stata determinata dall'estrazione.

Per i requisiti con `tipo: padre`: GG/U = 0 su tutte le colonne.

### Step 4 — Verifica le aree trasversali

Prima di compilare il foglio Requirements, verifica che siano presenti righe per le aree trasversali con i floor minimi:

| Area | Floor minimo | Quando alzare |
|---|---|---|
| Sicurezza e Compliance | Bassa (4-5 GG/U) | Se GDPR, audit, VAPT, dati sensibili → Media o Alta |
| Infrastruttura e DevOps | Media (8-10 GG/U) | Sempre per progetti nuovi; Alta se K8s, multi-env, HA/DR |
| Accessibilità | Bassa (3-4 GG/U) | Se WCAG/AgID citati → Media; se retrofit → Alta |
| PMO e Governance | Bassa (3-4 GG/U) | Se SAL formali PA → Media; se più vendor → Alta |

Se una di queste aree è presente nel JSON come `tipo: singolo` con complessità assegnata, usa quella. Se manca, aggiungila con il floor minimo.

### Step 5 — Consulta gli esempi per i casi dubbi

Se hai dubbi sulla classificazione o sulla stima di un requisito specifico, consulta `references/esempi_mapping.md` e scegli l'area prevalente. Cita l'area secondaria nelle note del foglio.

### Step 6 — Compila il foglio Requirements & Solution Mapping

Segui rigorosamente la struttura del template Excel.

**Colonne e regole**:
- **Colonna A** — scrivi l'ID del requisito (`REQ-001`, `REQ-001.1`, ecc.)
- **Colonna B** — Area funzionale: usa il label esatto del template
- **Colonna C** — scrivi direttamente il testo del campo `testo_bando`. Non scrivere il nome del campo né riferimenti al JSON.
- **Colonna D** — scrivi direttamente il testo del campo `soluzione_proposta` del requisito. Non scrivere il nome del campo, non scrivere riferimenti al JSON, non scrivere formule. Esempio: se `soluzione_proposta` vale "Implementare form di login con validazione lato client e autenticazione OAuth2", scrivi esattamente quel testo nella cella.
- **Colonna E** — Componente tecnica
- **Colonna F** — Complessità (`Alta`, `Media`, `Bassa`); per i padri: `—`
- **Colonne G/H/I** — GG/U per FE, BE, Data inseriti come **valori interi** (questi sono gli input stimati); per i padri: `0`
- **Colonna J** — Totale GG/U: la formula `=IFERROR(SUM(G{n}:I{n}),0)` è già presente nel template per ogni riga. **Non sovrascriverla mai** — scrivi solo i valori interi nelle colonne G, H, I e lascia che la colonna J si calcoli da sola. Per i padri: inserisci `0` nelle colonne G, H, I.
- **Colonna K** — scrivi la priorità tradotta in italiano: `must_have → Must Have`, `should_have → Should Have`, `nice_to_have → Nice to Have`
- **Colonna L** — scrivi il testo dei campi `inferenza` e `note_inferenza` separati da spazio. Per i requisiti padre scrivi: `Macro-requisito — GG/U stimati nei sub-requisiti figli`. Non scrivere i nomi dei campi.

**Regola formule obbligatoria**: nel foglio Requirements, la riga 21 (TOTALE) contiene già le formule `=SUM(G4:G20)`, `=SUM(H4:H20)`, `=SUM(I4:I20)`, `=SUM(J4:J20)` — non sovrascriverle con valori calcolati in Python. Nel foglio Summary, tutte le celle di riepilogo economico (Design, Test, Deploy, PMO, Infrastruttura) sono già derivate da `B16` tramite percentuali fisse hardcoded nel template (`B15=B16*25%`, `B17=B16*25%`, `B18=B16*3%`, `B19=B16*10%`, `B20=B16*60%`) — non alterarle. Scrivi solo i valori interi nelle colonne G, H, I del foglio Requirements e i metadati di progetto nel foglio Summary.

**Formattazione righe padre**:
- Sfondo azzurro chiaro (`FFD6E4F0`), font bold
- Colonna D: `— [decomposizione in REQ-NNN.1 → REQ-NNN.N]`
- Colonne G/H/I/J: `0`

### Step 7 — Genera Assumptions & Risks

Per ogni requisito con `inferenza: stimato` nel JSON, crea una voce nel foglio Assumptions:
> `A-NNN: Si assume che [testo da note_inferenza] — da confermare con il cliente`

Per ogni voce in `domande_bloccanti` del JSON, crea una voce nel foglio Risks:
> `R-NNN: [domanda bloccante] — impatto: [impatto_stima]`

Mantieni gli ID nel formato `A-001`, `R-001`.

### Step 8 — Compila il foglio Summary

La cella `D25` (Contingency) nel template contiene la formula fissa `=D24*20%` — non modificarla. La percentuale di contingency nel template è fissa al 20% e non è parametrica.

Usa la tabella seguente per **documentare nella cella Note/commento della riga Contingency** se il caso richiederebbe una percentuale diversa, segnalando all'utente di aggiornare manualmente la formula se necessario:

| Scenario | Contingency consigliata | Azione |
|---|---|---|
| JSON da documento funzionale dettagliato, stack noto, nessuna integrazione legacy | **15%** | Segnala all'utente di cambiare `D25` in `=D24*15%` |
| JSON da bando con specifiche incomplete, almeno 1 integrazione o area ambigua | **20%** | Nessuna modifica necessaria |
| JSON con ≥ 2 segnali di complessità trasversali | **25%** | Segnala all'utente di cambiare `D25` in `=D24*25%` |
| JSON con ≥ 1 `da_chiarire` significativo o sistemi legacy non documentati | **30%** | Segnala all'utente di cambiare `D25` in `=D24*30%` |

Nota: `D26` (Totale con contingency) e `D27` (Revenue) sono già calcolate tramite formule nel template — non sovrascriverle.

Compila i metadati di progetto nel foglio Summary (Nome Gara, Cliente, Data Elaborazione, ecc.)
usando i valori dal campo `meta` del JSON — o da `rfp_analysis.json` se disponibile e più completo.

Il tipo_documento nel campo `meta` del JSON è il segnale primario: `bando_gara` → default 20%
(nessuna modifica); `documento_funzionale` → valuta se scendere al 15%.

### Compila il foglio RFP Analysis (solo se `rfp_analysis.json` disponibile)

Trasferisci i dati dal JSON al foglio — le celle in azzurro sono le destinazioni:

- Sezione 1 (Valore economico): `importo_base_asta`, `massimale`, `durata_contratto_mesi`, `opzioni_rinnovo`, `modalita_prezzi`
- Sezione 2 (Criteri aggiudicazione): per ogni criterio in `criteri_aggiudicazione.criteri` compila una riga con nome, punteggio, peso%, priorità, sotto-criteri. Inserisci `raccomandazione` nella cella gialla "Raccomandazione strategica"
- Sezione 3 (Formato risposta): compila ogni riga da `formato_risposta`
- Sezione 4 (Summary tecnico): compila da `summary_tecnico` — scope applicativo, tipo progetto, architettura, stack richiesto/preferito, integrazioni, utenti
- Sezione 5 (Stack as-is EOL): compila da `stack_asis.componenti` se `applicable: true`; inserisci `sintesi_rischio` nell'ultima riga rossa

### Compila il foglio QA Open Points

Aggiungi una riga per ogni voce in `rfp_analysis.open_points_qa` e una per ogni voce in `requisiti_estratti.domande_bloccanti`. Usa prefisso `QA-` per le prime, `Q-` per le seconde.

Per ogni riga: ID, categoria, riferimento bando, domanda, opzioni/scenari, impatto stima. Le colonne "Risposta cliente" (gialla) e "Stato" restano vuote — sono da compilare dal cliente.

### Verifica valore economico (solo se `rfp_analysis.json` disponibile)

Dopo aver compilato il Summary, esegui il confronto tra stima e valore di gara:

1. Leggi `rfp_analysis.valore_economico.importo_base_asta` (importo netto, IVA esclusa).
2. Leggi il valore calcolato in `D26` (Totale con contingency) dal foglio Summary.
3. Calcola la percentuale: `(D26 / importo_base_asta) * 100`.

Applica questa logica e segnala all'utente **prima di chiudere il file**:

| Scenario | Azione |
|---|---|
| D26 < 70% della base d'asta | ⚠️ Stima molto al di sotto della base — verifica che nessun requisito sia stato omesso o sottostimato |
| D26 tra 70% e 100% della base d'asta | ✅ Stima compatibile con la base d'asta |
| D26 tra 100% e 120% della base d'asta | ⚠️ Stima leggermente superiore alla base — valuta con il commerciale se rivedere scope o contingency |
| D26 > 120% della base d'asta | 🚨 Stima significativamente superiore alla base d'asta — non procedere senza revisione: il progetto non è fattibile al valore indicato |

Riporta il confronto in una nota nella cella adiacente alla riga `D26` del Summary, con formato:
`"Base d'asta: €[importo] — Stima: €[D26] ([percentuale]%)"`.

Se `rfp_analysis.json` non è disponibile, salta questa verifica e segnala all'utente che
per un confronto con la base d'asta è necessario eseguire prima `gara-rfp-analyzer`.

## Regole operative

- **Fedeltà al JSON**: non alterare struttura, classificazione o numero di requisiti ricevuti.
- **Non ridecomporre**: se il JSON ha un requisito `singolo` per un'area, non aggiungere figli. La decomposizione era compito dell'estrazione.
- **Ogni `da_chiarire` → placeholder + nota leggibile** nel foglio Excel.
- **Ogni `stimato` → assunzione in A&R**.
- Ogni requisito `Alta` deve avere una motivazione nelle note.
- Nessuna cella obbligatoria vuota nell'Excel finale.

## Tracciabilità — regole obbligatorie

Ogni cella non banale dell'Excel deve avere una fonte verificabile o un ragionamento esplicito. Questo è il meccanismo che permette all'utente di verificare la stima senza rileggere il bando.

**Colonna M `Fonte / Pag.`** (foglio Requirements):
Inserisci per ogni requisito la pagina e sezione del bando da cui proviene + max 15 parole del testo originale. Leggi il campo `fonte_pag` e `fonte_estratto` dal JSON.

**Colonna N `Certezza`** (foglio Requirements):
Copia dal campo `certezza` del JSON: `🟢` = estratto, `🟡` = inferito, `🔴` = assunto.

**Certezza per le stime GG/U** — ogni riga del foglio Requirements ha anche una valutazione di certezza della *stima*, distinta dalla certezza del requisito. Usa la colonna N anche per questo:
- `🟢` se la stima segue direttamente da `regole_stima.md` senza correttivi soggettivi
- `🟡` se hai applicato correttivi da `segnali_complessita.md` con ragionamento
- `🔴` se la stima è puramente ipotetica per mancanza di informazioni (il requisito ha `da_chiarire: true`)

**Foglio Audit Trail** — aggiungi una riga per ogni decisione non ovvia sulla stima:
- Scelta di complessità (Alta/Media/Bassa) con ragionamento
- Applicazione di un correttivo da `segnali_complessita.md`
- Scelta della percentuale di contingency
- Qualsiasi stima con `certezza: assunto`

Per ogni riga: ID (`AT-EST-NNN`), foglio = `Requirements` o `Summary`, campo = ID requisito o cella, decisione, fonte (riferimento a `regole_stima.md` o `segnali_complessita.md`), ragionamento, alternativa scartata.

## Compilazione Excel — istruzioni operative sul template reale

Il template ha 16 righe precompilate (REQ-001→REQ-016, righe 4-19), una riga vuota alla 20 e la riga TOTALE alla 21. Se i requisiti del JSON superano 16, **inserisci righe nuove prima della riga 20** replicando il formato delle righe esistenti; la riga TOTALE si sposta automaticamente — verifica sempre che la formula `Build` nel Summary punti ancora alla riga corretta.

```python
# Per ogni requisito oltre REQ-016, inserisci una riga prima del totale:
ws_req.insert_rows(last_data_row + 1)
# Replica formato dalla riga precedente impostando stili manualmente
```

Se i requisiti sono meno di 16, lascia vuote le righe in eccesso (il template le gestisce già con `=IFERROR(SUM(G{n}:I{n}),0)` che restituisce 0).

**Non aggiungere, eliminare o rinominare fogli, colonne o intestazioni già presenti.**

Scrivi solo nelle colonne G, H, I (valori interi). La colonna J si aggiorna automaticamente tramite le formule del template. Non riscrivere le formule della riga TOTALE (riga 21) né quelle del foglio Summary.

Dopo aver scritto tutte le celle, esegui la ricalcolazione obbligatoria:

```bash
python3 /mnt/skills/public/xlsx/scripts/recalc.py output.xlsx
```

Verifica che `status` sia `success` e che il totale `Build` nel Summary coincida con il totale GG/U dei requisiti.

## Stile e formattazione

Il file output deve replicare esattamente font, allineamento, bordi e colori del template.

## Controlli finali

- Nessuna cella obbligatoria vuota
- Nessuna formula rotta
- Nessuna alterazione strutturale del template originale
- Il totale `Build` nel Summary coincide con il totale GG/U dei requisiti
- Ogni assunzione ha origine nel JSON (da `note_inferenza` o `domande_bloccanti`)
- I requisiti `da_chiarire` sono visibili e marcati nel foglio Excel
- Linguaggio professionale, adatto a un documento di offerta

## Riferimenti da leggere solo quando servono

- Per assegnare GG/U e split FE/BE/Data: `references/regole_stima.md`
- Per applicare correttivi trasversali: `references/segnali_complessita.md`
- Per esempi pratici di mapping: `references/esempi_mapping.md`
- Per verificare la classificazione di un'area: `references/aree_funzionali.md`
- Per il confronto con il valore di gara: `rfp_analysis.json` (prodotto da `gara-rfp-analyzer`)
