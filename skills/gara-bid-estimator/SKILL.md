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
- Template Excel ufficiale da compilare (obbligatorio)

Se il template ufficiale non è disponibile, fermati e richiedilo.
Il template di riferimento incluso come asset è `assets/Stima_SolutionDesign_Template.xlsx`.

Se ricevi un documento di gara invece del JSON, **non procedere**: rimanda l'utente a eseguire prima `gara-req-extractor` su quel documento.

## Uso delle skill di formato

Questa skill governa classificazione, stima e compilazione del template. Le skill di formato sono helper.

- Se la skill `xlsx` è installata, usala come helper per creare e aggiornare il file `.xlsx` di output.

## Workflow

### Step 1 — Leggi e valida il JSON

Carica `requisiti_estratti.json`. Verifica che:
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
- **Colonne G/H/I** — GG/U per FE, BE, Data; per i padri: `0`
- **Colonna J** — Totale GG/U (G+H+I); per i padri: `0`
- **Colonna K** — `priorita` dal JSON tradotto: `must_have → Must Have`, `should_have → Should Have`, `nice_to_have → Nice to Have`
- **Colonna L** — Note: includi `inferenza` e `note_inferenza` dal JSON; per i padri: `Macro-requisito — GG/U stimati nei sub-requisiti figli`

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

Aggrega i GG/U e applica la regola di contingency:

| Scenario | Contingency |
|---|---|
| JSON da documento funzionale dettagliato, stack noto, nessuna integrazione legacy | **15%** |
| JSON da bando con specifiche incomplete, almeno 1 integrazione o area ambigua | **20%** |
| JSON con ≥ 2 segnali di complessità trasversali | **25%** |
| JSON con ≥ 1 `da_chiarire` significativo o sistemi legacy non documentati | **30%** |

Documenta nel foglio Summary la motivazione del percentuale scelto.

Il tipo_documento nel campo `meta` del JSON è il segnale primario: `bando_gara` → default 20%; `documento_funzionale` → default 15%, da alzare se presenti `da_chiarire`.

## Regole operative

- **Fedeltà al JSON**: non alterare struttura, classificazione o numero di requisiti ricevuti.
- **Non ridecomporre**: se il JSON ha un requisito `singolo` per un'area, non aggiungere figli. La decomposizione era compito dell'estrazione.
- **Ogni `da_chiarire` → placeholder + nota leggibile** nel foglio Excel.
- **Ogni `stimato` → assunzione in A&R**.
- Ogni requisito `Alta` deve avere una motivazione nelle note.
- Nessuna cella obbligatoria vuota nell'Excel finale.

## Compilazione Excel — struttura template

- Il template contiene esattamente 3 fogli: `Summary`, `Requirements & Solution Mapping`, `Assumptions & Risks`.
- Foglio `Requirements & Solution Mapping`: righe intestazione 1-3, righe dati da 4, riga totale 21.
- Non aggiungere, eliminare o rinominare fogli, colonne o formule già presenti.
- Estendi le righe dati replicando la struttura esistente senza ridisegnare il layout.
- Senza LibreOffice: sostituisci le formule con valori interi calcolati nella colonna J.
- La formula `Build` in Summary punta a `='Requirements & Solution Mapping'!J21`: preservala.

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
