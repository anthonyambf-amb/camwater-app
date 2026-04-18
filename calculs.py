"""Moteur de calcul v2 - reproduit toutes les formules Excel.
Supporte : agence, DR, national, plage de mois, comparaison N/N-1."""
from database import get_db, TVA_RATE, STRUCTURE_CW

# ═══════════════════════════════════════════════════════════════
# Niveau Agence - mois unique
# ═══════════════════════════════════════════════════════════════

def get_volumes_agence(agence_id, mois, exercice=2026):
    db = get_db()
    rows = db.execute(
        "SELECT categorie, valeur FROM volumes WHERE agence_id=? AND mois=? AND exercice=?",
        (agence_id, mois, exercice)).fetchall()
    db.close()
    return {r['categorie']: r['valeur'] for r in rows}


def get_ca_specifiques_agence(agence_id, mois, exercice=2026):
    db = get_db()
    rows = db.execute(
        "SELECT rubrique, montant FROM ca_specifiques WHERE agence_id=? AND mois=? AND exercice=?",
        (agence_id, mois, exercice)).fetchall()
    db.close()
    return {r['rubrique']: r['montant'] for r in rows}


def get_encaissements_agence(agence_id, mois, exercice=2026):
    db = get_db()
    rows = db.execute(
        "SELECT section, rubrique, montant FROM encaissements WHERE agence_id=? AND mois=? AND exercice=?",
        (agence_id, mois, exercice)).fetchall()
    db.close()
    return {(r['section'], r['rubrique']): r['montant'] for r in rows}


def get_complement_travaux(agence_id, mois, exercice=2026):
    db = get_db()
    row = db.execute(
        "SELECT montant FROM complements_travaux WHERE agence_id=? AND mois=? AND exercice=?",
        (agence_id, mois, exercice)).fetchone()
    db.close()
    return row['montant'] if row else 0


