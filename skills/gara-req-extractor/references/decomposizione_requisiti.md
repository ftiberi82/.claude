# Guida alla Decomposizione in Micro-Requisiti

Usa questa reference durante lo step 2 del workflow per trasformare ogni blocco funzionale del bando in unità atomiche stimabili. La regola generale è: **una riga = una unità atomica**. Non stimare aggregati.

> **Nota sulla calibrazione dei GG/U negli esempi**: tutti i valori numerici riportati in questa guida sono calibrati sul **centro-alto del range** dell'area funzionale di riferimento (vedi `regole_stima.md`). Rappresentano il valore atteso e difendibile per un bando di gara tipico, non il minimo possibile. Per casi con tutti i driver di riduzione presenti, è possibile scendere verso il centro del range motivando esplicitamente nelle note.

---

## Decision tree per determinare le unità atomiche

### Checklist di pre-classificazione (eseguire PRIMA del decision tree)

Prima di entrare nel decision tree, verifica se il blocco funzionale presenta almeno uno di questi tre segnali di suddivisione. Se anche solo **uno** è presente, tratta il blocco come se gli elementi fossero elencati esplicitamente al punto 1, indipendentemente dal fatto che il bando li nomini come sotto-voci distinte.

| Segnale | Domanda da porsi | Esempio dal CSA PRIMO |
|---|---|---|
| **Natura tecnica diversa** | Le attività richiedono competenze o tecnologie diverse? | ETL/import ≠ normalizzazione metadati ≠ data quality testing |
| **Attore o responsabile diverso** | Una parte è verificata o accettata da un soggetto diverso? | Fornitore esegue ETL; SA verifica il sample testing 10% |
| **Deliverable separato** | Il bando cita output distinti per ciascuna attività? | "report import" ≠ "attestazione integrità" ≠ "backup dati" |

> **Regola anti-collasso**: il punto 4 del tree ("capability unitaria non divisibile") si applica **solo se nessuno** dei tre segnali sopra è presente. Se anche uno solo è presente, il blocco non è unitario e va scomposto. Non usare il punto 4 come scorciatoia per blocchi che sembrano semplici ma nascondono attività eterogenee.

---

### Decision tree

Prima di decomporre qualsiasi blocco funzionale, applica questo albero decisionale nell'ordine indicato. Fermati alla prima condizione vera.

```
[PRE] Almeno uno dei 3 segnali di pre-classificazione è presente?
   → SÌ: vai direttamente al punto 1, trattando le attività distinte
          come elementi esplicitamente elencati.
   → NO: procedi normalmente dal punto 1.

1. Il bando elenca esplicitamente elementi distinti
   (profili utente, sistemi, canali, moduli, sezioni, fasi, attività
   con natura tecnica diversa, attori diversi o deliverable separati)?
   → SÌ: crea una riga per elemento (tipo: figlio).
          Crea il padre se gli elementi sono ≥ 2.
          Nessuna marcatura aggiuntiva sugli elementi espliciti.
   → NO: vai a 2.

2. L'area ha una regola quantitativa di fallback in questa guida?
   → SÌ: applica il fallback per stimare le unità attese.
          Vai a 3 per decidere se tenere in una riga o dividere.
   → NO: vai a 4.

3. I GG/U attesi per questa riga superano la soglia di split dell'area?
   (vedi tabella soglie sotto)
   → SÌ: dividi in sotto-unità seguendo gli assi di split tipici dell'area,
          anche se non esplicitamente elencate nel bando.
          Crea padre + figli. Marca ogni figlio con inferenza: stimato.
   → NO: usa 1 riga singola. Marca il conteggio con [stimato].

4. Il blocco è una capability unitaria non divisibile — verificato che
   NESSUNO dei 3 segnali di pre-classificazione sia presente
   (es. "notifiche email", "audit trail", "governance SAL")?
   → SÌ: usa 1 riga singola, nessun padre.
   → NO: usa 1 riga padre con inferenza: da_chiarire.
          Aggiungi una domanda bloccante. Non creare figli finché
          non ricevi risposta.
```

### Tabella soglie di split per area

La soglia è il **bordo inferiore della fascia Alta** per quell'area: se il requisito raggiunge o supera quel valore con il fallback, è troppo grande per stare in una riga singola e va diviso.

