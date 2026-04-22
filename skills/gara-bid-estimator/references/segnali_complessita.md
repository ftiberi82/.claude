# Segnali Trasversali di Complessita

Applica questi correttivi dopo avere scelto il range per area funzionale.

## Correttivi che tendono a spostare la stima verso l'alto

- Integrazione con sistema legacy o vendor esterno con documentazione incompleta
- Requisiti normativi specifici: GDPR, AgID, CAD, audit formale, tracciabilita forte
- SLA stringenti: alta disponibilita, tempi risposta severi, finestre di manutenzione ridotte
- Volumi elevati: utenti, transazioni, documenti, storico, allegati pesanti
- Multi-tenant, multi-societa o multi-dominio applicativo
- Piu ambienti da coordinare o dipendenze infrastrutturali rilevanti
- Requisiti ambigui, incompleti o contraddittori
- Cut-over o milestone temporali non negoziabili

### Segnali specifici per AI & Machine Learning

- Fine-tuning su dati proprietari (vs. solo RAG o prompt engineering): l'effort Data aumenta significativamente
- Dataset di training con qualita incerta, bias potenziale o gap di copertura documentale
- Obbligo di spiegabilita (XAI): LIME, SHAP, audit AI o motivazione delle predizioni richiesta esplicitamente
- Compliance AI Act, NIST AI RMF, ISO/IEC 42001 o framework di AI governance formali
- Deployment on-premise, air-gapped o su infrastruttura certificata (es. PSN Difesa): esclude soluzioni cloud API-based
- MLOps continuativo: re-training periodico, model registry, drift detection, evaluation pipeline
- Piu modelli o domini verticali distinti con knowledge base separate
- LLM open source senza support commerciale: effort aggiuntivo per fine-tuning, aggiornamento e gestione

### Segnali specifici per Mobile App

- Doppia piattaforma nativa (iOS + Android separati, non cross-platform): FE quasi raddoppia
- Funzionalita offline con sincronizzazione: aggiunge complessita BE e Data significativa
- Integrazione device nativa (fotocamera, GPS, NFC, biometria): richiede competenze specifiche e test su device reali
- MDM o gestione dispositivi aziendali: dipendenze con infrastruttura cliente

### Segnali specifici per API Management

- Conformita PDND / AGID ModI: pattern di sicurezza, firma JWT, e-service obbligatori
- Developer portal con onboarding esterno: effort FE e documentazione aggiuntivi
- Versioning multi-versione con backward compatibility: complessita BE cresce nel tempo
- Rate limiting e throttling per SLA contrattuali verso terzi: infra e monitoring aggiuntivi

## Correttivi che permettono di stare sul bordo basso

- Standard gia adottati dal cliente
- API gia documentate e testate
- Stack tecnologico imposto ma gia disponibile
- Pattern implementativo noto e ripetibile
- Requisito ben delimitato e senza dipendenze forti
- LLM as-a-service gia disponibile via API cloud senza fine-tuning (solo prompt engineering o RAG su knowledge base strutturata)
- RAG su knowledge base ben strutturata, gia indicizzata e disponibile
- App mobile cross-platform (React Native/Flutter) con design system gia definito
- API da esporre gia implementate internamente, da sola pubblicare su gateway

## Regole di utilizzo

- Non applicare correttivi in modo meccanico uno per uno; usali per motivare il posizionamento nel range.
- Se piu correttivi sono contemporaneamente presenti, mantieni la stessa area funzionale ma spostati verso la parte alta della fascia.
- Se l'incertezza e elevata, aggiungi `[DA CHIARIRE]` nelle note e genera una assunzione o un rischio.
- Considera `Alta` come classe massima; non creare nuove classi. Se il caso e eccezionalmente oneroso, mantieni `Alta` e documenta l'extra effort.
