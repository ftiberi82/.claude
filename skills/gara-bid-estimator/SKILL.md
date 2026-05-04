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
- Template Excel da compilare: usa sempre `assets/Stima_SolutionDesign_Template.xlsx` come base, a meno che l'utente non fornisca esplicitamente un template diverso

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
- Foglio `Requirements & Solution Mapping`: righe intestazione 1-3, righe dati REQ-001→REQ-016 dalla riga 4 alla riga 19, riga vuota 20, riga TOTALE alla riga 21
- Foglio `Summary`: contiene dati di progetto, riepilogo economico e formula `Build` che punta a `='Requirements & Solution Mapping'!J21` — non alterarla
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

Il template è già caricato in memoria (vedi sezione precedente). Carica ora `requisiti_estratti.json`. Verifica che:
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
- **Colonna A** — ID gerarchico dal JSON (`REQ-001`, `REQ-001.1`, ecc.)
- **Colonna B** — Area funzionale: usa il label esatto del template
- **Colonna C** — `testo_bando` dal JSON
- **Colonna D** — `soluzione_proposta` dal JSON (non riscrivere, copia fedelmente)
- **Colonna E** — Componente tecnica
- **Colonna F** — Complessità (`Alta`, `Media`, `Bassa`); per i padri: `—`
- **Colonne G/H/I** — GG/U per FE, BE, Data inseriti come **valori interi** (questi sono gli input stimati); per i padri: `0`
- **Colonna J** — Totale GG/U: la formula `=IFERROR(SUM(G{n}:I{n}),0)` è già presente nel template per ogni riga. **Non sovrascriverla mai** — scrivi solo i valori interi nelle colonne G, H, I e lascia che la colonna J si calcoli da sola. Per i padri: inserisci `0` nelle colonne G, H, I.
- **Colonna K** — `priorita` dal JSON tradotto: `must_have → Must Have`, `should_have → Should Have`, `nice_to_have → Nice to Have`
- **Colonna L** — Note: includi `inferenza` e `note_inferenza` dal JSON; per i padri: `Macro-requisito — GG/U stimati nei sub-requisiti figli`

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

Compila i metadati di progetto nel foglio Summary (Nome Gara, Cliente, Data Elaborazione, ecc.) usando i valori dal campo `meta` del JSON.

Il tipo_documento nel campo `meta` del JSON è il segnale primario: `bando_gara` → default 20% (nessuna modifica); `documento_funzionale` → valuta se scendere al 15%.

## Regole operative

- **Fedeltà al JSON**: non alterare struttura, classificazione o numero di requisiti ricevuti.
- **Non ridecomporre**: se il JSON ha un requisito `singolo` per un'area, non aggiungere figli. La decomposizione era compito dell'estrazione.
- **Ogni `da_chiarire` → placeholder + nota leggibile** nel foglio Excel.
- **Ogni `stimato` → assunzione in A&R**.
- Ogni requisito `Alta` deve avere una motivazione nelle note.
- Nessuna cella obbligatoria vuota nell'Excel finale.

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
python scripts/recalc.py output.xlsx
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
