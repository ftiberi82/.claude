# Guida alla Decomposizione in Micro-Requisiti

Usa questa reference durante lo step 2 del workflow per trasformare ogni blocco funzionale del bando in unità atomiche stimabili. La regola generale è: **una riga = una unità atomica**. Non stimare aggregati.

> **Nota sulla calibrazione dei GG/U negli esempi**: tutti i valori numerici riportati in questa guida sono calibrati sul **centro-alto del range** dell'area funzionale di riferimento (vedi `regole_stima.md`). Rappresentano il valore atteso e difendibile per un bando di gara tipico, non il minimo possibile. Per casi con tutti i driver di riduzione presenti, è possibile scendere verso il centro del range motivando esplicitamente nelle note.

---

## Come leggere questa guida

Per ogni area trovi:
- **Unità atomica**: cosa costituisce una singola riga nel foglio Requirements
- **Segnali di suddivisione**: parole o strutture del bando che indicano che esistono più unità
- **Dimensioni Colonna D**: quali delle 4 dimensioni includere (obbligatorio = O, facoltativo = F, non applicabile = —)
  - `Schermate`: pagine, viste, form, sezioni UI
  - `API`: servizi REST, endpoint, operazioni BE
  - `Dati`: entità, tabelle, modello dati coinvolto
  - `Processi`: flussi, workflow, job, orchestrazioni
- **Regola di inferenza**: cosa si può inferire dal testo e cosa va marcato `[DA CHIARIRE]`

---

## Portale e Frontend

**Unità atomica**: journey utente o gruppo omogeneo di schermate per lo stesso profilo utente (max 3-5 schermate correlate).

**Segnali di suddivisione**: elenco di profili utente (pubblico, cittadino, operatore, amministratore), elenco di sezioni o moduli, verbi distinti (visualizza, compila, approva, monitora).

**Dimensioni Colonna D**:
- Schermate: O — nome e tipo (form/lista/dettaglio/landing/wizard)
- API: O — numero e operazione principale (GET lista, POST crea, PUT aggiorna, DELETE)
- Dati: F — entità lette/scritte da queste schermate
- Processi: F — validazioni multi-step, stati di navigazione, upload

**Esempio Colonna D**:
> Schermate: Home pubblica (landing), Ricerca servizi (lista+filtri), Dettaglio servizio (dettaglio) = 3 schermate [stimato]. API: GET /servizi (ricerca), GET /servizi/{id} (dettaglio) = 2 API. Dati: Servizio, Categoria. Processi: filtro per categoria e parola chiave.

**Regola di inferenza**: se il bando elenca profili utente, crea almeno una riga per profilo. Se descrive funzionalità senza specificare schermate, inferisci le schermate minime necessarie marcandole `[stimato]`. Se non è chiaro quanti moduli o sezioni esistono, metti `[DA CHIARIRE]`.

**Padre e figli**:
- **Soglia**: ≥ 2 profili utente o journey distinti → crea padre + figli.
- **Assi di split tipici**: profilo utente (pubblico, cittadino, operatore, amministratore), modulo funzionale omogeneo (es. ricerca, compilazione, istruttoria).
- **Esempio**:
  ```
  REQ-001   | Portale e Frontend | Portale con area pubblica e area riservata | — [REQ-001.1→001.3] | — | — | 0 | 0 | 0 | 0 | Must Have | Macro-requisito
  REQ-001.1 | Portale e Frontend | Area pubblica — consultazione servizi      | Schermate: ... | React | Media | 9 | 4 | 2 | 15 | Must Have | ...
  REQ-001.2 | Portale e Frontend | Area riservata cittadino — gestione pratiche| Schermate: ... | React | Alta  | 16| 10| 4 | 30 | Must Have | ...
  REQ-001.3 | Portale e Frontend | Area operatore — istruttoria e approvazione | Schermate: ... | React | Alta  | 14| 9 | 3 | 26 | Must Have | ...
  ```

---

## Integrazione Sistemi Legacy

**Unità atomica**: integrazione verso un sistema di destinazione distinto o un flusso con direzione e frequenza specifiche.

**Segnali di suddivisione**: lista di sistemi (SAP, CRM, protocollo, PEC, documentale), direzioni diverse (invio/ricezione), frequenze diverse (real-time vs batch), domini dati separati (ordini, anagrafiche, documenti).

**Dimensioni Colonna D**:
- Schermate: — (non applicabile)
- API: O — protocollo (REST, SOAP, file, batch, coda), direzione (inbound/outbound/bidirezionale), frequenza
- Dati: O — entità scambiate, numero di campi mappati [stimato se non specificato]
- Processi: O — error handling, retry, monitoraggio, scheduling

