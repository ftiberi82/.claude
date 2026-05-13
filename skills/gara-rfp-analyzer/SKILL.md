---
name: gara-rfp-analyzer
description: >
  Legge un documento di gara (RFP, capitolato, bando, CSA, disciplinare) e produce un'analisi strategica
  preliminare in formato JSON prima dell'estrazione dei requisiti.
  TRIGGER quando: l'utente carica un documento di gara e chiede un'analisi strategica, vuole capire
  come rispondere, vuole conoscere il valore della gara, i criteri di aggiudicazione o il formato di risposta atteso.
  OUTPUT: file `rfp_analysis.json` con analisi economica, criteri di aggiudicazione, formato risposta,
  summary scope/stack/architettura, open point QA per il cliente, verifica EOL/LTS stack as-is.
  SEQUENZA: questa skill va eseguita PRIMA di gara-req-extractor e gara-bid-estimator.
  NON USARE se l'utente vuole il pacchetto operativo per il team che dovrà stimare — cioè un
  PowerPoint di Executive Summary + un Excel multi-sheet con capability, driver di stima,
  matrice profili x capability, gap analysis, registro chiarimenti e nota di handoff verso il
  cost modeling: in quel caso usa `gara-rfp-handoff`. Questa skill (`gara-rfp-analyzer`) si
  attiva quando l'utente vuole un JSON strategico per costruire la RISPOSTA all'offerta
  (valore economico, criteri di aggiudicazione, formato risposta atteso, EOL/LTS dello stack
  as-is, open point QA per il cliente).
  SKIP se il documento è un contratto esecutivo, verbale, fattura, collaudo o documento privo di sezioni
  economiche o di valutazione dell'offerta.
---

# Gara RFP Analyzer

Analizza strategicamente un documento di gara prima dell'estrazione dei requisiti. Produce un'analisi
completa che orienta la costruzione dell'offerta: valore economico, criteri di aggiudicazione,
formato risposta atteso, summary tecnico-applicativo, domande aperte per il cliente e verifica EOL/LTS
dello stack as-is in caso di brownfield.

**Non estrarre requisiti in questa fase.** L'output è `rfp_analysis.json`, artefatto di contesto
da passare in input a `gara-req-extractor` e `gara-bid-estimator`.

## Input richiesti

- Documento di gara in `pdf`, `docx`, `xlsx`, `ppt` o `pptx`

Se il documento non contiene sezioni economiche né criteri di valutazione, comunicalo all'utente
e procedi ugualmente con le sezioni disponibili.

## Lettura documento

Segui la stessa strategia adattiva di `gara-req-extractor`: usa `document-skills` se disponibile
in Claude Code, altrimenti usa `extract-text` come prima mossa, poi `python-pptx` come fallback
per i `.pptx`.

Leggi **tutto il documento**, incluse le sezioni normalmente skippate da `gara-req-extractor`
(contesto as-is, allegati economici, disciplinare di gara, criteri di valutazione): questa skill
ha bisogno di quelle sezioni.

## Formato di output

Produce `rfp_analysis.json` con questa struttura:

```json
{
  "meta": {
    "documento": "nome del file",
    "tipo_documento": "bando_gara | rfp | capitolato | csa | disciplinare",
    "nome_progetto": "...",
    "cliente": "...",
    "stazione_appaltante": "...",
    "scadenza_offerta": "YYYY-MM-DD o null",
    "data_analisi": "YYYY-MM-DD",
    "versione_schema": "1.0"
  },
  "valore_economico": { ... },
  "criteri_aggiudicazione": { ... },
  "formato_risposta": { ... },
  "summary_tecnico": { ... },
  "stack_asis": { ... },
  "requisiti_non_funzionali": { ... },
  "open_points_qa": [ ... ]
}
```

Struttura dettagliata di ogni sezione:

### `valore_economico`

