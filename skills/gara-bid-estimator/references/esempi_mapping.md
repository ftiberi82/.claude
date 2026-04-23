# Esempi di Mapping

> **Nota sui valori negli esempi**: i GG/U riportati sono calibrati sul **centro-alto del range** di riferimento, che rappresenta il valore atteso per un bando di gara tipico. Non sono il minimo possibile — sono il valore difendibile in un'offerta. Per casi con tutti i driver di riduzione presenti, è possibile scendere verso il centro del range motivando esplicitamente nelle note.

---

## Esempio 1

Testo del bando:
`Il portale dovrà consentire autenticazione tramite SPID e CIE, con profilazione per ruoli e tracciamento degli accessi.`

- Area funzionale: `Autenticazione & IAM`
- Complessità: `Alta`
- Stima indicativa: `14-16` GG/U
- Motivazione: federazione identità pubblica (SPID + CIE = 2 IdP distinti), RBAC e audit accessi — tutti segnali di crescita presenti
- Split tipico: FE `2`, BE `11`, Data `2`
- Assunzione da generare: _Si assume integrazione con IdP SPID livello 2 e CIE 3.0 tramite Keycloak — schema attributi da confermare con SA_

## Esempio 2

Testo del bando:
`La piattaforma dovrà integrarsi con il sistema SAP del cliente per scambio ordini e anagrafiche fornitore.`

- Area funzionale: `Integrazione Sistemi Legacy`
- Complessità: `Alta`
- Stima indicativa: `18-22` GG/U
- Motivazione: integrazione SAP (SOAP/RFC), mapping dati bidirezionale, dipendenza da sistema esterno con documentazione tipicamente incompleta
- Split tipico: FE `0`, BE `16`, Data `5`
- Assunzione da generare: _Si assume integrazione SAP via SOAP/RFC — documentazione API e ambiente sandbox da richiedere alla SA_

## Esempio 2b

Testo del bando:
`La soluzione dovrà integrarsi con SAP, CRM, protocollo informatico, PEC e sistema documentale.`

- Non creare una sola riga `Integrazione Sistemi Legacy`
- Crea almeno `5` righe, una per sistema distinto, oppure cluster omogenei se il bando è poco dettagliato
- Aggiungi una riga ulteriore di orchestrazione se i flussi condividono error handling, monitoraggio o scheduling
- La complessità può restare `Alta` per più righe, ma il totale cresce per numerosità, non per cambio etichetta
- Stima orientativa totale per 5 integrazioni + orchestrazione: `80-110` GG/U

## Esempio 3

Testo del bando:
`Sarà disponibile un cruscotto con KPI di avanzamento e possibilità di filtrare per periodo e struttura organizzativa.`

- Area funzionale: `Cruscotto Analytics`
- Complessità: `Media`
- Stima indicativa: `11-13` GG/U
- Motivazione: dashboard con filtri e logica di aggregazione moderata — nessun segnale di riduzione esplicito, si parte dal centro del range
- Split tipico: FE `5`, BE `3`, Data `5`

## Esempio 4

Testo del bando:
`Il sistema dovrà consentire caricamento documenti firmati digitalmente e archiviazione nel repository centrale.`

- Area funzionale: `Gestione Documentale`
- Complessità: `Media`
- Stima indicativa: `10-12` GG/U
- Motivazione: workflow documentale con firma (segnale di crescita) e archiviazione — si posiziona al centro-alto della fascia Media
- Split tipico: FE `3`, BE `7`, Data `2`

## Esempio 5

Testo del bando:
`L'interfaccia utente dovrà essere responsive e conforme alle linee guida di accessibilità WCAG 2.1 AA.`

- Area prevalente: `Portale e Frontend`
- Area secondaria da citare in nota: `Accessibilità`
- Complessità: `Media` oppure `Alta` se il portale ha molte schermate o componenti custom
- Stima indicativa: `12-18` GG/U solo per il frontend; aggiungere `5-8` GG/U separati per Accessibilità
- Motivazione: vincolo WCAG è un segnale di crescita — non inglobare l'accessibilità nella voce frontend, stimarla come riga separata

