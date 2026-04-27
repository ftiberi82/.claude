# Regole di Stima per Area Funzionale

> **Nota per questa versione**: questa reference è usata da `gara-bid-estimator-v3`, che riceve in input un file `requisiti_estratti.json` già validato. I requisiti sono già decompositi e classificati. Il compito di questa skill è **solo assegnare i GG/U** seguendo queste regole, senza ridecomporsi o modificare la struttura dei requisiti ricevuti.
>
> **Regola di fedeltà all'input**: se il JSON contiene un requisito con `inferenza: da_chiarire`, assegna i GG/U usando la fascia media dell'area come placeholder e segnalalo nelle note. Non rimuovere, unire o rinominare requisiti ricevuti.

Usa questa reference per scegliere una baseline di effort. La complessità non assegna giorni in modo assoluto: posiziona il requisito all'interno del range dell'area funzionale.

## Regola generale di posizionamento nel range

> **Parti sempre dal centro del range come punto di partenza.**
> Scendi al bordo basso **solo se tutti i seguenti segnali di riduzione sono presenti contemporaneamente**: requisito ben delimitato, nessuna dipendenza esterna, stack tecnologico già adottato dal cliente, pattern implementativo noto e ripetibile.
> Sali al bordo alto **se anche un solo segnale di crescita è presente**: legacy, normativa, SLA stringenti, ambiguità, volumi elevati, dipendenze esterne.
> Se il requisito supera in modo netto la fascia Alta, mantieni Alta ma spiega nelle note il delta e quantificalo.

---

## Autenticazione & IAM

- Bassa: `3-5` GG/U
- Media: `6-10` GG/U
- Alta: `10-16` GG/U
- **Centro di default: `8` GG/U**
- Split tipico: FE `10-20%`, BE `70-85%`, Data `0-10%`
- Unità di misura: capability IAM principale
- Driver di crescita (→ bordo alto): multi-IdP, SPID/CIE, provisioning, audit forte, segregazione ruoli complessa, IdP esterno con documentazione parziale
- Driver di riduzione (→ bordo basso): login standard con un solo IdP già documentato, nessun requisito di audit o provisioning

## Gestione Documentale

- Bassa: `4-6` GG/U
- Media: `7-12` GG/U
- Alta: `12-20` GG/U
- **Centro di default: `9` GG/U**
- Split tipico: FE `20-30%`, BE `55-70%`, Data `10-20%`
- Unità di misura: workflow documentale o capability documentale significativa
- Driver di scala: numero di workflow, tipi documento, regole di metadatazione, repository coinvolti
- Regola: fino a `2` workflow può stare in una riga; oltre `2`, separa per workflow o gruppo omogeneo e aggiungi una riga di governance documentale se necessario
- Driver di crescita (→ bordo alto): full-text, workflow approvativi, conservazione a norma, protocollazione, ECM legacy, firma digitale qualificata
- Driver di riduzione (→ bordo basso): upload/download semplice senza workflow approvativo, repository standard già configurato

## Cruscotto Analytics

- Bassa: `4-7` GG/U
- Media: `8-14` GG/U
- Alta: `14-22` GG/U
- **Centro di default: `11` GG/U**
- Split tipico: FE `25-40%`, BE `20-35%`, Data `30-45%`
- Unità di misura: dashboard o reporting pack omogeneo
- Driver di scala: numero di KPI, report, dimensioni di filtro, sorgenti dati
- Regola: fino a `1` dashboard semplice o `5` KPI può stare in una riga; oltre questa soglia, separa per dashboard o cluster di KPI
- Driver di crescita (→ bordo alto): drill-down, storico lungo, KPI complessi, fonti dati multiple, data mart dedicato, export formali
- Driver di riduzione (→ bordo basso): KPI già calcolati disponibili via API, nessun drill-down, sorgente dati unica

## Integrazione Sistemi Legacy

- Bassa: `3-5` GG/U
- Media: `8-14` GG/U
- Alta: `15-25` GG/U
- **Centro di default: `11` GG/U**
- Split tipico: FE `0-10%`, BE `60-80%`, Data `15-30%`
- Unità di misura: integrazione significativa verso un sistema distinto
- Driver di scala: numero di sistemi, numero di interfacce, numero di flussi, sincrono/asincrono, mapping per dominio
- Regola: fino a `2` integrazioni semplici può avere senso una voce aggregata; da `3` in su, stima una riga per integrazione o per cluster omogeneo. Se le integrazioni sono più di `3`, aggiungi una riga trasversale per orchestrazione, error handling o monitoraggio
- Driver di crescita (→ bordo alto): SAP/SOAP, documentazione incompleta, mapping complesso, più sistemi sorgente, batch sincroni e asincroni, assenza di ambiente di test del sistema target
- Driver di riduzione (→ bordo basso): API già documentate e testate, REST standard, ambiente di test disponibile, mapping semplice