```json
{
  "importo_base_asta": 000000,
  "valuta": "EUR",
  "iva_inclusa": true,
  "importo_netto": 000000,
  "massimale": 000000,
  "ribasso_minimo_pct": null,
  "ribasso_massimo_pct": null,
  "durata_contratto_mesi": 24,
  "opzioni_rinnovo": "descrizione o null",
  "note": "estratto testuale che ha generato questi valori"
}
```

Se l'importo non è reperibile, imposta `importo_base_asta: null` e spiega in `note`.

### `criteri_aggiudicazione`

```json
{
  "metodo": "OEPV | massimo_ribasso | altro",
  "punteggio_totale": 100,
  "criteri": [
    {
      "nome": "Offerta tecnica",
      "punteggio_max": 70,
      "peso_pct": 70,
      "sotto_criteri": [
        {
          "nome": "Qualità della soluzione proposta",
          "punteggio_max": 30,
          "note": "valutazione discrezionale commissione"
        }
      ],
      "priorita": "alta | media | bassa"
    }
  ],
  "criterio_prioritario": "nome del criterio con punteggio maggiore",
  "raccomandazione": "indicazione strategica su dove concentrare l'effort di risposta"
}
```

`priorita` è `alta` se il criterio vale ≥ 40% del punteggio totale, `media` tra 20-39%, `bassa` < 20%.

### `formato_risposta`

```json
{
  "componenti_richieste": {
    "offerta_tecnica": true,
    "offerta_economica": true,
    "stima_giorni_uomo": true,
    "piano_di_progetto": false,
    "cv_team": false,
    "referenze": false,
    "certificazioni": false
  },
  "modalita_prezzi": "fixed_scope | time_and_material | tariffa_giornaliera | misto | non_specificato",
  "struttura_offerta_tecnica": "descrizione della struttura attesa (capitoli, allegati, max pagine se indicato)",
  "formato_file_richiesto": "pdf | word | entrambi | non_specificato",
  "limite_pagine": null,
  "lingua": "italiano",
  "note": "altri vincoli formali rilevanti"
}
```

### `summary_tecnico`

```json
{
  "scope_applicativo": "sintesi in max 5 righe dello scope funzionale high-level",
  "tipo_progetto": "nuovo_sviluppo | brownfield | evolutiva | migrazione | misto",
  "stack_tecnologico_richiesto": [
    { "componente": "linguaggio/framework/piattaforma", "versione": "se specificata", "obbligatorio": true }
  ],
  "stack_tecnologico_preferito": [
    { "componente": "...", "versione": "...", "note": "indicato come preferito o suggerito" }
  ],
  "architettura_applicativa": "monolitica | microservizi | serverless | ibrida | non_specificata",
  "architettura_note": "dettagli architetturali rilevanti (es. on-premise, cloud, SaaS, multi-tenant)",
  "integrazioni_principali": ["sistema A", "sistema B"],
  "utenti_target": "descrizione utenti finali e numerosità se indicata",
  "note": "altri elementi tecnici rilevanti non classificabili sopra"
}
```

### `stack_asis`

Compilare **solo** se `tipo_progetto` è `brownfield`, `evolutiva` o `migrazione`.
Se il documento non descrive un sistema as-is con versioni tecnologiche, impostare `applicable: false`.

```json
{
  "applicable": true,
  "componenti": [
    {
      "nome": "Java",
      "versione": "8",
      "stato": "EOL | LTS | active | unknown",
      "fine_supporto": "2030-12 o null",
      "fonte": "reference | web_search",
      "rischio": "alto | medio | basso",
      "nota": "Java 8 in EOL dal 2022 per uso commerciale Oracle — LTS su OpenJDK Adoptium fino al 2026"
    }
  ],
  "sintesi_rischio": "sintesi complessiva del rischio tecnologico dello stack as-is"
}
```