| Area funzionale | Soglia di split | Assi di split tipici da usare |
|---|---|---|
| Portale e Frontend | **16 GG/U** | profilo utente, modulo funzionale omogeneo |
| Integrazione Sistemi Legacy | **15 GG/U** | sistema target distinto, direzione flusso |
| Cruscotto Analytics | **14 GG/U** | audience (operativo/direzionale), dominio dati |
| Gestione Documentale | **12 GG/U** | workflow distinto, tipo documento con iter diverso |
| Migrazione Dati | **16 GG/U** | dominio dati, sistema sorgente distinto |
| AI & Machine Learning | **25 GG/U** | dominio verticale, pipeline separata |
| Mobile App | **25 GG/U** | journey utente, funzionalità device-native |
| API Management | **12 GG/U** | dominio API esposto, consumer distinto |
| Autenticazione & IAM | **10 GG/U** | capability IAM (auth / RBAC / audit / provisioning) |
| Sicurezza e Compliance | **10 GG/U** | normativa distinta, perimetro (applicativo/infra) |
| Infrastruttura e DevOps | **15 GG/U** | componente infra (ambienti / CI-CD / monitoring / DR) |
| Notifiche & Comunicazioni | **8 GG/U** | canale distinto, evento con template diverso |
| Accessibilità | **8 GG/U** | perimetro applicativo separato, fase distinta |
| PMO e Governance | **8 GG/U** | livello stakeholder, tipo deliverable |

**Come stimare i GG/U attesi al punto 3**: usa il centro del range dell'area moltiplicato per il numero di unità che il fallback quantitativo dell'area produce. Esempio: Portale con fallback di 4 schermate → centro range 12 GG/U → sotto soglia (16) → 1 riga singola. Portale con 2 profili da fallback → 12 × 2 = 24 GG/U → sopra soglia → divide in 2 figli da ~12 GG/U ciascuno.

**Regola padre-figlio**: la struttura padre-figlio si crea se il decision tree al punto 1 produce ≥ 2 elementi espliciti, oppure se il punto 3 determina che i GG/U superano la soglia. Non creare padri per ambiguità irrisolvibili (punto 4).

---

## Come leggere questa guida

Per ogni area trovi:
- **Unità atomica**: cosa costituisce una singola riga nel foglio Requirements
- **Segnali di suddivisione**: parole o strutture del bando che indicano che esistono più unità
- **Dimensioni Colonna D**: quali delle 4 dimensioni includere (obbligatorio = O, facoltativo = F, non applicabile = —)
- **Regola di inferenza chiusa**: lista esatta di ciò che è sempre inferibile e di ciò che non lo è mai
- **Regola quantitativa di fallback**: i valori predefiniti da usare quando il bando non specifica quantità

---

## Portale e Frontend

**Unità atomica**: journey utente o gruppo omogeneo di schermate per lo stesso profilo utente (max 3-5 schermate correlate).

**Segnali di suddivisione**: elenco di profili utente (pubblico, cittadino, operatore, amministratore), elenco di sezioni o moduli, verbi distinti (visualizza, compila, approva, monitora).

**Dimensioni Colonna D**:
- Schermate: O — nome e tipo (form/lista/dettaglio/landing/wizard)
- API: O — numero e operazione principale (GET lista, POST crea, PUT aggiorna, DELETE)
- Dati: F — entità lette/scritte da queste schermate
- Processi: F — validazioni multi-step, stati di navigazione, upload

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Home/landing pubblica | Sempre | nessuna |
| Schermata di lista + dettaglio per l'entità principale | Sempre | nessuna |
| Pagina di login (se area riservata presente) | Sempre | nessuna |
| Numero esatto di schermate non specificato | Sì, con fallback | `[stimato]` |
| Presenza di wizard multi-step | No | `[DA CHIARIRE]` |
| Componenti custom o design system proprietario | No | `[DA CHIARIRE]` |
| Funzionalità PWA / offline | No | `[DA CHIARIRE]` |
| CMS con editor visuale | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback** (quando il bando non specifica):
- Profilo utente senza dettaglio di schermate → assume **4 schermate** `[stimato]`
- API non specificate → assume **2 API** per profilo `[stimato]`
- Se il bando cita solo "portale" senza profili → assume **1 profilo, 4 schermate** `[stimato]`

**Esempio Colonna D**:
> Schermate: Home pubblica (landing), Ricerca servizi (lista+filtri), Dettaglio servizio (dettaglio) = 3 schermate [stimato]. API: GET /servizi (ricerca), GET /servizi/{id} (dettaglio) = 2 API. Dati: Servizio, Categoria. Processi: filtro per categoria e parola chiave.

