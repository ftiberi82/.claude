---
name: gara-req-extractor
description: >
  Legge un documento di gara o funzionale e produce un elenco strutturato di requisiti in formato JSON.
  TRIGGER quando: il documento è un capitolato, bando, CSA, RFP, disciplinare tecnico, analisi funzionale, SRS, specifiche funzionali, backlog di prodotto;
  l'utente chiede di estrarre requisiti, analizzare il bando, classificare i requisiti per area funzionale;
  il file caricato ha estensione `.ppt` o `.pptx` (presentazione PowerPoint).
  OUTPUT: tabella Markdown riepilogativa per validazione umana, poi file JSON `requisiti_estratti.json` scritto solo dopo conferma utente.
  SKIP se il documento è un contratto esecutivo, verbale, fattura, collaudo o documento privo di requisiti stimabili.
  SEQUENZA: questa skill va eseguita PRIMA di gara-bid-estimator. Non stimare GG/U — fermarsi al JSON.
---

# Gara Req Extractor

Legge un documento di gara o funzionale e produce un elenco strutturato e validabile di micro-requisiti in formato JSON.
**Non stimare GG/U in questa fase.** L'output è un artefatto intermedio da revisionare prima della stima.

## Input richiesti

- Documento di gara o funzionale in `pdf`, `docx`, `xlsx`, `csv`, `ppt` o `pptx`
- File `rfp_analysis.json` prodotto da `gara-rfp-analyzer` (opzionale ma raccomandato)

Se `rfp_analysis.json` è disponibile, leggilo prima di qualsiasi altra cosa: fornisce il contesto
strategico (tipo progetto, stack as-is, scope applicativo) che guida la classificazione e la
decomposizione dei requisiti. In particolare:
- `summary_tecnico.tipo_progetto` determina se applicare la verifica brownfield (Step 1b)
- `summary_tecnico.stack_tecnologico_richiesto` pre-popola il contesto tecnico dell'estrazione
- `open_points_qa` dal file RFP non va ripetuto nelle `domande_bloccanti` del JSON — sono domande distinte

Se il documento non è leggibile o non contiene requisiti stimabili, fermati e comunica il problema all'utente.

### Lettura documento — strategia adattiva

**Prima di leggere qualsiasi file**, verifica se la skill `document-skills@anthropic-agent-skills` è disponibile nell'ambiente. Questa skill fornisce un'API unificata di estrazione testo per tutti i formati supportati e va preferita ai metodi alternativi quando presente.

**Come verificare la disponibilità:**

`document-skills@anthropic-agent-skills` è un **plugin di Agent Skills per Claude Code**. Quando installato e abilitato, Claude Code inietta automaticamente i metadata delle skill (`pdf`, `docx`, `pptx`, `xlsx`) nel system prompt all'avvio — Claude le vede già nel proprio contesto senza dover cercare file su disco.

**Come verificare la disponibilità:**

Controlla il tuo contesto corrente: se il plugin è attivo, troverai già descrizioni di skill con nomi come `pdf`, `docx`, `pptx`, `xlsx` iniettate da Claude Code. Non eseguire script di ricerca su filesystem — il meccanismo di discovery è gestito interamente da Claude Code.

**Flusso di decisione:**

```
Nel contesto corrente sono presenti metadata di skill documento
(pdf / docx / pptx / xlsx) iniettati da Claude Code?
├── SÌ → usa la skill corrispondente al formato del file:
│         leggi il suo SKILL.md con view o bash, segui le istruzioni
│         per estrarre il testo, poi prosegui dallo Step 0
└── NO → usa i metodi alternativi per formato descritti nelle sezioni seguenti
```

> **Nota**: se stai operando in claude.ai anziché Claude Code, i metadata del plugin non saranno mai presenti nel contesto — passa direttamente ai metodi alternativi.

---

### Lettura file PowerPoint (`.ppt`, `.pptx`) — metodo alternativo

Se `document-skills` non è disponibile, usa sempre `extract-text` come prima mossa — è il metodo più veloce e completo:

```bash
extract-text documento.pptx
```