## Esempio 6

Testo del bando:
`Il portale prevede area pubblica, area riservata cittadino, area operatore e area amministratore per un totale di circa 30 schermate.`

- Non usare una sola riga `Portale e Frontend`
- Separa almeno per journey o modulo: area pubblica, cittadino, operatore, amministratore
- Con 30 schermate distribuite su 4 profili, la stima totale frontend si attesta tipicamente tra `60-90` GG/U
- Usa la complessità per ogni gruppo omogeneo e lascia che il numero di gruppi faccia crescere il totale

---

## Esempio 7 — Decomposizione Portale in micro-requisiti con Colonna D dettagliata

Testo del bando:
`La piattaforma prevede un portale con area pubblica per la consultazione dei servizi, area riservata per il cittadino (gestione pratiche, documenti, profilo), area operatore (istruttoria, approvazione, monitoraggio) e pannello di amministrazione (configurazione, utenti, log).`

**Come NON farlo** (aggregato, da evitare):
- REQ-001 | Portale e Frontend | Portale completo | Sviluppo portale con 4 profili utente | Alta | FE:40 BE:20

**Come farlo** (micro-requisiti, un profilo per riga — valori calibrati al centro-alto del range):

- REQ-001 | Portale e Frontend | Area pubblica — consultazione servizi
  - Colonna D: `Schermate: Home pubblica (landing), Catalogo servizi (lista+filtri), Dettaglio servizio (dettaglio), FAQ, Contatti = 5 schermate [stimato]. API: GET /servizi (lista+filtri), GET /servizi/{id} (dettaglio) = 2 API. Dati: Servizio, Categoria. Processi: ricerca testuale e filtro per categoria.`
  - Complessità: Media | FE:9, BE:4, Data:2 → Totale: 15

- REQ-002 | Portale e Frontend | Area riservata cittadino — gestione pratiche e documenti
  - Colonna D: `Schermate: Dashboard pratiche (lista), Nuova pratica (wizard 3 step), Dettaglio pratica (stato+allegati), Documenti personali (lista+upload), Profilo utente (form) = 5 schermate [stimato]. API: GET/POST /pratiche, GET /pratiche/{id}, POST /documenti (upload), GET/PUT /profilo = 6 API [stimato]. Dati: Pratica (stato, tipo, data), Documento (metadati), ProfiloUtente. Processi: wizard apertura pratica con validazione, upload allegati con anteprima.`
  - Complessità: Alta | FE:16, BE:10, Data:4 → Totale: 30

- REQ-003 | Portale e Frontend | Area operatore — istruttoria e approvazione
  - Colonna D: `Schermate: Lista pratiche da lavorare (lista+filtri avanzati), Dettaglio istruttoria (form compilazione), Approvazione/Rigetto (modale con note), Storico lavorazioni (timeline) = 4 schermate [stimato]. API: GET /pratiche?stato=in_istruttoria, PUT /pratiche/{id}/stato, POST /pratiche/{id}/note = 4 API [stimato]. Dati: Pratica, NoteIstruttore, StatoPratica. Processi: cambio stato pratica con notifica automatica al cittadino, assegnazione ad operatore.`
  - Complessità: Alta | FE:14, BE:9, Data:3 → Totale: 26

- REQ-004 | Portale e Frontend | Pannello amministrazione
  - Colonna D: `Schermate: Gestione utenti (lista+CRUD), Configurazione tipologie pratica (form), Visualizzazione log accessi (tabella) = 3 schermate [stimato]. API: GET/POST/PUT/DELETE /utenti, GET/POST /tipologie, GET /audit-log = 5 API [stimato]. Dati: Utente, Ruolo, TipologiaPratica, AuditLog. Processi: assegnazione ruoli, attivazione/disattivazione account.`
  - Complessità: Media | FE:10, BE:6, Data:2 → Totale: 18

**Totale GG/U area Frontend**: 15 + 30 + 26 + 18 = **89 GG/U**