**Padre e figli**:
- **Soglia**: ≥ 2 profili utente o journey **esplicitamente elencati** nel bando → crea padre + figli.
- **Assi di split tipici**: profilo utente (pubblico, cittadino, operatore, amministratore), modulo funzionale omogeneo.

---

## Integrazione Sistemi Legacy

**Unità atomica**: integrazione verso un sistema di destinazione distinto o un flusso con direzione e frequenza specifiche.

**Segnali di suddivisione**: lista di sistemi (SAP, CRM, protocollo, PEC, documentale), direzioni diverse (invio/ricezione), frequenze diverse (real-time vs batch), domini dati separati.

**Dimensioni Colonna D**:
- Schermate: — (non applicabile)
- API: O — protocollo (REST, SOAP, file, batch, coda), direzione (inbound/outbound/bidirezionale), frequenza
- Dati: O — entità scambiate, numero di campi mappati
- Processi: O — error handling, retry, monitoraggio, scheduling

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Protocollo per SAP | Sì (SOAP/RFC) | `[stimato]` |
| Protocollo per sistemi PA (protocollo informatico) | Sì (REST/API PA) | `[stimato]` |
| Direzione del flusso | Sì (da contesto) | `[stimato]` |
| Retry e error handling base | Sempre | nessuna |
| Numero di campi mappati non specificato | Sì, con fallback | `[stimato]` |
| Documentazione API del sistema target | No | `[DA CHIARIRE]` |
| Ambiente di test/sandbox disponibile | No | `[DA CHIARIRE]` |
| Frequenza/scheduling non esplicitata | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback** (quando il bando non specifica):
- Sistema citato senza dettaglio → assume **1 flusso bidirezionale** `[stimato]`
- Campi mappati non specificati → assume **10 campi** `[stimato]`
- Frequenza non specificata → assume **near-real-time** `[stimato]`

**Padre e figli**:
- **Soglia**: ≥ 2 sistemi target **esplicitamente elencati** → crea padre + figli (una riga per sistema).
- Se sistemi > 3, aggiungi una riga di orchestrazione/monitoraggio trasversale.

---

## Gestione Documentale

**Unità atomica**: workflow documentale distinto o capability documentale significativa.

**Segnali di suddivisione**: tipi di documento diversi con iter diversi, fasi del ciclo di vita (produzione, approvazione, archiviazione, conservazione), sistemi ECM distinti.

**Dimensioni Colonna D**:
- Schermate: F — form di caricamento, vista documenti, pannello approvazione
- API: O — upload, download, ricerca, firma, protocollo, anteprima
- Dati: O — entità documento, metadati, stati del workflow
- Processi: O — fasi del workflow, notifiche di stato

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Upload e download documenti | Sempre | nessuna |
| Visualizzazione lista documenti | Sempre | nessuna |
| Archiviazione base | Sempre (se repository citato) | nessuna |
| Metadati XDCM standard | Sì | `[stimato]` |
| Notifiche cambio stato (email) | Sì | `[stimato]` |
| Conservazione a norma | No | `[DA CHIARIRE]` |
| Firma digitale qualificata | No (solo se esplicitata) | `[DA CHIARIRE]` |
| Protocollazione con sistema esterno | No | `[DA CHIARIRE]` |
| Full-text search | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- "Fascicolo documentale" senza dettaglio → assume **1 workflow upload+archiviazione** `[stimato]`
- Numero di tipi documento non specificato → assume **1 tipo** `[stimato]`

**Padre e figli**:
- **Soglia**: ≥ 2 workflow documentali **esplicitamente distinti** o capability con cicli di vita separati → crea padre + figli.

---

## Cruscotto Analytics

**Unità atomica**: dashboard distinta o cluster omogeneo di KPI (max 5-7 KPI correlati per la stessa audience).

**Segnali di suddivisione**: audience diverse (operativo, direzionale, regolatorio), domini dati separati, report periodici vs real-time.