## Notifiche & Comunicazioni

- Bassa: `2-4` GG/U
- Media: `5-8` GG/U
- Alta: `8-12` GG/U
- **Centro di default: `6` GG/U**
- Split tipico: FE `10-20%`, BE `70-85%`, Data `0-10%`
- Unità di misura: capability di notifica o canale composito
- Driver di crescita (→ bordo alto): multicanale, template dinamici, regole evento complesse, tracciamento recapiti, PEC integrata, gestione bounce e retry
- Driver di riduzione (→ bordo basso): canale singolo (solo email), template statici, provider già configurato

## Portale e Frontend

- Bassa: `5-8` GG/U
- Media: `9-16` GG/U
- Alta: `16-28` GG/U
- **Centro di default: `12` GG/U**
- Split tipico: FE `60-80%`, BE `15-30%`, Data `0-10%`
- Unità di misura: gruppo omogeneo di schermate o journey utente
- Driver di scala: numero schermate, complessità journey, componenti custom, varianti responsive
- Regola: fino a `5-7` schermate correlate può stare in una riga; oltre, separa per journey, area funzionale o modulo
- Driver di crescita (→ bordo alto): molte schermate, journey articolati con stati, CMS, responsive spinto, component library dedicata, molti ruoli/profili distinti
- Driver di riduzione (→ bordo basso): design system già definito, schermate semplici (lista + dettaglio), nessun componente custom

## Migrazione Dati

- Bassa: `5-8` GG/U
- Media: `9-16` GG/U
- Alta: `16-30` GG/U
- **Centro di default: `12` GG/U**
- Split tipico: FE `0-5%`, BE `20-35%`, Data `60-80%`
- Unità di misura: dominio dati o cluster di entità omogenee
- Driver di scala: numero di entità, volume record, qualità dati, regole di bonifica, storico
- Regola: fino a `2-3` entità o un dataset semplice può stare in una riga; oltre, separa per dominio o cluster di tabelle e aggiungi una riga di cut-over o riconciliazione se necessaria
- Driver di crescita (→ bordo alto): alti volumi (>100k record), bonifica e deduplica, storico pluriennale, finestre di cut-over rigide, qualità dati incerta
- Driver di riduzione (→ bordo basso): dataset piccolo e pulito, mapping diretto senza trasformazioni, nessun requisito di storico

## Sicurezza e Compliance

- Bassa: `3-5` GG/U
- Media: `6-10` GG/U
- Alta: `10-18` GG/U
- **Centro di default: `8` GG/U**
- Split tipico: FE `0-10%`, BE `55-75%`, Data `10-20%`
- Unità di misura: capability di sicurezza o compliance
- Driver di crescita (→ bordo alto): audit trail esteso, cifratura dati sensibili, segregazione ambienti, VAPT certificato, norme specifiche di settore (Difesa, Sanità, PA critica), NIS2
- Driver di riduzione (→ bordo basso): GDPR di base su dati non sensibili, logging standard, nessun VAPT formale richiesto

## Infrastruttura e DevOps

- Bassa: `4-7` GG/U
- Media: `8-14` GG/U
- Alta: `15-24` GG/U
- **Centro di default: `11` GG/U**
- Split tipico: FE `0-5%`, BE `30-45%`, Data `5-15%`
- Unità di misura: capability infrastrutturale principale
- Nota: la parte restante ricade tipicamente su effort infra o devops non riconducibile a FE/BE/Data puro; distribuiscila sul BE solo se il template non prevede una colonna dedicata
- Driver di crescita (→ bordo alto): multi-environment, container K8s, IaC, monitoring avanzato, HA/DR cross-region, pipeline complesse, vincoli cloud provider imposti
- Driver di riduzione (→ bordo basso): infrastruttura già esistente da riutilizzare, deployment semplice, un solo ambiente

## Accessibilità

- Bassa: `3-4` GG/U
- Media: `5-8` GG/U
- Alta: `8-14` GG/U
- **Centro di default: `6` GG/U**
- Split tipico: FE `70-90%`, BE `0-10%`, Data `0-5%`
- Unità di misura: perimetro di verifica o correzione accessibilità
- Driver di crescita (→ bordo alto): retrofit su portale esteso, componenti custom non conformi, correzioni cross-browser, test assistivi completi con strumenti certificati, dichiarazione formale AgID
- Driver di riduzione (→ bordo basso): portale nuovo con design system conforme, perimetro limitato, nessun componente custom

## PMO e Governance

