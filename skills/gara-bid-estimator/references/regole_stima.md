# Regole di Stima per Area Funzionale

Usa questa reference per scegliere una baseline di effort. La complessita non assegna giorni in modo assoluto: posiziona il requisito all'interno del range dell'area funzionale.

## Autenticazione & IAM

- Bassa: `3-5` GG/U
- Media: `6-10` GG/U
- Alta: `10-16` GG/U
- Split tipico: FE `10-20%`, BE `70-85%`, Data `0-10%`
- Unita di misura: capability IAM principale
- Driver di crescita: multi-IdP, SPID/CIE, provisioning, audit forte, segregazione ruoli complessa

## Gestione Documentale

- Bassa: `4-6` GG/U
- Media: `7-12` GG/U
- Alta: `12-20` GG/U
- Split tipico: FE `20-30%`, BE `55-70%`, Data `10-20%`
- Unita di misura: workflow documentale o capability documentale significativa
- Driver di scala: numero di workflow, tipi documento, regole di metadatazione, repository coinvolti
- Regola: fino a `2` workflow puo stare in una riga; oltre `2`, separa per workflow o gruppo omogeneo e aggiungi una riga di governance documentale se necessario
- Driver di crescita: full-text, workflow approvativi, conservazione, protocollazione, ECM legacy

## Cruscotto Analytics

- Bassa: `4-7` GG/U
- Media: `8-14` GG/U
- Alta: `14-22` GG/U
- Split tipico: FE `25-40%`, BE `20-35%`, Data `30-45%`
- Unita di misura: dashboard o reporting pack omogeneo
- Driver di scala: numero di KPI, report, dimensioni di filtro, sorgenti dati
- Regola: fino a `1` dashboard semplice o `5` KPI puo stare in una riga; oltre questa soglia, separa per dashboard o cluster di KPI
- Driver di crescita: drill-down, storico lungo, KPI complessi, fonti dati multiple, data mart dedicato

## Integrazione Sistemi Legacy

- Bassa: `3-5` GG/U
- Media: `8-14` GG/U
- Alta: `15-25` GG/U
- Split tipico: FE `0-10%`, BE `60-80%`, Data `15-30%`
- Unita di misura: integrazione significativa verso un sistema distinto
- Driver di scala: numero di sistemi, numero di interfacce, numero di flussi, sincrono/asincrono, mapping per dominio
- Regola: fino a `2` integrazioni semplici puo avere senso una voce aggregata; da `3` in su, stima una riga per integrazione o per cluster omogeneo. Se le integrazioni sono piu di `3`, aggiungi una riga trasversale per orchestrazione, error handling o monitoraggio
- Driver di crescita: SAP/SOAP, documentazione parziale, mapping complesso, piu sistemi sorgente, batch sincroni e asincroni

## Notifiche & Comunicazioni

- Bassa: `2-4` GG/U
- Media: `5-8` GG/U
- Alta: `8-12` GG/U
- Split tipico: FE `10-20%`, BE `70-85%`, Data `0-10%`
- Unita di misura: capability di notifica o canale composito
- Driver di crescita: multicanale, template dinamici, regole evento, tracciamento recapiti, PEC integrata

## Portale e Frontend

- Bassa: `5-8` GG/U
- Media: `9-16` GG/U
- Alta: `16-28` GG/U
- Split tipico: FE `60-80%`, BE `15-30%`, Data `0-10%`
- Unita di misura: gruppo omogeneo di schermate o journey utente
- Driver di scala: numero schermate, complessita journey, componenti custom, varianti responsive
- Regola: fino a `5-7` schermate correlate puo stare in una riga; oltre, separa per journey, area funzionale o modulo
- Driver di crescita: molte schermate, journey articolati, CMS, responsive spinto, component library dedicata

## Migrazione Dati

- Bassa: `5-8` GG/U
- Media: `9-16` GG/U
- Alta: `16-30` GG/U
- Split tipico: FE `0-5%`, BE `20-35%`, Data `60-80%`
- Unita di misura: dominio dati o cluster di entita omogenee
- Driver di scala: numero di entita, volume record, qualita dati, regole di bonifica, storico
- Regola: fino a `2-3` entita o un dataset semplice puo stare in una riga; oltre, separa per dominio o cluster di tabelle e aggiungi una riga di cut-over o riconciliazione se necessaria
- Driver di crescita: alti volumi, bonifica, deduplica, storico pluriennale, finestre di cut-over rigide

## Sicurezza e Compliance

- Bassa: `3-5` GG/U
- Media: `6-10` GG/U
- Alta: `10-18` GG/U
- Split tipico: FE `0-10%`, BE `55-75%`, Data `10-20%`
- Unita di misura: capability di sicurezza o compliance
- Driver di crescita: audit trail esteso, cifratura, segregazione, VAPT certificato, norme specifiche di settore

