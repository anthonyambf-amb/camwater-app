"""Module de surveillance (Monitoring) — Alertes automatisées CAMWATER v2.

Six indicateurs prudentiels :
  1. Taux de Facturation
  2. Tarif Moyen HT du m³
  3. Taux de Recouvrement des Émissions Fraîches
  4. Taux de Réalisation des Branchements dans les Délais (≤ 15 j)
  5. Taux de Recouvrement des Impayés (Créances Antérieures)
  6. Taux de Réémission des Factures
"""
from database import get_db, STRUCTURE_CW

# ── Valeurs par défaut (surchargées via monitoring_params) ────────────────────
_SEUIL_FACTURATION          = 0.95
_SEUIL_TARIF_VARIATION      = 0.05
_SEUIL_REEMISSIONS          = 0.02
_SEUIL_IMPAYES_PCT_RECETTES = 0.05
_SEUIL_DELAIS_WARN_JOURS    = 12.0


# ════════════════════════════════════════════════════════════════════════════
# Paramètres configurables
# ════════════════════════════════════════════════════════════════════════════

def get_params(exercice=2026):
    db = get_db()
    rows = db.execute(
        "SELECT cle, valeur, libelle FROM monitoring_params WHERE exercice=?", (exercice,)
    ).fetchall()
    db.close()
    p = {r['cle']: r['valeur'] for r in rows}
    libelles = {r['cle']: r['libelle'] for r in rows}
    params = {
        'seuil_facturation':          p.get('seuil_facturation',          _SEUIL_FACTURATION),
        'seuil_tarif_variation':      p.get('seuil_tarif_variation',      _SEUIL_TARIF_VARIATION),
        'seuil_reemissions':          p.get('seuil_reemissions',          _SEUIL_REEMISSIONS),
        'seuil_impayes_pct_recettes': p.get('seuil_impayes_pct_recettes', _SEUIL_IMPAYES_PCT_RECETTES),
        'seuil_delais_warn_jours':    p.get('seuil_delais_warn_jours',    _SEUIL_DELAIS_WARN_JOURS),
    }
    params['_libelles'] = libelles
    return params


def save_params(updates, exercice=2026):
    db = get_db()
    for cle, valeur in updates.items():
        db.execute("""INSERT INTO monitoring_params (exercice, cle, valeur)
                      VALUES (?, ?, ?)
                      ON CONFLICT(exercice, cle)
                      DO UPDATE SET valeur=excluded.valeur""",
                   (exercice, cle, float(valeur)))
    db.commit()
    db.close()


# ════════════════════════════════════════════════════════════════════════════
# Helpers BD
# ════════════════════════════════════════════════════════════════════════════

def _get_all_agences():
    db = get_db()
    rows = db.execute("""
        SELECT a.id, a.nom, d.code as dr_code
        FROM agences a JOIN directions_regionales d ON a.dr_id = d.id
        ORDER BY d.code, a.nom
    """).fetchall()
    db.close()
    return [dict(r) for r in rows]


def _alert(type_, indicateur, ag_id, ag_nom, dr_code, mois, valeur, seuil, message):
    return {
        'type': type_,
        'indicateur': indicateur,
        'agence_id': ag_id,
        'agence_nom': ag_nom,
        'dr_code': dr_code,
        'mois': mois,
        'valeur': valeur,
        'seuil': seuil,
        'message': message,
    }


# ════════════════════════════════════════════════════════════════════════════
# INDICATEUR 1 — Taux de Facturation
# Formule : (abonnés_facturés / abonnés_actifs) × 100
# Critique : < seuil (défaut 95%)
# Warning  : baisse continue sur 2 cycles consécutifs
# ════════════════════════════════════════════════════════════════════════════