**Esempio Colonna D**:
> API: REST outbound verso CRM, real-time, trigger su evento di registrazione utente. Dati: Anagrafica cliente (nome, CF, email, indirizzo) = 4 campi [stimato]. Processi: retry su timeout (3 tentativi), log errori su DB, alert operatore.

**Regola di inferenza**: se il bando elenca sistemi senza specificare protocollo o frequenza, inferisci il protocollo più probabile per quel sistema (es. SAP → SOAP/RFC, protocollo informatico → REST/API PA) e marcalo `[stimato]`. Se la documentazione API è descritta come incompleta o da definire, metti `[DA CHIARIRE]` e crea un rischio.

**Padre e figli**:
- **Soglia**: ≥ 2 sistemi target distinti → crea padre + figli (una riga per sistema).
- **Assi di split tipici**: sistema target (SAP, CRM, protocollo, PEC, documentale), direzione del flusso (inbound/outbound/bidirezionale), dominio dati scambiato.
- **Esempio**:
  ```
  REQ-002   | Integrazione Sistemi Legacy | Integrazioni verso sistemi legacy | — [REQ-002.1→002.3] | — | — | 0 | 0 | 0 | 0 | Must Have | Macro-requisito
  REQ-002.1 | Integrazione Sistemi Legacy | Integrazione SAP — ordini e anagrafiche | API: SOAP outbound... | MuleSoft | Alta  | 0 | 14 | 4 | 18 | Must Have | ...
  REQ-002.2 | Integrazione Sistemi Legacy | Integrazione CRM — anagrafica utenti    | API: REST outbound...| MuleSoft | Alta  | 0 |  8 | 3 | 11 | Must Have | ...
  REQ-002.3 | Integrazione Sistemi Legacy | Integrazione protocollo informatico      | API: REST bidirez... | MuleSoft | Media | 0 |  6 | 2 |  8 | Must Have | ...
  ```

---

## Gestione Documentale

**Unità atomica**: workflow documentale distinto o capability documentale significativa (upload+firma, archiviazione, conservazione, ricerca full-text).

**Segnali di suddivisione**: tipi di documento diversi con iter diversi, fasi del ciclo di vita (produzione, approvazione, archiviazione, conservazione), sistemi ECM distinti.

**Dimensioni Colonna D**:
- Schermate: F — form di caricamento, vista documenti, pannello approvazione
- API: O — upload, download, ricerca, firma, protocollo, anteprima
- Dati: O — entità documento, metadati, stati del workflow, regole di metadatazione
- Processi: O — fasi del workflow (bozza → in approvazione → approvato → archiviato), notifiche di stato

**Esempio Colonna D**:
> API: POST /documenti (upload), GET /documenti (ricerca full-text), POST /documenti/{id}/firma (firma digitale), POST /documenti/{id}/archivia. Dati: Documento (tipo, stato, metadati XDCM [stimato]), Fascicolo. Processi: workflow bozza→approvazione→archiviazione con notifica PEC al cambio stato.

**Regola di inferenza**: "fascicolo documentale" implica almeno upload, visualizzazione e archiviazione come componenti minime — inferibili. Conservazione a norma e firma digitale qualificata sono aggiuntive e vanno marcate `[DA CHIARIRE]` se non esplicite.

**Padre e figli**:
- **Soglia**: ≥ 2 workflow documentali distinti o capability con cicli di vita separati → crea padre + figli.
- **Assi di split tipici**: tipo di workflow (produzione/approvazione/archiviazione/conservazione), tipo di documento con iter diverso, sistema ECM distinto.
- **Esempio**:
  ```
  REQ-003   | Gestione Documentale | Gestione documentale pratiche | — [REQ-003.1→003.2] | — | — | 0 | 0 | 0 | 0 | Must Have | Macro-requisito
  REQ-003.1 | Gestione Documentale | Upload e firma digitale documenti          | API: POST /documenti, POST /firma... | DocuStar | Media |  3 | 6 | 2 | 11 | Must Have | ...
  REQ-003.2 | Gestione Documentale | Workflow approvazione e archiviazione      | API: PUT /documenti/{id}/stato...   | DocuStar | Media |  2 | 5 | 2 |  9 | Must Have | ...
  ```

---

## Cruscotto Analytics

**Unità atomica**: dashboard distinta o cluster omogeneo di KPI (max 5-7 KPI correlati per la stessa audience).

**Segnali di suddivisione**: audience diverse (operativo, direzionale, regolatorio), domini dati separati (finanziario, operativo, HR), report periodici vs real-time.

