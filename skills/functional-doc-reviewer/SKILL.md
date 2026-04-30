---
name: functional-doc-reviewer
description: Analizza documenti funzionali (.docx, .pdf) presenti nella cartella documents/ e valuta la loro qualità per applicazioni web PA, sistemi gestionali e portali clienti. Usa questa skill ogni volta che l'utente chiede di revisionare, analizzare o valutare un documento funzionale, verificare la qualità di requisiti applicativi, controllare le specifiche di un progetto, trovare ambiguità o lacune in un'analisi, capire come strutturare il data model, verificare le specifiche tecniche dei campi, i vincoli, i tipi o le relazioni tra entità. Triggera anche su frasi come "controlla il funzionale", "analizza i requisiti", "rivedi le specifiche", "verifica il documento", "c'è qualcosa da chiarire nel documento", "quanto è completo il documento", "rivedi l'analisi funzionale", "struttura dati", "data model", "campi e vincoli", "specifica tecnica dei campi".
---

## Obiettivo

Leggere un documento funzionale (analisi, specifiche, requisiti) e produrre un **file XLS di revisione** salvato nella cartella `documents/`, strutturato su un template predefinito che contiene:

1. Uno **score 0–100 per ogni criterio di qualità**
2. Un **elenco strutturato di domande e chiarimenti** per criterio, pronti per essere lavorati insieme al documento funzionale

Il documento tipicamente riguarda applicazioni web per la PA, sistemi gestionali o portali clienti.

## Criteri di qualità

Leggi `references/quality-criteria.md` (relativo alla directory della skill) per la lista completa dei criteri, le istruzioni di valutazione e i pesi per lo Score Globale.

## Template XLS

Il file `assets/report_template.xlsx` definisce la struttura fissa del report. Contiene:

- **Sheet "Score"**: riepilogo score + sintesi
- **Uno sheet per ogni criterio** (Ambiguità, Flussi, Ruoli e Profili, Gestione Errori, Integrazioni, Glossario, Tracciabilità, Struttura Dati, Interfaccia Utente), ciascuno con:
  - Colonna `#` — numero progressivo
  - Colonna `Rif. Paragrafo` — riferimento al paragrafo/sezione del documento funzionale (es. "Par. 5.3", "Cap. 2")
  - Colonna `Domanda / Chiarimento` — testo azionabile
  - Colonna `Stato` — dropdown **Aperto / Chiuso**
  - Colonna `Risposta / Note` — da compilare a mano
  - Colonna `Priorità` — dropdown Alta / Media / Bassa

Non alterare la struttura del template (colonne, nomi sheet, dropdown). Popola solo le celle dati.

## Workflow

### Step 1 — Identifica il documento e la modalità

Controlla se nella cartella `documents/` esiste già un file `Review_[nome_documento].xlsx`:

- **Non esiste** → modalità **Prima analisi**: analisi completa del documento, tutte le domande inserite con Stato = "Aperto".
- **Esiste** → modalità **Revisione**: leggi il file esistente, esegui lo Step 2b per rilevare documenti referenziati nelle note, poi verifica ogni riga "Chiuso".

Se l'utente non specifica il file da analizzare, elenca `.docx` e `.pdf` in `documents/` e chiedi. Se c'è un solo file, usalo direttamente.

### Step 2 — Estrai il testo del documento

**2a — Documenti funzionali principali:**

- File **.pdf**: usa la skill `pdf`.
- File **.docx**: usa la skill `docx` per ottenere testo completo incluse tabelle.

Se le skill non sono disponibili, usa il tool `Read` come fallback per i `.pdf`; per i `.docx` segnala che serve la skill `docx`.

**2b — (Solo modalità Revisione) Rileva documenti referenziati nelle note:**

Per ogni riga con Stato = "Chiuso", analizza il testo della colonna "Risposta / Note" e cerca:

- Nomi file espliciti con estensione: `*.docx`, `*.pdf`, `*.xlsx`, `*.xls`, `*.csv`
- Frasi che introducono un riferimento: "fai riferimento a", "vedi", "cfr.", "come da", "documento", "allegato", "vedere"

Se trovi un nome file, cercalo in `documents/` e nelle sue sottocartelle (case-insensitive). Poi caricalo con la skill appropriata:

- `.docx` → skill `docx`
- `.pdf` → skill `pdf`
- `.xlsx` / `.xls` → skill `xlsx`
- `.csv` → script Python inline con pandas

```python
import pandas as pd
sheets = pd.read_excel('percorso/file.xlsx', sheet_name=None)
for nome, df in sheets.items():
    print(f"=== Sheet: {nome} ===")
    print(df.to_string(index=False))
```

**Regole di buon senso:**

- Non ricaricare un file già letto nella sessione corrente
- Se il file non esiste, annota `[⚠ documento non trovato: nome_file]` nella colonna "Risposta / Note" del report aggiornato
- Considera il contenuto di questi documenti come **contesto di verifica** per le righe "Chiuso" che li referenziano

### Step 3 — Analizza rispetto ai criteri

Per ogni criterio in `references/quality-criteria.md`:

1. Cerca nel documento le informazioni rilevanti.
2. Assegna uno **score 0–100**:
   - 90–100 → tutto presente e chiaro
   - 60–89 → presente ma con lacune significative
   - 30–59 → trattato parzialmente
   - 0–29 → quasi assente
3. Formula domande **specifiche e azionabili** (mai vaghe come "mancano i ruoli" — meglio "Chi può accedere alla funzione X?").

**Feedback intermedio**: dopo aver analizzato ogni criterio, mostra in chat una riga di riepilogo con score e conteggio domande prima di passare al successivo. Esempio:

```
Analisi in corso...
  1/9 Ambiguità:          55/100 — 12 domande
  2/9 Flussi:             70/100 — 10 domande
  3/9 Ruoli e Profili:    78/100 —  8 domande
  ...
```

**In modalità Revisione**: per ogni riga con Stato "Chiuso":

- Usa la risposta nella colonna "Risposta / Note" e il contenuto di eventuali documenti referenziati (caricati al Step 2b) per valutare se il punto è effettivamente risolto
- Se risolto → lo score del criterio viene ricalcolato con la formula:
  ```
  nuovo_score = vecchio_score + (domande_chiuse_risolte / domande_totali_criterio) × (100 - vecchio_score)
  ```
  dove `domande_chiuse_risolte` = righe "Chiuso" la cui risposta è stata verificata come effettivamente risolutiva; `domande_totali_criterio` = tutte le righe del criterio. Se una riga "Chiuso" non è effettivamente risolta, non conta come `chiusa_risolta`.
- Se la risposta è generica, il documento referenziato non contiene quanto atteso, o il punto rimane aperto → aggiungi una nuova riga follow-up con Stato = "Aperto" e indica cosa manca ancora
- Non modificare le righe già "Aperto" non ancora risposte

### Step 4 — Genera il file XLS dal template

1. Copia `assets/report_template.xlsx` in `documents/Review_[nome_documento].xlsx` (sovrascrivi se esiste).
2. Apri la copia con openpyxl e popola:

   **Sheet "Score"**:
   - Colonna B (Score): inserisci il valore numerico per ogni criterio
   - Colonna D (Contributo): inserisci `score × peso / 100`
   - Riga "SCORE GLOBALE" colonna B e D: inserisci il totale calcolato
   - Applica colore alla cella Score: verde (≥70), arancione (40–69), rosso (<40)
   - Cella Sintesi: 2–3 righe testuali sui punti critici principali

   **Sheet per criterio** (usa il nome breve del sheet, es. "Ambiguità" per "Assenza di Ambiguità"):
   - Riga 3 in poi: popola `#`, `Rif. Paragrafo` (riferimento al paragrafo/sezione del documento, es. "Par. 5.3"), `Domanda / Chiarimento`, `Stato` (= "Aperto"), `Risposta / Note` (= vuoto), `Priorità`
   - In modalità Revisione: mantieni le righe esistenti, aggiungi solo nuove righe in fondo

3. Salva il file.

### Step 5 — Comunica il risultato

Mostra in chat la tabella score in markdown e il percorso del file generato.

---

## Consigli per domande di qualità

Le domande devono essere **specifiche e azionabili**: non "mancano i ruoli" ma "Chi può accedere alla funzione X? Solo gli amministratori o anche i supervisori?". Ogni chiarimento deve essere direttamente indirizzabile agli autori senza ulteriori interpretazioni.

Lo Score Globale è la media pesata secondo i pesi in `references/quality-criteria.md`.