def ind_facturation(agence_id, mois, exercice=2026):
    db = get_db()
    row = db.execute(
        "SELECT abonnes_actifs, abonnes_factures FROM facturation_abonnes "
        "WHERE agence_id=? AND mois=? AND exercice=?",
        (agence_id, mois, exercice)
    ).fetchone()
    db.close()
    if not row or not row['abonnes_actifs']:
        return None
    return {
        'taux': row['abonnes_factures'] / row['abonnes_actifs'],
        'abonnes_actifs': row['abonnes_actifs'],
        'abonnes_factures': row['abonnes_factures'],
    }


def alerte_facturation(ag_id, ag_nom, dr_code, mois, exercice, params):
    seuil = params['seuil_facturation']
    cur = ind_facturation(ag_id, mois, exercice)
    if cur is None:
        return []

    taux = cur['taux']
    if taux < seuil:
        return [_alert('critique', 'Taux de Facturation', ag_id, ag_nom, dr_code, mois, taux, seuil,
            f"Taux de facturation critique : {taux*100:.1f}% (seuil {seuil*100:.0f}%) "
            f"— {cur['abonnes_factures']}/{cur['abonnes_actifs']} abonnés facturés")]

    alertes = []
    # Warning : baisse continue sur 2 cycles consécutifs
    if mois >= 3:
        prev1 = ind_facturation(ag_id, mois - 1, exercice)
        prev2 = ind_facturation(ag_id, mois - 2, exercice)
        if prev1 and prev2 and taux < prev1['taux'] < prev2['taux']:
            alertes.append(_alert('warning', 'Taux de Facturation', ag_id, ag_nom, dr_code, mois, taux, seuil,
                f"Baisse continue du taux de facturation sur 3 mois : "
                f"{prev2['taux']*100:.1f}% → {prev1['taux']*100:.1f}% → {taux*100:.1f}%"))
    return alertes


# ════════════════════════════════════════════════════════════════════════════
# INDICATEUR 2 — Tarif Moyen HT du m³
# Formule : CA Vente Eau HT / Volume total m³
# Critique : variation > 5% vs moyenne historique 6 mois
# Warning  : anomalie sur > 3 agences de la même DR
# ════════════════════════════════════════════════════════════════════════════

def ind_tarif_m3(agence_id, mois, exercice=2026):
    from calculs import calcul_ca_agence
    ca = calcul_ca_agence(agence_id, mois, exercice)
    vol = ca.get('total_volumes', 0)
    ca_ve = ca.get('total_ca_ve', 0)
    if not vol:
        return None
    return {'tarif_moyen': ca_ve / vol, 'ca_ve': ca_ve, 'volumes': vol}


def _tarif_hist_moy(agence_id, mois_ref, exercice=2026, nb_mois=6):
    vals = []
    for m in range(max(1, mois_ref - nb_mois), mois_ref):
        t = ind_tarif_m3(agence_id, m, exercice)
        if t:
            vals.append(t['tarif_moyen'])
    return sum(vals) / len(vals) if vals else None


def alerte_tarif_m3(ag_id, ag_nom, dr_code, mois, exercice, params, agences_dr):
    seuil_var = params['seuil_tarif_variation']
    cur = ind_tarif_m3(ag_id, mois, exercice)
    if cur is None:
        return []

    hist = _tarif_hist_moy(ag_id, mois, exercice)
    if not hist:
        return []

    variation = abs(cur['tarif_moyen'] - hist) / hist
    alertes = []

    if variation > seuil_var:
        direction = 'hausse' if cur['tarif_moyen'] > hist else 'baisse'
        alertes.append(_alert('critique', 'Tarif Moyen HT/m³', ag_id, ag_nom, dr_code, mois,
            cur['tarif_moyen'], hist,
            f"Variation brutale du tarif m³ à la {direction} : "
            f"{cur['tarif_moyen']:.0f} FCFA/m³ vs moy. hist. {hist:.0f} FCFA/m³ "
            f"({variation*100:.1f}% d'écart)"))

    # Warning : anomalie sur > 3 agences de la même DR
    anomalies_dr = 0
    for ag2_id, _ in agences_dr:
        t2 = ind_tarif_m3(ag2_id, mois, exercice)
        h2 = _tarif_hist_moy(ag2_id, mois, exercice)
        if t2 and h2 and h2 > 0 and abs(t2['tarif_moyen'] - h2) / h2 > seuil_var:
            anomalies_dr += 1
    if anomalies_dr > 3:
        alertes.append(_alert('warning', 'Tarif Moyen HT/m³', ag_id, ag_nom, dr_code, mois,
            cur['tarif_moyen'], seuil_var,
            f"Fluctuation anormale du tarif m³ sur {anomalies_dr} agences de {dr_code}"))

    return alertes