**Dimensioni Colonna D**:
- Schermate: F — nome dashboard, tipo visualizzazione (tabella, grafico, mappa, KPI card)
- API: F — API dati o query BI (es. GET /analytics/kpi, stored procedure, data mart)
- Dati: O — sorgenti dati, entità aggregate, dimensioni di filtro, granularità temporale
- Processi: F — scheduling aggiornamento, drill-down, export (PDF/Excel), alert su soglia

**Esempio Colonna D**:
> Schermate: Dashboard operativa con 4 KPI card (pratiche aperte, chiuse, in attesa, SLA) e 1 grafico trend settimanale [stimato]. Dati: Pratica, StatiPratica, SLA; aggiornamento ogni 15 min [stimato]. Processi: filtro per unità organizzativa e periodo; export Excel.

**Regola di inferenza**: se il bando cita "cruscotto" senza dettagliare KPI, inferisci i KPI principali dal dominio applicativo e marcali `[stimato]`. Se le sorgenti dati non sono specificate, metti `[DA CHIARIRE]`.

**Padre e figli**:
- **Soglia**: ≥ 2 dashboard distinte o audience con KPI eterogenei → crea padre + figli.
- **Assi di split tipici**: audience (operativo, direzionale, regolatorio), dominio dati (finanziario, operativo, HR), modalità di aggiornamento (real-time vs schedulato).
- **Esempio**:
  ```
  REQ-004   | Cruscotto Analytics | Cruscotti per monitoraggio avanzamento | — [REQ-004.1→004.2] | — | — | 0 | 0 | 0 | 0 | Must Have | Macro-requisito
  REQ-004.1 | Cruscotto Analytics | Dashboard operativa — avanzamento pratiche | Schermate: KPI card... | PowerBI | Media | 4 | 2 | 4 | 10 | Must Have | ...
  REQ-004.2 | Cruscotto Analytics | Dashboard direzionale — KPI strategici      | Schermate: grafici..  | PowerBI | Media | 5 | 2 | 5 | 12 | Should Have | ...
  ```

---

## AI & Machine Learning

**Unità atomica**: capability AI distinta per dominio verticale (es. chatbot per assistenza, modello predittivo per rischio frodi, pipeline RAG per ricerca documentale).

**Segnali di suddivisione**: domini applicativi diversi, tipi di modello diversi (NLP, predittivo, classificazione, generativo), knowledge base separate, pipeline di re-training indipendenti.

**Dimensioni Colonna D**:
- Schermate: F — interfaccia utente se prevista (chat widget, form di input, dashboard XAI)
- API: O — API di inference (POST /chat, POST /predict), API di ingestion dati, API di monitoraggio
- Dati: O — sorgente knowledge base o dataset di training, volume stimato, qualità attesa
- Processi: O — pipeline (ingestion → preprocessing → inference → output), re-training, monitoring drift

**Esempio Colonna D**:
> API: POST /chat (inference RAG), POST /documents/ingest (indicizzazione), GET /model/metrics (monitoraggio). Dati: Knowledge base documentale (PDF + DOCX), ~500 documenti [stimato]. Processi: pipeline RAG (chunking → embedding → retrieval → generazione risposta), re-indexing settimanale [stimato]. Schermate: chat widget embedded nel portale.

**Regola di inferenza**: "chatbot intelligente" implica almeno una pipeline di retrieval e un modello generativo — decomponibili. XAI e re-training sono aggiuntivi: metti `[DA CHIARIRE]` se non espliciti. Non aggiungere capability AI non citate nel bando.

**Padre e figli**:
- **Soglia**: ≥ 2 capability AI su domini verticali distinti → crea padre + figli.
- **Assi di split tipici**: dominio verticale (chatbot, predittivo, classificazione, raccomandazione), pipeline separata (RAG vs fine-tuning vs rule-based), knowledge base diversa.
- **Esempio**:
  ```
  REQ-005   | AI & Machine Learning | Componenti AI per assistenza e classificazione | — [REQ-005.1→005.2] | — | — | 0 | 0 |  0 |  0 | Must Have | Macro-requisito
  REQ-005.1 | AI & Machine Learning | Chatbot RAG — assistenza utenti                | API: POST /chat...  | LangChain | Alta  | 4 | 12 | 18 | 34 | Must Have | ...
  REQ-005.2 | AI & Machine Learning | Classificazione automatica pratiche             | API: POST /predict..| Scikit    | Media | 1 |  6 | 10 | 17 | Should Have | ...
  ```

---

## Mobile App

