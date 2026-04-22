# Esempi di Mapping

## Esempio 1

Testo del bando:
`Il portale dovra consentire autenticazione tramite SPID e CIE, con profilazione per ruoli e tracciamento degli accessi.`

- Area funzionale: `Autenticazione & IAM`
- Complessita: `Alta`
- Stima indicativa: `12-15` GG/U
- Motivazione: federazione identita pubblica, profiling e audit accessi
- Split tipico: FE `2`, BE `10`, Data `1`

## Esempio 2

Testo del bando:
`La piattaforma dovra integrarsi con il sistema SAP del cliente per scambio ordini e anagrafiche fornitore.`

- Area funzionale: `Integrazione Sistemi Legacy`
- Complessita: `Alta`
- Stima indicativa: `16-22` GG/U
- Motivazione: integrazione SAP, mapping dati e dipendenza da sistema esterno
- Split tipico: FE `0`, BE `14`, Data `4`

## Esempio 2b

Testo del bando:
`La soluzione dovra integrarsi con SAP, CRM, protocollo informatico, PEC e sistema documentale.`

- Non creare una sola riga `Integrazione Sistemi Legacy`
- Crea almeno `5` righe, una per sistema distinto, oppure cluster omogenei se il bando e poco dettagliato
- Aggiungi una riga ulteriore di orchestrazione se i flussi condividono error handling, monitoraggio o scheduling
- La complessita puo restare `Alta` per piu righe, ma il totale cresce per numerosita, non per cambio etichetta

## Esempio 3

Testo del bando:
`Sara disponibile un cruscotto con KPI di avanzamento e possibilita di filtrare per periodo e struttura organizzativa.`

- Area funzionale: `Cruscotto Analytics`
- Complessita: `Media`
- Stima indicativa: `9-12` GG/U
- Motivazione: dashboard con filtri e logica di aggregazione moderata
- Split tipico: FE `4`, BE `2`, Data `4`

## Esempio 4

Testo del bando:
`Il sistema dovra consentire caricamento documenti firmati digitalmente e archiviazione nel repository centrale.`

- Area funzionale: `Gestione Documentale`
- Complessita: `Media`
- Stima indicativa: `8-11` GG/U
- Motivazione: workflow documentale con firma e archiviazione, ma senza full-text o conservazione avanzata
- Split tipico: FE `2`, BE `6`, Data `1`

## Esempio 5

Testo del bando:
`L'interfaccia utente dovra essere responsive e conforme alle linee guida di accessibilita WCAG 2.1 AA.`

- Area prevalente: `Portale e Frontend`
- Area secondaria da citare in nota: `Accessibilita`
- Complessita: `Media` oppure `Alta` se il portale ha molte schermate o componenti custom
- Stima indicativa: `10-18` GG/U
- Motivazione: forte lavoro FE con vincolo trasversale di accessibilita

## Esempio 6

Testo del bando:
`Il portale prevede area pubblica, area riservata cittadino, area operatore e area amministratore per un totale di circa 30 schermate.`

- Non usare una sola riga `Portale e Frontend`
- Separa almeno per journey o modulo: area pubblica, cittadino, operatore, amministratore
- Usa la complessita per ogni gruppo omogeneo e lascia che il numero di gruppi faccia crescere il totale

---

## Esempio 7 — Decomposizione Portale in micro-requisiti con Colonna D dettagliata

Testo del bando:
`La piattaforma prevede un portale con area pubblica per la consultazione dei servizi, area riservata per il cittadino (gestione pratiche, documenti, profilo), area operatore (istruttoria, approvazione, monitoraggio) e pannello di amministrazione (configurazione, utenti, log).`

**Come NON farlo** (aggregato, da evitare):
- REQ-001 | Portale e Frontend | Portale completo | Sviluppo portale con 4 profili utente | Alta | FE:40 BE:20

**Come farlo** (micro-requisiti, un profilo per riga):

- REQ-001 | Portale e Frontend | Area pubblica — consultazione servizi
  - Colonna D: `Schermate: Home (landing), Catalogo servizi (lista+filtri), Dettaglio servizio (dettaglio), FAQ, Contatti = 5 schermate [stimato]. API: GET /servizi (lista+filtri), GET /servizi/{id} (dettaglio) = 2 API. Dati: Servizio, Categoria. Processi: ricerca testuale e filtro per categoria.`
  - Complessita: Media | FE:7, BE:3, Data:2