L'output è un testo strutturato con una sezione `## Slide N` per ogni diapositiva, inclusi titoli, bullet, note del relatore e testi nelle forme. Tratta questo output esattamente come il testo di un PDF o DOCX e prosegui dal **Step 0** normalmente.

**Se `extract-text` non è disponibile nell'ambiente**, fallback con `python-pptx`:

```bash
python -c "import pptx" 2>/dev/null || pip install python-pptx --quiet --break-system-packages
```

```python
#!/usr/bin/env python3
"""Estrae testo da ogni slide di un file PPTX."""
from pptx import Presentation
import sys

path = sys.argv[1]
prs = Presentation(path)

for i, slide in enumerate(prs.slides, 1):
    print(f"\n## Slide {i}")
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                testo = para.text.strip()
                if testo:
                    print(testo)
    # Note del relatore
    if slide.has_notes_slide:
        note = slide.notes_slide.notes_text_frame.text.strip()
        if note:
            print(f"[NOTE RELATORE]: {note}")
```

```bash
python estrai_pptx.py documento.pptx
```

**Contenuti non testuali nelle slide** (diagrammi, flowchart, immagini): se una slide contiene forme senza testo leggibile, esportala come immagine ad alta risoluzione e analizzala visivamente:

```bash
# Converti le slide in immagini per analisi visiva
python scripts/office/soffice.py --headless --convert-to pdf documento.pptx
pdftoppm -jpeg -r 200 -f N -l N documento.pdf slide_N
# Dove -f N -l N è il numero della slide da esportare (es. -f 3 -l 3 per slide 3)
```

Analizza visivamente le immagini risultanti: inferisci i requisiti dai pattern visivi (forme, frecce, swimlane, box colorati) marcando ogni inferenza con `[stimato]`.

## Formato di output

Produce un file `requisiti_estratti.json` con questa struttura:

```json
{
  "meta": {
    "documento": "nome del file",
    "tipo_documento": "bando_gara | documento_funzionale",
    "nome_progetto": "...",
    "cliente": "...",
    "data_estrazione": "YYYY-MM-DD",
    "versione_schema": "1.0"
  },
  "requisiti": [
    {
      "id": "REQ-001",
      "tipo": "padre | figlio | singolo",
      "padre_id": null,
      "area_funzionale": "...",
      "testo_bando": "citazione o parafrasi fedele del bando",
      "soluzione_proposta": "dimensioni Colonna D: Schermate, API, Dati, Processi",
      "inferenza": "esplicito | stimato | da_chiarire",
      "note_inferenza": "motivazione se stimato o da_chiarire",
      "priorita": "must_have | should_have | nice_to_have"
    }
  ],
  "domande_bloccanti": [
    {
      "id": "Q-001",
      "area": "area funzionale coinvolta",
      "testo_bando": "estratto che genera ambiguità",
      "domanda": "testo della domanda",
      "opzioni": ["(a) ...", "(b) ..."],
      "impatto_stima": "descrizione dell'impatto sui GG/U"
    }
  ],
  "aree_trasversali_aggiunte": ["Sicurezza e Compliance", "Infrastruttura e DevOps"]
}
```

### Regole sul campo `inferenza`

| Valore | Quando usarlo |
|---|---|
| `esplicito` | Il bando nomina esplicitamente il componente |
| `stimato` | Componente inferibile secondo le regole chiuse di `decomposizione_requisiti.md` |
| `da_chiarire` | Nessuna inferenza possibile; bloccante per la stima |

## Workflow

### Step 0 — Scansione struttura e filtro sezioni non stimabili

**Eseguito prima di qualsiasi altra lettura.** Scansiona l'indice o la struttura del documento per identificare le sezioni presenti, poi classifica ciascuna sezione in una delle due categorie seguenti. Leggi il contenuto completo **solo** delle sezioni marcate come STIMABILE.

**Sezioni da SKIPPARE sistematicamente** (non contengono requisiti funzionali o tecnici stimabili):