# ════════════════════════════════════════════════════════════════════════════
# INDICATEUR 3 — Taux de Recouvrement des Émissions Fraîches
# Formule : (Enc. EF / Facturation fraîche) × 100
# >= 95% → OK ; 80%-95% → warning ; < 80% → critique
# Warning pente : stagnation ou baisse observée
# ════════════════════════════════════════════════════════════════════════════

def ind_recouvrement_ef(agence_id, mois_debut, mois_fin, exercice=2026):
    from calculs import calcul_cumul_agence
    data = calcul_cumul_agence(agence_id, mois_debut, mois_fin, exercice)
    return {
        'taux': data.get('taux_recouvrement_ef', 0),
        'recouvrement_ef': data.get('recouvrement_ef', 0),
        'facturation_ef': data.get('facturation_ef', 0),
    }


def alerte_recouvrement_ef(ag_id, ag_nom, dr_code, mois, exercice, params):
    cur = ind_recouvrement_ef(ag_id, mois, mois, exercice)
    taux = cur['taux']
    alertes = []

    if cur['facturation_ef'] <= 0:
        return alertes

    if taux < 0.80:
        alertes.append(_alert('critique', 'Taux Recouvrement EF', ag_id, ag_nom, dr_code, mois,
            taux, 0.80,
            f"Taux recouvrement EF insuffisant : {taux*100:.1f}% (seuil critique < 80%)"))
        return alertes

    if taux < 0.95:
        alertes.append(_alert('warning', 'Taux Recouvrement EF', ag_id, ag_nom, dr_code, mois,
            taux, 0.95,
            f"Taux recouvrement EF à surveiller : {taux*100:.1f}% (objectif ≥ 95%)"))
        return alertes

    # Warning pente décroissante sur 2 mois consécutifs (même si taux > 95%)
    if mois >= 3:
        p1 = ind_recouvrement_ef(ag_id, mois - 1, mois - 1, exercice)
        p2 = ind_recouvrement_ef(ag_id, mois - 2, mois - 2, exercice)
        if (p1['facturation_ef'] > 0 and p2['facturation_ef'] > 0
                and taux <= p1['taux'] and p1['taux'] <= p2['taux']):
            alertes.append(_alert('warning', 'Taux Recouvrement EF', ag_id, ag_nom, dr_code, mois,
                taux, 0.95,
                f"Pente décroissante taux EF : "
                f"{p2['taux']*100:.1f}% → {p1['taux']*100:.1f}% → {taux*100:.1f}%"))

    return alertes


# ════════════════════════════════════════════════════════════════════════════
# INDICATEUR 4 — Taux de Réalisation des Branchements dans les Délais (≤ 15 j)
# Formule : (branchements réalisés ≤ 15j / total devis payés) × 100
# Critique : < 100% (objectif réglementaire strict)
# Warning  : délai moyen ≥ 12 jours (sur échantillon récent)
# ════════════════════════════════════════════════════════════════════════════

