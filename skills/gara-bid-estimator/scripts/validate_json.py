#!/usr/bin/env python3
"""
validate_json.py — Valida requisiti_estratti.json prima della compilazione del template.

Uso: python3 scripts/validate_json.py requisiti_estratti.json
Output JSON: { "status": "success"|"errors_found"|"warnings_found", "errors": [...], "warnings": [...] }

Supporta entrambi gli schema:
  - v1.0 (legacy): nessun rationale, nessun categoria_scope. Genera warning soft suggerendo upgrade.
  - v2.0 (current): rationale_requisito, rationale_soluzione, categoria_scope obbligatori per ogni requisito.
                    scope_dettaglio obbligatorio se categoria_scope != custom_software.
La versione è letta da meta.versione_schema; default "1.0" se assente.
"""

import json
import sys
from pathlib import Path

AREE_VALIDE = {
    "Gestione Utenti e IAM",
    "Frontend e UX",
    "Backend e API",
    "Data & AI",
    "Integrazioni e Middleware",
    "Infrastruttura e DevOps",
    "Sicurezza Applicativa",
    "Mobile",
    "Reporting e BI",
    "Document Management",
    "Workflow e BPM",
    "Notifiche e Comunicazioni",
    "Pagamenti e Fatturazione",
    "Accessibilità e Conformità",
}

COMPLESSITA_VALIDE = {"Bassa", "Media", "Alta"}
CERTEZZA_VALIDE   = {"estratto", "inferito", "assunto"}
IMPATTO_VALIDE    = {"alto", "medio", "basso"}
TIPO_REQ_VALIDI   = {"funzionale", "non_funzionale", "trasversale"}
CATEGORIA_SCOPE_VALIDE = {"custom_software", "cots_product", "service_external", "out_of_scope"}
TIPO_COSTO_VALIDI = {"licenza", "abbonamento", "servizio_consulenza", "infrastruttura_cloud", None}

SCHEMA_VERSIONS_SUPPORTED = {"1.0", "2.0"}
SCHEMA_VERSION_LATEST = "2.0"

GGU_MAX_WARN = 30   # GG/U su singolo componente oltre cui emette warning
GGU_MAX_ERR  = 100  # GG/U su singolo componente oltre cui emette errore

errors   = []
warnings = []

def err(msg):  errors.append(msg)
def warn(msg): warnings.append(msg)

def check_meta(meta):
    for field in ["nome_progetto", "cliente", "tipo_documento", "data_estrazione"]:
        if not meta.get(field):
            warn(f"meta.{field} mancante o vuoto")
    tipo = meta.get("tipo_documento", "")
    if tipo not in ("bando_gara", "documento_funzionale", "rfp", "capitolato", "csa"):
        warn(f"meta.tipo_documento '{tipo}' non riconosciuto — valori attesi: bando_gara, documento_funzionale, rfp, capitolato, csa")
    versione = meta.get("versione_schema", "")
    if not versione:
        warn("meta.versione_schema mancante — interpretato come schema v1.0; i campi rationale_*, categoria_scope, scope_dettaglio non saranno validati come obbligatori")
    elif versione not in SCHEMA_VERSIONS_SUPPORTED:
        warn(f"meta.versione_schema '{versione}' non supportato — versioni valide: {sorted(SCHEMA_VERSIONS_SUPPORTED)}")
    elif versione != SCHEMA_VERSION_LATEST:
        warn(f"meta.versione_schema '{versione}' è una versione precedente — la versione attuale è {SCHEMA_VERSION_LATEST}; valuta di rieseguire gara-req-extractor per beneficiare di rationale, categoria_scope e shift forbice nel template Excel")