Per compilare `stato`, `fine_supporto` e `rischio`:
1. Cerca prima in `references/eol_lts.md` — se la versione è coperta, usa quella fonte (`"fonte": "reference"`).
2. Se non coperta, esegui una web search `"{tecnologia} {versione} end of life support date"` e usa il risultato (`"fonte": "web_search"`).
3. Se nessuna fonte è conclusiva, imposta `"stato": "unknown"` e `"fonte": "non_trovata"`.

Criteri di rischio:
- `alto`: versione in EOL senza patch di sicurezza attive
- `medio`: versione in LTS ma con fine supporto entro 18 mesi
- `basso`: versione in active support o LTS con orizzonte > 18 mesi

### `requisiti_non_funzionali`

Vista strategica anticipata sui requisiti non funzionali (NFR) — utile per pricing, go/no-go e per pre-popolare le aree trasversali di `gara-req-extractor`.

Otto categorie standard, ognuna è una lista di item (può essere vuota se non emergono requisiti pertinenti):

```json
{
  "prestazioni":    [ /* tempi risposta, throughput, TPS, latenza */ ],
  "sla":            [ /* uptime %, RTO/RPO, severity & response time, penali */ ],
  "sicurezza":      [ /* autenticazione, autorizzazione, cifratura, audit log, pentest, VAPT */ ],
  "compliance":     [ /* GDPR, AgID, CAD, NIS2, ISO 27001, accessibilità AgID, normative settoriali */ ],
  "accessibilita":  [ /* WCAG 2.1 AA, linee guida AgID, target utenti con disabilità */ ],
  "scalabilita":    [ /* utenti concorrenti, volumi dati, picchi, crescita attesa */ ],
  "disponibilita":  [ /* HA, DR, multi-region, business continuity */ ],
  "manutenibilita": [ /* logging, monitoring, documentazione, code quality, manutenzione evolutiva */ ]
}
```

Schema di ogni singolo item:

```json
{
  "categoria": "prestazioni | sla | sicurezza | compliance | accessibilita | scalabilita | disponibilita | manutenibilita",
  "descrizione": "es. tempo di risposta < 2s per il 95% delle richieste sotto carico nominale",
  "valore_target": "es. '<2s p95' | '99,9%' | 'WCAG 2.1 AA' | null se non quantificato",
  "fonte_pag": "pag. X, Sez. Y",
  "fonte_estratto": "max 20 parole testo originale",
  "certezza": "estratto | inferito | assunto",
  "impatto_stima": "alto | medio | basso"
}
```

**`impatto_stima`** è un hint per `gara-req-extractor` e `gara-bid-estimator`:
- `alto`: NFR che richiede componenti/architettura dedicati (es. HA multi-region, SLA <2s p95 con volumi alti, pentest formale) → tipicamente alza la complessità delle aree trasversali a Media/Alta
- `medio`: NFR standard ma non banale (es. WCAG AA, GDPR base, monitoring) → manda a Media le aree trasversali
- `basso`: NFR di compliance standard senza vincoli particolari (es. logging applicativo, backup giornaliero) → resta al floor minimo

**Regola di compilazione:** una categoria può restare lista vuota (`[]`) se il documento non cita requisiti pertinenti. Non riempire con item generici di default. Se il documento è solo commerciale (no specs tecniche), tutte le categorie possono restare vuote — la sezione è comunque presente nello schema.

### `open_points_qa`

Domande strategiche da fare al cliente **prima** di costruire l'offerta — distinte dalle domande
tecniche di `gara-req-extractor` che riguardano i requisiti funzionali.
Queste riguardano l'ambito dell'offerta, le condizioni economiche e le aspettative della SA.

```json
[
  {
    "id": "QA-001",
    "categoria": "economica | tecnica | contrattuale | procedurale",
    "testo": "domanda specifica con riferimento alla sezione del documento",
    "motivazione": "perché questa informazione è rilevante per costruire l'offerta",
    "impatto": "alto | medio | basso",
    "scadenza_suggerita": "prima della presentazione dell'offerta | entro N giorni"
  }
]
```

