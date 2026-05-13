---
name: gara-req-extractor
description: >
  Legge un documento di gara o funzionale e produce un elenco strutturato di requisiti in formato JSON.
  TRIGGER quando: il documento è un capitolato, bando, CSA, RFP, disciplinare tecnico, analisi funzionale, SRS, specifiche funzionali, backlog di prodotto;
  l'utente chiede di estrarre requisiti, analizzare il bando, classificare i requisiti per area funzionale;
  il file caricato ha estensione `.ppt` o `.pptx` (presentazione PowerPoint).
  OUTPUT: tabella Markdown riepilogativa + file JSON `requisiti_estratti.json` scritto immediatamente dopo.
  SKIP se il documento è un contratto esecutivo, verbale, fattura, collaudo o documento privo di requisiti stimabili.
  SEQUENZA: questa skill va eseguita PRIMA di gara-bid-estimator. Non stimare GG/U — fermarsi al JSON.
  INTERRUZIONI: questa skill può sospendersi al termine dell'estrazione per richiedere chiarimenti di scope bloccanti. In quel caso restituisce le domande all'utente e attende risposta prima di procedere. Questo è comportamento intenzionale, non un errore — non riprendere automaticamente.
---

# Gara Req Extractor

Legge un documento di gara o funzionale e produce un elenco strutturato e validabile di micro-requisiti in formato JSON.
**Non stimare GG/U in questa fase.** L'output è un artefatto intermedio da revisionare prima della stima.

## Input richiesti

- Documento di gara o funzionale in `pdf`, `docx`, `xlsx`, `csv`, `ppt` o `pptx`
- File `rfp_analysis.json` prodotto da `gara-rfp-analyzer` (opzionale ma raccomandato)

Se `rfp_analysis.json` è disponibile, leggilo prima di qualsiasi altra cosa: fornisce il contesto
strategico (tipo progetto, stack as-is, scope applicativo, requisiti non funzionali) che guida
la classificazione e la decomposizione dei requisiti. In particolare:
- `summary_tecnico.tipo_progetto` determina se applicare la verifica brownfield (Step 1b)
- `summary_tecnico.stack_tecnologico_richiesto` pre-popola il contesto tecnico dell'estrazione
- `requisiti_non_funzionali` (8 categorie) pre-popola le aree trasversali (Step 1c) evitando duplicazioni
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
    "versione_schema": "2.0"
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
      "rationale_requisito": "perché questo requisito è incluso / come è stato interpretato (1-2 frasi, sempre presente)",
      "rationale_soluzione": "perché la soluzione proposta dimensiona così (componenti, pattern, librerie, ragionamento — sempre presente)",
      "categoria_scope": "custom_software | cots_product | service_external | out_of_scope",
      "scope_dettaglio": {
        "nome_prodotto": "es. SAP S/4HANA, Azure AD, Dynatrace — solo se categoria_scope != custom_software",
        "fornitore": "es. SAP, Microsoft, Dynatrace — opzionale",
        "tipo_costo": "licenza | abbonamento | servizio_consulenza | infrastruttura_cloud | null",
        "motivazione": "perché è classificato così (es. 'citato come prodotto già in uso dal cliente')"
      },
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

### Regole sui nuovi campi (schema v2.0)

| Campo | Obbligatorio | Quando popolarlo |
|---|---|---|
| `rationale_requisito` | sempre | 1-2 frasi che spiegano perché il requisito è incluso e come è stato interpretato. Per `inferenza: esplicito` spiega interpretazione/perimetro. Per `stimato`/`da_chiarire` deve includere la logica di `note_inferenza` (i due campi convivono, non si sovrappongono: `note_inferenza` resta tecnica/operativa, `rationale_requisito` è di business). |
| `rationale_soluzione` | sempre | Spiega componenti, pattern architetturali, librerie scelte per dimensionare la `soluzione_proposta`. Es. "Form di login con OAuth2 PKCE + libreria react-oidc-context; back-end FastAPI con dipendenza su Keycloak già citato nel bando". |
| `categoria_scope` | sempre | Default `custom_software`. Segnali per gli altri valori sono in `references/aree_funzionali.md`. |
| `scope_dettaglio` | solo se `categoria_scope != custom_software`; `null` altrimenti | Identifica prodotto/servizio out-of-scope custom. |

### Regole sul campo `categoria_scope`