def ind_branchements_delais(agence_id, mois, exercice=2026):
    db = get_db()
    row = db.execute(
        "SELECT total_devis_payes, dans_15j, delai_moyen_jours FROM branchements_delais "
        "WHERE agence_id=? AND mois=? AND exercice=?",
        (agence_id, mois, exercice)
    ).fetchone()
    db.close()
    if not row or not row['total_devis_payes']:
        return None
    return {
        'taux': row['dans_15j'] / row['total_devis_payes'],
        'dans_15j': row['dans_15j'],
        'total_devis_payes': row['total_devis_payes'],
        'delai_moyen_jours': row['delai_moyen_jours'],
    }


def alerte_branchements_delais(ag_id, ag_nom, dr_code, mois, exercice, params):
    seuil_warn = params['seuil_delais_warn_jours']
    cur = ind_branchements_delais(ag_id, mois, exercice)
    if cur is None:
        return []

    if cur['taux'] < 1.0:
        return [_alert('critique', 'Branchements dans les délais', ag_id, ag_nom, dr_code, mois,
            cur['taux'], 1.0,
            f"Délai réglementaire non respecté : {cur['taux']*100:.1f}% réalisés en ≤ 15j "
            f"({cur['dans_15j']}/{cur['total_devis_payes']} devis)")]

    alertes = []
    if cur['delai_moyen_jours'] is not None and cur['delai_moyen_jours'] >= seuil_warn:
        alertes.append(_alert('warning', 'Branchements dans les délais', ag_id, ag_nom, dr_code, mois,
            cur['delai_moyen_jours'], seuil_warn,
            f"Délai moyen de réalisation en hausse : {cur['delai_moyen_jours']:.1f} jours "
            f"(seuil d'alerte : {seuil_warn:.0f} jours)"))
    return alertes


# ════════════════════════════════════════════════════════════════════════════
# INDICATEUR 5 — Taux de Recouvrement des Impayés (Créances Antérieures)
# Formule : (Enc. impayés / Stock créances ciblées) × 100
# Critique : enc. impayés < seuil_impayes_pct_recettes × recettes mensuelles
# Warning 1 : baisse continue enc. impayés sur 2 mois consécutifs
# Warning 2 : croissance du portefeuille d'impayés
# ════════════════════════════════════════════════════════════════════════════

def _stock_impayes(agence_id, mois, exercice=2026):
    db = get_db()
    row = db.execute("""
        SELECT COALESCE(particuliers_actifs,0)+COALESCE(gco_actifs,0)
              +COALESCE(particuliers_resilies,0)+COALESCE(gco_resilies,0)
              +COALESCE(bf_actifs,0)+COALESCE(bfc_actifs,0)
              +COALESCE(bf_resilies,0)+COALESCE(bfc_resilies,0)
              +COALESCE(gestion_manuelle,0) AS total
        FROM impayes WHERE agence_id=? AND mois=? AND exercice=?
    """, (agence_id, mois, exercice)).fetchone()
    db.close()
    return row['total'] if row and row['total'] else 0


def ind_recouvrement_impayes(agence_id, mois, exercice=2026):
    from calculs import calcul_ca_agence
    ca = calcul_ca_agence(agence_id, mois, exercice)
    enc_impayes = ca.get('budget', {}).get('recouvrement_impayes', 0)
    total_enc = ca.get('total_encaissements', 0)
    stock = _stock_impayes(agence_id, mois, exercice)
    if not stock:
        return None
    return {
        'enc_impayes': enc_impayes,
        'stock': stock,
        'total_enc': total_enc,
        'taux_recouvrement': enc_impayes / stock,
        'pct_recettes': enc_impayes / total_enc if total_enc else 0,
    }