| Categoria | Segnali nel titolo o nel contenuto |
|---|---|
| Intestazioni e metadati | Copertina, indice/sommario, acronimi e definizioni, lista abbreviazioni |
| Riferimenti normativi di cornice | Sezioni che elencano solo leggi e decreti senza descrivere funzionalità (es. "Documentazione a riferimento", "Normativa applicabile") |
| Contesto as-is | Descrizione della situazione attuale della SA, strumenti oggi in uso, organizzazione interna — senza requisiti to-be |
| Premessa e obiettivi generali | Sezioni introduttive che descrivono il contesto del progetto senza specificare funzionalità (es. "Premessa", "Obiettivo del documento") |
| Requisiti fornitore | Certificazioni richieste, composizione team, CV e seniority figure professionali, requisiti organizzativi, sostenibilità (tipicamente Allegato C o equivalente) |
| Tempi, risorse e milestone contrattuali | Cronoprogramma esecutivo, distribuzione FTE per fase, modalità di pagamento, penali, milestone con date (tipicamente Allegato D o equivalente) |
| Clausole contrattuali | Modalità di fornitura ed esecuzione, garanzie, riservatezza, proprietà intellettuale |
| Supporto e manutenzione generica | Sezioni che descrivono solo SLA di assistenza post-go-live senza funzionalità aggiuntive da stimare |

**Sezioni STIMABILI** (da leggere integralmente):

- Descrizione generale della piattaforma / soluzione to-be
- Architettura generale del sistema
- Requisiti funzionali (e relativi allegati)
- Requisiti non funzionali / tecnico-operativi (e relativi allegati)
- Fasi di realizzazione **solo** per estrarre attività che generano deliverable funzionali non coperti dai requisiti (es. migrazione dati, formazione, testing con UAT)
- Allegati con elenchi di requisiti obbligatori funzionali o tecnici

**Regola di dubbio**: se una sezione ha un titolo ambiguo, leggi solo le prime 3-5 righe. Se contiene funzionalità, API, dati o processi da realizzare → STIMABILE. Se contiene solo obblighi contrattuali, normativa citata o descrizione organizzativa → SKIP.

Annota in una lista interna le sezioni skippate, da includere nel riepilogo Step 7 come nota informativa per l'utente.

### Step 1 — Leggi il documento e annota il contesto

Identifica il tipo di documento e annota nel campo `meta`:
- **Bando di gara** (capitolato, CSA, RFP, bando): nome gara, cliente/stazione appaltante, scadenza offerta, tipologia appalto.
- **Documento funzionale** (analisi, SRS, specifiche, backlog): nome progetto, versione, cliente, fase progettuale, ambito del documento.

Il tipo di documento non cambia il workflow, ma determina il livello di dettaglio atteso:
- Bando → alta ambiguità strutturale: inferisci liberamente seguendo le regole chiuse, documenta ogni inferenza.
- Documento funzionale → usa i dati già presenti (schermate nominate, endpoint API, entità): non marcare `[stimato]` ciò che è già esplicitato.

### Step 1b — Brownfield: estrai e verifica stack as-is (solo se applicabile)

**Eseguire solo se** `rfp_analysis.json` indica `tipo_progetto: brownfield | evolutiva | migrazione`,
oppure se il documento descrive esplicitamente un sistema esistente con versioni tecnologiche citate.
In tutti gli altri casi (nuovo sviluppo), salta direttamente allo Step 2.

Se `rfp_analysis.json` è disponibile e contiene già `stack_asis` compilato da `gara-rfp-analyzer`,
**non ripetere la verifica**: leggi il campo e riportane la sintesi nel campo `meta.stack_asis_sintesi`
del JSON di output.

Se invece la verifica non è stata fatta in precedenza:
1. Estrai dal documento tutte le versioni tecnologiche citate per il sistema as-is (linguaggi, framework, database, OS, middleware).
2. Per ciascuna versione, verifica stato EOL/LTS usando `references/eol_lts.md` (se coperta) o web search `"{tecnologia} {versione} end of life support date"` (se non coperta).
3. Popola il campo `meta.stack_asis` del JSON con la struttura:

```json
"stack_asis": [
  {
    "nome": "Java",
    "versione": "8",
    "stato": "LTS",
    "fine_supporto": "2026-11",
    "fonte": "reference",
    "rischio": "medio",
    "nota": "LTS su OpenJDK Temurin, EOL su Oracle commercial"
  }
]
```

4. Aggiungi `meta.stack_asis_sintesi` con un giudizio complessivo in max 2 righe.
5. Se sono presenti componenti in EOL, aggiungi una voce in `domande_bloccanti` con categoria `tecnica`
   e impatto `alto`: es. "Java 8 risulta EOL — è previsto un upgrade contestuale al nuovo sviluppo o
   la manutenzione prosegue sulla versione attuale?".

### Step 2 — Applica il decision tree per ogni blocco funzionale

Per ogni blocco funzionale del documento, prima di creare righe, applica il **decision tree** di `references/decomposizione_requisiti.md`:

```
1. Il bando elenca esplicitamente elementi distinti?
   → SÌ: una riga per elemento (tipo: figlio o singolo)
   → NO: vai a 2

2. L'area ha una regola quantitativa di fallback?
   → SÌ: applica il fallback, marca [stimato]
   → NO: vai a 3

3. È una capability unitaria non divisibile?
   → SÌ: 1 riga singola (tipo: singolo)
   → NO: 1 riga padre con inferenza=da_chiarire, aggiungi domanda bloccante
```

**Regola critica**: la struttura padre-figlio si crea **solo** se il decision tree al punto 1 produce ≥ 2 elementi esplicitamente distinti, oppure se il fallback al punto 2 produce ≥ 2 unità. Non creare padri per inferenze incerte.

### Step 3 — Classifica in area funzionale

Per ogni requisito, assegna l'area usando `references/aree_funzionali.md`.
Se un requisito copre due aree, assegna quella con effort dominante e annota l'area secondaria in `note_inferenza`.

### Step 4 — Valorizza la soluzione proposta (Colonna D)

Compila `soluzione_proposta` seguendo le **dimensioni obbligatorie** per l'area (da `decomposizione_requisiti.md`):
- `Schermate:` — obbligatorio per Portale, Mobile App
- `API:` — obbligatorio per Portale, Integrazione, API Management, Autenticazione
- `Dati:` — obbligatorio per Migrazione Dati, AI/ML
- `Processi:` — obbligatorio per Documentale, Integrazione, Notifiche, DevOps, PMO

Per ogni valore inferito (non esplicitato nel bando), aggiungi il suffisso `[stimato]`.
Per ogni valore non determinabile, scrivi `[DA CHIARIRE]` e aggiungi una voce in `domande_bloccanti`.

### Step 5 — Gestisci le ambiguità

Per ogni requisito non riconducibile a una regola chiusa o a un fallback:

1. Il valore è inferibile dal contesto con ragionamento solido? → `inferenza: stimato` + nota.
2. L'ambiguità ha impatto significativo sulla stima (>20% variazione GG/U attesa) o blocca la decomposizione? → `inferenza: da_chiarire` + aggiungi voce in `domande_bloccanti`.
3. L'ambiguità riguarda un dettaglio di basso impatto? → `inferenza: da_chiarire` + nota, non bloccare.

**Formato domande bloccanti**: le domande devono essere specifiche (citare il testo del bando), binarie o a scelta multipla quando possibile, con indicazione dell'impatto stimativo per ciascuna opzione.

**Limite domande**: se sono già presenti ≥ 3 voci in `domande_bloccanti`, preferisci assunzioni documentate per i casi successivi per non bloccare il workflow.

### Step 6 — Aggiungi le aree trasversali obbligatorie

Prima di chiudere il JSON, verifica che siano presenti righe per le aree trasversali. Se mancano, aggiungile con `tipo: singolo` e `inferenza: stimato`:

| Area | Condizione di aggiunta | Complessità default |
|---|---|---|
| Sicurezza e Compliance | Sempre | Bassa |
| Infrastruttura e DevOps | Sempre (progetto nuovo) | Media |
| Accessibilità | Se il documento è PA o cita UI/portale | Bassa |
| PMO e Governance | Sempre | Bassa |