def calcul_ca_agence(agence_id, mois, exercice=2026):
    """Calcul complet du CA pour une agence/mois. Retourne un dict structuré."""
    db = get_db()
    prix = {r['categorie']: r['prix'] for r in
            db.execute("SELECT categorie, prix FROM prix_unitaires WHERE exercice=?", (exercice,)).fetchall()}
    db.close()

    volumes = get_volumes_agence(agence_id, mois, exercice)
    ca_spec = get_ca_specifiques_agence(agence_id, mois, exercice)
    enc = get_encaissements_agence(agence_id, mois, exercice)
    complement = get_complement_travaux(agence_id, mois, exercice)

    # --- Section A: CA Vente Eau ---
    ca_auto_details = {}
    categories_auto = [
        "Particuliers <= 10m3", "Particuliers > 10m3 T2", "Particuliers > 10m3 T3",
        "Sonel 870", "Sonel 872",
        "Cadre Eneo 890", "Cadre Eneo 891", "Cadre Eneo 892",
        "Cadre Eneo 880", "Cadre Eneo 881",
        "B.F. Payantes", "Dépasst agts CDE", "Dépasst Adm. CDE", "Ventes Directes",
        "Rappel T1", "Rappel T2", "Sinistres",
        "Partants <= 10m3", "Partants > 10m3", "Fraudes",
    ]
    for cat in categories_auto:
        vol = volumes.get(cat, 0)
        pu = prix.get(cat, 0)
        ca_auto_details[cat] = vol * pu

    ca_auto_details["Administrations"] = volumes.get("Administrations", 0) * prix.get("Administrations", 0)
    ca_auto_details["Bâtiments communaux"] = volumes.get("Bâtiments communaux", 0) * prix.get("Bâtiments communaux", 0)
    ca_auto_details["B.F.C"] = volumes.get("B.F.C", 0) * prix.get("B.F.C", 0)
    for cat in ["Val Part Agent CDE", "Val Services CDE", "Val Part Adm CDE", "Val Part agts Camwater"]:
        ca_auto_details[cat] = volumes.get(cat, 0) * prix.get(cat, 0)

    total_ca_auto = sum(ca_auto_details.values())

    # CA spécifiques (saisie manuelle)
    eneo_871 = ca_spec.get("ENEO 871", 0)
    eneo_873 = ca_spec.get("ENEO 873", 0)
    gco_ca = ca_spec.get("GCO", 0)
    loc_part = ca_spec.get("Location compteur Particuliers", 0)
    loc_gco = ca_spec.get("Location compteur GCO", 0)
    loc_adm = ca_spec.get("Location compteur ADM", 0)
    loc_bc = ca_spec.get("Location compteur BC", 0)
    loc_bfc = ca_spec.get("Location compteur BFC", 0)

    total_locations = loc_part + loc_gco + loc_adm + loc_bc + loc_bfc
    total_ca_spec = eneo_871 + eneo_873 + gco_ca + total_locations

    # Sous-totaux par catégorie client
    ca_particuliers = (
        sum(ca_auto_details.get(c, 0) for c in categories_auto)
        + eneo_871 + eneo_873 + loc_part
    )
    ca_gco = gco_ca + loc_gco
    ca_communes = (ca_auto_details["Bâtiments communaux"] + ca_auto_details["B.F.C"]
                   + loc_bc + loc_bfc)
    ca_adm = ca_auto_details["Administrations"] + loc_adm
    ca_camwater = sum(ca_auto_details[c] for c in
                      ["Val Part Agent CDE", "Val Services CDE", "Val Part Adm CDE", "Val Part agts Camwater"])

    total_ca_ve = ca_particuliers + ca_gco + ca_communes + ca_adm + ca_camwater
    total_ve = total_ca_ve  # L86 equivalent

    # --- Section B: Travaux Remboursables ---
    enc_devis_brts = enc.get(("trvx_cciale", "Dévis brts P."), 0)
    enc_devis_tr_part = enc.get(("trvx_cciale", "Dévis T.R. part"), 0)
    enc_devis_tr_ext = enc.get(("trvx_cciale", "Dévis T.R. Ext."), 0)
    brchts_neufs = enc_devis_brts + enc_devis_tr_part + enc_devis_tr_ext

    enc_frais_coupures = enc.get(("trvx_cciale", "Frais de coupures"), 0)
    penalites = enc_frais_coupures * (1 + TVA_RATE)

    devis_ext = ca_spec.get("Dévis ext. part.", 0) or 0
    fraudes_trvx = ca_spec.get("Fraudes travaux", 0) or 0

    enc_frais_pose = enc.get(("trvx_cciale", "Frais pose cptrs"), 0)
    enc_frais_verif = enc.get(("trvx_cciale", "Frais vérif/étalon."), 0)
    enc_mutation = enc.get(("trvx_cciale", "Mutation"), 0)
    autres_trvx_auto = enc_frais_pose + enc_frais_verif + enc_mutation
    autres_trvx = autres_trvx_auto + complement

    total_trvx_remb = brchts_neufs + penalites + devis_ext + autres_trvx + fraudes_trvx

    # --- CA GLOBAL ---
    ca_global = total_ve + total_trvx_remb

    # --- Encaissements totaux ---
    enc_cciale = sum(v for (s, _), v in enc.items() if s == "cciale")
    enc_adm = sum(v for (s, _), v in enc.items() if s == "adm")
    enc_banques = sum(v for (s, _), v in enc.items() if s == "banques")
    total_vte_eau = enc_cciale + enc_adm + enc_banques

    enc_trvx_cciale = sum(v for (s, _), v in enc.items() if s == "trvx_cciale")
    enc_trvx_adm = sum(v for (s, _), v in enc.items() if s == "trvx_adm")
    total_travaux_enc = enc_trvx_cciale + enc_trvx_adm

    asc = enc.get(("asc", "ASC"), 0)
    total_encaissements = total_vte_eau + total_travaux_enc + asc

    # Paiements électroniques
    enc_electroniques = enc.get(("cciale", "Enc. Électroniques"), 0)

    # --- Emissions fraîches & recouvrement ---
    facturation_ef = (
        sum(ca_auto_details.get(c, 0) for c in [
            "Particuliers <= 10m3", "Particuliers > 10m3 T2", "Particuliers > 10m3 T3",
            "Sonel 870", "Sonel 872",
            "Cadre Eneo 890", "Cadre Eneo 892",
            "B.F. Payantes", "Dépasst agts CDE",
            "Partants > 10m3", "Partants <= 10m3", "Fraudes",
        ])
        + eneo_871 + eneo_873
        + gco_ca + loc_part + loc_gco
        + ca_communes + loc_bc + loc_bfc
    ) * (1 + TVA_RATE)

    recouvrement_ef = (
        enc.get(("cciale", "Part. 1 & 2"), 0)
        + enc.get(("cciale", "Enc. Électroniques"), 0)
        + enc.get(("cciale", "GCO"), 0)
        + enc.get(("cciale", "Hors site"), 0)
        + enc.get(("cciale", "Communes"), 0)
    )

    taux_recouvrement_ef = recouvrement_ef / facturation_ef if facturation_ef else 0

    # --- Données fiscales ---
    tranche_sociale = ca_auto_details.get("Particuliers <= 10m3", 0) + ca_auto_details.get("Particuliers > 10m3 T2", 0)
    ca_adm_ht = ca_auto_details["Administrations"] + loc_adm
    ca_hors_adm_ht = total_ve - ca_adm_ht
    ca_total_ttc = total_ve * (1 + TVA_RATE)
    trvx_ttc = total_trvx_remb * (1 + TVA_RATE)

    # --- Données Budget ---
    vente_eau_budget = total_ca_ve * (1 + TVA_RATE)
    trvx_remb_budget = total_trvx_remb - (enc_devis_brts + enc_devis_tr_part)
    recouvrement_impayes = (
        enc.get(("cciale", "Impayés CDE"), 0)
        + enc.get(("cciale", "Clts douteux CDE"), 0)
        + enc.get(("cciale", "Clts douteux CW"), 0)
    )
    fraude_enc = enc.get(("trvx_cciale", "Enc fact fraude"), 0)
    sinistre_enc = enc.get(("trvx_cciale", "Sinistres"), 0)
    penalites_enc = enc_frais_coupures
    loc_budget = total_locations * (1 + TVA_RATE)
    branchements_budget = enc_devis_brts + enc_devis_tr_part

    # --- Taux d'encaissement ---
    taux_enc_ve = total_vte_eau / total_ve if total_ve else 0
    taux_enc_trvx = total_travaux_enc / total_trvx_remb if total_trvx_remb else 0
    taux_enc_global = total_encaissements / ca_global if ca_global else 0

    return {
        # Section A - CA Vente Eau
        "ca_auto_details": ca_auto_details,
        "total_ca_auto": total_ca_auto,
        "eneo_871": eneo_871, "eneo_873": eneo_873,
        "gco_ca": gco_ca,
        "locations": {"Part": loc_part, "GCO": loc_gco, "ADM": loc_adm, "BC": loc_bc, "BFC": loc_bfc},
        "total_locations": total_locations,
        "total_ca_spec": total_ca_spec,
        "total_ca_ve": total_ca_ve,
        "total_ve": total_ve,
        # Répartition par catégorie client
        "ca_particuliers": ca_particuliers,
        "ca_gco": ca_gco,
        "ca_communes": ca_communes,
        "ca_adm": ca_adm,
        "ca_camwater": ca_camwater,
        # Section B - Travaux Remboursables
        "brchts_neufs": brchts_neufs,
        "penalites": penalites,
        "devis_ext": devis_ext,
        "autres_trvx_auto": autres_trvx_auto,
        "complement": complement,
        "autres_trvx": autres_trvx,
        "fraudes_trvx": fraudes_trvx,
        "total_trvx_remb": total_trvx_remb,
        # CA Global
        "ca_global": ca_global,
        # Encaissements
        "enc_cciale": enc_cciale,
        "enc_adm_enc": enc_adm,
        "enc_banques": enc_banques,
        "enc_vte_eau": total_vte_eau,
        "enc_travaux": total_travaux_enc,
        "enc_asc": asc,
        "total_encaissements": total_encaissements,
        "enc_electroniques": enc_electroniques,
        # Taux d'encaissement
        "taux_enc_ve": taux_enc_ve,
        "taux_enc_trvx": taux_enc_trvx,
        "taux_enc_global": taux_enc_global,
        # Recouvrement EF
        "facturation_ef": facturation_ef,
        "recouvrement_ef": recouvrement_ef,
        "taux_recouvrement_ef": taux_recouvrement_ef,
        # Fiscal
        "tranche_sociale": tranche_sociale,
        "ca_adm_ht": ca_adm_ht,
        "ca_hors_adm_ht": ca_hors_adm_ht,
        "ca_total_ttc": ca_total_ttc,
        "trvx_ttc": trvx_ttc,
        # Budget
        "budget": {
            "vente_eau": vente_eau_budget,
            "trvx_remb": trvx_remb_budget,
            "recouvrement_impayes": recouvrement_impayes,
            "fraude": fraude_enc,
            "sinistre": sinistre_enc,
            "penalites": penalites_enc,
            "locations": loc_budget,
            "branchements": branchements_budget,
        },
        # Volumes
        "total_volumes": sum(volumes.values()),
    }