**Unità atomica**: modulo funzionale o journey mobile omogeneo (es. onboarding, ricerca e prenotazione, area personale, notifiche).

**Segnali di suddivisione**: journey utente distinte, funzionalità device-native separate (fotocamera, GPS, biometria), piattaforme distinte (iOS nativo vs Android nativo).

**Dimensioni Colonna D**:
- Schermate: O — nome e tipo schermata nativa (lista, dettaglio, form, mappa, camera preview)
- API: O — API BE chiamate (sincrone o offline-first), autenticazione mobile
- Dati: F — entità sincronizzate, strategia offline/cache
- Processi: O — flusso di navigazione, funzionalità device-native, notifiche push

**Esempio Colonna D**:
> Schermate: Lista pratiche (lista scroll), Dettaglio pratica (dettaglio+allegati), Upload documento (camera + file picker), Firma biometrica = 4 schermate. API: GET /pratiche, GET /pratiche/{id}, POST /allegati (multipart), POST /firma. Dati: Pratica, Allegato (cache locale per offline [stimato]). Processi: cattura foto tramite camera nativa, firma biometrica TouchID/FaceID.

**Regola di inferenza**: se il bando richiede app mobile senza specificare iOS/Android, inferisci cross-platform (React Native/Flutter) e marcalo `[stimato]`. Funzionalità offline: `[DA CHIARIRE]` se non esplicita.

**Padre e figli**:
- **Soglia**: ≥ 2 journey mobile distinti o funzionalità device-native separate → crea padre + figli.
- **Assi di split tipici**: journey utente (onboarding, ricerca/prenotazione, area personale, notifiche), funzionalità device-native (fotocamera, GPS, biometria) che costituiscono moduli a sé.
- **Esempio**:
  ```
  REQ-006   | Mobile App | App mobile per cittadini | — [REQ-006.1→006.3] | — | — | 0 | 0 | 0 |  0 | Must Have | Macro-requisito
  REQ-006.1 | Mobile App | Onboarding e autenticazione mobile    | Schermate: login, registrazione... | Flutter | Alta  | 6 | 4 | 2 | 12 | Must Have | ...
  REQ-006.2 | Mobile App | Ricerca e prenotazione servizi        | Schermate: lista, dettaglio...     | Flutter | Media | 8 | 4 | 2 | 14 | Must Have | ...
  REQ-006.3 | Mobile App | Area personale e notifiche push       | Schermate: profilo, storico...     | Flutter | Media | 6 | 3 | 2 | 11 | Must Have | ...
  ```

---

## API Management

**Unità atomica**: API o gruppo omogeneo di API per lo stesso dominio/servizio esposto verso terzi.

**Segnali di suddivisione**: domini diversi da esporre (anagrafi, pratiche, documenti), consumer diversi (altri enti, privati, mobile app), livelli di autenticazione diversi.

**Dimensioni Colonna D**:
- Schermate: F — developer portal, documentazione Swagger se prevista
- API: O — numero di endpoint, metodi HTTP, versioning, autenticazione (OAuth2, JWT, API key)
- Dati: O — modello dati esposto, payload in/out, SLA per endpoint
- Processi: O — rate limiting, throttling, logging, audit accessi API

**Esempio Colonna D**:
> API: 4 endpoint GET (lista, dettaglio, ricerca, export) + 1 POST (notifica evento) per dominio Pratiche. Autenticazione: OAuth2 client_credentials. Dati: PraticaDTO (id, stato, dataCreazione, descrizione). Processi: rate limiting 100 req/min per client, audit log su DB, versioning /v1/.

**Regola di inferenza**: "interoperabilità con altri enti" implica conformità PDND/ModI — inferibile e da marcare `[stimato]`. Numero di endpoint: inferisci dal dominio se non esplicitato, metti `[DA CHIARIRE]` se il perimetro non è definibile.

**Padre e figli**:
- **Soglia**: ≥ 2 domini API distinti o consumer con livelli di autenticazione diversi → crea padre + figli.
- **Assi di split tipici**: dominio dati esposto (pratiche, documenti, anagrafe, notifiche), consumer (enti PA, partner privati, mobile app), livello autenticazione (API key, OAuth2, PDND).
- **Esempio**:
  ```
  REQ-007   | API Management | Esposizione API verso enti e partner | — [REQ-007.1→007.2] | — | — | 0 | 0 | 0 |  0 | Must Have | Macro-requisito
  REQ-007.1 | API Management | API Pratiche — esposizione verso enti PA   | API: GET/POST /pratiche v1...  | Kong | Alta  | 0 | 6 | 2 |  8 | Must Have | ...
  REQ-007.2 | API Management | API Documenti — esposizione verso partner  | API: GET /documenti v1...      | Kong | Media | 0 | 5 | 2 |  7 | Should Have | ...
  ```