**Dimensioni Colonna D**:
- Schermate: F — nome dashboard, tipo visualizzazione
- API: F — API dati o query BI
- Dati: O — sorgenti dati, entità aggregate, dimensioni di filtro, granularità temporale
- Processi: F — scheduling aggiornamento, drill-down, export, alert su soglia

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| KPI principali del dominio applicativo | Sì (dal contesto) | `[stimato]` |
| Filtro per periodo | Sempre (se dashboard citata) | nessuna |
| Export base (Excel/PDF) | Sì | `[stimato]` |
| Aggiornamento periodico | Sì | `[stimato]` |
| Numero esatto di KPI | Sì, con fallback | `[stimato]` |
| Sorgenti dati specifiche | No | `[DA CHIARIRE]` |
| Data mart dedicato | No | `[DA CHIARIRE]` |
| Real-time streaming | No | `[DA CHIARIRE]` |
| Drill-down gerarchico | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- "Cruscotto" senza dettaglio KPI → assume **5 KPI** `[stimato]`, **1 dashboard**
- Audience non specificata → assume **audience operativa** `[stimato]`
- Se ≥ 2 audience citate → crea padre + figli (una riga per audience)

**Padre e figli**:
- **Soglia**: ≥ 2 dashboard **esplicitamente distinte** o audience con KPI eterogenei → crea padre + figli.

---

## AI & Machine Learning

**Unità atomica**: capability AI distinta per dominio verticale.

**Segnali di suddivisione**: domini applicativi diversi, tipi di modello diversi, knowledge base separate, pipeline di re-training indipendenti.

**Dimensioni Colonna D**:
- Schermate: F — interfaccia utente se prevista
- API: O — API di inference, API di ingestion dati, API di monitoraggio
- Dati: O — sorgente knowledge base o dataset, volume stimato, qualità attesa
- Processi: O — pipeline (ingestion → preprocessing → inference → output), re-training, monitoring drift

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Pipeline RAG base (chunking + retrieval + generazione) | Sì (se "chatbot intelligente" citato) | `[stimato]` |
| API di inference | Sempre (se AI citata) | nessuna |
| Indicizzazione documenti | Sì (se knowledge base citata) | `[stimato]` |
| Volume knowledge base | Sì, con fallback | `[stimato]` |
| XAI / spiegabilità | No | `[DA CHIARIRE]` |
| Re-training periodico | No | `[DA CHIARIRE]` |
| Fine-tuning su dati proprietari | No | `[DA CHIARIRE]` |
| Deployment on-premise / air-gapped | No | `[DA CHIARIRE]` |
| MLOps continuativo | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- Knowledge base non quantificata → assume **500 documenti** `[stimato]`
- Capability AI senza dettaglio → assume **1 pipeline RAG** `[stimato]`

**Padre e figli**:
- **Soglia**: ≥ 2 capability AI su domini verticali **esplicitamente distinti** → crea padre + figli.

---

## Mobile App

**Unità atomica**: modulo funzionale o journey mobile omogeneo.

**Segnali di suddivisione**: journey utente distinte, funzionalità device-native separate, piattaforme distinte.

**Dimensioni Colonna D**:
- Schermate: O — nome e tipo schermata nativa
- API: O — API BE chiamate, autenticazione mobile
- Dati: F — entità sincronizzate, strategia offline/cache
- Processi: O — flusso di navigazione, funzionalità device-native, notifiche push

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Piattaforma cross-platform (Flutter/React Native) | Sì (se non specificato) | `[stimato]` |
| Schermata di login mobile | Sempre | nessuna |
| Notifiche push base | Sì (se notifiche citate) | `[stimato]` |
| Numero schermate per journey | Sì, con fallback | `[stimato]` |
| Funzionalità offline | No | `[DA CHIARIRE]` |
| Doppia piattaforma nativa (iOS + Android separati) | No | `[DA CHIARIRE]` |
| Integrazione MDM aziendale | No | `[DA CHIARIRE]` |
| Funzionalità device-native (NFC, GPS, biometria) | No (solo se esplicitate) | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- Journey non specificati → assume **3 journey** (onboarding, funzione principale, area personale) `[stimato]`
- Schermate per journey non specificate → assume **3 schermate** per journey `[stimato]`

**Padre e figli**:
- **Soglia**: ≥ 2 journey **esplicitamente citati** o funzionalità device-native separate → crea padre + figli.

---

## API Management

**Unità atomica**: API o gruppo omogeneo di API per lo stesso dominio/servizio esposto verso terzi.

**Segnali di suddivisione**: domini diversi da esporre, consumer diversi, livelli di autenticazione diversi.