# ═══════════════════════════════════════════════════════════════
# Agrégation multi-niveaux
# ═══════════════════════════════════════════════════════════════

def get_agences_dr(dr_code):
    db = get_db()
    rows = db.execute("""
        SELECT a.id, a.nom FROM agences a
        JOIN directions_regionales d ON a.dr_id = d.id
        WHERE d.code = ? ORDER BY a.nom
    """, (dr_code,)).fetchall()
    db.close()
    return [(r['id'], r['nom']) for r in rows]


def _aggregate_dicts(target, source):
    """Agrège source dans target, additionnant les valeurs numériques."""
    for key, val in source.items():
        if key == "ca_auto_details":
            continue
        if isinstance(val, (int, float)):
            target[key] = target.get(key, 0) + val
        elif isinstance(val, dict):
            if key not in target:
                target[key] = {}
            for k2, v2 in val.items():
                if isinstance(v2, (int, float)):
                    target[key][k2] = target[key].get(k2, 0) + v2


def _fix_taux(d):
    """Recalcule les taux après agrégation."""
    if d.get("facturation_ef", 0) > 0:
        d["taux_recouvrement_ef"] = d.get("recouvrement_ef", 0) / d["facturation_ef"]
    else:
        d["taux_recouvrement_ef"] = 0
    if d.get("total_ve", 0) > 0:
        d["taux_enc_ve"] = d.get("enc_vte_eau", 0) / d["total_ve"]
    else:
        d["taux_enc_ve"] = 0
    if d.get("total_trvx_remb", 0) > 0:
        d["taux_enc_trvx"] = d.get("enc_travaux", 0) / d["total_trvx_remb"]
    else:
        d["taux_enc_trvx"] = 0
    if d.get("ca_global", 0) > 0:
        d["taux_enc_global"] = d.get("total_encaissements", 0) / d["ca_global"]
    else:
        d["taux_enc_global"] = 0
    if d.get("total_encaissements", 0) > 0:
        d["pct_paiements_elec"] = d.get("enc_electroniques", 0) / d["total_encaissements"]
    else:
        d["pct_paiements_elec"] = 0