Includi **solo** domande ad alto e medio impatto. Limite massimo: 10 domande. Ordina per impatto decrescente.

## Workflow

### Step 1 — Leggi il documento integralmente

Leggi tutto il documento senza saltare sezioni. Annota mentalmente:
- Sezioni economiche (importi, massimali, basi d'asta, opzioni di rinnovo)
- Sezioni di valutazione offerta (criteri, punteggi, sotto-criteri)
- Sezioni di requisiti formali della risposta (struttura offerta, formati, limiti)
- Sezioni tecniche (stack richiesto, architettura, integrazioni, contesto as-is)
- Sezioni normative che vincolano la risposta (codice appalti, CAD, GDPR)

### Step 2 — Compila `valore_economico`

Cerca: importo a base d'asta, massimale, durata, opzioni di proroga o rinnovo.
Attenzione: nei bandi pubblici italiani l'importo può essere espresso al netto IVA — verifica sempre.
Se sono presenti lotti distinti, crea un campo `lotti` con la lista. Analizza tutti i lotti e produci l'analisi sul lotto con importo maggiore come default; documenta questa scelta nell'`_audit_trail`.

### Step 3 — Compila `criteri_aggiudicazione`

Estrai metodo di aggiudicazione e criteri con relativi punteggi.
Se il metodo è OEPV (offerta economicamente più vantaggiosa): estrai tutti i criteri e sotto-criteri,
calcola `peso_pct` come percentuale sul totale 100, assegna `priorita`.
Identifica il `criterio_prioritario` (quello con punteggio max) e scrivi la `raccomandazione` strategica:
es. "Il criterio con punteggio maggiore è 'Qualità soluzione tecnica' (40 pt) — concentrare l'effort
sulla descrizione architetturale e sui casi d'uso implementativi."

### Step 4 — Compila `formato_risposta`

Identifica cosa va prodotto e come. Cerca: elenchi di elaborati richiesti, allegati obbligatori,
struttura dell'offerta tecnica, limiti di pagine, formati accettati, modalità di presentazione prezzi.
Determina `modalita_prezzi`:
- `fixed_scope`: il prezzo è unico e comprensivo (tipico bandi PA)
- `time_and_material`: si fattura a consuntivo su tariffe concordate
- `tariffa_giornaliera`: si offre una tariffa/GG e i GG stimati separatamente
- `misto`: parte fixed, parte a consumo

### Step 5 — Compila `summary_tecnico`

Sintetizza in linguaggio executive lo scope applicativo in max 5 righe.
Estrai stack tecnologico richiesto (obbligatorio) vs preferito (indicativo).
Determina il tipo di architettura applicativa dal contesto (anche se non nominata esplicitamente).
Elenca le principali integrazioni citate (sistemi esistenti, API esterne, middleware).

### Step 6 — Compila `stack_asis` (solo brownfield)

Se `tipo_progetto` è brownfield, evolutiva o migrazione: estrai le versioni tecnologiche dello stack
as-is citate nel documento. Per ciascuna, verifica stato EOL/LTS come descritto nel campo.
Produci `sintesi_rischio` con un giudizio complessivo (es. "Stack ad alto rischio: Java 8 EOL
e Angular 11 EOL richiedono upgrade obbligatorio prima o contestualmente al nuovo sviluppo.").

### Step 7 — Compila `requisiti_non_funzionali`

Estrai dal documento i requisiti non funzionali e classificali nelle 8 categorie standard.
Fonti tipiche: sezione "Requisiti tecnico-operativi", "Requisiti non funzionali", "Livelli di
servizio", "Sicurezza", allegato SLA, allegato accessibilità.

Per ogni NFR identificato:

1. Determina la categoria (`prestazioni`, `sla`, `sicurezza`, `compliance`, `accessibilita`,
   `scalabilita`, `disponibilita`, `manutenibilita`). Se un NFR ricade in più categorie, scegli
   quella prevalente e cita la secondaria in `descrizione`.
2. Estrai `valore_target` quantitativo se presente (es. "99,9%", "<2s p95", "WCAG 2.1 AA"). Se il
   bando cita solo principio ("buona performance") senza numero, lascia `null`.
3. Compila `fonte_pag`, `fonte_estratto`, `certezza` come per le altre sezioni.
4. Assegna `impatto_stima` secondo la regola della sezione schema:
   - `alto` → richiede componenti/architettura dedicati (HA multi-region, SLA stringenti con volumi
     alti, pentest formale, certificazioni ISO/SOC)
   - `medio` → NFR standard ma non banale (WCAG AA, GDPR base, monitoring strutturato)
   - `basso` → compliance standard senza vincoli particolari

**Mapping di default categoria → segnali nel bando** (per orientare l'estrazione):

| Categoria | Segnali tipici |
|---|---|
| `prestazioni` | "tempo di risposta", "throughput", "TPS", "carico nominale", "latenza" |
| `sla` | "uptime %", "RTO", "RPO", "severity", "tempo di risposta a ticket", "penali" |
| `sicurezza` | "OWASP", "VAPT", "pentest", "cifratura", "MFA", "audit log", "RBAC" |
| `compliance` | "GDPR", "AgID", "CAD", "NIS2", "ISO 27001", "DPIA", normative settoriali |
| `accessibilita` | "WCAG", "accessibilità", "AgID accessibilità", "screen reader" |
| `scalabilita` | "utenti concorrenti", "milioni di transazioni", "picchi", "scalabilità orizzontale" |
| `disponibilita` | "HA", "alta affidabilità", "DR", "disaster recovery", "business continuity", "multi-region" |
| `manutenibilita` | "logging", "monitoring", "documentazione", "manutenzione evolutiva", "code quality" |

**Regola di completezza**: tutte e 8 le categorie devono apparire nel JSON (anche come lista vuota
`[]`). Non omettere chiavi anche se non emergono requisiti — la struttura uniforme è necessaria a
valle per `gara-req-extractor`.

**Documentazione downstream**: questa sezione è input opzionale ma raccomandato per `gara-req-extractor`.
Lo Step di lettura NFR in `gara-req-extractor` userà `requisiti_non_funzionali` per pre-popolare le
aree trasversali (Sicurezza e Compliance, Infrastruttura e DevOps, Accessibilità, PMO e Governance)
evitando duplicazioni.

### Step 8 — Compila `open_points_qa`

Identifica le lacune informative che impattano la costruzione dell'offerta — non i requisiti funzionali
(quelli li gestirà `gara-req-extractor`), ma le condizioni quadro:
- Ambiguità sui criteri di aggiudicazione
- Mancanza di chiarimenti su modalità economiche
- Requisiti formali dell'offerta non specificati
- Vincoli contrattuali non chiari
- Aspettative su composizione del team o certificazioni

Ordina per impatto (alto prima) e limita a 10 voci massimo.

### Step 9 — Scrivi il JSON e presenta il riepilogo

Scrivi immediatamente `rfp_analysis.json` senza attendere conferma. Poi presenta all'utente un riepilogo sintetico in Markdown:

> **Analisi RFP — [Nome Progetto]**
>
> **Valore:** €[importo] ([durata] mesi) | **Metodo:** [OEPV/massimo ribasso] | **Tipo:** [nuovo/brownfield/...]
>
> **Criterio prioritario:** [nome] ([punteggio] pt su [totale]) → [raccomandazione sintetica]
>
> **Formato risposta:** [componenti richieste] | **Modalità prezzi:** [fixed/T&M/tariffa]
>
> **Stack as-is:** [sintesi rischio EOL/LTS o "N/A — nuovo sviluppo"]
>
> **NFR rilevanti:** [N requisiti non funzionali estratti — categorie con impatto alto: ...]
>
> **Open point QA:** [N domande da fare al cliente — vedi `open_points_qa` nel JSON]
>
> `rfp_analysis.json` generato. Passa questo file a `gara-req-extractor` per l'estrazione dei requisiti.

## Tracciabilità — regole obbligatorie

Per ogni dato inserito nel JSON e nel template Excel, devi documentare:

**Certezza** — assegna uno dei tre livelli a ogni campo compilato:
- `estratto` — il dato è presente verbatim nel documento (cita pagina/sezione e max 20 parole del testo originale)
- `inferito` — il dato non è esplicito ma è ricavabile con ragionamento dal contesto del documento (spiega il ragionamento)
- `assunto` — il dato è assente nel documento; è un'assunzione operativa necessaria per procedere

Aggiungi nel JSON un campo `_meta` per ogni sezione con la struttura:
```json
"valore_economico": {
  "importo_base_asta": 500000,
  "_meta": {
    "certezza": "estratto",
    "fonte": "Sezione 4.2 — Quadro economico, pag. 18",
    "estratto": "L'importo a base d'asta è fissato in € 500.000,00 IVA esclusa"
  }
}
```

**Audit Trail** — per ogni decisione non ovvia (classificazione ambigua, inferenza, assunzione) aggiungi una voce in `rfp_analysis._audit_trail`:
```json
"_audit_trail": [
  {
    "id": "AT-001",
    "foglio": "RFP Analysis",
    "campo": "modalita_prezzi",
    "decisione": "fixed_scope",
    "fonte": "Sezione 6.1, pag. 23",
    "ragionamento": "Il bando richiede un 'prezzo complessivo onnicomprensivo' senza menzione di consuntivi",
    "alternativa_scartata": "time_and_material (escluso perché il bando non prevede rendicontazione ore)",
    "certezza": "inferito"
  }
]
```

Includi nell'audit trail almeno: metodo aggiudicazione (se non esplicitato), modalità prezzi, ogni criterio con punteggio dedotto, tipo progetto.

## Regole operative

**Principio assoluto — zero domande all'utente**: questa skill non fa mai domande in chat. Nessuna eccezione.

Quando un'informazione è ambigua o mancante:
- Fai l'assunzione più ragionevole basata sul contesto del documento
- Documentala nel campo `_audit_trail` con `certezza: assunto`
- Se impatta l'offerta, aggiungila in `open_points_qa` come domanda per il **cliente** — non per l'utente che usa la skill

**Vietato in ogni circostanza:**
- Proporre opzioni o scenari alternativi (es. "preferisci Agile o Waterfall?", "vuoi che aggiunga il margine commerciale?")
- Chiedere conferma prima di procedere a uno step successivo
- Presentare "prossimi passi possibili" chiedendo se continuare
- Interrompere per ambiguità non critiche
- Suggerire varianti di scope, team, approccio progettuale o stima

**Nessuna interruzione consentita.** Anche se il documento è parziale o ambiguo: assumi e documenta, non chiedere.

- **Non estrarre requisiti funzionali**: lo farà `gara-req-extractor`. Questa skill si ferma all'analisi strategica.
- **Non stimare GG/U**: nessun valore di effort in output.
- **Scrivi il JSON immediatamente** al termine dell'analisi, senza attendere conferma. Il riepilogo Markdown viene presentato dopo la scrittura del file.
- **Sii conservativo sugli importi**: se ci sono dubbi su IVA inclusa/esclusa, riporta entrambi i valori.
- **Le domande QA devono essere azionabili**: ogni domanda deve avere un impatto misurabile sull'offerta.
- **Per la verifica EOL/LTS**: preferisci la reference locale per velocità; usa web search solo per versioni non coperte. Documenta sempre la fonte.

## Riferimenti da leggere solo quando servono

- Per verificare stato EOL/LTS di versioni tecnologiche: `references/eol_lts.md`
