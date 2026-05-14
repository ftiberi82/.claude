---
name: gara-rfp-deck
description: >
  Genera un deck PowerPoint Executive Summary di 10 slide a partire da un workbook Excel
  di handoff prodotto da `gara-rfp-handoff`. Copia il template aziendale
  `assets/template_executive_summary.pptx` (10 slide pre-formattate con stile RAI Accenture,
  layout 16:9 da 10x5.62") e sostituisce i testi placeholder con i valori letti dal sheet
  `1. Info Sintetiche RFP` (anagrafica, scope, durata, modello commerciale, criteri di
  valutazione, SLA, delivery, requisiti formali) e dal sheet `6. Assunzioni` (per il quadro
  assunzioni a rischio ALTO).
  TRIGGER quando: l'utente fornisce un file `rfp_handoff.xlsx` (o qualsiasi `.xlsx` con sheet
  `1. Info Sintetiche RFP` strutturato come da template `gara-rfp-handoff`) e chiede di
  generare il deck, l'executive summary slides, il PPT della gara, la presentazione, le slide,
  la vista executive, il deck dall'Excel handoff.
  OUTPUT: file `executive_summary.pptx` con esattamente 10 slide pre-formattate, salvato
  nella stessa cartella del file Excel di input (default) o in path indicato dall'utente.
  COMPORTAMENTO NON INTERATTIVO: zero domande all'utente. I dati nello sheet 1 dell'Excel
  sono già stati validati a monte da `gara-rfp-handoff` (registro scelte interpretative
  approvato). Questa skill esegue solo lettura → sostituzione testi → rendering.
  POSIZIONAMENTO NEL FLUSSO: questa skill è lo STEP 2 OBBLIGATORIO subito dopo
  `gara-rfp-handoff` (Fase 1). Il deck PPT è il PRIMO deliverable di brainstorming
  delivery/bid, usato per allinearsi PRIMA della Fase 2 manuale (chiarimenti cliente).
  Non è uno step finale né opzionale: va invocata immediatamente dopo che l'utente ha
  approvato l'`rfp_handoff.xlsx`.
  AUTONOMIA: skill standalone, invocata sempre dall'utente in modo esplicito.
  `gara-rfp-handoff` NON la chiama automaticamente — la generazione del deck è invocazione
  separata a valle dell'Excel di handoff, ma è il NEXT STEP raccomandato dalla Fase 1.
  NON USARE se: il file di input non è un workbook handoff valido (manca sheet `1. Info
  Sintetiche RFP`); l'utente ha solo documenti RFP grezzi e non un Excel handoff esistente
  → in quel caso usa `gara-rfp-handoff`.
  SKIP se l'Excel di input non è leggibile, è vuoto o non ha la struttura attesa.
---

# Gara RFP Deck

Genera un deck PowerPoint Executive Summary di 10 slide a partire da un workbook Excel di
handoff prodotto da `gara-rfp-handoff`. Il deck è pensato per il bid manager / commerciale
che deve presentare una sintesi della gara a stakeholder interni.

**Skill non interattiva.** Zero domande, lettura → sostituzione placeholder → rendering →
riepilogo.

