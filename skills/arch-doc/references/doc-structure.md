# Guida alla Struttura del Documento di Architettura

Istruzioni dettagliate per il contenuto di ogni sezione. Segui l'ordine e rispetta i vincoli indicati.

---

## Struttura completa del documento

```
1. Introduzione
2. Panoramica Architetturale
   2.1 Architecture Overview
   2.2 Deployment Topology         (se K8s o OpenShift)
   2.3 Comunicazione Asincrona     (se Kafka presente)
3. Descrizione Microservizi
   3.1 <Nome Microservizio 1>
   3.2 <Nome Microservizio 2>
   ...
4. Specifiche API
   4.1 <Nome Microservizio 1>
   4.2 <Nome Microservizio 2>
   ...
5. Modello Dati
   5.1 <Nome Microservizio 1>
   5.2 <Nome Microservizio 2>
   ...
6. Modello di Autenticazione
Appendice A: Open Points           (se ci sono [DA DEFINIRE])
```

---

## Sezione 1 — Introduzione

**Obiettivo:** dare al lettore il contesto sufficiente per capire cosa viene descritto nelle sezioni successive.

**Contenuto obbligatorio:**
- 1-2 paragrafi di testo: nome sistema, ente committente, scopo applicativo, utenti target
- Tabella "Stack Tecnologico":

| Layer | Tecnologie |
|-------|-----------|
| Frontend | React 18 / Angular 17 / Vue 3 / altro |
| Backend | Spring Boot 3.x / Node.js 20 / Python 3.11 / altro |
| Database | PostgreSQL 15 / MySQL 8 / MongoDB 6 / altro |
| Infrastruttura | Kubernetes 1.28 / OpenShift 4.x / Docker Compose |
| Messaggistica | Apache Kafka 3.x / RabbitMQ / N/A |
| Cache | Redis 7 / N/A |
| Object Storage | MinIO / AWS S3 / N/A |
| Autenticazione | SPID L2 / CIE / OIDC + KeyCloak / JWT |

- Versione documento + data (es. "v1.0 — 17 aprile 2026")

**NON includere qui:** dettagli API, specifiche database, flussi di processo — quelle vanno nelle sezioni successive.

---

## Sezione 2 — Panoramica Architetturale

**Obiettivo:** dare una visione d'insieme dell'architettura con i diagrammi principali.

### 2.1 Architecture Overview (obbligatorio)