---

## Autenticazione & IAM

**Unità atomica**: capability IAM principale (es. autenticazione SPID/CIE, gestione ruoli e profili, SSO federato, provisioning utenti).

**Segnali di suddivisione**: provider di identità multipli (SPID + CIE + username/password), sistemi target con SSO distinto, audit con requisiti diversi, provisioning da sistemi HR separati.

**Dimensioni Colonna D**:
- Schermate: F — login page, gestione profilo, pannello amministrazione ruoli
- API: O — endpoint autenticazione (POST /auth/login, POST /auth/token, POST /auth/refresh), API gestione utenti e ruoli
- Dati: O — entità Utente, Ruolo, Sessione, AuditLog; dimensione stimata del registro accessi
- Processi: O — flusso di autenticazione (redirect IdP → callback → emissione token), provisioning, revoca, audit

**Esempio Colonna D**:
> API: POST /auth/spid/callback (SPID), POST /auth/cie/callback (CIE), GET /me (profilo), POST /auth/logout. Dati: Utente (CF, email, ruoli), Sessione (token, scadenza), AuditAccesso (evento, IP, timestamp). Processi: flusso SAML2 SPID livello 2, mappatura attributi SPID → ruoli applicativi [stimato].

**Regola di inferenza**: se il bando cita "autenticazione SPID", SAML2 e livello 2 sono standard — inferibili. MFA aggiuntiva, provisioning da AD/LDAP: `[DA CHIARIRE]` se non esplicitato.

**Padre e figli**:
- **Soglia**: ≥ 2 capability IAM distinte (es. schermate auth + API + RBAC) → crea padre + figli. Se il bando cita solo "login utente" con un solo IdP, usa riga diretta senza padre.
- **Assi di split tipici**: layer tecnico (UI, API, gestione identità), capability IAM (autenticazione, autorizzazione/RBAC, audit trail, provisioning), provider IdP distinto.
- **Esempio**:
  ```
  REQ-008   | Autenticazione & IAM | Sistema IAM — SSO, RBAC e audit trail | — [REQ-008.1→008.3] | — | — | 0 | 0 | 0 |  0 | Must Have | Macro-requisito
  REQ-008.1 | Autenticazione & IAM | Schermate autenticazione — login, MFA, recupero pwd | Schermate: login (form), MFA (wizard)... | React    | Alta  | 5 | 0 | 0 |  5 | Must Have | ...
  REQ-008.2 | Autenticazione & IAM | API autenticazione e token management               | API: POST /auth/token, POST /auth/refresh... | Keycloak | Alta  | 0 | 10| 2 | 12 | Must Have | ...
  REQ-008.3 | Autenticazione & IAM | Gestione profili, RBAC e audit trail                | API: GET/PUT /utenti/{id}/ruoli, GET /audit... | Keycloak | Alta  | 1 | 6 | 3 | 10 | Must Have | ...
  ```

---

## Migrazione Dati

**Unità atomica**: dominio dati omogeneo o cluster di entità correlate da migrare (es. anagrafiche utenti, storico pratiche, allegati documentali).

**Segnali di suddivisione**: sistemi sorgente distinti, domini dati con regole di bonifica diverse, fasi di cut-over separate, tipologie di dati con vincoli diversi (strutturati vs non strutturati).

**Dimensioni Colonna D**:
- Schermate: — (non applicabile)
- API: F — API o connettore di estrazione dal sistema sorgente
- Dati: O — entità da migrare, volume record stimato, regole di mapping, regole di bonifica
- Processi: O — fasi ETL (estrazione → trasformazione → caricamento), validazione, riconciliazione, cut-over

**Esempio Colonna D**:
> Dati: Anagrafica Utenti (~50.000 record [stimato]), mapping CF → UUID nuovo sistema, bonifica email duplicate. Processi: estrazione da DB Oracle (sorgente), trasformazione con normalizzazione telefono/indirizzo, caricamento incrementale con log errori, riconciliazione pre-go-live. API: connettore JDBC sorgente [stimato].

**Regola di inferenza**: volumi dati quasi mai esplicitati — inferisci un ordine di grandezza dal dominio applicativo e marcalo `[stimato]`. Regole di bonifica specifiche: `[DA CHIARIRE]` se non descritte nel bando.