**Strategia di rendering**: la skill **NON crea il deck da zero**. Copia il template
aziendale pre-formattato `assets/template_executive_summary.pptx` (10 slide con stile RAI
Accenture, layout 16:9 ridotto da 10x5.62", footer aziendale, colori e icone) e sostituisce
i testi placeholder con i valori dall'Excel handoff. Questo garantisce coerenza grafica e
velocità (non si ricostruiscono layout, tabelle, icone ad ogni esecuzione).

**Identificazione dei placeholder — text-matching, non indici.** L'approccio robusto è
matchare il **testo esatto** dello shape contro una mappa `(slide_idx, testo_originale) →
nuovo_testo`. Gli indici numerici delle shape sono fragili (off-by-one frequente tra ordine
1-based del dump e indicizzazione 0-based di `python-pptx`, shape decorative invisibili che
spostano gli indici). Esempio di mappa:
```python
REPL = {
    (0, "BB2480578E"): "<nuovo CIG>",      # Slide 1 cover
    (0, "07.04.2026"): "<nuova data>",
    (3, "63"): "<nuova durata max>",       # Slide 4 numero big
    (3, "3 mesi"): "<startup>",            # Slide 4 valore fase
    (2, "07 APR\n2026"): "<data ML>",      # Slide 3 date multi-paragrafo
}
```

**Preservazione formattazione**: la funzione di sostituzione deve preservare:
- font name, size, bold, italic, color del primo run del paragrafo
- alignment (`pPr algn`) e level (`pPr lvl`) del primo paragrafo
- multi-paragrafi: i testi del template con newline (es. date "07 APR\n2026") vanno mantenuti
  come due paragrafi separati, NON fusi in una sola riga. Il nuovo testo deve essere splittato
  per `\n` e ogni sub-riga aggiunta come `<a:p>` separato.

Non usare `text_frame.clear()` + assegnazione semplice: cancella tutto il `pPr` (alignment
viene persa) e collassa multi-paragrafi. Usare invece manipolazione diretta dell'XML
`<a:txBody>` con lxml: rimuovere i `<a:p>` esistenti e ricrearli con `<a:pPr>` + `<a:r>` +
`<a:rPr>` calibrati sul template originale.

## Input richiesto

- File `.xlsx` con almeno il sheet `1. Info Sintetiche RFP` strutturato come da template
  `gara-rfp-handoff` (label in colonna A, valori in colonna B, sezioni `DATI IDENTIFICATIVI
  GARA`, `SCADENZE CHIAVE`, `VALORE APPALTO`, `DURATA CONTRATTO`, `MODELLO COMMERCIALE`,
  `CRITERI DI VALUTAZIONE`, `SLA & PENALI CHIAVE`, `SKILL MIX E DELIVERY`, `REQUISITI DI
  QUALIFICAZIONE`).
- **Consigliato**: sheet `2. Mappatura Capability` — usato per derivare lo stack tecnologico
  della slide 7 (estrazione di linguaggi, framework, DB, CMS dalle note delle capability L3).
  Se assente, slide 7 mantiene i placeholder generici del template.
- Opzionale: sheet `6. Assunzioni` — riferimento per il bid manager nella revisione manuale
  post-generazione (non viene renderizzato in slide dedicata nel template attuale).

Se il file fornito non ha il Sheet 1, comunica l'errore e termina senza produrre output.

## Output

- `executive_summary.pptx` con esattamente 10 slide pre-formattate dal template.
- Default: salvato nella stessa cartella del file Excel di input.
- Path alternativo: se l'utente specifica una destinazione diversa, usala.

## Asset

- `assets/template_executive_summary.pptx` — template ufficiale del deck. Contiene 10 slide
  con stile aziendale Accenture (intestazione blu, footer pagina, layout 16:9 ridotto
  10x5.62"). Layout master: `DEFAULT`. Le slide hanno shape pre-posizionate con testi
  placeholder calibrati sulla gara RAI (CIG BB2480578E, valore €19.977.320, 39 mesi base,
  41 risorse presidio, ecc.) che la skill sostituisce con i valori dell'Excel handoff
  in input.

**Non modificare il template in place**: copialo nella working directory dell'utente come
`executive_summary.pptx` e popolalo lì.

## Distinzione vs `gara-rfp-handoff` e `gara-rfp-analyzer`

| | `gara-rfp-analyzer` | `gara-rfp-handoff` | `gara-rfp-deck` (questa) |
|---|---|---|---|
| **Input** | Documenti RFP (PDF, DOCX, ...) | Documenti RFP | Workbook Excel handoff |
| **Output** | `rfp_analysis.json` | `rfp_handoff.xlsx` | `executive_summary.pptx` |
| **Comportamento** | Non interattivo | Interattivo (registro scelte) | Non interattivo |
| **Quando** | Pre-stima, analisi strategica | Pacchetto operativo per cost modeler | **Step 2: brainstorming subito dopo handoff, PRIMA della Fase 2 chiarimenti** |

**In caso di dubbio sul trigger**: l'input è discriminante.
- Input = documenti RFP grezzi → `gara-rfp-analyzer` (analisi) oppure `gara-rfp-handoff`
  (pacchetto stima).
- Input = `rfp_handoff.xlsx` (o equivalente) → `gara-rfp-deck`.

## Struttura del deck (10 slide del template)

| # | Slide | Contenuto principale | Sorgente principale Excel |
|---|---|---|---|
| 1 | **Cover** | Cliente + Titolo + CIG + Pubblicazione + Valore Totale + Durata Base + Proroga Max + Presidio Min. | Sheet 1 B4-9, B17-20, B25-26, B61 |
| 2 | **Contesto Cliente & Scope RFP** | Box CLIENTE (stazione appaltante, struttura committente, portfolio) + Box SCOPE RFP (oggetto, modello dual-track, copertura tecnologica) | Sheet 1 B4, B7 + descrizione narrativa |
| 3 | **Scadenze Chiave & Valore Appalto** | Timeline 4 milestone (Pubblicazione, Chiarimenti, Offerte, Prima seduta) + tabella Valore Appalto (breakdown startup/canone/T&M/proroga) | Sheet 1 B8, B12-14, B17-20 |
| 4 | **Durata Contratto & Modello Commerciale** | Box DURATA (63 mesi max + 3 fasi) + Box MODELLO (Canone con 5 servizi + T&M con 4 servizi) | Sheet 1 B23-28, B31-33 |
| 5 | **Criteri di Valutazione** | 3 KPI cards (80pt tecnica / 40pt sbarramento / 20pt economica) + dettaglio offerta tecnica (3 sotto-criteri) + offerta economica (rate card 4 profili) | Sheet 1 B34-37, B41-47 |
| 6 | **Vincoli SLA / KPI e Regime Penali** | Tabella tempi presa in carico/risoluzione + 5 fasce prestazione A-E + 6 indicatori I1-I6 | Sheet 1 B50-56 |
| 7 | **Aspetti Tecnologici** | 6 box stack: Backend, Frontend, Mobile/SmartTV, Database, DevOps/Cloud, AI/ML | Sheet 2 (note capability L3) + fallback testi template |
| 8 | **Modello di Delivery & Skill Mix Richiesto** | 3 modelli delivery (On-Site / Remoto / Ibrido) + tabella skill mix con 41 risorse + turn over | Sheet 1 B61-67 |
| 9 | **Aspetti Procedurali & Requisiti di Partecipazione** | Box requisiti qualificazione + Box inversione procedimentale + Box giustificazione anomalia + Box parco applicativo | Sheet 1 B70-75 + Sheet 2 (parco app) |
| 10 | **Key Actions & Next Steps** | 5 step numerati con scadenza chiarimenti, requisiti qualifica, stima canone, strategia tecnica, deadline offerta | Sheet 1 B12-14 + sintesi |

## Mapping testi placeholder → campi Excel

Il template ha testi pre-popolati con valori RAI specifici. La skill sostituisce ogni testo
per posizione `(slide_idx, shape_idx)`. Sotto, la mappa per le shape principali. Lo script
deve iterare le shape del template e, quando incontra una corrispondenza nella mappa,
sostituire `text_frame.text` con il valore dall'Excel preservando il font/colore/dimensione.

### Slide 1 — Cover
| Shape (testo originale) | Campo Excel |
|---|---|
| Shape 4 (`BB2480578E`) | Sheet 1 B5 (CIG) |
| Shape 7 (`07.04.2026`) | Sheet 1 B8 (Data pubblicazione, formato gg.mm.aaaa) |
| Shape 10 (`€ 19.977.320`) | Sheet 1 B20 (Valore totale) |
| Shape 13 (`39 mesi`) | Sheet 1 B25 (Durata base totale) |
| Shape 16 (`+24 mesi`) | Sheet 1 B26 (Opzione proroga, prefisso `+`) |
| Shape 19 (`41 risorse`) | Sheet 1 B61 (Risorse minime presidio, primo token numerico) |
| Shape 22 (`RAI`) | Sheet 1 B4 (Stazione appaltante, primo token) |
| Shape 23 (`Radiotelevisione Italiana S.p.A.`) | Sheet 1 B4 (resto del nome stazione appaltante) |
| Shape 25 (`RFP Executive Summary`) | Costante (titolo deck) |
| Shape 26 (`Servizi a Progetto — Sistemi Informativi`) | Sheet 1 A1 (titolo gara, parte dopo trattino) |
| Shape 27 (`Procedura Aperta sopra soglia comunitaria ex art. 71 D.lgs. 36/2023`) | Sheet 1 B6 (Tipo procedura) |

### Slide 2 — Contesto Cliente & Scope RFP
| Shape (testo originale) | Campo Excel |
|---|---|
| Box CLIENTE | Statico + Sheet 1 B4, B7 |
| Box SCOPE RFP | Statico + nome gara |
| Bullet "RAI – Radiotelevisione…" | Sheet 1 B4 |
| Bullet "CTO – Direzione Reti…" | Sheet 1 B7 |
| Footer pagina (slide 2-10) | `[Cliente] – RFP Servizi a Progetto Sistemi Informativi | Riservato e Confidenziale` |

### Slide 3 — Scadenze + Valore Appalto
| Shape (testo originale) | Campo Excel |
|---|---|
| `07 APR | 2026` (Pubblicazione) | Sheet 1 B8 |
| `29 APR | 2026` (Chiarimenti) | Sheet 1 B12 |
| `13 MAG | 2026` (Offerte) | Sheet 1 B13 |
| `14 MAG | 2026` (Prima seduta) | Sheet 1 B14 |
| Tabella valore appalto | Sheet 1 B17-20 (5 righe: startup + canone + T&M + proroga + totale) |

### Slide 4 — Durata + Modello Commerciale
| Shape (testo originale) | Campo Excel |
|---|---|
| `63` mesi max | Sheet 1 B27 (Durata massima complessiva, primo token) |
| `3 mesi` (Start-Up) | Sheet 1 B23 |
| `36 mesi` (Operativo) | Sheet 1 B24 |
| `+24 mesi` (Proroga opz.) | Sheet 1 B26 |
| Penali warning footer | Sheet 1 B28 |
| Box CANONE FISSO + 5 bullet (MAC/REP/GES/GST/CON) | Sheet 1 B32 (Servizi a Canone) |
| Box T&M + 4 bullet (MAV/MEV/PRJ/Specialistici) | Sheet 1 B33 (Servizi a Richiesta) |

### Slide 5 — Criteri di Valutazione
| Shape (testo originale) | Campo Excel |
|---|---|
| `80` pt tecnica | Sheet 1 B41 (primo token numerico) |
| `40` MIN sbarramento | Sheet 1 B46 (primo token numerico) |
| `20` pt economica | Sheet 1 B45 (primo token numerico) |
| `30 pt` Soluzioni Organizzative | Sheet 1 B42 |
| `10 pt` Certificazioni Aziendali | Sheet 1 B43 |
| `40 pt` Skill & Competences | Sheet 1 B44 |
| Bullet rate card Architect `€280/gg` | Sheet 1 B34 |
| Bullet rate card Tech Leader `€250/gg` | Sheet 1 B35 |
| Bullet rate card Analyst `€210/gg` | Sheet 1 B36 |
| Bullet rate card Programmer `€200/gg` | Sheet 1 B37 |

### Slide 6 — SLA / KPI / Penali
| Shape (testo originale) | Campo Excel |
|---|---|
| Tabella tempi MAC/REP/GES (cella accettazione + P1/P2/P3/P4) | Sheet 1 B50-54 |
| Soglie fasce A `≥ 0,99` / B `≥ 0,95` / C `≥ 0,90` / D `≥ 0,85` / E `< 0,85` | Sheet 1 B55 (parsing fasce) |
| Penali footer "attive dal Mese 7" | Sheet 1 B28 |
| Indicatori I1-I6 + P1/P2 | Sheet 1 B56 (parsing indicatori) |

### Slide 7 — Aspetti Tecnologici
| Box (titolo + 4 bullet) | Campo Excel |
|---|---|
| Box Backend (Java, Python, Node, REST/Microservizi) | Sheet 2 col `Note` → keyword `Java`, `Spring`, `Python`, `NodeJS`, `GraphQL`, `.NET` |
| Box Frontend (React, Angular, HTML5, Typescript) | Sheet 2 col `Note` → keyword `React`, `Angular`, `HTML`, `CSS`, `NextJS`, `Vue` |
| Box Mobile (Swift, Kotlin, RN, SmartTV) | Sheet 2 col `Note` → keyword `iOS`, `Android`, `Swift`, `Kotlin`, `React Native`, `HbbTV`, `VegaOS`, `Tizen` |
| Box Database (Oracle, MongoDB, ES, Redis) | Sheet 2 col `Note` → keyword `Oracle`, `MongoDB`, `Elastic`, `Postgres`, `MySQL`, `Redis` |
| Box DevOps/Cloud (Docker, K8s, OpenShift, AWS/Azure/GCP) | Sheet 2 col `Note` → keyword `Docker`, `Kubernetes`, `OpenShift`, `Jenkins`, `AWS`, `Azure`, `GCP` |
| Box AI/ML (Azure Cognitive, TensorFlow, PyTorch, Scikit) | Sheet 2 col `Note` → keyword `Cognitive`, `TensorFlow`, `PyTorch`, `Keras`, `Scikit`, `ML`, `AI` |

Se Sheet 2 è assente o non ha keyword utili, mantieni i placeholder del template (valori
RAI di default già coerenti per gare media/broadcaster).

### Slide 8 — Delivery & Skill Mix
| Shape (testo originale) | Campo Excel |
|---|---|
| Box On-Site (orari, sede) | Sheet 1 B62-64 |
| Box Remoto T&M | Sheet 1 B65 |
| Tabella skill mix 41 risorse | Sheet 1 B61 + composizione dal Capitolato (se disponibile in Sheet 2/7) |
| Footer "Turn over max 5% • Affiancamento 10gg" | Sheet 1 B66-67 |

### Slide 9 — Procedurali & Requisiti
| Shape (testo originale) | Campo Excel |
|---|---|
| Bullet `Fatturato IT specifico ≥ €10M` | Sheet 1 B70 |
| Bullet `Siti web e portali ≥ €4M` | Sheet 1 B71 |
| Bullet `Sistemi CMS ≥ €1M` | Sheet 1 B72 |
| Bullet `App mobile / Smart TV ≥ €2M` | Sheet 1 B73 |
| Bullet avvalimento/RTI | Sheet 1 B74 |
| Box Inversione procedimentale | Sheet 1 B9 (norma) |
| Box Giustificazione anomalia | Sheet 1 B75 |
| Box Parco applicativo (8 app principali) | Sheet 2 capability L3 / Allegato 1 cap.7 |

### Slide 10 — Key Actions & Next Steps
| Shape (testo originale) | Campo Excel |
|---|---|
| Step 01 "Chiarimenti entro 29 Aprile 2026" | Sheet 1 B12 |
| Step 02 "Verifica requisiti" | Sheet 1 B70-73 (sintesi requisiti) |
| Step 03 "Stima canone (41 risorse)" | Sheet 1 B61 |
| Step 04 "Strategia tecnica (60+ pt su 80)" | Sheet 1 B41-46 |
| Step 05 "Deadline offerta: 13 Maggio 2026 ore 12:00" | Sheet 1 B13-14 |

## Comportamento sui campi mancanti

I campi vuoti o contenenti i marker `<da Disciplinare — non disponibile>` (o varianti)
**lasciano in place il placeholder del template**. Il template ha valori RAI di default
coerenti come fallback grafico — è preferibile non sostituire con stringa vuota.

**Eccezione — campo critico mancante**: se TUTTI i campi della slide sono vuoti/mancanti,
sovrapponi sulla slide un'avvertenza testuale rossa: `⚠ Sezione incompleta — Dati non
disponibili nel workbook`.

## Stile del deck

Il template ha già stile aziendale Accenture pre-configurato. **Non modificare** font, colori
o layout — la skill cambia solo i contenuti testuali. Caratteristiche del template:
- **Layout**: 16:9 ridotto 10x5.62" (9.144.000 x 5.143.500 EMU).
- **Layout master**: `DEFAULT` (unico).
- **Intestazione**: barra blu scuro 10x0.7" con titolo bianco.
- **Footer**: barra footer con `[Cliente] – RFP Servizi a Progetto Sistemi Informativi |
  Riservato e Confidenziale` + numero pagina.
- **Cover (slide 1)**: layout speciale full-width con barra laterale destra contenente i KPI
  chiave (CIG, Valore, Durata, Proroga, Presidio).
- **Box colorati**: card con bordo superiore colorato e contenuto strutturato bullet/icone.

## Workflow

### Step 1 — Validazione input
1. Verifica che il file `.xlsx` di input esista e sia leggibile.
2. Apri il workbook (delegando alla skill `xlsx`).
3. Verifica la presenza del sheet `1. Info Sintetiche RFP`. Se manca: errore, termina.
4. Annota se i sheet `2. Mappatura Capability` e `6. Assunzioni` sono presenti o no.

### Step 2 — Estrazione dati
1. **Sheet 1** — leggi tutte le celle, popolando un dizionario interno `{row: {label, value}}`
   usando coppie (A_n, B_n).
2. **Sheet 2** (se presente) — scansiona la colonna `Note` (col H) di tutte le righe L2/L3 e
   raccogli i token tecnologici per categorie (BE/FE/Mobile/SmartTV/DB/CMS/DevOps/AI) usando
   le keyword listate nella sezione "Mapping testi placeholder → campi Excel" sopra.
   Deduplica e mantieni l'ordine di apparizione.

### Step 3 — Copia del template
1. Copia `assets/template_executive_summary.pptx` nella working directory dell'utente come
   `executive_summary.pptx`.
2. Apri il file copiato con `python-pptx`.

### Step 4 — Sostituzione testi placeholder
Per ogni slide del deck (1-10), itera le shape e applica la sostituzione secondo la mappa
documentata nella sezione "Mapping testi placeholder → campi Excel".

**Tecnica di sostituzione**: per ogni shape con testo, se il testo corrente matcha un
pattern noto della mappa (es. contiene `BB2480578E` o `€ 19.977.320` o `RAI`), sostituisci
con il valore dall'Excel preservando il `run.font` (mantieni dimensione, colore, bold della
prima `run` del paragrafo).

**Tabelle (Slide 3, 6, 8)**: alcune slide contengono shape `TABLE`. Per queste, accedere a
`shape.table.rows[i].cells[j].text_frame` e applicare la sostituzione per cella.

### Step 5 — Aggiornamento footer
Per le slide 2-10, sostituisci nel testo del footer (penultimo shape di ogni slide) la
stringa `RAI – RFP Servizi a Progetto Sistemi Informativi` con `[Cliente] – RFP [Nome gara
da Sheet 1 A1]`.

### Step 6 — Salvataggio
Salva in `executive_summary.pptx` nella stessa directory del file Excel di input (a meno
che l'utente non abbia specificato un path diverso).

### Step 7 — Riepilogo finale
Presenta in chat un riepilogo Markdown:

> **Deck Executive Summary generato — [Cliente]**
>
> File prodotto: `executive_summary.pptx` (10 slide)
>
> **Slide popolate dall'Excel**: N (su 10)
> **Slide con placeholder del template (fallback)**: N
> **Path:** `[path completo del file]`

Se durante la generazione hai incontrato anomalie (es. sheet 6 mancante, dati Sheet 1
parzialmente vuoti), elencale brevemente sotto il riepilogo come avvertimenti.

## Regole operative

- **Non interpretare i dati del workbook**: il workbook è la verità, lo prendi così com'è.
  Se un campo è ambiguo o mancante, lasci il placeholder del template (non sostituire con
  stringa vuota).
- **Non chiedere conferme**: la validazione interpretativa è già stata fatta da
  `gara-rfp-handoff`. Questa skill esegue.
- **10 slide esatte, sempre**: il template ha 10 slide pre-formattate. Non aggiungere/
  rimuovere/riordinare slide.
- **Non modificare lo stile**: font, colori, layout, dimensioni shape sono parte del template
  aziendale. La skill cambia SOLO i contenuti testuali (e i valori delle tabelle).
- **Preserva il font del template**: usa la prima `run` del paragrafo come riferimento per
  font/size/colore quando sostituisci il testo.
- **Lingua delle slide**: italiano (coerente con l'Excel handoff). Se l'Excel handoff è in
  un'altra lingua, usa quella ma mantieni le label statiche del template in italiano (es.
  `CIG`, `Pubblicazione`, `Valore Totale`).
- **Path output**: di default nella cartella del file Excel di input. Se l'utente specifica
  un path, rispettalo.