**Nota**: il bando non specifica il numero esatto di schermate per area. I numeri sono inferiti dalla descrizione funzionale e marcati `[stimato]`. Generare 4 assunzioni corrispondenti nel foglio Assumptions & Risks.

---

## Esempio 8 — Decomposizione requisito AI/ML vago con stima inferita

Testo del bando:
`La soluzione dovrà prevedere un assistente virtuale intelligente per supportare i cittadini nella compilazione delle pratiche, con capacità di rispondere a domande frequenti e suggerire la documentazione necessaria. Il sistema dovrà inoltre garantire la spiegabilità delle risposte.`

**Come NON farlo** (aggregato, da evitare):
- REQ-010 | AI & Machine Learning | Chatbot intelligente | Sviluppo chatbot con RAG e XAI | Alta | FE:5, BE:15, Data:25

**Come farlo** (micro-requisiti per capability AI distinta — valori al centro-alto del range):

- REQ-010 | AI & Machine Learning | Chatbot assistente — pipeline RAG per FAQ e documentazione
  - Colonna D: `API: POST /chat/message (inference RAG), POST /knowledge/ingest (indicizzazione documenti), GET /chat/history. Dati: Knowledge base (FAQ istituzionali + template pratiche, ~200 documenti [stimato]); embedding su vector DB. Processi: pipeline RAG: chunking → embedding → retrieval top-k → generazione risposta con LLM; re-indexing settimanale [stimato]. Schermate: chat widget embedded nel portale area pubblica.`
  - Complessità: Alta | FE:5, BE:14, Data:20 → Totale: 39
  - Assunzione A-005: _Si assume knowledge base di ~200 documenti (FAQ + template) già disponibili in formato digitale — da confermare con il cliente [stimato]_

- REQ-011 | AI & Machine Learning | Spiegabilità risposte chatbot (XAI)
  - Colonna D: `API: GET /chat/{id}/explanation (riferimenti documentali usati nella risposta). Dati: Chunk sorgente recuperati, score di rilevanza, metadati documento. Processi: tracciamento chunk utilizzati per ogni risposta, visualizzazione in UI dei documenti di riferimento con highlight sezione. Schermate: pannello "Perché questa risposta?" con link ai documenti sorgente [stimato].`
  - Complessità: Media | FE:4, BE:6, Data:5 → Totale: 15
  - Assunzione A-006: _Si assume che la spiegabilità sia implementata tramite citation dei documenti sorgente (approccio RAG nativo), non tramite XAI post-hoc (LIME/SHAP) — da confermare con il cliente [stimato]_

**Nota**: il bando non specifica il tipo di XAI richiesto. L'interpretazione "citation-based" (tipica RAG) è preferita rispetto a LIME/SHAP post-hoc perché più leggera e coerente con un assistente documentale. L'assunzione documenta questa scelta e richiede conferma.

---

## Esempio 9 — Gerarchia padre-figlio su Autenticazione & IAM

Testo del bando:
`Il sistema deve supportare autenticazione SSO tramite IAM della Difesa, RBAC granulare per almeno 4 profili, MFA obbligatoria per ruoli amministrativi e audit trail completo e immutabile degli accessi.`

**Come NON farlo** (aggregato, da evitare):
- REQ-001 | Autenticazione & IAM | SSO, RBAC e audit trail | Sviluppo sistema IAM completo | Alta | FE:5, BE:18, Data:3

**Come farlo** (padre + 3 figli — valori al centro-alto del range per ogni segnale di crescita):

- REQ-001 | Autenticazione & IAM | Sistema IAM — SSO, RBAC granulare, MFA e audit trail
  - Colonna D: `— [decomposizione in REQ-001.1 → REQ-001.3]`
  - Colonne G/H/I/J: `0`
  - Colonna K: Must Have
  - Colonna L: `Macro-requisito — GG/U stimati nei sub-requisiti figli`
  - Formattazione: sfondo azzurro chiaro (FFD6E4F0), font bold

