# Aree Funzionali

Usa questa reference per classificare i requisiti del documento di gara.

## Autenticazione & IAM

Include SSO, MFA, SPID, CIE, gestione ruoli, profilazione utenti, audit accessi, federazione identita.
Segnali tipici: `single sign-on`, `identity provider`, `RBAC`, `MFA`, `SPID`, `CIE`, `profilazione`, `ruoli`.

## Gestione Documentale

Include upload/download, fascicoli, metadata, workflow documentali, PEC, firma digitale, protocollazione, conservazione, ricerca full-text.
Segnali tipici: `documentale`, `ECM`, `firma`, `PEC`, `archiviazione`, `protocollo`, `conservazione`.

## Cruscotto Analytics

Include dashboard, KPI, reportistica operativa o direzionale, drill-down, cruscotti, BI, monitoraggio indicatori.
Segnali tipici: `dashboard`, `KPI`, `report`, `business intelligence`, `analytics`, `cruscotto`.

## Integrazione Sistemi Legacy

Include integrazioni con ERP, CRM, SAP, SOAP, middleware, ESB, API gateway, file exchange, batch, sincronizzazioni applicative.
Segnali tipici: `integrazione`, `legacy`, `SAP`, `SOAP`, `middleware`, `ESB`, `web service`, `flussi`.

## Notifiche & Comunicazioni

Include email, SMS, push, alert, PEC notifiche, reminder, template comunicazioni, canali multicanale.
Segnali tipici: `notifica`, `email`, `SMS`, `push`, `reminder`, `comunicazione`.

## Portale e Frontend

Include portali web, aree riservate, journey utente, form online, responsive, mobile web, CMS, componenti UX/UI.
Segnali tipici: `portale`, `frontend`, `interfaccia`, `responsive`, `schermate`, `ux`, `cms`.

## Migrazione Dati

Include ETL, bonifica, mapping, caricamento storico, conversione dati, data quality, deduplica, migrazione massiva.
Segnali tipici: `migrazione`, `ETL`, `data quality`, `storico`, `bonifica`, `deduplica`.

## Sicurezza e Compliance

Include GDPR, logging, audit trail, segregazione ruoli, crittografia, VAPT, hardening, requisiti AgID/CAD, compliance normativa.
Segnali tipici: `GDPR`, `audit`, `VAPT`, `hardening`, `compliance`, `AgID`, `CAD`, `sicurezza`.

## Infrastruttura e DevOps

Include cloud, ambienti, CI/CD, container, orchestrazione, monitoring, observability, deployment pipeline, backup e DR.
Segnali tipici: `cloud`, `container`, `kubernetes`, `CI/CD`, `monitoring`, `backup`, `disaster recovery`.

## Accessibilita

Include WCAG, usabilita assistita, conformita linee guida, verifiche accessibilita, test assistivi.
Segnali tipici: `WCAG`, `accessibilita`, `AgID`, `screen reader`, `contrasto`.

## PMO e Governance

Include SAL, reporting di avanzamento, steering committee, coordinamento fornitori, risk management, piani di progetto, governance.
Segnali tipici: `PMO`, `governance`, `SAL`, `steering`, `piano di progetto`, `coordina`.

## AI & Machine Learning

Include LLM, GenAI, RAG, fine-tuning, MLOps, chatbot AI, modelli predittivi, XAI, embeddings, vector database, AI governance, pipeline di re-training, valutazione modelli.
Segnali tipici: `LLM`, `GenAI`, `RAG`, `fine-tuning`, `MLOps`, `chatbot`, `modello`, `predittivo`, `intelligenza artificiale`, `machine learning`, `XAI`, `LIME`, `SHAP`, `AI Act`, `open source model`.
Nota: non usare `Cruscotto Analytics` per requisiti AI/ML anche se prevedono output visuali; l'effort dominante è su Data e BE, con natura tecnica completamente diversa dalla BI tradizionale.

## Mobile App

Include app native iOS/Android, framework cross-platform (React Native, Flutter), funzionalità device-native (fotocamera, GPS, biometria), offline mode, MDM, notifiche push mobile.
Segnali tipici: `app mobile`, `iOS`, `Android`, `native`, `React Native`, `Flutter`, `offline`, `MDM`, `biometria`, `applicazione mobile`.
Nota: non usare `Portale e Frontend` per app native; lo split e il modello di stima sono diversi. Se il bando prevede sia web responsive che app mobile, crea righe separate.

## API Management

Include progettazione ed esposizione di API REST, specifica OpenAPI, setup API gateway, developer portal, rate limiting, versioning API, autenticazione OAuth2/JWT, interoperabilità PDND/AGID ModI.
Segnali tipici: `API gateway`, `OpenAPI`, `PDND`, `developer portal`, `rate limiting`, `esposizione API`, `catalogo API`, `ModI`, `interoperabilita`.
Nota: distinto da `Integrazione Sistemi Legacy` che riguarda il consumo di API esterne; questa area copre la progettazione e pubblicazione di API proprie verso terzi.

## Regole di classificazione

- Se un requisito parla di una capability principale e di un vincolo accessorio, assegna l'area alla capability principale e annota il vincolo nelle note.
- Se un requisito contiene due capability indipendenti, dividilo in due righe.
- Se non trovi un match netto, scegli l'area che guida la maggior parte dell'effort implementativo.
- Per aree ad alta numerosita non usare una sola riga aggregata quando il bando elenca componenti distinte: integrazioni, schermate/feature frontend, KPI/report, workflow documentali, entita o dataset da migrare.
- Se il bando elenca sistemi o componenti differenti, considera ciascun elemento come potenziale unita stimabile.
- Quando possibile usa in colonna B il label esatto gia presente nel template Excel.
