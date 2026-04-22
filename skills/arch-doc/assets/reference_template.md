# Template Architettura: [NOME SISTEMA]

<!-- 
  ISTRUZIONI PER L'UTENTE
  ========================
  Questo file è opzionale. Se lo compili PRIMA di invocare la skill arch-doc,
  la skill lo usa come punto di partenza rispettando i vincoli e le sezioni
  che hai già definito — senza inventare informazioni non presenti.

  Compila solo le sezioni che conosci. Lascia vuote le parti incerte.
  La skill segnalerà le lacune come [DA DEFINIRE] nel documento finale.

  Per usarlo:
  1. Copia questo file in <cartella-progetto>/assets/reference_template.md
  2. Compilalo con le informazioni che conosci
  3. Invoca la skill con "genera il documento di architettura"
-->

---

## Metadati

- **Nome Sistema:** [es. Sistema Gestione Pratiche - SGP]
- **Ente / Cliente:** [es. Comune di Roma - Dipartimento Servizi Digitali]
- **Versione documento:** 1.0
- **Autore:** [nome e cognome]
- **Data:** [gg/mm/aaaa]
- **Tipo applicazione:** [ ] webapp PA  [ ] gestionale interno  [ ] portale cittadino  [ ] piattaforma B2B

---

## Vincoli Architetturali

<!-- 
  Elencare i vincoli tecnici e organizzativi imposti (es. dalla governance IT,
  da contratti CONSIP, da normative AgID, da scelte già fatte).
  Questo evita che la skill proponga soluzioni incompatibili.
-->

- **Containerizzazione obbligatoria:** [ ] Docker Compose  [ ] Kubernetes  [ ] OpenShift  [ ] non definita
- **Cloud provider:** [ ] Azure  [ ] AWS  [ ] GCP  [ ] On-premise  [ ] Polo Strategico Nazionale (PSN)
- **Vincoli di sicurezza:** [es. "nessun dato fuori dal territorio UE", "log retention 90 giorni"]
- **Vincoli normativi:** [es. "GDPR", "CAD art. 64 (SPID obbligatorio)", "Linee Guida AgID sicurezza"]
- **Tecnologie imposte:** [es. "Java Spring Boot (standard aziendale)", "PostgreSQL only", "no servizi SaaS esterni"]
- **Altri vincoli:** 

---

## Microservizi Previsti

<!-- 
  Elencare i microservizi già identificati dall'analisi funzionale.
  Usa il naming convention: <ente>-<dominio>-service
  (es. sgp-utenti-service, sgp-pratiche-service)
-->

| Nome Microservizio | Responsabilità principale | Tecnologia (se nota) |
|-------------------|--------------------------|---------------------|
| [ms-nome-1-service] | [cosa fa] | [Spring Boot / Node.js / Python] |
| [ms-nome-2-service] | [cosa fa] | |
| [ms-nome-3-service] | [cosa fa] | |

---

## Servizi Infrastrutturali

<!-- Indica quali servizi infrastrutturali sono presenti o richiesti -->

| Servizio | Presente | Note |
|---------|---------|------|
| API Gateway | [ ] Sì  [ ] No  [ ] TBD | [es. "Kong", "Nginx", "Spring Cloud Gateway"] |
| Kafka (messaggistica async) | [ ] Sì  [ ] No  [ ] TBD | [topics principali se noti] |
| Redis (cache) | [ ] Sì  [ ] No  [ ] TBD | [use case: sessioni / data cache] |
| Object Storage | [ ] Sì  [ ] No  [ ] TBD | [es. "MinIO on-premise", "Azure Blob"] |
| Elasticsearch | [ ] Sì  [ ] No  [ ] TBD | |
| Altro | | |

---

## Servizi Esterni PA

<!-- Indicare le integrazioni con sistemi esterni PA -->

| Servizio Esterno | Integrazione richiesta | Note |
|----------------|----------------------|------|
| SPID / CIE | [ ] Sì  [ ] No  [ ] TBD | [livello SPID: L1/L2/L3] |
| PagoPA | [ ] Sì  [ ] No  [ ] TBD | [tipo pagamento: spontaneo / avvisi] |
| ANPR | [ ] Sì  [ ] No  [ ] TBD | |
| PDND / ModI | [ ] Sì  [ ] No  [ ] TBD | [e-service da consumare/erogare] |
| Altro | | |

---

## Modello di Autenticazione

<!-- Descrivere come si autenticano gli utenti del sistema -->

- **Tipo utenti:** [ ] Operatori interni  [ ] Cittadini  [ ] Entrambi  [ ] Solo API B2B
- **Meccanismo di autenticazione:** [ ] SPID  [ ] CIE  [ ] OIDC (KeyCloak)  [ ] Azure AD  [ ] Basic Auth  [ ] API Key  [ ] Non definito
- **Identity Provider:** [es. "KeyCloak on-premise", "SPID via Aruba / Poste / InfoCert"]
- **Tipo token:** [ ] JWT stateless  [ ] Token opaque (introspection)  [ ] Cookie sessione
- **Modello autorizzazione:** [ ] RBAC (ruoli)  [ ] ABAC (attributi)  [ ] Non definito
- **Ruoli applicativi noti:** [es. "ROLE_ADMIN, ROLE_OPERATORE, ROLE_VIEWER, ROLE_CITTADINO"]

---

## Processi Complessi

<!-- 
  Elencare i processi applicativi più complessi che richiedono un diagramma
  di sequenza nel documento (es. flussi multi-step, integrazioni esterne,
  transazioni Saga, ecc.).
-->

| Processo | Microservizi coinvolti | Breve descrizione |
|---------|----------------------|------------------|
| [es. Registrazione utente con SPID] | [ms-auth, ms-utenti] | [SPID auth → creazione account → notifica benvenuto] |
| [es. Upload e protocollazione documento] | [ms-documenti, ms-protocollo] | [upload → OCR → protocollazione → notifica] |
| | | |

---

## Sezioni Aggiuntive

<!-- 
  Se il documento richiede sezioni non standard (es. piano di migrazione,
  disaster recovery, SLA, piano di test), elencarle qui.
  La skill le aggiungerà dopo la sezione 6.
-->

- [ ] Disaster Recovery / Business Continuity
- [ ] SLA e metriche di sistema
- [ ] Piano di migrazione da sistema legacy
- [ ] Considerazioni di sicurezza (OWASP, GDPR)
- [ ] Piano di monitoring e alerting
- [ ] Altro: [specificare]

---

## Note Aggiuntive

<!-- 
  Qualsiasi informazione rilevante non catturata nelle sezioni precedenti.
  Es. contesto storico, decision log, riferimenti a documenti correlati.
-->