- REQ-001.1 | Autenticazione & IAM | Schermate autenticazione — login SSO, MFA e recupero credenziali
  - Colonna D: `Schermate: Login (landing+redirect SSO), MFA (wizard 2-step OTP), Recupero credenziali (form) = 3 schermate [stimato]. API: GET /auth/sso/redirect, GET /auth/callback, POST /auth/mfa/verify = 3 API. Processi: redirect verso IdP IAM Difesa, callback validazione token, emissione sessione applicativa.`
  - Complessità: Alta | FE:5, BE:0, Data:0 → Totale: 5
  - Note: Alta per integrazione IdP esterno (IAM Difesa) — dipende da documentazione SAML/OIDC fornita dalla SA.

- REQ-001.2 | Autenticazione & IAM | API autenticazione, token management e gestione sessioni
  - Colonna D: `API: POST /auth/token (emissione JWT), POST /auth/refresh (refresh), POST /auth/logout (revoca), GET /auth/me (profilo) = 4 API. Dati: Token (JWT, scadenza, claims), Sessione (userId, roles, lastActivity). Processi: validazione token IAM Difesa, mappatura claims → profili applicativi [stimato], refresh automatico, blacklist token revocati.`
  - Complessità: Alta | FE:0, BE:10, Data:2 → Totale: 12
  - Note: Alta per mapping claims IdP esterno → RBAC applicativo; schema attributi IAM Difesa da acquisire dalla SA.

- REQ-001.3 | Autenticazione & IAM | Gestione profili, RBAC granulare e audit trail immutabile
  - Colonna D: `API: GET/PUT /utenti/{id}/profilo, GET/POST /utenti/{id}/ruoli, GET /audit/accessi = 5 API [stimato]. Dati: Utente (id, profilo, ruoli), Ruolo (nome, permessi, scope), AuditLog (evento, userId, IP, timestamp, hash). Processi: provisioning automatico al primo login SSO [stimato], matrice permessi ≥4 profili, audit trail append-only con hash catena [stimato per immutabilità].`
  - Complessità: Alta | FE:1, BE:6, Data:3 → Totale: 10
  - Note: Alta per RBAC granulare (≥4 profili) + audit trail immutabile. Si assume DB separato append-only — da confermare.

**Totale GG/U area IAM**: 0 (padre REQ-001) + 5 (REQ-001.1) + 12 (REQ-001.2) + 10 (REQ-001.3) = **27 GG/U**

---

## Esempio 10 — Voci trasversali obbligatorie (da generare sempre)

Anche se il bando non le nomina esplicitamente, le seguenti voci vanno sempre aggiunte. Esempio per un progetto PA di medie dimensioni:

- REQ-T01 | Sicurezza e Compliance | Audit trail, cifratura dati e conformità GDPR
  - Complessità: Media | FE:0, BE:7, Data:3 → Totale: 10
  - Note: GDPR implicito per trattamento dati personali; VAPT [DA CHIARIRE] — aggiungere rischio R-001

- REQ-T02 | Infrastruttura e DevOps | Setup ambienti cloud, pipeline CI/CD e monitoring
  - Complessità: Media | FE:0, BE:10, Data:2 → Totale: 12
  - Note: 3 ambienti (sviluppo, collaudo, produzione) [stimato]; stack cloud [DA CHIARIRE]

- REQ-T03 | Accessibilità | Conformità WCAG 2.1 AA e dichiarazione AgID
  - Complessità: Media | FE:6, BE:0, Data:0 → Totale: 6
  - Note: obbligatorio per bandi PA; perimetro = portale pubblico e area riservata [stimato]

- REQ-T04 | PMO e Governance | SAL mensili, piano di progetto e reporting avanzamento
  - Complessità: Bassa | FE:0, BE:0, Data:4 → Totale: 4
  - Note: struttura governance standard PA; steering [DA CHIARIRE] se più vendor

**Totale voci trasversali**: 32 GG/U — tipicamente il 15-25% del totale build in un progetto PA medio.
