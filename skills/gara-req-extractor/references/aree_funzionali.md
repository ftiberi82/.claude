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

## Segnali per `categoria_scope` (schema v2.0) — riconoscere quando NON è custom software

Default: `custom_software`. Cambia solo se uno dei segnali sotto è presente.

### Segnali per `cots_product` (prodotto commerciale già in possesso o da acquistare)

- Bando cita nome esatto di un prodotto SaaS/commerciale: `SAP S/4HANA`, `Salesforce`, `ServiceNow`, `Microsoft 365`, `Dynamics 365`, `Power BI`, `Tableau`, `Qlik`, `Oracle EBS`, `SharePoint`, `Confluence`, `Jira`, `Workday`, `SAS`, `Adobe Experience Manager`.
- Frasi tipo: `"utilizzo del prodotto X già in possesso"`, `"licenze X fornite dal cliente"`, `"piattaforma X come abilitatore"`, `"configurazione del prodotto X"`.
- Per area **Cruscotto Analytics**: se il bando cita `Power BI` o `Tableau` come strumento e non un sviluppo custom di BI → `cots_product`. Lo sviluppo di report custom su quei tool resta `custom_software` (consulenza/configurazione).
- Per area **Gestione Documentale**: se cita `SharePoint`, `Alfresco`, `Documentum`, `OnBase`, `OpenText` come piattaforma da configurare → `cots_product`.

### Segnali per `service_external` (API/servizio di terzi con cui il custom interagisce)

- Bando cita servizi nazionali italiani: `SPID`, `CIE`, `PagoPA`, `ANPR`, `ANAC`, `AgID ModI`, `PDND`, `AppIO`.
- Bando cita servizi cloud-as-a-service: `Google Maps API`, `Stripe`, `Twilio`, `SendGrid`, `OpenAI API`, `Auth0`, `Okta`, `Azure AD (come IdP esistente)`, `Azure OpenAI`.
- Per area **Autenticazione & IAM**: se il bando dice `"il sistema deve autenticarsi via SPID/CIE"` o `"integrazione con l'IdP aziendale Azure AD"` → l'autenticazione *come servizio* è `service_external`. La parte di integrazione custom (handler OAuth/SAML lato applicazione) resta `custom_software`, va estratto come riga separata.
- Per area **Notifiche & Comunicazioni**: se cita `SendGrid`, `Mailgun`, `Twilio` come servizio di delivery → `service_external` (il costo del servizio è out-of-scope custom). Il wrapper applicativo resta `custom_software`.
- Per area **Pagamenti**: `PagoPA`, `Stripe`, `Nexi` come gateway → `service_external`.

### Segnali per `out_of_scope` (citato ma fuori responsabilità del fornitore)

- Frasi tipo: `"a carico del cliente"`, `"fornito da altro fornitore"`, `"infrastruttura già esistente fuori scope"`, `"hardware fornito dalla SA"`, `"connettività di rete a carico di terzi"`.
- Per area **Infrastruttura e DevOps**: se il bando dice `"l'infrastruttura cloud AWS è già attiva e configurata, il fornitore eredita gli ambienti"` → l'infrastruttura è `out_of_scope`, il setup CI/CD applicativo resta `custom_software`.
- Migrazione dati: se il dump è `"fornito dal cliente in formato CSV pronto"` → l'ETL resta `custom_software` ma la *bonifica dati* a monte può essere `out_of_scope`.

### Regola operativa per requisiti ibridi

Molti requisiti combinano servizio esterno + sviluppo custom (es. "autenticazione SPID" = SPID `service_external` + handler applicativo `custom_software`). In questi casi, **dividi in due righe**:

1. Riga 1: `categoria_scope: service_external` con `nome_prodotto: SPID`, GG/U a 0 (sarà filtrato dal bid-estimator nello sheet COTS), descrive la dipendenza esterna.
2. Riga 2: `categoria_scope: custom_software`, descrive l'integration layer custom (handler SAML, callback URL, gestione sessione) → stimabile in GG/U.

Annota la coppia nel campo `rationale_requisito` di entrambe le righe (es. "Coppia con REQ-NNN per integration layer custom").
