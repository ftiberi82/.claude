# Criteri di Qualità — Documento Funzionale

Questo file configura i criteri su cui viene valutato ogni documento funzionale.
Per modificare la valutazione, aggiungi/rimuovi criteri o modifica le istruzioni.
I pesi nella tabella in fondo determinano lo Score Globale.

---

## 1. Assenza di Ambiguità

**Cosa cercare:** Frasi vaghe, termini non definiti, condizionali senza risoluzione ("potrebbe", "di solito", "in alcuni casi", "opportunamente"), comportamenti non deterministici o lasciati all'interpretazione dello sviluppatore.

**Esempi di problema:**
- "Il sistema gestirà gli errori in modo opportuno" → cosa significa "opportuno"?
- "Gli utenti autorizzati possono accedere" → chi sono esattamente gli utenti autorizzati?
- "Il dato viene validato" → quali regole di validazione? Cosa succede se fallisce?

**Score alto (>80):** Ogni comportamento descritto è preciso e non lascia spazio a interpretazioni. I termini usati hanno un significato univoco nel contesto.

---

## 2. Completezza dei Flussi Applicativi

**Cosa cercare:** Per ogni funzionalità descritta devono essere presenti:
- Flusso principale (happy path)
- Flussi alternativi (scelte o percorsi diversi dell'utente)
- Casi di errore e come vengono gestiti
- Precondizioni (cosa deve essere vero prima che il flusso parta)
- Postcondizioni (stato del sistema dopo il completamento)

**Esempi di problema:**
- Il flusso di login descrive solo il caso di successo, senza dire cosa accade dopo 3 tentativi falliti.
- Una funzione di ricerca non specifica cosa mostrare se non ci sono risultati.
- Un flusso di approvazione non indica cosa succede se l'approvatore è assente.

**Score alto (>80):** Tutti i flussi principali sono descritti end-to-end, senza salti logici o passaggi impliciti. I casi limite più probabili sono coperti.

---

## 3. Ruoli, Utenti e Profili di Accesso

**Cosa cercare:**
- Elenco completo dei profili utente (es. amministratore, operatore, cittadino, supervisore, back-office)
- Per ogni funzionalità o schermata: quali profili possono accedervi
- Distinzione tra permessi di visualizzazione, creazione, modifica, cancellazione
- Regole di visibilità dei dati per profilo (es. un operatore vede solo i propri record)
- Eventuali gerarchie o deleghe tra ruoli

**Esempi di problema:**
- "Solo gli utenti abilitati possono modificare" → chi sono gli utenti abilitati? Come si abilitano?
- La funzione X è descritta senza indicare quale profilo la usa.
- Non è chiaro se un supervisore ha gli stessi permessi di un amministratore o un sottoinsieme.

**Score alto (>80):** Ogni funzionalità ha indicato il/i profilo/i che possono usarla, con distinzione chiara tra permessi di lettura e scrittura.

---

## 4. Gestione Errori e Casi Limite

**Cosa cercare:**
- Comportamento in caso di input errati o mancanti (validazioni lato client e server)
- Cosa mostrare all'utente in caso di errore (messaggio o almeno una descrizione)
- Comportamento in caso di timeout o indisponibilità di sistemi esterni
- Limiti operativi documentati (dimensione massima file upload, numero massimo di elementi in lista, lunghezza massima campi)
- Gestione della sessione scaduta durante un'operazione

**Score alto (>80):** I principali casi di errore sono documentati con comportamento atteso e feedback all'utente. I limiti operativi rilevanti sono esplicitati.

---

## 5. Integrazioni con Sistemi Esterni

**Cosa cercare:**
- Elenco di tutti i sistemi con cui l'applicazione si integra (es. anagrafe, PEC, SPID, sistemi di pagamento, CRM)
- Direzione del flusso dati: chi chiama chi, con quale frequenza
- Dati scambiati (anche solo concettualmente: "invia codice fiscale, riceve dati anagrafici")
- Comportamento funzionale in caso di indisponibilità del sistema esterno
- Eventuali requisiti di autenticazione o sicurezza per le integrazioni

**Esempi di problema:**
- "L'applicazione si integra con il sistema di autenticazione regionale" → tramite quale protocollo? SPID? CIE? Cosa succede se non è raggiungibile?
- Viene menzionato un invio di notifica email senza specificare chi gestisce il servizio mail.

**Score alto (>80):** Tutte le integrazioni sono nominate e descritte almeno a livello funzionale, con indicazione del comportamento in caso di errore.

---

## 6. Glossario e Termini di Business

**Cosa cercare:**
- Termini specifici del dominio che potrebbero avere significati diversi per developer e stakeholder (es. "pratica", "fascicolo", "posizione", "atto", "istanza")
- Acronimi usati senza definizione
- Concetti di business dati per scontati ma non universali

**Score alto (>80):** I termini chiave del dominio sono definiti esplicitamente, oppure il loro significato è inequivocabile dal contesto per chiunque lavori al progetto.

---

## 7. Tracciabilità dei Requisiti

**Cosa cercare:**
- I requisiti sono identificati con codici univoci (es. REQ-001, UC-003, FUN-012)?
- Ogni funzionalità è referenziabile?
- Ci sono riferimenti a normative, leggi o standard da rispettare (es. CAD, GDPR, WCAG)?
- Sono presenti priorità o classificazioni (es. must/should/could)?

**Score alto (>80):** I requisiti sono numerati e referenziabili, il che permette di tracciare ogni decisione di implementazione a un requisito preciso.

---

## 8. Struttura Dati e Specifiche dei Campi

**Cosa cercare:**
- **Tipo di modello dati**: è specificato se il modello è relazionale (tabelle, FK) o non relazionale (documenti JSON, key-value, grafo)? È motivata la scelta?
- **Entità / Tabelle**: sono identificate e nominate esplicitamente tutte le entità principali del dominio?
- **Campi per entità**: per ogni campo sono specificati nome, tipo dato (String, Integer, Boolean, Date, DateTime, Decimal, Enum, UUID, BLOB), e formato (es. yyyy-MM-dd per date, 2 decimali per importi)?
- **Vincoli di campo**: nullable/obbligatorio, lunghezza minima e massima per le stringhe, range min/max per i numerici, pattern/regex (es. codice fiscale = 16 caratteri alfanumerici), valori ammessi per gli enum?
- **Relazioni tra entità**: sono documentate con tipo (1-a-1, 1-a-molti, molti-a-molti) e cardinalità? Le FK sono esplicitate?
- **Chiavi primarie**: ogni entità ha una PK documentata (surrogate key, natural key, chiave composta)?
- **Valori di default**: sono documentati i valori di default per i campi che ne hanno?
- **Regole di business sui dati**: es. "data fine ≥ data inizio", "importo > 0", "almeno un recapito obbligatorio"?

**Esempi di problema:**
- "La pratica ha un numero identificativo" → che tipo? Numerico auto-increment? UUID? Formato specifico (es. ANNO-NNNN)?
- "Il sistema memorizza i dati dell'utente" → quali campi? Obbligatori? Lunghezza massima del nome?
- "La data di scadenza non può essere nel passato" → questa è una regola di business, ma manca la specifica del campo (tipo Date vs DateTime, formato, nullable).
- Le relazioni tra "pratica" e "allegati" non indicano la cardinalità (una pratica può avere 0 o più allegati?).

**Score alto (>80):** Le principali entità del dominio sono nominate, i campi chiave hanno tipo e vincoli documentati, le relazioni tra entità sono descritte con cardinalità, e le regole di business sui dati sono esplicitate.

---

## Configurazione Pesi

Modifica i pesi per adattare lo Score Globale alle priorità del progetto. I valori devono sommare a 100.

| Criterio | Peso |
|----------|------|
| Assenza di Ambiguità | 15 |
| Completezza dei Flussi | 20 |
| Ruoli, Utenti e Profili | 15 |
| Gestione Errori e Casi Limite | 15 |
| Integrazioni con Sistemi Esterni | 10 |
| Glossario e Termini di Business | 5 |
| Tracciabilità dei Requisiti | 5 |
| Struttura Dati e Specifiche dei Campi | 15 |