- Bassa: `2-4` GG/U
- Media: `5-8` GG/U
- Alta: `8-12` GG/U
- **Centro di default: `6` GG/U**
- Split tipico: FE `0%`, BE `0-10%`, Data `0-5%`
- Unità di misura: pacchetto di governance
- Nota: se il template richiede solo FE/BE/Data, registra questi GG/U nel Summary e non gonfiare artificialmente i singoli requisiali
- Driver di crescita (→ bordo alto): molti stakeholder, più vendor, reporting regolato, governance formale, milestone ravvicinate, SAL frequenti
- Driver di riduzione (→ bordo basso): governance leggera, un solo stakeholder, nessun requisito formale di reporting

## AI & Machine Learning

- Bassa: `8-12` GG/U
- Media: `15-25` GG/U
- Alta: `25-45` GG/U
- **Centro di default: `20` GG/U**
- Split tipico: FE `5-15%`, BE `25-40%`, Data `45-65%`
- Unità di misura: capability AI distinta (es. chatbot, modello predittivo, pipeline RAG, dominio verticale)
- Driver di scala: numero di domini verticali, numero di modelli distinti, requisiti XAI, governance AI Act
- Regola: ogni dominio verticale o modello distinto è una riga; aggiungi una riga trasversale per MLOps/monitoring se il bando prevede pipeline di re-training, model registry o valutazione continuativa
- Driver di crescita (→ bordo alto): fine-tuning su dati proprietari, XAI obbligatorio, AI Act compliance, dataset di qualità incerta, deployment on-premise o air-gapped, GPU/infra specializzata, multi-modello, knowledge base non strutturata
- Driver di riduzione (→ bordo basso): LLM as-a-service via API cloud, RAG su knowledge base già strutturata e disponibile, nessun fine-tuning

## Mobile App

- Bassa: `8-14` GG/U
- Media: `15-25` GG/U
- Alta: `25-40` GG/U
- **Centro di default: `20` GG/U**
- Split tipico: FE `60-75%`, BE `20-30%`, Data `5-10%`
- Unità di misura: modulo funzionale o journey mobile omogeneo
- Driver di scala: numero di schermate, piattaforme richieste (iOS, Android, entrambe), funzionalità device-native
- Regola: se il bando richiede iOS e Android nativi separatamente, considera un correttivo FE fino al raddoppio; se cross-platform (React Native/Flutter), stima unitaria con correttivo di piattaforma ridotto (`+20-30%`)
- Driver di crescita (→ bordo alto): funzionalità offline, integrazione device (fotocamera, GPS, biometria, NFC), MDM, doppia piattaforma nativa, UX molto custom
- Driver di riduzione (→ bordo basso): app cross-platform con design system già definito, nessuna funzionalità device-native, solo lettura dati

## API Management

- Bassa: `3-6` GG/U
- Media: `7-12` GG/U
- Alta: `12-20` GG/U
- **Centro di default: `9` GG/U**
- Split tipico: FE `5-10%`, BE `65-80%`, Data `10-20%`
- Unità di misura: API o gruppo omogeneo di API per dominio
- Driver di scala: numero di API da esporre, complessità dei contratti, livelli di autenticazione, versioning multi-versione
- Regola: fino a `3` API semplici può stare in una riga; da `4` in su, raggruppa per dominio o servizio e aggiungi una riga separata per API gateway e developer portal se previsti
- Driver di crescita (→ bordo alto): PDND/AGID ModI, autenticazione OAuth2/JWT complessa, developer portal, rate limiting avanzato, SLA per API, conformità a standard interoperabilità PA
- Driver di riduzione (→ bordo basso): API interne già implementate da sola pubblicare su gateway esistente, nessun developer portal

---

## Regola contingency (da applicare nel foglio Summary)

Applica sempre il contingency **dopo aver totalizzato i GG/U dei requisiti**. Non è opzionale.

| Scenario | Contingency minimo |
|---|---|
| Documento funzionale dettagliato (SRS, analisi), stack noto, nessuna integrazione legacy | **15%** |
| Bando di gara con specifiche incomplete, almeno 1 integrazione o area ambigua | **20%** |
| Bando con ≥ 2 segnali di complessità trasversali (legacy + normativa, AI + compliance, migrazione + SLA) | **25%** |
| Bando con requisiti contraddittori, sistemi legacy non documentati, o aree [DA CHIARIRE] significative | **30%** |

> Il contingency copre: requisiti emersi in fase di analisi, variazioni di scope concordate, attività di coordinamento non stimate, imprevisti tecnici su sistemi terzi.
> Non ridurre il contingency per "ottimismo contrattuale": sottostimare oggi genera extra-budget non approvato in esecuzione.