def alerte_recouvrement_impayes(ag_id, ag_nom, dr_code, mois, exercice, params):
    seuil_pct = params['seuil_impayes_pct_recettes']
    cur = ind_recouvrement_impayes(ag_id, mois, exercice)
    if cur is None:
        return []

    alertes = []

    # Critique : enc impayés trop faibles par rapport aux recettes
    if cur['total_enc'] > 0 and cur['pct_recettes'] < seuil_pct:
        alertes.append(_alert('critique', 'Recouvrement Impayés', ag_id, ag_nom, dr_code, mois,
            cur['pct_recettes'], seuil_pct,
            f"Recouvrement impayés insuffisant : {cur['pct_recettes']*100:.1f}% des recettes "
            f"(seuil {seuil_pct*100:.0f}%) — {cur['enc_impayes']:,.0f} FCFA encaissés"))
        return alertes

    # Warning 1 : baisse continue sur 2 mois consécutifs
    if mois >= 3:
        p1 = ind_recouvrement_impayes(ag_id, mois - 1, exercice)
        p2 = ind_recouvrement_impayes(ag_id, mois - 2, exercice)
        if p1 and p2 and cur['enc_impayes'] <= p1['enc_impayes'] <= p2['enc_impayes']:
            alertes.append(_alert('warning', 'Recouvrement Impayés', ag_id, ag_nom, dr_code, mois,
                cur['enc_impayes'], p1['enc_impayes'],
                f"Baisse continue encaissements impayés sur 3 mois : "
                f"{p2['enc_impayes']:,.0f} → {p1['enc_impayes']:,.0f} → "
                f"{cur['enc_impayes']:,.0f} FCFA"))

    # Warning 2 : croissance du portefeuille d'impayés
    if mois >= 2:
        stock_prev = _stock_impayes(ag_id, mois - 1, exercice)
        if stock_prev > 0 and cur['stock'] > stock_prev:
            pct_growth = (cur['stock'] - stock_prev) / stock_prev
            alertes.append(_alert('warning', 'Recouvrement Impayés', ag_id, ag_nom, dr_code, mois,
                cur['stock'], stock_prev,
                f"Portefeuille impayés en croissance : +{pct_growth*100:.1f}% vs M-1 "
                f"({stock_prev:,.0f} → {cur['stock']:,.0f} FCFA)"))

    return alertes


# ════════════════════════════════════════════════════════════════════════════
# INDICATEUR 6 — Taux de Réémission des Factures
# Formule : (factures annulées/réémises / total factures émises) × 100
# Critique : > 2%
# Warning  : augmentation sur 2 cycles consécutifs
# ════════════════════════════════════════════════════════════════════════════

def ind_reemissions(agence_id, mois, exercice=2026):
    db = get_db()
    row = db.execute(
        "SELECT nb_factures_emises, nb_reemissions FROM reemissions_factures "
        "WHERE agence_id=? AND mois=? AND exercice=?",
        (agence_id, mois, exercice)
    ).fetchone()
    db.close()
    if not row or not row['nb_factures_emises']:
        return None
    return {
        'taux': row['nb_reemissions'] / row['nb_factures_emises'],
        'nb_factures_emises': row['nb_factures_emises'],
        'nb_reemissions': row['nb_reemissions'],
    }


def alerte_reemissions(ag_id, ag_nom, dr_code, mois, exercice, params):
    seuil = params['seuil_reemissions']
    cur = ind_reemissions(ag_id, mois, exercice)
    if cur is None:
        return []

    taux = cur['taux']
    if taux > seuil:
        return [_alert('critique', 'Réémissions de Factures', ag_id, ag_nom, dr_code, mois,
            taux, seuil,
            f"Taux de réémission dépassé : {taux*100:.2f}% (seuil {seuil*100:.0f}%) "
            f"— {cur['nb_reemissions']}/{cur['nb_factures_emises']} factures réémises")]

    alertes = []
    # Warning : augmentation sur 2 cycles consécutifs
    if mois >= 3:
        p1 = ind_reemissions(ag_id, mois - 1, exercice)
        p2 = ind_reemissions(ag_id, mois - 2, exercice)
        if p1 and p2 and taux > p1['taux'] > p2['taux']:
            alertes.append(_alert('warning', 'Réémissions de Factures', ag_id, ag_nom, dr_code, mois,
                taux, seuil,
                f"Hausse continue du taux de réémission sur 3 mois : "
                f"{p2['taux']*100:.2f}% → {p1['taux']*100:.2f}% → {taux*100:.2f}%"))
    return alertes