**Regola struttura trasversali**: le aree trasversali aggiunte automaticamente hanno sempre `tipo: singolo` (nessun padre-figlio) a meno che il bando non citi esplicitamente ≥ 2 capability distinte per quell'area.

Popola il campo `aree_trasversali_aggiunte` con le aree inserite automaticamente.

### Step 7 — Presenta la tabella riepilogativa e attendi validazione

**Non scrivere ancora il file JSON.** La scrittura del JSON è onerosa e viene posticipata a dopo la validazione umana, per evitare di riscriverlo se emergono correzioni o risposte alle domande bloccanti.

Presenta all'utente un **riepilogo in tabella Markdown** con:
- ID, area funzionale, descrizione sintetica, tipo (padre/figlio/singolo), inferenza
- Conteggio totale e per tipo di inferenza
- Elenco numerato delle domande bloccanti (se presenti), ciascuna con le opzioni e l'impatto stimativo
- Elenco delle sezioni skippate allo Step 0, con motivazione sintetica per ciascuna (es. "contesto as-is", "requisiti fornitore", "milestone contrattuali"). Formato:

  > **Sezioni skippate (N% del documento):**
  > - [titolo sezione] → [motivazione skip in max 8 parole]
  > - ...
  > Se una sezione è stata skippata per errore, segnalalo nella risposta di conferma:
  > la rileggo e integro i requisiti mancanti prima di scrivere il JSON.

Usa questo formato:

> **Riepilogo estratto: N requisiti (X espliciti, Y stimati, Z da chiarire)**
>
> [tabella Markdown]
>
> **Domande bloccanti prima di procedere:**
> Q-001: [testo domanda + opzioni + impatto]
> Q-002: ...
>
> Puoi modificare l'elenco, aggiungere o rimuovere requisiti, e rispondere alle domande.
> Quando sei pronto, scrivi **"conferma"** (con eventuali correzioni e risposte alle domande)
> e genererò il file `requisiti_estratti.json`.

Attendi la risposta dell'utente. Non procedere oltre.

### Step 8 — Incorpora le risposte e scrivi il JSON

Eseguito **solo dopo che l'utente ha confermato** (con o senza correzioni).

1. Incorpora nel modello in memoria tutte le correzioni indicate dall'utente (aggiunte, rimozioni, modifiche a singoli requisiti).
2. Per ogni domanda bloccante a cui l'utente ha risposto: aggiorna `inferenza` da `da_chiarire` a `stimato` o `esplicito`, aggiorna `note_inferenza` con la risposta ricevuta, rimuovi la voce corrispondente da `domande_bloccanti`.
3. Verifica che le aree trasversali siano presenti (Step 6).
4. Scrivi il file `requisiti_estratti.json` con la struttura completa e aggiornata.
5. Comunica all'utente che il file è pronto e può essere passato a `gara-bid-estimator-v3`.

**Non procedere alla stima.** Il file JSON è l'unico output di questa skill.

### Step 8b — Genera il file open_points.xlsx

Eseguito subito dopo la scrittura del JSON, senza attendere ulteriore conferma.

Prendi tutte le voci presenti in `domande_bloccanti` del JSON appena scritto e producile come
file Excel `open_points.xlsx` — da condividere con il cliente per raccogliere le risposte.

Prima di scrivere il file, leggi `/mnt/skills/public/xlsx/SKILL.md` per seguire le istruzioni
di ambiente. Poi genera il file con openpyxl con questa struttura:

**Foglio: "Open Points"**

| Colonna | Header | Contenuto |
|---|---|---|
| A | ID | `Q-001`, `Q-002`, ... |
| B | Area | `area` della domanda bloccante |
| C | Riferimento bando | `testo_bando` della domanda bloccante |
| D | Domanda | `domanda` della domanda bloccante |
| E | Opzioni | `opzioni` join con newline |
| F | Impatto stima | `impatto_stima` |
| G | Risposta cliente | vuota — da compilare dal cliente |
| H | Stato | `Aperto` (default) |