**Padre e figli**:
- **Soglia**: ≥ 2 domini dati con regole ETL diverse o sistemi sorgente distinti → crea padre + figli.
- **Assi di split tipici**: dominio dati (anagrafiche, storico transazioni, allegati documentali), sistema sorgente distinto, cut-over in fasi separate.
- **Esempio**:
  ```
  REQ-009   | Migrazione Dati | Migrazione dati da sistema legacy | — [REQ-009.1→009.3] | — | — | 0 | 0 |  0 |  0 | Must Have | Macro-requisito
  REQ-009.1 | Migrazione Dati | Migrazione anagrafiche utenti       | Dati: ~50.000 record [stimato]... | ETL Python | Alta  | 0 | 6 |  8 | 14 | Must Have | ...
  REQ-009.2 | Migrazione Dati | Migrazione storico pratiche         | Dati: ~200.000 record [stimato]...| ETL Python | Alta  | 0 | 5 | 10 | 15 | Must Have | ...
  REQ-009.3 | Migrazione Dati | Migrazione allegati documentali     | Dati: ~500 GB file [stimato]...   | ETL Python | Media | 0 | 4 |  6 | 10 | Must Have | ...
  ```

---

## Sicurezza e Compliance

**Unità atomica**: capability di sicurezza distinta (es. VAPT, audit trail applicativo, cifratura dati, hardening infra, conformità GDPR).

**Segnali di suddivisione**: normative diverse (GDPR vs AgID vs CAD), perimetri diversi (applicativo vs infrastrutturale), attività distinte (test vs implementazione vs documentazione).

**Dimensioni Colonna D**:
- Schermate: — (raramente applicabile)
- API: F — API di audit log, API di consent management se previste
- Dati: O — dati sensibili trattati, log di sicurezza, retention policy
- Processi: O — flussi di audit, processi di verifica periodica, procedure di incident response, DPIA

**Esempio Colonna D**:
> Dati: Log accessi (utente, azione, timestamp, IP) con retention 24 mesi [stimato], dati personali cifrati a riposo (AES-256). Processi: DPIA obbligatoria, procedura breach notification entro 72h, VAPT annuale su perimetro applicativo [stimato].

**Regola di inferenza**: se il bando cita GDPR, trattamento dati personali e DPIA sono impliciti — inferibili. VAPT certificato e penetration test formale: `[DA CHIARIRE]` se non esplicitati.

**Padre e figli**:
- **Soglia**: ≥ 2 capability di sicurezza su perimetri o normative diverse → crea padre + figli.
- **Assi di split tipici**: normativa di riferimento (GDPR, AgID, NIS2, normativa Difesa), tipo di attività (implementazione vs verifica vs documentazione), perimetro (applicativo vs infrastrutturale).
- **Esempio**:
  ```
  REQ-010   | Sicurezza e Compliance | Sicurezza e compliance normativa | — [REQ-010.1→010.3] | — | — | 0 | 0 | 0 |  0 | Must Have | Macro-requisito
  REQ-010.1 | Sicurezza e Compliance | Audit trail applicativo e cifratura dati   | Dati: log accessi, AES-256... | Spring | Alta  | 0 | 6 | 3 |  9 | Must Have | ...
  REQ-010.2 | Sicurezza e Compliance | VAPT e hardening infrastruttura             | Processi: VAPT annuale...     | —      | Alta  | 0 | 4 | 0 |  4 | Must Have | ...
  REQ-010.3 | Sicurezza e Compliance | DPIA e gestione consensi GDPR               | Processi: DPIA, consensi...   | —      | Media | 2 | 3 | 2 |  7 | Must Have | ...
  ```

---

## Infrastruttura e DevOps

**Unità atomica**: capability infrastrutturale principale (es. setup ambienti cloud, pipeline CI/CD, monitoring e alerting, backup e DR).

**Segnali di suddivisione**: ambienti multipli (sviluppo, collaudo, produzione), requisiti di HA/DR distinti, componenti infra separati (K8s, database, CDN, WAF).

**Dimensioni Colonna D**:
- Schermate: — (non applicabile)
- API: — (raramente applicabile)
- Dati: F — volumi di storage, requisiti di backup (RPO/RTO)
- Processi: O — pipeline CI/CD (build → test → deploy), monitoring (metriche, alert, log), procedure DR

**Esempio Colonna D**:
> Processi: pipeline CI/CD su GitLab (build → unit test → deploy su K8s) [stimato], monitoring con Prometheus/Grafana (latenza, disponibilità, errori), alert su canale dedicato. Dati: backup giornaliero DB con retention 30gg [stimato], RPO 1h / RTO 4h [DA CHIARIRE].