def calcul_dr(dr_code, mois, exercice=2026):
    """Agrège les calculs de toutes les agences d'une DR pour un mois."""
    agences = get_agences_dr(dr_code)
    if not agences:
        return None
    totaux = {}
    for ag_id, _ in agences:
        ca = calcul_ca_agence(ag_id, mois, exercice)
        _aggregate_dicts(totaux, ca)
    _fix_taux(totaux)
    return totaux


def calcul_national(mois, exercice=2026):
    """Agrège toutes les DRs = Ensemble CAMWATER pour un mois."""
    totaux = {}
    details_dr = {}
    for dr_code in STRUCTURE_CW:
        dr_data = calcul_dr(dr_code, mois, exercice)
        if dr_data:
            details_dr[dr_code] = dr_data
            _aggregate_dicts(totaux, dr_data)
    _fix_taux(totaux)
    totaux["details_dr"] = details_dr
    return totaux


# ═══════════════════════════════════════════════════════════════
# Calculs sur plage de mois
# ═══════════════════════════════════════════════════════════════

def calcul_cumul_agence(agence_id, mois_debut, mois_fin, exercice=2026):
    """Cumul d'une agence sur une plage de mois."""
    totaux = {}
    for m in range(mois_debut, mois_fin + 1):
        data = calcul_ca_agence(agence_id, m, exercice)
        _aggregate_dicts(totaux, data)
    _fix_taux(totaux)
    return totaux