**Dimensioni Colonna D**:
- Schermate: F — developer portal, documentazione Swagger
- API: O — numero endpoint, metodi HTTP, versioning, autenticazione
- Dati: O — modello dati esposto, payload in/out, SLA per endpoint
- Processi: O — rate limiting, throttling, logging, audit accessi API

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Autenticazione OAuth2/JWT | Sì (standard de facto) | `[stimato]` |
| Versioning /v1/ | Sì | `[stimato]` |
| Rate limiting base | Sì | `[stimato]` |
| Audit log API | Sì | `[stimato]` |
| Numero di endpoint | Sì, con fallback | `[stimato]` |
| Conformità PDND/ModI | No | `[DA CHIARIRE]` |
| Developer portal con onboarding esterno | No | `[DA CHIARIRE]` |
| SLA contrattuali per endpoint | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- Dominio API senza dettaglio endpoint → assume **4 endpoint** (GET lista, GET dettaglio, POST crea, PUT aggiorna) `[stimato]`

**Padre e figli**:
- **Soglia**: ≥ 2 domini API **esplicitamente distinti** o consumer con autenticazione diversa → crea padre + figli.

---

## Autenticazione & IAM

**Unità atomica**: capability IAM principale (autenticazione, gestione ruoli, SSO, provisioning).

**Segnali di suddivisione**: provider di identità multipli, sistemi target con SSO distinto, provisioning da sistemi HR separati.

**Dimensioni Colonna D**:
- Schermate: F — login page, gestione profilo, pannello amministrazione ruoli
- API: O — endpoint autenticazione, API gestione utenti e ruoli
- Dati: O — entità Utente, Ruolo, Sessione, AuditLog
- Processi: O — flusso di autenticazione, provisioning, revoca, audit

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Flusso SAML2 per SPID | Sì (se SPID citato) | nessuna |
| Livello SPID 2 | Sì (standard PA) | `[stimato]` |
| RBAC base (ruoli applicativi) | Sempre (se area riservata presente) | nessuna |
| Audit log accessi base | Sempre | nessuna |
| Mappatura attributi IdP → ruoli applicativi | Sì | `[stimato]` |
| MFA aggiuntiva (oltre SPID) | No | `[DA CHIARIRE]` |
| Provisioning da AD/LDAP | No | `[DA CHIARIRE]` |
| SSO federato multi-applicazione | No | `[DA CHIARIRE]` |
| Schema attributi IdP | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- "Login utente" senza dettaglio → assume **1 IdP, RBAC base** → 1 riga diretta senza padre `[stimato]`
- Se 2+ IdP citati esplicitamente → crea padre + figli (una riga per capability IAM: autenticazione, RBAC, audit)

**Padre e figli**:
- **Soglia**: ≥ 2 capability IAM **esplicitamente distinte** (es. multi-IdP + provisioning + audit separato) → crea padre + figli.
- "Login utente" generico → riga singola, nessun padre.

---

## Migrazione Dati

**Unità atomica**: dominio dati omogeneo o cluster di entità correlate da migrare.

**Segnali di suddivisione**: sistemi sorgente distinti, domini dati con regole di bonifica diverse, fasi di cut-over separate.

**Dimensioni Colonna D**:
- Schermate: — (non applicabile)
- API: F — connettore di estrazione dal sistema sorgente
- Dati: O — entità da migrare, volume record stimato, regole di mapping, regole di bonifica
- Processi: O — fasi ETL, validazione, riconciliazione, cut-over

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Pipeline ETL base (estrazione → trasformazione → caricamento) | Sempre | nessuna |
| Log errori e riconciliazione | Sempre | nessuna |
| Volume record | Sì, con fallback | `[stimato]` |
| Connettore JDBC per DB relazionale | Sì (se DB legacy citato) | `[stimato]` |
| Regole di bonifica specifiche | No | `[DA CHIARIRE]` |
| Finestra di cut-over | No | `[DA CHIARIRE]` |
| Qualità dei dati sorgente | No | `[DA CHIARIRE]` |
| Migrazione incrementale vs full-load | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- Dominio dati senza volume → assume **50.000 record** `[stimato]`
- "Migrazione dati" senza dettaglio domini → assume **1 dominio dati** `[stimato]`, riga singola