**Regola di inferenza**: cloud provider e stack tecnologico spesso non specificati — metti `[DA CHIARIRE]`. Pipeline CI/CD e monitoring base sono inferibili come standard di delivery. HA multi-zona e DR cross-region: `[DA CHIARIRE]` se non esplicitati.

**Padre e figli**:
- **Soglia**: ≥ 2 capability infrastrutturali su componenti tecnologici separati → crea padre + figli.
- **Assi di split tipici**: componente infra (ambienti/K8s, CI/CD, monitoring/alerting, backup/DR), ambiente (sviluppo, collaudo, produzione) se i costi di setup sono significativamente diversi.
- **Esempio**:
  ```
  REQ-011   | Infrastruttura e DevOps | Setup infrastruttura e delivery pipeline | — [REQ-011.1→011.3] | — | — | 0 | 0 | 0 |  0 | Must Have | Macro-requisito
  REQ-011.1 | Infrastruttura e DevOps | Ambienti cloud e orchestrazione K8s     | Processi: setup 3 ambienti... | Terraform | Alta  | 0 | 8 | 2 | 10 | Must Have | ...
  REQ-011.2 | Infrastruttura e DevOps | Pipeline CI/CD e release management     | Processi: GitLab CI...        | GitLab    | Media | 0 | 6 | 0 |  6 | Must Have | ...
  REQ-011.3 | Infrastruttura e DevOps | Monitoring, alerting e disaster recovery | Processi: Prometheus/Grafana...| Grafana   | Media | 0 | 5 | 2 |  7 | Must Have | ...
  ```

---

## Notifiche & Comunicazioni

**Unità atomica**: capability di notifica per canale distinto o per evento applicativo significativo.

**Segnali di suddivisione**: canali multipli (email, SMS, push, PEC), eventi diversi con template diversi, audience diverse (cittadino, operatore, ente esterno).

**Dimensioni Colonna D**:
- Schermate: F — pannello gestione template se previsto
- API: O — POST /notifiche (invio), GET /notifiche (storico), API provider esterno (SendGrid, Infobip, ecc.)
- Dati: F — entità Notifica, Template, Log invio, preferenze utente
- Processi: O — trigger di invio (evento applicativo), gestione bounce/errori, tracciamento recapito

**Esempio Colonna D**:
> API: POST /notifiche/email (invio via provider SMTP), POST /notifiche/pec (invio PEC istituzionale). Dati: Template (tipo evento, corpo, variabili), Log invio (stato, timestamp). Processi: trigger su cambio stato pratica, retry su errore di recapito (3 tentativi), log per audit.

**Regola di inferenza**: se il bando cita "notifica all'utente" senza specificare il canale, inferisci email come canale minimo e marcalo `[stimato]`. PEC istituzionale e SMS: `[DA CHIARIRE]` se non esplicitati.

**Padre e figli**:
- **Soglia**: ≥ 2 canali distinti o eventi con template e logiche di recapito diverse → crea padre + figli.
- **Assi di split tipici**: canale (email, SMS, push, PEC), evento applicativo con template diverso (apertura pratica vs cambio stato vs scadenza), audience distinta (cittadino vs operatore vs ente).
- **Esempio**:
  ```
  REQ-012   | Notifiche & Comunicazioni | Sistema notifiche multicanale | — [REQ-012.1→012.2] | — | — | 0 | 0 | 0 |  0 | Must Have | Macro-requisito
  REQ-012.1 | Notifiche & Comunicazioni | Notifiche email per eventi applicativi | API: POST /notifiche/email... | SendGrid | Media | 0 | 4 | 2 |  6 | Must Have | ...
  REQ-012.2 | Notifiche & Comunicazioni | Notifiche PEC istituzionale             | API: POST /notifiche/pec...   | PEC lib  | Media | 0 | 5 | 2 |  7 | Must Have | ...
  ```

---

## PMO e Governance

**Unità atomica**: pacchetto di governance distinto (es. SAL mensili, piano di progetto, reporting avanzamento, gestione rischi).

**Segnali di suddivisione**: stakeholder diversi con reporting diverso, milestone formali con deliverable distinti, più fornitori da coordinare.

**Dimensioni Colonna D**:
- Schermate: — (non applicabile)
- API: — (non applicabile)
- Dati: F — piano di progetto, registro rischi, verbali SAL
- Processi: O — cadenza SAL, modalità di escalation, struttura governance (steering, operational, working group)