Formattazione:
- Riga 1: intestazioni in bold, sfondo grigio chiaro (`D9D9D9`), testo nero, altezza 20px
- Colonne A-B: larghezza 12
- Colonna C-D: larghezza 45, wrap text attivo
- Colonna E-F: larghezza 35, wrap text attivo
- Colonna G: larghezza 40, sfondo giallo chiaro (`FFFDE7`) — evidenzia che va compilata
- Colonna H: larghezza 12
- Righe dati: altezza minima 40px, bordi sottili su tutte le celle
- Freeze della riga 1 (intestazioni sempre visibili)

Dopo aver scritto `open_points.xlsx`, comunica all'utente:
- `requisiti_estratti.json` → da passare a `gara-bid-estimator-v3` per la stima
- `open_points.xlsx` → da inviare al cliente per raccogliere le risposte alle domande bloccanti

## Tracciabilità — regole obbligatorie

Per ogni requisito estratto devi documentare fonte e certezza, sia nel JSON che nelle colonne M e N del foglio `Requirements & Solution Mapping`.

**Nel JSON**, aggiungi a ogni requisito i campi:
```json
{
  "id": "REQ-001",
  "certezza": "estratto | inferito | assunto",
  "fonte_pag": "pag. 12, Sez. 3.2 — Requisiti di accesso",
  "fonte_estratto": "Il sistema deve supportare autenticazione SSO con provider SAML 2.0"
}
```

**Criteri di certezza:**
- `estratto` — il requisito è presente verbatim o quasi nel documento; cita pagina e sezione, riporta max 20 parole del testo originale in `fonte_estratto`
- `inferito` — il requisito non è esplicito ma è ricavabile dal contesto (es. un requisito di logging dedotto da un requisito di audit); spiega il ragionamento in `note_inferenza`
- `assunto` — il requisito è assente nel documento ma necessario per completezza tecnica; va marcato come domanda bloccante

**Nell'Excel** (colonne M e N del foglio Requirements):
- Colonna M `Fonte / Pag.`: inserisci pagina, sezione e max 15 parole del testo originale
- Colonna N `Certezza`: inserisci `🟢` per estratto, `🟡` per inferito, `🔴` per assunto

**Audit Trail** — aggiungi una riga nel foglio `Audit Trail` per ogni:
- Requisito padre creato per aggregazione (campo `decomposizione`)
- Requisito con certezza `inferito` o `assunto`
- Scelta di area funzionale non ovvia

Per ogni riga dell'Audit Trail: ID progressivo (`AT-REQ-NNN`), foglio = `Requirements`, campo = ID requisito, decisione presa, fonte nel bando, ragionamento, alternativa scartata se presente.

## Regole operative

- **Decomponi prima di classificare**: applica sempre il decision tree prima di assegnare l'area funzionale.
- **Non stimare GG/U**: nessun valore numerico di effort nel JSON. Solo struttura e classificazione.
- **Non scrivere il JSON prima della conferma**: il file `requisiti_estratti.json` viene scritto solo allo Step 8, dopo che l'utente ha confermato la tabella e risposto alle domande bloccanti. La tabella Markdown è l'output intermedio.
- **Ogni `da_chiarire` deve avere una voce in `domande_bloccanti`** o almeno una nota in `note_inferenza`.
- **Ogni `stimato` deve avere una `note_inferenza`** che spiega il ragionamento.
- **Non creare padri speculativi**: il padre esiste solo se i figli sono determinati con certezza (espliciti o da fallback).
- **Documenta le aree trasversali aggiunte** nel campo `aree_trasversali_aggiunte`.
- Un requisito = un solo owner di area funzionale primaria.

## Riferimenti da leggere solo quando servono

- Per applicare il decision tree e le regole chiuse di inferenza: `references/decomposizione_requisiti.md`
- Per classificare un requisito in area funzionale: `references/aree_funzionali.md`
- Per esempi pratici di mapping e decomposizione: `references/esempi_mapping.md`
- Per verificare stato EOL/LTS di versioni tecnologiche (Step 1b): `references/eol_lts.md`
- Per generare il file Excel open_points (Step 8b): `/mnt/skills/public/xlsx/SKILL.md`