# ════════════════════════════════════════════════════════════════════════════
# MOTEUR CENTRAL — Génération de toutes les alertes
# ════════════════════════════════════════════════════════════════════════════

def generer_alertes(mois, exercice=2026, scope='national', scope_id=None):
    """
    Calcule et retourne toutes les alertes actives.
    scope : 'national' | 'dr' | 'agence'
    scope_id : code DR (str) ou agence_id (int)
    """
    params = get_params(exercice)
    agences = _get_all_agences()

    if scope == 'dr' and scope_id:
        agences = [a for a in agences if a['dr_code'] == scope_id]
    elif scope == 'agence' and scope_id:
        agences = [a for a in agences if a['id'] == int(scope_id)]

    # Regrouper par DR pour Indicateur 2
    agences_par_dr = {}
    for a in agences:
        agences_par_dr.setdefault(a['dr_code'], []).append((a['id'], a['nom']))

    all_alertes = []

    for ag in agences:
        ag_id  = ag['id']
        ag_nom = ag['nom']
        dr     = ag['dr_code']
        dr_ags = agences_par_dr.get(dr, [])

        all_alertes.extend(alerte_facturation(ag_id, ag_nom, dr, mois, exercice, params))
        all_alertes.extend(alerte_tarif_m3(ag_id, ag_nom, dr, mois, exercice, params, dr_ags))
        all_alertes.extend(alerte_recouvrement_ef(ag_id, ag_nom, dr, mois, exercice, params))
        all_alertes.extend(alerte_branchements_delais(ag_id, ag_nom, dr, mois, exercice, params))
        all_alertes.extend(alerte_recouvrement_impayes(ag_id, ag_nom, dr, mois, exercice, params))
        all_alertes.extend(alerte_reemissions(ag_id, ag_nom, dr, mois, exercice, params))

    # Tri : critiques en premier, puis par DR, puis par agence
    all_alertes.sort(key=lambda a: (
        0 if a['type'] == 'critique' else 1,
        a['dr_code'],
        a['agence_nom'],
        a['indicateur'],
    ))

    nb_critiques = sum(1 for a in all_alertes if a['type'] == 'critique')
    nb_warnings  = sum(1 for a in all_alertes if a['type'] == 'warning')

    return {
        'alertes': all_alertes,
        'nb_critiques': nb_critiques,
        'nb_warnings': nb_warnings,
        'total': len(all_alertes),
        'mois': mois,
        'exercice': exercice,
        'params': {k: v for k, v in params.items() if k != '_libelles'},
    }


def synthese_par_dr(mois, exercice=2026):
    """Synthèse du nombre d'alertes par DR — pour affichage dans le dashboard principal."""
    result = {}
    for dr_code in STRUCTURE_CW:
        data = generer_alertes(mois, exercice, scope='dr', scope_id=dr_code)
        result[dr_code] = {
            'critiques': data['nb_critiques'],
            'warnings': data['nb_warnings'],
        }
    return result


def indicateurs_agence(agence_id, mois, exercice=2026):
    """Retourne les valeurs brutes des 6 indicateurs pour une agence/mois."""
    params = get_params(exercice)
    return {
        'facturation':       ind_facturation(agence_id, mois, exercice),
        'tarif_m3':          ind_tarif_m3(agence_id, mois, exercice),
        'recouvrement_ef':   ind_recouvrement_ef(agence_id, mois, mois, exercice),
        'branchements':      ind_branchements_delais(agence_id, mois, exercice),
        'impayes':           ind_recouvrement_impayes(agence_id, mois, exercice),
        'reemissions':       ind_reemissions(agence_id, mois, exercice),
        'params':            {k: v for k, v in params.items() if k != '_libelles'},
    }