**Esempio Colonna D**:
> Processi: SAL mensile con cliente + steering trimestrale, piano di progetto su MS Project [stimato], registro rischi aggiornato a ogni SAL, verbali condivisi entro 5 giorni lavorativi. Dati: Piano di progetto (WBS, milestone, RAG status), Registro rischi (probabilità, impatto, piano di mitigazione).

**Regola di inferenza**: struttura governance di base (SAL, piano di progetto, registro rischi) è sempre inferibile in gare PA. Numero di steering, più vendor, PMO esterno: `[DA CHIARIRE]` se non esplicitati.

**Padre e figli**:
- **Soglia**: ≥ 2 pacchetti di governance con deliverable e stakeholder distinti → crea padre + figli. In gare semplici con governance standard, spesso basta una sola riga diretta senza padre.
- **Assi di split tipici**: livello stakeholder (operativo, steering, working group), tipo di deliverable (SAL/verbali vs piano di progetto vs reporting direzionale), più vendor da coordinare.
- **Esempio**:
  ```
  REQ-013   | PMO e Governance | Governance e coordinamento progetto | — [REQ-013.1→013.2] | — | — | 0 | 0 | 0 | 0 | Must Have | Macro-requisito
  REQ-013.1 | PMO e Governance | SAL operativi, piano di progetto e registro rischi | Processi: SAL mensile... | MS Project | Media | 0 | 0 | 3 | 3 | Must Have | ...
  REQ-013.2 | PMO e Governance | Steering board e reporting direzionale              | Processi: steering trim... | —         | Bassa | 0 | 0 | 2 | 2 | Must Have | ...
  ```

---

## Accessibilità

**Unità atomica**: perimetro di verifica o intervento accessibilità (es. conformità WCAG sul portale, test assistivi su componenti custom, dichiarazione di accessibilità).

**Segnali di suddivisione**: perimetri applicativi separati (portale pubblico vs area riservata), componenti custom con requisiti specifici, attività distinte (audit iniziale, fix, dichiarazione, test periodico).

**Dimensioni Colonna D**:
- Schermate: O — perimetro delle schermate/componenti da verificare
- API: — (non applicabile)
- Dati: — (non applicabile)
- Processi: O — audit WCAG 2.1 AA, fix componenti non conformi, compilazione dichiarazione accessibilità AgID, test con screen reader

**Esempio Colonna D**:
> Schermate: perimetro = tutte le schermate del portale pubblico (~10 pagine [stimato]). Processi: audit WCAG 2.1 AA con tool automatico + revisione manuale, fix contrasto/focus/alt-text, dichiarazione accessibilità su sito, test con NVDA/JAWS su Chrome.

**Regola di inferenza**: se il bando cita "conformità linee guida AgID", WCAG 2.1 AA e dichiarazione accessibilità sono obbligatori per legge — inferibili. Retrofit su portale esistente e test periodico: `[DA CHIARIRE]` se non specificati.

**Padre e figli**:
- **Soglia**: ≥ 2 perimetri applicativi separati o fasi distinte (audit + fix + dichiarazione) con effort rilevante → crea padre + figli. Se il bando cita solo "conformità WCAG" genericamente, una sola riga è sufficiente.
- **Assi di split tipici**: perimetro applicativo (portale pubblico vs area riservata), fase del ciclo (audit/verifica vs fix/implementazione vs dichiarazione formale), componenti custom con effort specifico.
- **Esempio**:
  ```
  REQ-014   | Accessibilità | Conformità WCAG 2.1 AA — portale e dichiarazione | — [REQ-014.1→014.2] | — | — | 0 | 0 | 0 | 0 | Must Have | Macro-requisito
  REQ-014.1 | Accessibilità | Audit WCAG 2.1 AA e fix componenti               | Schermate: ~10 pag [stimato]... | —  | Media | 5 | 0 | 0 | 5 | Must Have | ...
  REQ-014.2 | Accessibilità | Dichiarazione accessibilità AgID e test assistivi  | Processi: test NVDA/JAWS...    | —  | Bassa | 2 | 0 | 0 | 2 | Must Have | ...
  ```

---

## Regola generale di inferenza

| Situazione | Azione |
|------------|--------|
| Il bando elenca componenti distinte (sistemi, profili, sezioni) | Crea una riga per componente — nessuna marcatura |
| Un componente è implicito nel dominio ma non esplicitato | Inseriscilo con suffisso `[stimato]` e crea assunzione in A&R |
| Non è possibile dedurre nulla dal testo | Scrivi `[DA CHIARIRE]` nella cella e crea assunzione o rischio in A&R |
| Il bando è contraddittorio o ambiguo | Scegli l'interpretazione più prudente, documenta l'ambiguità in A&R |