| Valore | Quando usarlo | Segnali nel bando |
|---|---|---|
| `custom_software` | Default — il requisito richiede sviluppo custom da stimare in GG/U | Bando descrive funzionalità da realizzare ex-novo o personalizzazione significativa |
| `cots_product` | Prodotto commerciale citato per uso/configurazione (no sviluppo custom oltre configurazione) | "utilizzo di SAP S/4HANA", "Microsoft 365", "Power BI", "Tableau", "ServiceNow" — senza richiesta di custom development |
| `service_external` | API/servizio gestito da terzi con cui il custom interagisce ma non costruisce | "integrazione con SPID", "PagoPA", "Google Maps API", "ANPR", "AgID Identity Provider" |
| `out_of_scope` | Citato nel bando ma esplicitamente fuori responsabilità del fornitore | "fornito dal cliente", "a carico di altro fornitore", "infrastruttura già esistente non in scope" |

I requisiti con `categoria_scope != custom_software` vanno comunque estratti (servono a `gara-bid-estimator` per popolare lo sheet "Prodotti & Servizi Esterni") ma non saranno stimati in GG/U.

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

### Step 1c — Pre-popola aree trasversali da `rfp_analysis.requisiti_non_funzionali`

**Eseguire solo se** `rfp_analysis.json` è disponibile e contiene `requisiti_non_funzionali` con
almeno una categoria non vuota. Altrimenti salta direttamente allo Step 2 — le aree trasversali
verranno aggiunte allo Step 6 con il floor minimo.

**Mapping categoria NFR → area funzionale di destinazione:**

| Categoria NFR (Analyzer) | Area funzionale (Extractor) |
|---|---|
| `prestazioni` | Infrastruttura e DevOps (carico/throughput → sizing) |
| `sla` | Infrastruttura e DevOps |
| `disponibilita` | Infrastruttura e DevOps (HA/DR) |
| `scalabilita` | Infrastruttura e DevOps |
| `sicurezza` | Sicurezza e Compliance |
| `compliance` | Sicurezza e Compliance |
| `accessibilita` | Accessibilità |
| `manutenibilita` | PMO e Governance (logging/monitoring strutturato, doc) |

**Procedura:**

