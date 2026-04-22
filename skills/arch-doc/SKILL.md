---
name: arch-doc
description: "Genera documentazione di architettura applicativa completa per applicazioni web della Pubblica Amministrazione italiana, sistemi gestionali, portali clienti e piattaforme digitali PA. Usa questa skill SEMPRE quando l'utente chiede di: generare un documento di architettura, creare un HLD (High Level Design), produrre un documento tecnico di architettura, descrivere l'architettura di un sistema a microservizi, generare diagrammi Mermaid di architettura, creare documentazione tecnica da analisi funzionale, produrre un 'architecture document', 'arch doc', 'documento architetturale', 'documento di progetto tecnico', 'technical design document', 'TDD', 'HLD', 'architecture overview'. Trigger anche su: 'architettura microservizi', 'architettura a microservizi', 'diagrammi di sequenza', 'ER diagram', 'data model', 'API specification', 'autenticazione JWT', 'autenticazione OAuth2', 'OIDC', 'Kafka', 'Redis', 'Kubernetes', 'OpenShift', 'Docker Compose', 'Object Storage', 'MinIO', 'SPID', 'PagoPA'. La skill legge i documenti funzionali dalla cartella documents/ (tramite le skill docx, xlsx, pptx) e genera sia un .docx (consegna formale PA) sia un .md (repository/uso interno), entrambi con diagrammi Mermaid embedded come codice. NON usare per semplici domande su architetture — solo quando si vuole produrre un documento di output."
---

# arch-doc — Generatore Documentazione Architetturale PA

Legge i documenti funzionali in input, estrae i requisiti tecnici e produce due file di output:
- `<nome-sistema>-architecture-<YYYY-MM-DD>.docx` — per consegna formale PA
- `<nome-sistema>-architecture-<YYYY-MM-DD>.md` — per repository/uso interno

Tutti i diagrammi sono in Mermaid (embedded come code block in entrambi i formati).

## Input attesi

| Tipo file | Come leggere |
|-----------|-------------|
| `documents/*.docx` | skill **docx** |
| `documents/*.xlsx` | skill **xlsx** |
| `documents/*.pdf`  | skill **docx** |
| `assets/reference_template.md` | Read diretto — template opzionale pre-compilato dall'utente |

## Workflow in 5 Step

### Step 1 — Raccolta input

1. Elenca tutti i file in `documents/` con `ls "documents/"` (o il path corretto se diverso)
2. Controlla se esiste `~/.claude/skills/arch-doc/assets/reference_template.md` compilato dall'utente: se sì, leggilo per capire le sezioni e i vincoli attesi
3. Per ogni `.docx`: usa il pattern della skill **docx** 
4. Per ogni `.xlsx`: usa il pattern della skill **xlsx** 
5. Per ogni `.pdf`: usa il pattern della skill **pdf** 
6. Se nessun documento trovato: chiedi all'utente una descrizione testuale del sistema prima di procedere

### Step 2 — Estrazione e analisi

Analizza i documenti letti e popola internamente questo schema. Se un campo non è ricavabile dai documenti, marcalo come `[DA DEFINIRE]` — non inventare mai nomi di microservizi, endpoint o entità:

```yaml
sistema:
  nome: <nome applicazione>
  tipo: webapp_pa | gestionale | portale_clienti | piattaforma
  ente: <ente/cliente>
  descrizione_breve: <1-2 frasi>
  stack_frontend: <React / Angular / Vue / altro>
  stack_backend: <Spring Boot / Node.js / Python / altro>

microservizi:
  - nome: <nome>             # es. ms-utenti-service
    responsabilita: <cosa fa>
    tecnologia: <framework>
    db_tipo: PostgreSQL | MySQL | MongoDB | altro
    db_nome: <nome schema/db>
    entita_principali: [<entita1>, <entita2>]
    api_esposte:
      - path: /api/v1/...
        method: GET | POST | PUT | DELETE | PATCH
        descrizione: ...
        request_body: {...}   # campi chiave, abbreviato
        response: {...}       # campi chiave, abbreviato
        auth_required: true | false
    processi_complessi: [<nome processo>]   # quelli che richiedono sequence diagram

infrastruttura:
  containerizzazione: Docker Compose | Kubernetes | OpenShift
  message_broker: Kafka | RabbitMQ | nessuno
    topics: [<nome-topic>]
  cache: Redis | nessuno
  object_storage: MinIO | S3 | nessuno
  api_gateway: presente | assente

servizi_esterni:
  - nome: <servizio>
    tipo: SPID | CIE | PagoPA | ANPR | PDND | altro
    protocollo: REST | SOAP | OAuth2 | SAML

autenticazione:
  tipo: JWT | OAuth2 | OIDC | SPID | CIE | basic | session
  identity_provider: <nome IdP>
  token_claims: [sub, roles, exp, iss, aud]
  modello_autorizzazione: RBAC | ABAC | nessuno
```