- REQ-002 | Portale e Frontend | Area riservata cittadino — gestione pratiche e documenti
  - Colonna D: `Schermate: Dashboard pratiche (lista), Nuova pratica (wizard 3 step), Dettaglio pratica (stato+allegati), Documenti personali (lista+upload), Profilo utente (form) = 5 schermate [stimato]. API: GET/POST /pratiche, GET /pratiche/{id}, POST /documenti (upload), GET/PUT /profilo = 6 API [stimato]. Dati: Pratica (stato, tipo, data), Documento (metadati), ProfiloUtente. Processi: wizard apertura pratica con validazione, upload allegati con anteprima.`
  - Complessita: Alta | FE:14, BE:8, Data:3

- REQ-003 | Portale e Frontend | Area operatore — istruttoria e approvazione
  - Colonna D: `Schermate: Lista pratiche da lavorare (lista+filtri avanzati), Dettaglio istruttoria (form compilazione), Approvazione/Rigetto (modale con note), Storico lavorazioni (timeline) = 4 schermate [stimato]. API: GET /pratiche?stato=in_istruttoria, PUT /pratiche/{id}/stato, POST /pratiche/{id}/note = 4 API [stimato]. Dati: Pratica, NoteIstruttore, StatoPratica. Processi: cambio stato pratica con notifica automatica al cittadino, assegnazione ad operatore.`
  - Complessita: Alta | FE:12, BE:7, Data:2

- REQ-004 | Portale e Frontend | Pannello amministrazione
  - Colonna D: `Schermate: Gestione utenti (lista+CRUD), Configurazione tipologie pratica (form), Visualizzazione log accessi (tabella) = 3 schermate [stimato]. API: GET/POST/PUT/DELETE /utenti, GET/POST /tipologie, GET /audit-log = 5 API [stimato]. Dati: Utente, Ruolo, TipologiaPratica, AuditLog. Processi: assegnazione ruoli, attivazione/disattivazione account.`
  - Complessita: Media | FE:8, BE:5, Data:2

**Nota**: il bando non specifica il numero esatto di schermate per area. I numeri sono inferiti dalla descrizione funzionale e marcati `[stimato]`. Generare 4 assunzioni corrispondenti nel foglio Assumptions & Risks.

---

## Esempio 8 — Decomposizione requisito AI/ML vago con stima inferita

Testo del bando:
`La soluzione dovra prevedere un assistente virtuale intelligente per supportare i cittadini nella compilazione delle pratiche, con capacita di rispondere a domande frequenti e suggerire la documentazione necessaria. Il sistema dovra inoltre garantire la spiegabilita delle risposte.`

**Come NON farlo** (aggregato, da evitare):
- REQ-010 | AI & Machine Learning | Chatbot intelligente | Sviluppo chatbot con RAG e XAI | Alta | FE:5, BE:15, Data:25

**Come farlo** (micro-requisiti per capability AI distinta):

- REQ-010 | AI & Machine Learning | Chatbot assistente — pipeline RAG per FAQ e documentazione
  - Colonna D: `API: POST /chat/message (inference RAG), POST /knowledge/ingest (indicizzazione documenti), GET /chat/history. Dati: Knowledge base (FAQ istituzionali + template pratiche, ~200 documenti [stimato]); embedding su vector DB. Processi: pipeline RAG: chunking → embedding → retrieval top-k → generazione risposta con LLM; re-indexing settimanale [stimato]. Schermate: chat widget embedded nel portale area pubblica.`
  - Complessita: Alta | FE:4, BE:12, Data:18
  - Assunzione A-005: _Si assume knowledge base di ~200 documenti (FAQ + template) gia disponibili in formato digitale — da confermare con il cliente [stimato]_

- REQ-011 | AI & Machine Learning | Spiegabilita risposte chatbot (XAI)
  - Colonna D: `API: GET /chat/{id}/explanation (riferimenti documentali usati nella risposta). Dati: Chunk sorgente recuperati, score di rilevanza, metadati documento. Processi: tracciamento chunk utilizzati per ogni risposta, visualizzazione in UI dei documenti di riferimento con highlight sezione. Schermate: pannello "Perche questa risposta?" con link ai documenti sorgente [stimato].`
  - Complessita: Media | FE:3, BE:5, Data:4
  - Assunzione A-006: _Si assume che la spiegabilita sia implementata tramite citation dei documenti sorgente (approccio RAG nativo), non tramite XAI post-hoc (LIME/SHAP) — da confermare con il cliente [stimato]_

