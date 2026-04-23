# Segnali Trasversali di Complessità

Applica questi correttivi dopo avere scelto il range per area funzionale.

## Regola di utilizzo

- Non applicare correttivi in modo meccanico uno per uno; usali per motivare il posizionamento nel range.
- Se più correttivi sono contemporaneamente presenti, mantieni la stessa area funzionale ma spostati verso la parte alta della fascia.
- Se l'incertezza è elevata, aggiungi `[DA CHIARIRE]` nelle note e genera una assunzione o un rischio.
- Considera `Alta` come classe massima; non creare nuove classi. Se il caso è eccezionalmente oneroso, mantieni `Alta` e documenta l'extra effort.

> **Regola bando di gara**: un bando di gara è per definizione un documento ad alta ambiguità strutturale. In assenza di segnali espliciti di riduzione, il default è posizionarsi al centro-alto del range (non al centro-basso). Ogni area non descritta esplicitamente nel bando ma necessaria al progetto va stimata con complessità Media come floor minimo.

---

## Correttivi che tendono a spostare la stima verso l'alto

- Integrazione con sistema legacy o vendor esterno con documentazione incompleta
- Requisiti normativi specifici: GDPR, AgID, CAD, NIS2, audit formale, tracciabilità forte
- SLA stringenti: alta disponibilità, tempi risposta severi, finestre di manutenzione ridotte
- Volumi elevati: utenti, transazioni, documenti, storico, allegati pesanti
- Multi-tenant, multi-società o multi-dominio applicativo
- Più ambienti da coordinare o dipendenze infrastrutturali rilevanti
- Requisiti ambigui, incompleti o contraddittori
- Cut-over o milestone temporali non negoziabili
- Assenza di ambiente di test o sandbox del sistema target
- Team cliente non tecnico o con scarsa disponibilità per i chiarimenti

### Segnali specifici per AI & Machine Learning

- Fine-tuning su dati proprietari (vs. solo RAG o prompt engineering): l'effort Data aumenta significativamente
- Dataset di training con qualità incerta, bias potenziale o gap di copertura documentale
- Obbligo di spiegabilità (XAI): LIME, SHAP, audit AI o motivazione delle predizioni richiesta esplicitamente
- Compliance AI Act, NIST AI RMF, ISO/IEC 42001 o framework di AI governance formali
- Deployment on-premise, air-gapped o su infrastruttura certificata (es. PSN Difesa): esclude soluzioni cloud API-based
- MLOps continuativo: re-training periodico, model registry, drift detection, evaluation pipeline
- Più modelli o domini verticali distinti con knowledge base separate
- LLM open source senza support commerciale: effort aggiuntivo per fine-tuning, aggiornamento e gestione

### Segnali specifici per Mobile App

- Doppia piattaforma nativa (iOS + Android separati, non cross-platform): FE quasi raddoppia
- Funzionalità offline con sincronizzazione: aggiunge complessità BE e Data significativa
- Integrazione device nativa (fotocamera, GPS, NFC, biometria): richiede competenze specifiche e test su device reali
- MDM o gestione dispositivi aziendali: dipendenze con infrastruttura cliente

### Segnali specifici per API Management

- Conformità PDND / AGID ModI: pattern di sicurezza, firma JWT, e-service obbligatori
- Developer portal con onboarding esterno: effort FE e documentazione aggiuntivi
- Versioning multi-versione con backward compatibility: complessità BE cresce nel tempo
- Rate limiting e throttling per SLA contrattuali verso terzi: infra e monitoring aggiuntivi

---

## Correttivi che permettono di stare sul bordo basso

> Questi correttivi si applicano **solo se tutti presenti contemporaneamente**. La presenza anche di uno solo dei segnali di crescita sopra elencati annulla la riduzione.

- Standard già adottati dal cliente e documentati
- API già documentate, testate e con ambiente sandbox disponibile
- Stack tecnologico imposto ma già disponibile e configurato nel progetto
- Pattern implementativo noto e ripetibile (già fatto in progetti analoghi)
- Requisito ben delimitato e senza dipendenze forti
- LLM as-a-service già disponibile via API cloud senza fine-tuning (solo prompt engineering o RAG su knowledge base strutturata)
- RAG su knowledge base ben strutturata, già indicizzata e disponibile
- App mobile cross-platform (React Native/Flutter) con design system già definito
- API da esporre già implementate internamente, da sola pubblicare su gateway

---

## Checklist aree trasversali obbligatorie

Alla fine della decomposizione, prima di chiudere la stima, verifica che le seguenti aree siano presenti nel foglio Requirements. Se mancano righe per una di queste aree, aggiungile con la complessità indicata come **floor minimo**:

| Area | Floor minimo | Quando alzare |
|---|---|---|
| Sicurezza e Compliance | Bassa (4-5 GG/U) | Se il bando cita GDPR, audit, VAPT, dati sensibili → Media o Alta |
| Infrastruttura e DevOps | Media (8-10 GG/U) | Sempre per progetti nuovi; Alta se K8s, multi-env o HA/DR richiesti |
| Accessibilità | Bassa (3-4 GG/U) | Se il bando cita WCAG o AgID → Media; se retrofit su portale esteso → Alta |
| PMO e Governance | Bassa (3-4 GG/U) | Se bando PA con SAL formali → Media; se più vendor o steering → Alta |
| Testing (incluso nel Summary) | 10-15% del totale Build | 20% se VAPT, test accessibilità o UAT formale richiesti |

> Queste voci esistono in ogni progetto IT anche se il bando non le nomina esplicitamente. Non aggiungerle è la causa più frequente di sottostima sistematica.