**Esempio di pre-classificazione obbligatoria**: un blocco "migrazione dati storici" che include ETL/import + normalizzazione metadati + validazione integrità con sample testing SA attiva tutti e 3 i segnali della checklist (natura tecnica diversa: ETL ≠ data quality; attore diverso: SA verifica il sample; deliverable separato: report import ≠ attestazione integrità). Va al punto 1 del tree anche se il bando non li nomina come sotto-voci distinte.

**Padre e figli**:
- **Soglia**: ≥ 2 domini dati con regole ETL **diverse** o sistemi sorgente **distinti esplicitamente**, oppure presenza di almeno 1 segnale di pre-classificazione → crea padre + figli.

---

## Sicurezza e Compliance

**Unità atomica**: capability di sicurezza distinta per normativa o perimetro.

**Segnali di suddivisione**: normative diverse, perimetri diversi (applicativo vs infrastrutturale), attività distinte (test vs implementazione vs documentazione).

**Dimensioni Colonna D**:
- Schermate: — (raramente applicabile)
- API: F — API di audit log, consent management
- Dati: O — dati sensibili trattati, log di sicurezza, retention policy
- Processi: O — audit, verifiche periodiche, incident response, DPIA

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| DPIA (se GDPR citato) | Sempre | nessuna |
| Breach notification 72h (se GDPR citato) | Sempre | nessuna |
| Audit trail base (log accessi) | Sempre | nessuna |
| Cifratura dati a riposo AES-256 | Sì (se dati sensibili citati) | `[stimato]` |
| Retention log (24 mesi) | Sì | `[stimato]` |
| VAPT certificato | No | `[DA CHIARIRE]` |
| Penetration test formale | No | `[DA CHIARIRE]` |
| Hardening infrastruttura specifico | No | `[DA CHIARIRE]` |
| Normativa di settore (NIS2, Difesa, Sanità) | No | `[DA CHIARIRE]` |

**Regola area trasversale** (vedi Step 7 della SKILL):
- In assenza di segnali espliciti → **1 riga singola senza padre**, complessità Bassa (4-5 GG/U)
- Struttura padre-figlio solo se il bando cita ≥ 2 capability distinte (es. GDPR + VAPT + hardening)

---

## Infrastruttura e DevOps

**Unità atomica**: capability infrastrutturale principale (ambienti, CI/CD, monitoring, backup/DR).

**Segnali di suddivisione**: ambienti multipli, requisiti HA/DR distinti, componenti infra separati.

**Dimensioni Colonna D**:
- Schermate: — (non applicabile)
- API: — (raramente applicabile)
- Dati: F — volumi storage, requisiti backup (RPO/RTO)
- Processi: O — pipeline CI/CD, monitoring, procedure DR

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Pipeline CI/CD base | Sempre (progetto nuovo) | `[stimato]` |
| 3 ambienti (sviluppo, collaudo, produzione) | Sempre (progetto nuovo) | `[stimato]` |
| Monitoring base (metriche, alert, log) | Sempre | `[stimato]` |
| Backup giornaliero DB | Sempre | `[stimato]` |
| Cloud provider | No | `[DA CHIARIRE]` |
| HA multi-zona | No | `[DA CHIARIRE]` |
| DR cross-region | No | `[DA CHIARIRE]` |
| RPO/RTO specifici | No | `[DA CHIARIRE]` |
| K8s / container orchestration | No (solo se esplicitato) | `[DA CHIARIRE]` |

**Regola area trasversale** (vedi Step 7 della SKILL):
- In assenza di segnali espliciti → **1 riga singola senza padre**, complessità Media (8-10 GG/U)
- Struttura padre-figlio solo se il bando cita ≥ 2 componenti distinti (es. K8s + CI/CD + monitoring separati con effort rilevante)

---

## Notifiche & Comunicazioni

**Unità atomica**: capability di notifica per canale distinto o per evento applicativo significativo.

**Segnali di suddivisione**: canali multipli (email, SMS, push, PEC), eventi diversi con template diversi.

**Dimensioni Colonna D**:
- Schermate: F — pannello gestione template
- API: O — API invio, storico, provider esterno
- Dati: F — entità Notifica, Template, Log invio
- Processi: O — trigger, gestione bounce/errori, tracciamento recapito

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Email come canale minimo | Sempre (se "notifica" citata) | `[stimato]` |
| Retry su errore di recapito | Sempre | nessuna |
| Log invii | Sempre | nessuna |
| Template base per evento | Sì | `[stimato]` |
| PEC istituzionale | No | `[DA CHIARIRE]` |
| SMS | No | `[DA CHIARIRE]` |
| Pannello gestione template (UI) | No | `[DA CHIARIRE]` |
| Gestione preferenze utente per canale | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- "Notifica" senza canale → assume **email** `[stimato]`, 1 riga singola
- Se ≥ 2 canali esplicitamente citati → crea padre + figli (una riga per canale)