def calcul_cumul_dr(dr_code, mois_debut, mois_fin, exercice=2026):
    """Cumul d'une DR sur une plage de mois."""
    totaux = {}
    for m in range(mois_debut, mois_fin + 1):
        dr_data = calcul_dr(dr_code, m, exercice)
        if dr_data:
            _aggregate_dicts(totaux, dr_data)
    _fix_taux(totaux)
    return totaux


def calcul_cumul_national(mois_debut, mois_fin, exercice=2026):
    """Cumul national sur une plage de mois."""
    totaux = {}
    for m in range(mois_debut, mois_fin + 1):
        data = calcul_national(m, exercice)
        data.pop("details_dr", None)
        _aggregate_dicts(totaux, data)
    _fix_taux(totaux)
    return totaux


def calcul_site(site_type, site_id, mois_debut, mois_fin, exercice=2026):
    """Calcul unifié : site_type='national'|'dr'|'agence', site_id=code DR ou agence_id."""
    if site_type == 'agence':
        return calcul_cumul_agence(int(site_id), mois_debut, mois_fin, exercice)
    elif site_type == 'dr':
        return calcul_cumul_dr(site_id, mois_debut, mois_fin, exercice)
    else:
        return calcul_cumul_national(mois_debut, mois_fin, exercice)


# ═══════════════════════════════════════════════════════════════
# Branchements (par agence, agrégé DR et national)
# ═══════════════════════════════════════════════════════════════

def get_branchements_agence(agence_id, mois_debut, mois_fin, exercice=2026):
    db = get_db()
    rows = db.execute("""
        SELECT type, SUM(valeur) as total FROM branchements
        WHERE agence_id=? AND exercice=? AND mois BETWEEN ? AND ?
        GROUP BY type
    """, (agence_id, exercice, mois_debut, mois_fin)).fetchall()
    db.close()
    return {r['type']: r['total'] for r in rows}


def get_branchements_dr(dr_code, mois_debut, mois_fin, exercice=2026):
    db = get_db()
    rows = db.execute("""
        SELECT b.type, SUM(b.valeur) as total
        FROM branchements b
        JOIN agences a ON b.agence_id = a.id
        JOIN directions_regionales d ON a.dr_id = d.id
        WHERE d.code=? AND b.exercice=? AND b.mois BETWEEN ? AND ?
        GROUP BY b.type
    """, (dr_code, exercice, mois_debut, mois_fin)).fetchall()
    db.close()
    return {r['type']: r['total'] for r in rows}


def get_branchements_national(mois_debut, mois_fin, exercice=2026):
    db = get_db()
    rows = db.execute("""
        SELECT type, SUM(valeur) as total FROM branchements
        WHERE exercice=? AND mois BETWEEN ? AND ? GROUP BY type
    """, (exercice, mois_debut, mois_fin)).fetchall()
    db.close()
    return {r['type']: r['total'] for r in rows}


def get_branchements_par_dr(mois_debut, mois_fin, exercice=2026):
    """Branchements ventilés par DR (pour le graphique)."""
    db = get_db()
    rows = db.execute("""
        SELECT d.code, b.type, SUM(b.valeur) as total
        FROM branchements b
        JOIN agences a ON b.agence_id = a.id
        JOIN directions_regionales d ON a.dr_id = d.id
        WHERE b.exercice=? AND b.mois BETWEEN ? AND ?
        GROUP BY d.code, b.type
    """, (exercice, mois_debut, mois_fin)).fetchall()
    db.close()
    result = {}
    for r in rows:
        if r['code'] not in result:
            result[r['code']] = {}
        result[r['code']][r['type']] = r['total']
    return result


# ═══════════════════════════════════════════════════════════════
# Historique et comparaison N/N-1
# ═══════════════════════════════════════════════════════════════