1. Per ogni item NFR in ogni categoria di `rfp_analysis.requisiti_non_funzionali`, crea un requisito
   con:
   - `area_funzionale` dal mapping sopra
   - `tipo: singolo`
   - `testo_bando` = `descrizione` + eventuale `valore_target` tra parentesi
   - `soluzione_proposta` dimensionata sulla base dell'NFR (es. per "uptime 99,9%" → "HA con 2 nodi
     + load balancer; monitoring Prometheus")
   - `inferenza: esplicito` (l'NFR è già estratto dal documento via Analyzer)
   - `rationale_requisito` = "Pre-popolato da rfp_analysis.json — categoria NFR: {categoria}, impatto: {impatto_stima}"
   - `rationale_soluzione` = componenti tecnici che soddisfano il valore_target
   - `categoria_scope: custom_software` (default per NFR; eccezione: alcuni `service_external` come
     SPID/PagoPA che restano `service_external`)
   - `priorita: must_have`
   - `certezza: estratto` se l'NFR ha `certezza: estratto` nell'Analyzer
   - `fonte_pag`, `fonte_estratto` ereditati dall'Analyzer
2. Annota nel campo `aree_trasversali_aggiunte` da quale fonte provengono (es.
   `"Sicurezza e Compliance (pre-popolata da rfp_analysis NFR)"`).
3. **Deduplicazione**: se nello Step 2 successivo il documento descrive funzionalmente lo stesso NFR
   già pre-popolato, **non duplicare** — aggiorna il rationale del requisito esistente menzionando
   la doppia fonte.

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

### Step 4b — Compila i rationale e classifica `categoria_scope` (nuovi campi schema v2.0)

Per **ogni** requisito (incluse aree trasversali) compila i 4 nuovi campi:

1. **`rationale_requisito`** (sempre, 1-2 frasi) — perché il requisito è incluso e come è stato
   interpretato. Esempi:
   - Esplicito: `"Sezione 3.2 cita autenticazione SSO SAML — incluso così come scritto, perimetro: solo IdP primario, no federazione cross-org."`
   - Stimato: `"Inferito dalla descrizione del workflow di approvazione: richiede notifiche email perché menziona 'notifiche di stato' senza specificare canale."`
   - Da chiarire: `"Il bando cita una 'integrazione con il gestionale' senza specificare quale — interpretato come SAP S/4 vista la sezione 1.4, ma serve conferma."`
2. **`rationale_soluzione`** (sempre, 1-3 frasi tecniche) — componenti, pattern, librerie scelte
   per dimensionare `soluzione_proposta`. Esempi:
   - `"Form di login React + OAuth2 PKCE flow + libreria react-oidc-context; backend FastAPI con dipendenza su Keycloak già citato nel bando."`
   - `"Microservizio Spring Boot esposto via API Gateway interno; payload validato con JSON Schema; persistenza PostgreSQL su schema dedicato."`
3. **`categoria_scope`** — assegna secondo la tabella nella sezione "Regole sul campo
   `categoria_scope`". Default = `custom_software`. Consulta `references/aree_funzionali.md` per i
   segnali specifici dell'area.
4. **`scope_dettaglio`** — solo se `categoria_scope != custom_software`:
   - `nome_prodotto`: nome esatto citato nel bando
   - `fornitore`: opzionale, solo se noto
   - `tipo_costo`: `licenza` (one-shot), `abbonamento` (ricorrente), `servizio_consulenza` (giorni
     consulenza esterna), `infrastruttura_cloud` (IaaS/PaaS), `null` se non determinabile
   - `motivazione`: 1 frase con il segnale che ha portato alla classificazione (es. "Bando cita 'utilizzo di Microsoft 365 già in possesso della SA' — no sviluppo custom richiesto")

**Regola di coerenza**: se `categoria_scope != custom_software`, il `rationale_soluzione` deve
spiegare quale parte è di configurazione/integrazione (eventualmente stimabile) e quale è prodotto
commerciale (non stimabile). `gara-bid-estimator` userà questa distinzione per separare GG/U custom
da costi di terzi nello sheet "Prodotti & Servizi Esterni".

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

### Step 7 — Presenta la tabella riepilogativa

Presenta all'utente un **riepilogo in tabella Markdown** con:
- ID, area funzionale, descrizione sintetica, tipo (padre/figlio/singolo), inferenza
- Conteggio totale e per tipo di inferenza
- Elenco delle sezioni skippate allo Step 0, con motivazione sintetica per ciascuna. Formato:

  > **Sezioni skippate (N% del documento):**
  > - [titolo sezione] → [motivazione skip in max 8 parole]

Usa questo formato per la tabella:

> **Riepilogo estratto: N requisiti (X espliciti, Y stimati, Z da chiarire)**
>
> [tabella Markdown]

### Step 7b — Verifica domande bloccanti e decidi

Dopo la tabella, verifica se esistono domande che soddisfano i criteri bloccanti definiti nelle Regole operative.

**Caso A — Nessuna domanda bloccante**: procedi immediatamente allo Step 8, scrivi il JSON senza interruzioni.

**Caso B — Ci sono domande bloccanti**: presenta SOLO le domande in questo formato e **FERMATI**:

> ⚠️ **Prima di procedere ho bisogno di [N] chiarimenti di scope:**
>
> **Q-001 — [area]** *(motivo: [fuori scope / integrazione ambigua / informazione strutturale mancante])*
> [testo domanda con riferimento alla sezione del bando]
> Opzioni: A) ... | B) ... | C) Non so — farò un'assunzione conservativa
>
> **Q-002 — [area]** *(motivo: ...)*
> [testo domanda]
> Opzioni: A) ... | B) ...
>
> Rispondi con numero e opzione (es. "Q-001: B, Q-002: A").

**STOP — input utente richiesto prima di procedere.**
Questa skill non può continuare senza le risposte alle domande sopra.
Non eseguire step successivi. Non chiamare altre skill. Non generare file.
Restituisci il controllo all'utente e attendi la sua risposta.
Riprendere dallo Step 8 solo dopo aver ricevuto le risposte.

### Step 8 — Incorpora le risposte e scrivi il JSON

Eseguito solo dopo che l'utente ha risposto alle domande bloccanti (se presenti), oppure immediatamente se non ce ne sono.

1. Per ogni domanda a cui l'utente ha risposto: aggiorna `inferenza` da `da_chiarire` a `stimato` o `esplicito`, aggiorna `note_inferenza` con la risposta ricevuta, rimuovi la voce da `domande_bloccanti`.
2. Per ogni "Non so": mantieni `da_chiarire`, fai l'assunzione più conservativa, documentala in `note_inferenza`.
3. Verifica che le aree trasversali siano presenti (Step 6).
4. Scrivi il file `requisiti_estratti.json` con la struttura completa e aggiornata.
5. Comunica all'utente che il file è pronto e può essere passato a `gara-bid-estimator`.