---

## PMO e Governance

**Unità atomica**: pacchetto di governance distinto (SAL, piano di progetto, reporting, gestione rischi).

**Segnali di suddivisione**: stakeholder diversi con reporting diverso, milestone formali con deliverable distinti, più fornitori da coordinare.

**Dimensioni Colonna D**:
- Schermate: — (non applicabile)
- API: — (non applicabile)
- Dati: F — piano di progetto, registro rischi, verbali SAL
- Processi: O — cadenza SAL, modalità escalation, struttura governance

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| SAL periodici con cliente | Sempre (gara PA) | `[stimato]` |
| Piano di progetto (WBS, milestone) | Sempre | `[stimato]` |
| Registro rischi | Sempre | nessuna |
| Verbali condivisi | Sempre | nessuna |
| Cadenza SAL | Sì (mensile default) | `[stimato]` |
| Steering committee | No | `[DA CHIARIRE]` |
| PMO esterno | No | `[DA CHIARIRE]` |
| Più vendor da coordinare | No | `[DA CHIARIRE]` |
| Reporting direzionale separato | No | `[DA CHIARIRE]` |

**Regola area trasversale** (vedi Step 7 della SKILL):
- In assenza di segnali espliciti → **1 riga singola senza padre**, complessità Bassa (3-4 GG/U)
- Struttura padre-figlio solo se il bando cita ≥ 2 pacchetti con stakeholder e deliverable **esplicitamente distinti**

---

## Accessibilità

**Unità atomica**: perimetro di verifica o intervento accessibilità.

**Segnali di suddivisione**: perimetri applicativi separati, attività distinte (audit, fix, dichiarazione, test periodico).

**Dimensioni Colonna D**:
- Schermate: O — perimetro delle schermate da verificare
- API: — (non applicabile)
- Dati: — (non applicabile)
- Processi: O — audit WCAG 2.1 AA, fix componenti, dichiarazione AgID, test screen reader

**Regola di inferenza chiusa**:

| Componente | Inferibile? | Marcatura |
|---|---|---|
| Audit WCAG 2.1 AA (se AgID citato) | Sempre | nessuna |
| Dichiarazione accessibilità AgID | Sempre (se AgID o PA) | nessuna |
| Fix contrasto/focus/alt-text base | Sì | `[stimato]` |
| Numero schermate da verificare | Sì, con fallback | `[stimato]` |
| Test con screen reader (NVDA/JAWS) | Sì (se WCAG esplicito) | `[stimato]` |
| Retrofit su portale esistente | No | `[DA CHIARIRE]` |
| Componenti custom non conformi | No | `[DA CHIARIRE]` |
| Test periodico post-lancio | No | `[DA CHIARIRE]` |

**Regola quantitativa di fallback**:
- Schermate da verificare non specificate → assume **il numero di schermate del portale** (dalla stima frontend) `[stimato]`
- "Conformità WCAG" senza dettaglio → **1 riga singola**, complessità Bassa

**Regola area trasversale** (vedi Step 7 della SKILL):
- In assenza di segnali espliciti → **1 riga singola senza padre**, complessità Bassa (3-4 GG/U)
- Struttura padre-figlio solo se il bando cita ≥ 2 perimetri separati (es. portale pubblico + app mobile) o fasi distinte con effort rilevante

---

## Regola generale di inferenza

| Situazione | Azione |
|---|---|
| Il bando elenca componenti distinte (sistemi, profili, sezioni) | Crea una riga per componente — nessuna marcatura |
| Un componente è standard del dominio e sempre presente | Inseriscilo senza marcatura |
| Un componente è implicito ma dipende da scelte progettuali | Inseriscilo con `[stimato]` + assunzione in A&R |
| Non è possibile dedurre nulla dal testo | Scrivi `[DA CHIARIRE]` + assunzione o rischio in A&R |
| Il bando è contraddittorio o ambiguo | Scegli l'interpretazione più prudente, documenta in A&R |
| Il conteggio è assente ma l'area ha un fallback in questa guida | Usa il fallback + `[stimato]` |