### Step 3 — Generazione diagrammi Mermaid

Leggi `~/.claude/skills/arch-doc/references/mermaid-templates.md` per i template pronti e adattali ai dati estratti.

Diagrammi da generare:

| Diagramma | Tipo Mermaid | Quando |
|-----------|-------------|--------|
| Architecture Overview | `graph TB` | sempre |
| Deployment Topology | `graph TB` (K8s/OpenShift) | se containerizzazione != Docker Compose |
| Kafka Topic Flow | `sequenceDiagram` | se Kafka presente |
| Sequence per processo complesso | `sequenceDiagram` | per ogni processo in `processi_complessi` |
| Auth Flow | `sequenceDiagram` | sempre |
| ER per ogni microservizio | `erDiagram` | per ogni ms con entità note |

Leggi `~/.claude/skills/arch-doc/references/architecture-patterns.md` per scegliere il pattern corretto di containerizzazione e servizi PA.

**Regole sintassi Mermaid:**
- IDs senza spazi e senza caratteri speciali (es. `UserService` non `User Service`)
- Subgraph nidificati: non superare 3 livelli
- Per `erDiagram`: includi solo le entità di quel microservizio
- Valida mentalmente ogni blocco prima di includerlo (frecce, subgraph chiusi, IDs univoci)

### Step 4 — Assemblaggio documento

Leggi `~/.claude/skills/arch-doc/references/doc-structure.md` per le istruzioni dettagliate su ogni sezione.

Struttura obbligatoria dell'output:

| # | Sezione | Contenuto principale |
|---|---------|---------------------|
| 1 | Introduzione | Nome, ente, scopo, stack tecnologico (tabella) |
| 2 | Panoramica Architetturale | Overview diagram + descrizione layer + K8s/Kafka se presenti |
| 3 | Descrizione Microservizi | Per ms: responsabilità, tech, sequence se flusso complesso |
| 4 | Specifiche API | Per ms: tabella endpoint (Method/Path/Descrizione/Request/Response/Auth) |
| 5 | Modello Dati | Per ms: erDiagram + tabella campi principali |
| 6 | Modello di Autenticazione | Flusso auth sequence + tabella token claims + RBAC/ABAC |
| App | Open Points | Tabella di tutti i `[DA DEFINIRE]` con motivo |

Se `reference_template.md` dell'utente definisce sezioni aggiuntive o vincoli, rispettali e aggiungili dopo la sezione 6.

### Step 5 — Generazione output (due file)

**File 1 — Markdown (`.md`)**

Genera direttamente il file Markdown con:
- Heading H1 per sezioni principali, H2 per sottosezioni microservizi
- Blocchi Mermaid come ` ```mermaid ... ``` `
- Tabelle GFM per API e data model
- Nome file: `<nome-sistema>-architecture-<YYYY-MM-DD>.md`

**File 2 — Word (`.docx`)**

Usa il pattern della skill **docx** con docx-js. Impostazioni:

```javascript
// Formato A4, margini 2.5cm
const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    // ... children
  }]
});
```

- Font default: Calibri 11pt
- Header: `<Nome Sistema> — Documento di Architettura`
- Footer: numero di pagina centrato
- Table of Contents: `new TableOfContents("Indice", { headingStyleRange: "1-3" })`
- Blocchi Mermaid nel .docx: paragrafo in `Courier New` 9pt con shading `E8E8E8`, preceduto da titolo in Heading 3
- Valida con `python ~/.agents/skills/docx/scripts/office/validate.py <output.docx>`

**Nome file output:**
```
<nome-sistema>-architecture-<YYYY-MM-DD>.docx
<nome-sistema>-architecture-<YYYY-MM-DD>.md
```
Esempio: `mgs-elenco-fornitori-architecture-2026-04-17.docx`

## Gestione errori e ambiguità

- File non leggibile: avvisa l'utente, continua con gli altri
- Microservizi non identificabili dai documenti: interrompi al passo 2 e chiedi all'utente prima di procedere
- Informazioni parziali: includi `[DA DEFINIRE — motivo]` come placeholder rosso/grassetto nel testo
- Sezioni senza dati sufficienti: includile ugualmente con placeholder + inseriscile nella tabella Open Points in Appendice
- Mai inventare nomi di microservizi, endpoint o entità non presenti nei documenti

## File di riferimento

| File | Quando leggere |
|------|---------------|
| `references/mermaid-templates.md` | Step 3 — template Mermaid per ogni tipo di diagramma |
| `references/architecture-patterns.md` | Step 3 — pattern K8s/OpenShift/Kafka/PA per scegliere l'approccio |
| `references/doc-structure.md` | Step 4 — guida dettagliata per il contenuto di ogni sezione |
| `assets/reference_template.md` | Step 1 — se presente, vincoli e microservizi pre-definiti dall'utente |