## Infrastruttura e DevOps

- Bassa: `4-7` GG/U
- Media: `8-14` GG/U
- Alta: `15-24` GG/U
- Split tipico: FE `0-5%`, BE `30-45%`, Data `5-15%`
- Unita di misura: capability infrastrutturale principale
- Nota: la parte restante ricade tipicamente su effort infra o devops non riconducibile a FE/BE/Data puro; distribuiscila sul BE solo se il template non prevede una colonna dedicata
- Driver di crescita: multi-environment, container, IaC, monitoring, HA/DR, pipeline articolate

## Accessibilita

- Bassa: `3-4` GG/U
- Media: `5-8` GG/U
- Alta: `8-14` GG/U
- Split tipico: FE `70-90%`, BE `0-10%`, Data `0-5%`
- Unita di misura: perimetro di verifica o correzione accessibilita
- Driver di crescita: retrofit su portale esteso, componenti custom, correzioni cross-browser, test assistivi completi

## PMO e Governance

- Bassa: `2-4` GG/U
- Media: `5-8` GG/U
- Alta: `8-12` GG/U
- Split tipico: FE `0%`, BE `0-10%`, Data `0-5%`
- Unita di misura: pacchetto di governance
- Nota: se il template richiede solo FE/BE/Data, registra questi GG/U nel Summary e non gonfiare artificialmente i singoli requisiti
- Driver di crescita: molti stakeholder, piu vendor, reporting regolato, governance formale, milestone ravvicinate

## AI & Machine Learning

- Bassa: `8-12` GG/U
- Media: `15-25` GG/U
- Alta: `25-45` GG/U
- Split tipico: FE `5-15%`, BE `25-40%`, Data `45-65%`
- Unita di misura: capability AI distinta (es. chatbot, modello predittivo, pipeline RAG, dominio verticale)
- Driver di scala: numero di domini verticali, numero di modelli distinti, requisiti XAI, governance AI Act
- Regola: ogni dominio verticale o modello distinto è una riga; aggiungi una riga trasversale per MLOps/monitoring se il bando prevede pipeline di re-training, model registry o valutazione continuativa
- Driver di crescita: fine-tuning su dati proprietari, XAI obbligatorio, AI Act compliance, dataset di qualità incerta, deployment on-premise o air-gapped, GPU/infra specializzata, multi-modello

## Mobile App

- Bassa: `8-14` GG/U
- Media: `15-25` GG/U
- Alta: `25-40` GG/U
- Split tipico: FE `60-75%`, BE `20-30%`, Data `5-10%`
- Unita di misura: modulo funzionale o journey mobile omogeneo
- Driver di scala: numero di schermate, piattaforme richieste (iOS, Android, entrambe), funzionalità device-native
- Regola: se il bando richiede iOS e Android nativi separatamente, considera un correttivo FE fino al raddoppio; se cross-platform (React Native/Flutter), stima unitaria con correttivo di piattaforma ridotto (`+20-30%`)
- Driver di crescita: funzionalità offline, integrazione device (fotocamera, GPS, biometria, NFC), MDM, doppia piattaforma nativa, UX molto custom

## API Management

- Bassa: `3-6` GG/U
- Media: `7-12` GG/U
- Alta: `12-20` GG/U
- Split tipico: FE `5-10%`, BE `65-80%`, Data `10-20%`
- Unita di misura: API o gruppo omogeneo di API per dominio
- Driver di scala: numero di API da esporre, complessità dei contratti, livelli di autenticazione, versioning multi-versione
- Regola: fino a `3` API semplici può stare in una riga; da `4` in su, raggruppa per dominio o servizio e aggiungi una riga separata per API gateway e developer portal se previsti
- Driver di crescita: PDND/AGID ModI, autenticazione OAuth2/JWT complessa, developer portal, rate limiting avanzato, SLA per API, conformità a standard interoperabilità PA

## Regole di posizionamento nel range

- Usa il bordo basso del range quando il requisito e standard, ben specificato e con pochi vincoli.
- Usa il centro del range quando c'e configurazione significativa o una singola integrazione.
- Usa il bordo alto del range quando ci sono legacy, vincoli normativi, volumi elevati, piu dipendenze o forte incertezza.
- Se il requisito supera in modo netto la fascia `Alta`, mantieni `Alta` ma spiega nelle note perche superi la baseline dell'area.
- Per le aree con driver di scala, la numerosita non alza da sola la complessita unitaria: aumenta il numero di unita da stimare o richiede una riga trasversale aggiuntiva.