- Inizia con il diagramma `graph TB` Overview (template #1 da mermaid-templates.md)
- Segui con 1 paragrafo per ogni layer del diagramma:
  - **Client Layer:** tipo di client (browser, mobile, API B2B)
  - **API Gateway / Ingress:** tecnologia, ruolo (autenticazione, routing, rate limiting)
  - **Microservizi:** elenco con 1 riga di descrizione ciascuno
  - **Infrastruttura:** Kafka, Redis, Object Storage — ruolo di ciascuno
  - **Persistenza:** tipo DB per ogni ms
  - **Servizi Esterni:** integrazioni PA — quali e perché

### 2.2 Deployment Topology (se K8s o OpenShift)

- Aggiungi il diagramma K8s (template #2) o OpenShift (template #3)
- 1 breve paragrafo su namespace, naming convention, policy di scaling

### 2.3 Comunicazione Asincrona (se Kafka presente)

- Aggiungi il diagramma Kafka Event Flow (template #5)
- Tabella dei topic:

| Topic | Producer | Consumer | Scopo | Retention |
|-------|---------|---------|-------|-----------|
| `ente.dominio.evento` | ms-A | ms-B | descrizione | 7gg |

---

## Sezione 3 — Descrizione Microservizi

**Obiettivo:** descrivere responsabilità e comportamento di ogni microservizio. Le API vanno nella sezione 4.

**Ordine:** dal microservizio più centrale/core verso i servizi di supporto.

**Per ogni microservizio, una sottosezione H2 con:**

1. **Responsabilità** — 1-2 paragrafi: cosa fa, quali dati gestisce, quale dominio applicativo presidia
2. **Tecnologie** — tabella:

| Tecnologia | Versione | Ruolo |
|-----------|---------|-------|
| Spring Boot | 3.2 | Framework applicativo |
| PostgreSQL | 15 | Persistenza dati |
| Redis | 7 | Cache sessioni |

3. **Sequence diagram** — SOLO se il microservizio:
   - Orchestrata chiamate verso 2+ altri servizi
   - Gestisce un processo multi-step non ovvio (es. upload+OCR+notifica, checkout+pagamento+conferma)
   - Usa Saga pattern o compensating transactions

   Se il microservizio fa semplice CRUD → NON aggiungere sequence diagram, è ridondante.

**NON includere qui:** endpoint API, schema tabelle DB — vanno nelle sezioni 4 e 5.

---

## Sezione 4 — Specifiche API

**Obiettivo:** documentare tutti gli endpoint esposti da ogni microservizio.

**Per ogni microservizio, una sottosezione H2 con:**

1. **Base URL:** `http://ms-nome-service:8080/api/v1`
2. **Autenticazione:** JWT Bearer / API Key / mTLS (riferimento alla Sezione 6)
3. **Tabella endpoint:**

| Method | Path | Descrizione | Auth |
|--------|------|-------------|------|
| GET | `/risorsa` | Lista risorse con paginazione | JWT |
| GET | `/risorsa/{id}` | Dettaglio risorsa | JWT |
| POST | `/risorsa` | Crea nuova risorsa | JWT (ROLE_ADMIN) |
| PUT | `/risorsa/{id}` | Aggiorna risorsa | JWT (ROLE_ADMIN) |
| DELETE | `/risorsa/{id}` | Elimina risorsa | JWT (ROLE_ADMIN) |

4. **Per gli endpoint principali (non tutti)** — esempio request/response in JSON abbreviato:

```
POST /api/v1/documenti

Request Body:
{
  "titolo": "string (required)",
  "tipo": "CONTRATTO | DELIBERA | ATTO (required)",
  "file": "multipart/form-data"
}

Response 201 Created:
{
  "id": "uuid",
  "titolo": "string",
  "url": "string (pre-signed URL)",
  "createdAt": "ISO-8601"
}

Response 400 Bad Request:
{
  "error": "VALIDATION_ERROR",
  "message": "string",
  "fields": [{"field": "titolo", "message": "obbligatorio"}]
}
```

**Standard:** seguire REST (sostantivi plurali, HTTP verbs semantici, status code corretti: 200/201/204/400/401/403/404/409/500).

**Placeholder:** se gli endpoint non sono noti dai documenti → `[DA DEFINIRE — specificare gli endpoint esposti da <nome ms>]`

---

## Sezione 5 — Modello Dati

**Obiettivo:** documentare le entità di ogni microservizio e le loro relazioni.

**Per ogni microservizio, una sottosezione H2 con:**

1. **ER Diagram** (template #7 da mermaid-templates.md) — includi SOLO le entità di questo ms
2. **Tabella entità principali** (una tabella per ogni entità principale):

**Entità: NOME_ENTITA**

| Campo | Tipo | Constraints | Descrizione |
|-------|------|------------|-------------|
| id | UUID | PK, NOT NULL | Identificatore univoco |
| nome_campo | VARCHAR(255) | NOT NULL | Descrizione del campo |
| campo_fk | UUID | FK → ALTRA_ENTITA.id | Chiave esterna verso ... |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Data creazione record |
| updated_at | TIMESTAMP | NOT NULL | Data ultima modifica |

**Note:**
- Includi sempre `id`, `created_at`, `updated_at` come campi standard
- Per le FK: specifica sempre la tabella e colonna di riferimento
- Soft delete: aggiungi `deleted_at TIMESTAMP NULL` e nota il pattern

**Placeholder:** `[DA DEFINIRE — specificare le entità gestite da <nome ms>]`

---

## Sezione 6 — Modello di Autenticazione

**Obiettivo:** descrivere come gli utenti si autenticano e come vengono autorizzati.

**Contenuto obbligatorio:**

### 6.1 Strategia di Autenticazione

Paragrafo che descrive:
- Tipo di autenticazione (OIDC, SPID, OAuth2 Client Credentials, JWT stateless, session-based)
- Identity Provider utilizzato (KeyCloak, Authelia, SPID IdP, CIE)
- Tipo di token (JWT access token, opaque token, SAML assertion)

### 6.2 Flusso di Autenticazione

Sequence diagram obbligatorio (template #4 da mermaid-templates.md), adattato al tipo specifico.

Se SPID: evidenziare `AuthnRequest`, `SAMLResponse`, `fiscalNumber`.
Se OIDC: evidenziare `authorization_code`, `access_token`, `id_token`.
Se B2B (Client Credentials): mostrare `client_credentials` flow senza utente.

### 6.3 Token Claims

Tabella dei claims nel JWT/token:

| Claim | Tipo | Descrizione | Esempio |
|-------|------|-------------|---------|
| `sub` | string | Identificatore utente | `codiceFiscale` |
| `roles` | string[] | Ruoli applicativi | `["ROLE_OPERATORE"]` |
| `iss` | string | Issuer (IdP) | `https://idp.ente.it` |
| `aud` | string | Audience (applicazione) | `ms-nome-service` |
| `exp` | integer | Scadenza (Unix timestamp) | `1745000000` |
| `<claim custom>` | type | Descrizione | valore |

### 6.4 Modello di Autorizzazione (se RBAC/ABAC)

Tabella ruoli → permessi:

| Ruolo | Risorse accessibili | Note |
|-------|-------------------|------|
| ROLE_ADMIN | Tutto | Solo utenti interni |
| ROLE_OPERATORE | CRUD su risorse di competenza | |
| ROLE_VIEWER | Solo lettura | |
| ROLE_CITTADINO | Proprio fascicolo | Solo accesso B2C |

---

## Appendice A — Open Points

Includi questa appendice SOLO SE ci sono sezioni con `[DA DEFINIRE]`.

**Tabella open points:**

| # | Sezione | Descrizione lacuna | Azione richiesta |
|---|---------|-------------------|-----------------|
| 1 | 4.1 | Endpoint ms-pagamenti non definiti nei doc. funzionali | Richiedere specifiche API al team tecnico |
| 2 | 5.3 | Schema DB ms-notifiche non presente nell'analisi | Verificare con il DBA |
| 3 | 6 | Identity Provider non specificato (KeyCloak vs SPID?) | Decisione architetturale da prendere |

---

## Stile e Formattazione

**Tono:** tecnico, conciso, in italiano. Evitare circonlocuzioni.

**Tabelle:** preferire le tabelle a elenchi puntati per dati strutturati.

**Codice/JSON:** sempre in code block con syntax highlighting appropriato.

**Diagrammi Mermaid:**
- Nel `.md`: blocco ` ```mermaid ``` ` nativo
- Nel `.docx`: paragrafo Courier New 9pt con shading grigio (E8E8E8), preceduto da titolo H3 "[Tipo Diagramma] — [Nome]"

**Placeholder:** scrivere sempre in formato `**[DA DEFINIRE — motivo specifico]**` (grassetto) così sono facili da trovare nel documento.

**Versioning:** aggiungere in fondo al documento una tabella revisioni:

| Versione | Data | Autore | Modifiche |
|---------|------|--------|-----------|
| 1.0 | 2026-04-17 | arch-doc skill | Prima emissione |
