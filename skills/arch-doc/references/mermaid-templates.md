# Mermaid Templates per Architettura PA

Template pronti all'uso. Adatta sostituendo i nomi dei servizi con quelli reali estratti dai documenti.
Le righe con `# →` indicano cosa personalizzare.

---

## 1. Architecture Overview — `graph TB`

Usa sempre come primo diagramma della sezione "Panoramica Architetturale".
Adatta il numero di microservizi e aggiungi/rimuovi blocchi infrastrutturali.

```mermaid
graph TB
    subgraph Client["Client Layer"]
        BROWSER[Browser / App Mobile]
    end

    subgraph Ingress["API Gateway / Ingress"]
        GW[API Gateway]          %% → sostituisci con nome reale (es. Kong, Nginx, Spring Gateway)
    end

    subgraph Microservizi["Microservizi"]
        MS1[ms-utenti-service]   %% → nome microservizio 1
        MS2[ms-documenti-service] %% → nome microservizio 2
        MS3[ms-notifiche-service] %% → nome microservizio 3 (rimuovi se non presente)
    end

    subgraph Infrastruttura["Infrastruttura"]
        KAFKA[Kafka Broker]      %% → rimuovi se non presente
        REDIS[(Redis Cache)]     %% → rimuovi se non presente
        S3[(Object Storage\nMinIO / S3)] %% → rimuovi se non presente
    end

    subgraph Persistenza["Persistenza"]
        DB1[(PostgreSQL\ndb-utenti)]       %% → adatta per ms 1
        DB2[(PostgreSQL\ndb-documenti)]    %% → adatta per ms 2
    end

    subgraph Esterni["Servizi Esterni PA"]
        SPID[SPID / CIE IdP]    %% → rimuovi se non presente
        PAGOPA[PagoPA]          %% → rimuovi se non presente
    end

    BROWSER --> GW
    GW --> MS1
    GW --> MS2
    GW --> MS3
    MS1 --> DB1
    MS2 --> DB2
    MS2 --> S3
    MS3 --> KAFKA
    MS1 --> REDIS
    MS1 --> SPID
    MS2 --> PAGOPA
```

---

## 2. Kubernetes Deployment Topology — `graph TB`

Usa quando la containerizzazione è Kubernetes (produzione PA standard).

```mermaid
graph TB
    subgraph cluster["Kubernetes Cluster"]
        subgraph ns_app["Namespace: applicazione"]
            ING[Ingress Controller]
            subgraph deploy_ms1["Deployment: ms-utenti"]
                POD1A[Pod ms-utenti-1]
                POD1B[Pod ms-utenti-2]
            end
            subgraph deploy_ms2["Deployment: ms-documenti"]
                POD2A[Pod ms-documenti-1]
            end
            SVC1[Service ms-utenti]
            SVC2[Service ms-documenti]
            HPA1[HPA ms-utenti]
        end
        subgraph ns_infra["Namespace: infrastruttura"]
            KAFKA_SVC[Kafka StatefulSet]
            REDIS_SVC[Redis StatefulSet]
        end
        subgraph ns_mon["Namespace: monitoring"]
            PROM[Prometheus]
            GRAF[Grafana]
        end
    end

    subgraph storage["Storage"]
        PVC1[(PVC PostgreSQL)]
        PVC2[(PVC MinIO)]
    end

    ING --> SVC1
    ING --> SVC2
    SVC1 --> POD1A
    SVC1 --> POD1B
    SVC2 --> POD2A
    HPA1 -.->|scala| deploy_ms1
    POD1A --> KAFKA_SVC
    POD1A --> REDIS_SVC
    POD1A --> PVC1
    POD2A --> PVC2
```

---

## 3. OpenShift Deployment Topology — `graph TB`

Usa quando la containerizzazione è OpenShift (CONSIP/AgID compliant).