def get_historique_cumul(mois_debut, mois_fin, exercice, table="historique_ca"):
    db = get_db()
    row = db.execute(
        f"SELECT SUM(total) as s FROM {table} WHERE exercice=? AND mois BETWEEN ? AND ?",
        (exercice, mois_debut, mois_fin)).fetchone()
    db.close()
    return row['s'] if row and row['s'] else 0


def calcul_evolution(valeur_n, valeur_n1):
    if valeur_n1 == 0:
        return valeur_n, 0
    diff = valeur_n - valeur_n1
    taux = diff / abs(valeur_n1)
    return diff, taux


# ═══════════════════════════════════════════════════════════════
# Dashboard KPIs v2
# ═══════════════════════════════════════════════════════════════

def calcul_dashboard(mois_debut, mois_fin, exercice=2026, site_type='national', site_id=None):
    """Calcule tous les KPIs pour le dashboard décideur."""

    # --- Cumul principal sur la plage sélectionnée ---
    cumul = calcul_site(site_type, site_id, mois_debut, mois_fin, exercice)

    # --- Comparaison N-1 (mêmes mois, exercice précédent) ---
    cumul_n1 = calcul_site(site_type, site_id, mois_debut, mois_fin, exercice - 1)

    evolutions = {}
    for key in ["ca_global", "total_encaissements", "total_volumes",
                "total_ve", "total_trvx_remb"]:
        val_n = cumul.get(key, 0)
        val_n1 = cumul_n1.get(key, 0) if cumul_n1 else 0
        _, taux = calcul_evolution(val_n, val_n1)
        evolutions[key] = {"valeur_n": val_n, "valeur_n1": val_n1, "taux": taux}

    # Évolution du taux de recouvrement EF
    taux_recouv_n = cumul.get("taux_recouvrement_ef", 0)
    taux_recouv_n1 = cumul_n1.get("taux_recouvrement_ef", 0) if cumul_n1 else 0
    evolutions["taux_recouvrement_ef"] = {
        "valeur_n": taux_recouv_n, "valeur_n1": taux_recouv_n1,
        "taux": taux_recouv_n - taux_recouv_n1
    }

    # --- KPIs par DR (cumul sur la plage) ---
    kpis_dr = {}
    for dr_code in STRUCTURE_CW:
        dr_cumul = calcul_cumul_dr(dr_code, mois_debut, mois_fin, exercice)
        kpis_dr[dr_code] = {
            "ca_global": dr_cumul.get("ca_global", 0),
            "total_encaissements": dr_cumul.get("total_encaissements", 0),
            "total_volumes": dr_cumul.get("total_volumes", 0),
            "taux_recouvrement_ef": dr_cumul.get("taux_recouvrement_ef", 0),
            "taux_enc_ve": dr_cumul.get("taux_enc_ve", 0),
            "taux_enc_trvx": dr_cumul.get("taux_enc_trvx", 0),
            "taux_enc_global": dr_cumul.get("taux_enc_global", 0),
            "enc_electroniques": dr_cumul.get("enc_electroniques", 0),
            "pct_paiements_elec": dr_cumul.get("pct_paiements_elec", 0),
        }

    # --- Répartition catégories clients ---
    repartition_clients = {
        "Particuliers": cumul.get("ca_particuliers", 0),
        "GCO": cumul.get("ca_gco", 0),
        "Communes": cumul.get("ca_communes", 0),
        "Administrations": cumul.get("ca_adm", 0),
        "CAMWATER": cumul.get("ca_camwater", 0),
    }

    # --- Évolution mensuelle (pour graphiques) ---
    evolution_mensuelle = []
    for m in range(mois_debut, mois_fin + 1):
        if site_type == 'national':
            data_m = calcul_national(m, exercice)
            data_m.pop("details_dr", None)
        elif site_type == 'dr':
            data_m = calcul_dr(site_id, m, exercice) or {}
        else:
            data_m = calcul_ca_agence(int(site_id), m, exercice) or {}
        evolution_mensuelle.append({
            "mois": m,
            "ca_global": data_m.get("ca_global", 0),
            "encaissements": data_m.get("total_encaissements", 0),
            "volumes": data_m.get("total_volumes", 0),
        })

    # --- Branchements ---
    if site_type == 'national':
        brch = get_branchements_national(mois_debut, mois_fin, exercice)
    elif site_type == 'dr':
        brch = get_branchements_dr(site_id, mois_debut, mois_fin, exercice)
    else:
        brch = get_branchements_agence(int(site_id), mois_debut, mois_fin, exercice)

    brch_par_dr = get_branchements_par_dr(mois_debut, mois_fin, exercice)

    # --- Objectifs ---
    db = get_db()

    # Requête adaptée selon le scope : national ou DR
    if site_type == 'national' or not site_id:
        obj_rows = db.execute("""
            SELECT rubrique, SUM(montant) as total FROM objectifs
            WHERE exercice=? AND scope_type='national'
            GROUP BY rubrique
        """, (exercice,)).fetchall()
    elif site_type == 'dr':
        dr_row = db.execute("SELECT id FROM directions_regionales WHERE code=?", (site_id,)).fetchone()
        dr_id = dr_row['id'] if dr_row else None
        obj_rows = db.execute("""
            SELECT rubrique, SUM(montant) as total FROM objectifs
            WHERE exercice=? AND scope_type='dr' AND scope_id=?
            GROUP BY rubrique
        """, (exercice, dr_id)).fetchall()
    else:
        obj_rows = db.execute("""
            SELECT rubrique, SUM(montant) as total FROM objectifs
            WHERE exercice=? AND scope_type=? AND scope_id=?
            GROUP BY rubrique
        """, (exercice, site_type, site_id)).fetchall()

    objectifs = {r['rubrique']: r['total'] for r in obj_rows}

    # Proratiser les objectifs annuels sur la période sélectionnée
    nb_mois_periode = mois_fin - mois_debut + 1
    objectifs_prorata = {}
    for rub, total in objectifs.items():
        objectifs_prorata[rub] = (total / 12) * nb_mois_periode if total else 0

    # Objectif encaissements : chercher sous plusieurs noms possibles
    objectif_enc = (objectifs_prorata.get('Encaissements', 0)
                    or objectifs_prorata.get('Encaissements facturation fraîche', 0))
    taux_realisation = (cumul.get("total_encaissements", 0) / objectif_enc) if objectif_enc else 0

    # Construire les objectifs vs réalisations pour toutes les rubriques
    # Mapping flexible : rubrique objectif → clé cumul ou branchements
    RUBRIQUE_TO_REALISE = {
        # CA
        'CA Vente Eau': lambda c, b: c.get('total_ve', 0),
        'CA Travaux': lambda c, b: c.get('total_trvx_remb', 0),
        'CA Travaux Remboursables': lambda c, b: c.get('total_trvx_remb', 0),
        'CA Branchements': lambda c, b: c.get('brchts_neufs', 0),
        # Encaissements
        'Encaissements': lambda c, b: c.get('total_encaissements', 0),
        'Encaissements facturation fraîche': lambda c, b: c.get('total_encaissements', 0),
        'Encaissements impayés': lambda c, b: 0,  # Pas de champ spécifique
        # Volumes
        'Volumes': lambda c, b: c.get('total_volumes', 0),
        'Volumes facturés': lambda c, b: c.get('total_volumes', 0),
        # Branchements
        'Nb branchements vendus': lambda c, b: b.get('vendus', 0),
        'Branchements Vendus': lambda c, b: b.get('vendus', 0),
        'Branchements Exécutés': lambda c, b: b.get('exécutés', 0) or b.get('executes', 0),
        'Nb compteurs à renouveler': lambda c, b: 0,
        # Impayés
        'Impayés Actifs': lambda c, b: c.get('impayes_actifs', 0),
        'Impayés Résiliés': lambda c, b: c.get('impayes_resilies', 0),
    }

    objectifs_vs_real = []
    for rub in objectifs_prorata:
        obj_val = objectifs_prorata[rub]
        if obj_val == 0:
            continue
        # Chercher le getter correspondant
        getter = RUBRIQUE_TO_REALISE.get(rub)
        if getter:
            real_val = getter(cumul, brch)
        else:
            real_val = 0
        taux = (real_val / obj_val) if obj_val else 0
        objectifs_vs_real.append({
            "rubrique": rub,
            "objectif": obj_val,
            "objectif_annuel": objectifs.get(rub, 0),
            "realise": real_val,
            "taux": taux,
        })

    # Trier : les plus importants en premier (Encaissements, CA, Volumes, Branchements)
    priority = {'Encaissements': 0, 'Encaissements facturation fraîche': 0, 'CA Vente Eau': 1,
                'CA Travaux Remboursables': 2, 'CA Branchements': 3, 'Volumes': 4,
                'Nb branchements vendus': 5}
    objectifs_vs_real.sort(key=lambda x: priority.get(x['rubrique'], 10))

    # --- Paiements électroniques (depuis le module PE dédié) ---
    # Priorité : données validées (definitif), sinon données CSV brutes
    pe_total = 0
    try:
        pe_def = db.execute("""
            SELECT COALESCE(SUM(montant_total), 0) as total
            FROM paiements_elec_definitif
            WHERE exercice=? AND mois_debut<=? AND mois_fin>=?
        """, (exercice, mois_fin, mois_debut)).fetchone()
        if pe_def and pe_def['total'] and pe_def['total'] > 0:
            pe_total = pe_def['total']
        else:
            pe_csv = db.execute("""
                SELECT COALESCE(SUM(montant), 0) as total
                FROM paiements_elec_csv
                WHERE exercice=? AND (mois BETWEEN ? AND ? OR mois IS NULL)
            """, (exercice, mois_debut, mois_fin)).fetchone()
            pe_total = pe_csv['total'] if pe_csv and pe_csv['total'] else 0
    except Exception:
        pe_total = 0

    total_enc = cumul.get("total_encaissements", 0)
    pct_elec = pe_total / total_enc if total_enc > 0 else 0

    db.close()

    return {
        "cumul": cumul,
        "evolutions": evolutions,
        "kpis_dr": kpis_dr,
        "repartition_clients": repartition_clients,
        "evolution_mensuelle": evolution_mensuelle,
        "branchements": brch,
        "branchements_par_dr": brch_par_dr,
        "objectifs": objectifs,
        "objectifs_prorata": objectifs_prorata,
        "objectifs_vs_real": objectifs_vs_real,
        "objectif_enc": objectif_enc,
        "taux_realisation": taux_realisation,
        "taux_recouvrement_national": cumul.get("taux_recouvrement_ef", 0),
        "pct_paiements_elec": pct_elec,
        "pe_total": pe_total,
        "site_type": site_type,
        "site_id": site_id,
        "mois_debut": mois_debut,
        "mois_fin": mois_fin,
    }