def check_requisito(r, idx, schema_version="1.0"):
    rid = r.get("id", f"[indice {idx}]")
    is_v2 = (schema_version == "2.0")

    # Campi obbligatori
    for field in ["id", "area", "descrizione_bando", "tipo", "complessita"]:
        if not r.get(field):
            err(f"{rid}: campo obbligatorio '{field}' mancante o vuoto")

    # Campi obbligatori introdotti in schema v2.0
    if is_v2:
        for field in ["rationale_requisito", "rationale_soluzione", "categoria_scope"]:
            v = r.get(field)
            if v is None or (isinstance(v, str) and not v.strip()):
                err(f"{rid}: campo obbligatorio v2.0 '{field}' mancante o vuoto")
        cat_scope = r.get("categoria_scope", "")
        if cat_scope and cat_scope not in CATEGORIA_SCOPE_VALIDE:
            err(f"{rid}: categoria_scope '{cat_scope}' non valida — valori attesi: {sorted(CATEGORIA_SCOPE_VALIDE)}")
        # scope_dettaglio obbligatorio se categoria_scope != custom_software
        if cat_scope and cat_scope != "custom_software":
            scope_dett = r.get("scope_dettaglio")
            if not scope_dett or not isinstance(scope_dett, dict):
                err(f"{rid}: scope_dettaglio mancante o non oggetto — obbligatorio quando categoria_scope='{cat_scope}'")
            else:
                if not scope_dett.get("nome_prodotto"):
                    err(f"{rid}: scope_dettaglio.nome_prodotto mancante — obbligatorio quando categoria_scope='{cat_scope}'")
                if not scope_dett.get("motivazione"):
                    warn(f"{rid}: scope_dettaglio.motivazione mancante — raccomandato per tracciabilità")
                tc = scope_dett.get("tipo_costo")
                if tc not in TIPO_COSTO_VALIDI:
                    warn(f"{rid}: scope_dettaglio.tipo_costo '{tc}' non valido — valori attesi: licenza, abbonamento, servizio_consulenza, infrastruttura_cloud, null")
        # Coerenza: GG/U > 0 con categoria_scope != custom_software è incoerente (out-of-scope custom non si stima in GG/U)
        if cat_scope and cat_scope != "custom_software":
            ggu_tot = (r.get("ggu_fe", 0) or 0) + (r.get("ggu_be", 0) or 0) + (r.get("ggu_data", 0) or 0)
            if ggu_tot > 0:
                warn(f"{rid}: GG/U={ggu_tot} ma categoria_scope='{cat_scope}' — out-of-scope custom dovrebbero avere GG/U=0; il costo va nello sheet 'Prodotti & Servizi Esterni'")
    else:
        # In schema v1.0, segnala come info se mancano i nuovi campi (informativo, non bloccante)
        if not r.get("rationale_requisito") and not r.get("rationale_soluzione"):
            pass  # silenzioso in v1.0

    # Area valida
    area = r.get("area", "")
    if area and area not in AREE_VALIDE:
        err(f"{rid}: area '{area}' non valida — deve essere una delle {len(AREE_VALIDE)} aree funzionali")

    # Tipo valido
    tipo = r.get("tipo", "")
    if tipo and tipo not in TIPO_REQ_VALIDI:
        warn(f"{rid}: tipo '{tipo}' non riconosciuto — valori attesi: {', '.join(TIPO_REQ_VALIDI)}")

    # Complessità valida
    comp = r.get("complessita", "")
    if comp and comp not in COMPLESSITA_VALIDE:
        err(f"{rid}: complessita '{comp}' non valida — valori attesi: Bassa, Media, Alta")

    # GG/U
    ggu_fe   = r.get("ggu_fe",   0) or 0
    ggu_be   = r.get("ggu_be",   0) or 0
    ggu_data = r.get("ggu_data", 0) or 0
    ggu_tot  = ggu_fe + ggu_be + ggu_data

    is_padre = r.get("is_padre", False)
    # In schema v2.0, GG/U=0 è atteso per requisiti con categoria_scope != custom_software
    # (il costo va nello sheet "Prodotti & Servizi Esterni", non in GG/U)
    is_out_of_scope_custom = (
        is_v2
        and r.get("categoria_scope")
        and r.get("categoria_scope") != "custom_software"
    )

    if not is_padre and not is_out_of_scope_custom:
        if ggu_tot == 0:
            err(f"{rid}: GG/U totale è 0 su un requisito non padre — verifica la stima")
        if ggu_tot > GGU_MAX_ERR:
            err(f"{rid}: GG/U totale {ggu_tot} supera il massimo consentito ({GGU_MAX_ERR}) — probabilmente va decomposto")
        if ggu_tot > GGU_MAX_WARN:
            warn(f"{rid}: GG/U totale {ggu_tot} è elevato — valuta se decomporre ulteriormente")

    if is_padre and ggu_tot != 0:
        warn(f"{rid}: requisito padre ha GG/U != 0 — i padri devono avere GG/U = 0 (la stima va sui figli)")

    # GG/U negativi
    for comp_name, val in [("ggu_fe", ggu_fe), ("ggu_be", ggu_be), ("ggu_data", ggu_data)]:
        if val < 0:
            err(f"{rid}: {comp_name} è negativo ({val})")

    # Certezza
    certezza = r.get("certezza", "")
    if certezza and certezza not in CERTEZZA_VALIDE:
        warn(f"{rid}: certezza '{certezza}' non valida — valori attesi: estratto, inferito, assunto")

    if certezza == "assunto" and not r.get("da_chiarire"):
        warn(f"{rid}: certezza 'assunto' ma da_chiarire non impostato — considera di aggiungere una domanda bloccante")

    if certezza in ("estratto", "inferito") and not r.get("fonte_pag"):
        warn(f"{rid}: certezza '{certezza}' ma fonte_pag mancante — aggiungi riferimento pagina/sezione")