```mermaid
graph TB
    subgraph ocp["OpenShift Cluster"]
        subgraph proj_app["Project: applicazione"]
            ROUTE[Route / HAProxy]
            subgraph dc1["DeploymentConfig: ms-utenti"]
                RC1[ReplicationController]
                P1[Pod ms-utenti]
            end
            subgraph dc2["DeploymentConfig: ms-documenti"]
                RC2[ReplicationController]
                P2[Pod ms-documenti]
            end
            IS1[ImageStream ms-utenti]
            BC1[BuildConfig ms-utenti]
            CM[ConfigMap / Secret]
        end
        subgraph proj_infra["Project: infrastruttura"]
            KAFKA_OCP[Kafka - AMQ Streams]
            REDIS_OCP[Redis Enterprise]
        end
    end

    subgraph registry["Registry"]
        NEXUS[Nexus / Quay.io]
    end

    BC1 -->|build| IS1
    IS1 -->|deploy| dc1
    NEXUS --> IS1
    ROUTE --> dc1
    ROUTE --> dc2
    P1 --> KAFKA_OCP
    P1 --> CM
```

---

## 4. Auth Flow OIDC / SPID — `sequenceDiagram`

Usa per la sezione "Modello di Autenticazione". Adatta per OAuth2/OIDC standard o SPID.

```mermaid
sequenceDiagram
    actor Utente
    participant Browser
    participant APIGateway as API Gateway
    participant AuthService as Auth Service
    participant IdP as Identity Provider<br/>(SPID / OIDC / KeyCloak)

    Utente->>Browser: Accede all'applicazione
    Browser->>APIGateway: GET /app (no token)
    APIGateway-->>Browser: 302 Redirect → /auth/login

    Browser->>AuthService: GET /auth/login
    AuthService-->>Browser: 302 Redirect → IdP (con client_id, scope, redirect_uri)

    Browser->>IdP: Autenticazione utente
    IdP-->>Browser: Authorization Code

    Browser->>AuthService: GET /auth/callback?code=<CODE>
    activate AuthService
    AuthService->>IdP: POST /token (code, client_secret)
    IdP-->>AuthService: access_token + id_token
    AuthService->>AuthService: Valida token, crea sessione JWT
    AuthService-->>Browser: Set-Cookie: session_jwt (HttpOnly)
    deactivate AuthService

    Browser->>APIGateway: GET /api/v1/risorsa (con JWT cookie)
    APIGateway->>AuthService: Verifica JWT
    AuthService-->>APIGateway: JWT valido + claims (sub, roles)
    APIGateway->>APIGateway: Verifica autorizzazione RBAC
    APIGateway-->>Browser: 200 OK + dati
```

---

## 5. Kafka Event Flow — `sequenceDiagram`

Usa nella sezione "Panoramica Architetturale / Comunicazione Asincrona" se Kafka è presente.

```mermaid
sequenceDiagram
    participant Producer as Microservizio Producer<br/>(es. ms-pagamenti)
    participant Kafka as Kafka Broker
    participant CG as Consumer Group<br/>(es. ms-notifiche)
    participant DB as Database<br/>Consumer

    Producer->>Kafka: Publish evento<br/>Topic: ente.dominio.evento<br/>{payload JSON}
    activate Kafka
    Note over Kafka: Retention: 7 giorni<br/>Partitions: 3<br/>Replication: 3
    Kafka-->>Producer: ACK (acks=all)
    deactivate Kafka

    Kafka->>CG: Deliver messaggio (offset N)
    activate CG
    CG->>CG: Deserializza + valida schema
    CG->>DB: Persisti effetto evento
    DB-->>CG: OK
    CG->>Kafka: Commit offset N
    deactivate CG
```

---

## 6. REST Request Chain (3 microservizi) — `sequenceDiagram`

Usa per processi complessi che coinvolgono più microservizi in sequenza.