# ═══════════════════════════════════════════════════════════════
# Classement des performances (objectifs)
# ═══════════════════════════════════════════════════════════════

def classement_performances(mois_debut, mois_fin, exercice=2026, rubrique='Encaissements'):
    """Classe les DR par taux de réalisation vs objectif."""
    db = get_db()
    ranking = []
    for dr_code in STRUCTURE_CW:
        dr_cumul = calcul_cumul_dr(dr_code, mois_debut, mois_fin, exercice)
        obj = db.execute("""
            SELECT montant FROM objectifs
            WHERE exercice=? AND scope_type='dr'
            AND scope_id=(SELECT id FROM directions_regionales WHERE code=?)
            AND rubrique=? AND mois IS NULL
        """, (exercice, dr_code, rubrique)).fetchone()
        objectif = obj['montant'] if obj else 0
        # Proratiser l'objectif annuel sur la période
        objectif_periode = objectif * (mois_fin - mois_debut + 1) / 12 if objectif else 0

        if rubrique == 'Encaissements':
            realise = dr_cumul.get("total_encaissements", 0)
        elif rubrique == 'CA':
            realise = dr_cumul.get("ca_global", 0)
        elif rubrique == 'Volumes':
            realise = dr_cumul.get("total_volumes", 0)
        else:
            realise = 0

        taux = realise / objectif_periode if objectif_periode else 0
        ranking.append({
            "dr_code": dr_code,
            "objectif": objectif,
            "objectif_periode": objectif_periode,
            "realise": realise,
            "taux": taux,
        })
    db.close()
    ranking.sort(key=lambda x: x["taux"], reverse=True)
    for i, r in enumerate(ranking):
        r["rang"] = i + 1
    return ranking