**Nota**: il bando non specifica il tipo di XAI richiesto. L'interpretazione "citation-based" (tipica RAG) e preferita rispetto a LIME/SHAP post-hoc perche piu leggera e coerente con un assistente documentale. L'assunzione documenta questa scelta e richiede conferma.

---

## Esempio 9 — Gerarchia padre-figlio su Autenticazione & IAM

Testo del bando:
`Il sistema deve supportare autenticazione SSO tramite IAM della Difesa, RBAC granulare per almeno 4 profili, MFA obbligatoria per ruoli amministrativi e audit trail completo e immutabile degli accessi.`

**Come NON farlo** (aggregato, da evitare):
- REQ-001 | Autenticazione & IAM | SSO, RBAC e audit trail | Sviluppo sistema IAM completo | Alta | FE:5, BE:18, Data:3

**Come farlo** (padre + 3 figli):

- REQ-001 | Autenticazione & IAM | Sistema IAM — SSO, RBAC granulare, MFA e audit trail
  - Colonna D: `— [decomposizione in REQ-001.1 → REQ-001.3]`
  - Colonna E: `—`
  - Colonna F: `—`
  - Colonne G/H/I/J: `0`
  - Colonna K: Must Have
  - Colonna L: `Macro-requisito — GG/U stimati nei sub-requisiti figli`
  - Formattazione: sfondo azzurro chiaro (FFD6E4F0), font bold

- REQ-001.1 | Autenticazione & IAM | Schermate autenticazione — login SSO, MFA e recupero credenziali
  - Colonna D: `Schermate: Login (landing+redirect SSO), MFA (wizard 2-step OTP), Recupero credenziali (form) = 3 schermate [stimato]. API: GET /auth/sso/redirect, GET /auth/callback, POST /auth/mfa/verify = 3 API. Processi: redirect verso IdP IAM Difesa, callback validazione token, emissione sessione applicativa.`
  - Complessita: Alta | FE:4, BE:0, Data:0 → Totale: 4
  - Note: Alta per integrazione IdP esterno (IAM Difesa) — dipende da documentazione SAML/OIDC fornita dalla SA.

- REQ-001.2 | Autenticazione & IAM | API autenticazione, token management e gestione sessioni
  - Colonna D: `API: POST /auth/token (emissione JWT), POST /auth/refresh (refresh), POST /auth/logout (revoca), GET /auth/me (profilo) = 4 API. Dati: Token (JWT, scadenza, claims), Sessione (userId, roles, lastActivity). Processi: validazione token IAM Difesa, mappatura claims → profili applicativi [stimato], refresh automatico, blacklist token revocati.`
  - Complessita: Alta | FE:0, BE:8, Data:1 → Totale: 9
  - Note: Alta per mapping claims IdP esterno → RBAC applicativo; schema attributi IAM Difesa da acquisire dalla SA.

- REQ-001.3 | Autenticazione & IAM | Gestione profili, RBAC granulare e audit trail immutabile
  - Colonna D: `API: GET/PUT /utenti/{id}/profilo, GET/POST /utenti/{id}/ruoli, GET /audit/accessi = 5 API [stimato]. Dati: Utente (id, profilo, ruoli), Ruolo (nome, permessi, scope), AuditLog (evento, userId, IP, timestamp, hash). Processi: provisioning automatico al primo login SSO [stimato], matrice permessi ≥4 profili, audit trail append-only con hash catena [stimato per immutabilita].`
  - Complessita: Alta | FE:1, BE:5, Data:2 → Totale: 8
  - Note: Alta per RBAC granulare (≥4 profili) + audit trail immutabile. Si assume DB separato append-only — da confermare.

**Totale GG/U area IAM**: 0 (padre REQ-001) + 4 (REQ-001.1) + 9 (REQ-001.2) + 8 (REQ-001.3) = **21 GG/U**

**Nota**: Il padre REQ-001 traccia l'origine dal bando senza portare GG/U. Solo i figli contribuiscono al totale. Il padre ha sfondo azzurro (FFD6E4F0) e font bold per distinguerlo visivamente nel foglio Excel.

**Assunzioni da generare nel foglio Assumptions & Risks**:
- _Si assume che l'IdP IAM Difesa esponga un endpoint SAML2 o OIDC compatibile con Keycloak — da confermare con la SA [stimato]_
- _Si assume mappatura claims IdP → 4 profili applicativi definiti dalla SA — da confermare con il cliente [stimato]_
- _Si assume audit trail immutabile implementato con hash concatenato su DB separato — da confermare con la SA [stimato]_
- _Si assume provisioning automatico utente al primo login SSO — da confermare con il cliente [stimato]_