```mermaid
sequenceDiagram
    actor Utente
    participant GW as API Gateway
    participant MS1 as ms-utenti-service
    participant MS2 as ms-documenti-service
    participant MS3 as ms-notifiche-service
    participant DB1 as DB Utenti
    participant S3 as Object Storage

    Utente->>GW: POST /api/v1/documenti/carica<br/>{file, metadati}
    GW->>GW: Verifica JWT + RBAC
    GW->>MS2: POST /documenti/carica (forward)

    activate MS2
    MS2->>MS1: GET /utenti/{sub} (verifica identità)
    activate MS1
    MS1->>DB1: SELECT utente
    DB1-->>MS1: dati utente
    MS1-->>MS2: 200 OK {utente}
    deactivate MS1

    MS2->>S3: PUT oggetto/{uuid}
    S3-->>MS2: ETag + URL
    MS2->>MS2: Salva metadati documento
    MS2->>MS3: POST /notifiche/invia {evento: DOCUMENTO_CARICATO}
    MS3-->>MS2: 202 Accepted
    MS2-->>GW: 201 Created {id, url}
    deactivate MS2

    GW-->>Utente: 201 Created {id, url}
```

---

## 7. ER Diagram per Microservizio — `erDiagram`

Usa una istanza per ogni microservizio nella sezione "Modello Dati".
Includi solo le entità del microservizio corrente (non le entità di altri ms).

```mermaid
erDiagram
    UTENTE {
        uuid id PK
        string codice_fiscale UK
        string nome
        string cognome
        string email
        string ruolo
        timestamp created_at
        timestamp updated_at
        boolean attivo
    }

    SESSIONE {
        uuid id PK
        uuid utente_id FK
        string jwt_token_hash
        timestamp scadenza
        string ip_address
    }

    RUOLO {
        int id PK
        string codice UK
        string descrizione
    }

    UTENTE_RUOLO {
        uuid utente_id FK
        int ruolo_id FK
        timestamp assegnato_il
    }

    UTENTE ||--o{ SESSIONE : "ha"
    UTENTE }o--o{ RUOLO : "UTENTE_RUOLO"
```

---

## 8. C4Container — Alternativa a graph TB (sperimentale)

Usa come alternativa alla `graph TB` se si vuole una vista C4. Nota: sintassi sperimentale in Mermaid.

```mermaid
C4Container
    title Architettura Container — [Nome Sistema]

    Person(utente, "Utente PA", "Operatore o cittadino")

    System_Boundary(sistema, "Sistema [Nome]") {
        Container(gw, "API Gateway", "Nginx / Kong", "Routing, auth, rate limiting")
        Container(ms1, "ms-utenti-service", "Spring Boot", "Gestione utenti e autenticazione")
        Container(ms2, "ms-documenti-service", "Node.js", "Upload e gestione documenti")
        ContainerDb(db1, "DB Utenti", "PostgreSQL", "Dati utenti e sessioni")
        ContainerDb(db2, "DB Documenti", "PostgreSQL", "Metadati documenti")
        Container(cache, "Cache", "Redis", "Sessioni e dati frequenti")
    }

    System_Ext(spid, "SPID IdP", "Identity Provider nazionale")
    System_Ext(s3, "Object Storage", "MinIO / S3")

    Rel(utente, gw, "Usa", "HTTPS")
    Rel(gw, ms1, "Autentica", "HTTP/REST")
    Rel(gw, ms2, "Documenti", "HTTP/REST")
    Rel(ms1, db1, "Legge/Scrive", "JDBC")
    Rel(ms2, db2, "Legge/Scrive", "JDBC")
    Rel(ms1, cache, "Cache", "Redis Protocol")
    Rel(ms1, spid, "Auth", "SAML2 / OIDC")
    Rel(ms2, s3, "Archivia", "S3 API")
```

---

## 9. CI/CD Pipeline — `graph LR` (opzionale)

Includi nella sezione Introduzione o come appendice se richiesto.

```mermaid
graph LR
    GIT[Git Repository\nGitLab / GitHub] -->|push| CI

    subgraph CI["CI Pipeline"]
        BUILD[Build & Test]
        SAST[SAST / SCA\nSonarQube]
        IMG[Build Docker Image]
        SCAN[Image Scan\nTrivy / Clair]
    end

    CI -->|image push| REG[Container Registry\nNexus / Quay]
    REG -->|deploy| CD

    subgraph CD["CD Pipeline"]
        DEV[Deploy DEV]
        INT[Deploy INT/Test]
        PROD[Deploy PROD\n(manuale / approvazione)]
    end

    DEV --> INT --> PROD
```