**Non procedere alla stima.** Il file JSON è l'unico output di questa skill.

### Step 8b — Comunica output

Dopo aver scritto `requisiti_estratti.json`, comunica all'utente:
- `requisiti_estratti.json` → da passare a `gara-bid-estimator` per la stima
- Le domande bloccanti (se presenti) verranno inserite nel foglio `QA Open Points` del template Excel dal bid-estimator, insieme alle domande strategiche dell'rfp_analysis.json. Non generare un file open_points.xlsx separato.

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
- Colonna N `Certezza`: inserisci `E` per estratto (sfondo verde), `I` per inferito (sfondo giallo), `A` per assunto (sfondo rosso)

**Audit Trail** — aggiungi una riga nel foglio `Audit Trail` per ogni:
- Requisito padre creato per aggregazione (campo `decomposizione`)
- Requisito con certezza `inferito` o `assunto`
- Scelta di area funzionale non ovvia

Per ogni riga dell'Audit Trail: ID progressivo (`AT-REQ-NNN`), foglio = `Requirements`, campo = ID requisito, decisione presa, fonte nel bando, ragionamento, alternativa scartata se presente.

## Regole operative

**Principio — human in the loop solo per domande bloccanti**: il flusso procede in autonomia senza interruzioni tra gli step. L'unica interruzione consentita è al termine dell'estrazione, se esistono domande bloccanti che soddisfano i criteri sotto.

**Criteri per una domanda bloccante valida** (almeno una condizione deve essere vera):
- Un requisito è potenzialmente fuori scope ma il documento è contraddittorio — senza chiarimento non è possibile decidere se estrarlo o escluderlo
- Manca un'informazione strutturale che cambia radicalmente il numero o il tipo di requisiti da estrarre: es. "il sistema deve gestire 10 utenti o 10 milioni?" determina se esistono requisiti di scalabilità/performance; "l'integrazione X è da realizzare o è già esistente e da riusare?" determina se va estratto un requisito di integrazione
- Un'integrazione o un modulo è citato nel documento ma non è chiaro se è in scope oppure è un sistema esterno già disponibile

**Vietato in ogni circostanza:**
- Chiedere preferenze su approccio progettuale (Agile/Waterfall, durata, team)
- Proporre scenari alternativi di scope
- Fare domande sulla stima (i GG/U non esistono ancora in questa fase)
- Interrompere tra uno step e l'altro
- Presentare "prossimi passi" chiedendo se continuare


- **Decomponi prima di classificare**: applica sempre il decision tree prima di assegnare l'area funzionale.
- **Non stimare GG/U**: nessun valore numerico di effort nel JSON. Solo struttura e classificazione.
- **Scrivi il JSON subito dopo la tabella riepilogativa** se non ci sono domande bloccanti. Se ci sono domande bloccanti, il JSON viene scritto solo dopo aver ricevuto le risposte dall'utente.
- **Ogni `da_chiarire` deve avere una voce in `domande_bloccanti`** o almeno una nota in `note_inferenza`.
- **Ogni `stimato` deve avere una `note_inferenza`** che spiega il ragionamento.
- **`rationale_requisito` e `rationale_soluzione` sono sempre obbligatori** (schema v2.0) — anche per requisiti `esplicito` con `categoria_scope: custom_software`. Niente stringa vuota o `null`.
- **`categoria_scope` è sempre obbligatorio** (default `custom_software`). Se diverso da `custom_software`, anche `scope_dettaglio` deve essere compilato (no `null`).
- **`versione_schema` deve essere `"2.0"`** in nuovi JSON. Vecchi JSON v1.0 restano leggibili a valle ma non sfruttano i nuovi campi nel template Excel.
- **Non creare padri speculativi**: il padre esiste solo se i figli sono determinati con certezza (espliciti o da fallback).
- **Documenta le aree trasversali aggiunte** nel campo `aree_trasversali_aggiunte`.
- Un requisito = un solo owner di area funzionale primaria.

## Riferimenti da leggere solo quando servono

- Per applicare il decision tree e le regole chiuse di inferenza: `references/decomposizione_requisiti.md`
- Per classificare un requisito in area funzionale: `references/aree_funzionali.md`
- Per esempi pratici di mapping e decomposizione: `references/esempi_mapping.md`
- Per verificare stato EOL/LTS di versioni tecnologiche (Step 1b): `references/eol_lts.md`