def check_domande_bloccanti(domande):
    for i, d in enumerate(domande):
        did = d.get("id", f"[indice {i}]")
        for field in ["id", "area", "domanda", "impatto_stima"]:
            if not d.get(field):
                warn(f"domande_bloccanti {did}: campo '{field}' mancante")
        impatto = d.get("impatto_stima", "")
        if impatto and impatto not in IMPATTO_VALIDE:
            warn(f"domande_bloccanti {did}: impatto_stima '{impatto}' non valido — valori attesi: alto, medio, basso")

def check_duplicati(requisiti):
    ids = [r.get("id") for r in requisiti if r.get("id")]
    duplicati = [rid for rid in set(ids) if ids.count(rid) > 1]
    for rid in duplicati:
        err(f"ID duplicato: '{rid}' compare più volte")

def check_gerarchia(requisiti):
    """Verifica che ogni figlio abbia un padre esistente e viceversa."""
    tutti_ids = {r.get("id") for r in requisiti if r.get("id")}
    padri_dichiarati = {r.get("id") for r in requisiti if r.get("is_padre")}
    for r in requisiti:
        padre_id = r.get("padre_id")
        if padre_id and padre_id not in tutti_ids:
            err(f"{r.get('id')}: padre_id '{padre_id}' non esiste tra i requisiti")
    for padre in padri_dichiarati:
        figli = [r for r in requisiti if r.get("padre_id") == padre]
        if not figli:
            warn(f"Requisito padre '{padre}' non ha figli — considera se è necessario mantenerlo come padre")

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "errors": ["Uso: python3 validate_json.py <path_json>"], "warnings": []}))
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(json.dumps({"status": "error", "errors": [f"File non trovato: {path}"], "warnings": []}))
        sys.exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "errors": [f"JSON non valido: {e}"], "warnings": []}))
        sys.exit(1)

    # Check meta
    meta = data.get("meta")
    if not meta:
        err("Campo 'meta' mancante — obbligatorio")
        schema_version = "1.0"
    else:
        check_meta(meta)
        schema_version = meta.get("versione_schema") or "1.0"
        if schema_version not in SCHEMA_VERSIONS_SUPPORTED:
            schema_version = "1.0"  # fallback per validare cmq il resto

    # Check requisiti
    requisiti = data.get("requisiti", [])
    if not requisiti:
        err("Campo 'requisiti' mancante o vuoto — nessun requisito da stimare")
    else:
        check_duplicati(requisiti)
        check_gerarchia(requisiti)
        for i, r in enumerate(requisiti):
            check_requisito(r, i, schema_version=schema_version)

    # Check domande bloccanti
    domande = data.get("domande_bloccanti", [])
    check_domande_bloccanti(domande)

    # Check GG/U totale di progetto
    ggu_totale = sum(
        (r.get("ggu_fe", 0) or 0) +
        (r.get("ggu_be", 0) or 0) +
        (r.get("ggu_data", 0) or 0)
        for r in requisiti if not r.get("is_padre")
    )
    if ggu_totale == 0:
        err("GG/U totale di progetto è 0 — nessun requisito ha una stima")
    elif ggu_totale < 5:
        warn(f"GG/U totale di progetto molto basso ({ggu_totale}) — verifica che tutti i requisiti siano stati stimati")

    # Output
    status = "errors_found" if errors else ("warnings_found" if warnings else "success")
    result = {
        "status": status,
        "total_requisiti": len(requisiti),
        "ggu_totale_progetto": ggu_totale,
        "errors":   errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
