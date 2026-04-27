"""Base de données CAMWATER - Schéma v2."""
import sqlite3
import os

# Chemin de la base : configurable via la variable d'environnement
# CAMWATER_DATA_DIR (ex. /var/data sur Render). En local on garde data/ à
# côté du code. Le dossier est créé automatiquement s'il n'existe pas.
_DATA_DIR = os.environ.get(
    'CAMWATER_DATA_DIR',
    os.path.join(os.path.dirname(__file__), 'data')
)
os.makedirs(_DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(_DATA_DIR, 'camwater.db')

# Organisation: 12 DRs et leurs agences
STRUCTURE_CW = {
    "DRYA": ["Ekounou", "Tsinga", "Mvog Ada", "Etoudi", "Obili", "Soa", "Mbankomo", "Olembé", "Biteng", "Messamendongo"],
    "DRDA": ["Koumassi", "Deido", "Bassa", "Bonamoussadi", "Bonaberi", "Nyalla"],
    "DREN": ["Maroua", "Mokolo", "Yagoua", "Doukoula", "Kousseri", "Makari", "Mora", "Kolofata", "Maga", "Kaélé", "Koza", "Bogo", "Tokombéré"],
    "DRN": ["Garoua", "Guider", "Figuil", "Mayo Oulo", "Pitoa"],
    "DRA": ["Ngaoundéré", "Meiganga", "Tibati", "Banyo", "Mbé"],
    "DRC": ["Akonolinga", "Akono", "Ayos", "Bafia", "Batchenga", "Bikok", "Bokito", "Eseka", "Evodoula", "Makak", "Makenene", "Matomb", "Mbalmayo", "Mbandjock", "Mfou", "Monatélé", "Nanga Eboko", "Ndikinimeki", "Ngoumou", "Obala", "Okola", "Ombessa", "Sa'a", "Yoko"],
    "DRS": ["Ambam", "Campo", "Djoum", "Ebolowa", "Kribi", "Meyomessala", "Sangmélima", "Zoétélé"],
    "DRE": ["Bertoua", "Abong Mbang", "Batouri", "Belabo", "Yokadouma", "Dimako", "Lomié"],
    "DRO": ["Bafoussam", "Bafang", "Bandjoun", "Bangangté", "Tonga", "Bazou", "Dschang", "Foumban", "Foumbot", "Mbouda", "Melong", "Kekem", "Bankim", "Bamendjou", "Baham", "Bansoa", "Bana", "Bangoua", "Bayangam", "Bangou", "Batié"],
    "DRNO": ["Bamenda", "Batibo", "Fundong", "Jakiri", "Njikijem", "Mbengwi", "Ndop", "Njinikom", "Nkambè", "Wum"],
    "DRSO": ["Limbé", "Buea", "Kumba", "Tiko", "Mamfé", "Mundemba", "Muyuka", "Nguti"],
    "DRL": ["Nkongsamba", "Edea", "Loum", "Mbanga", "Njombé", "Manjo", "Penja", "Yabassi", "Ngambè", "Pouma", "Dizangué", "Dibang"],
}

# 22 catégories de volumes avec prix unitaires
CATEGORIES_VOLUMES = [
    ("Particuliers <= 10m3", 293),
    ("Particuliers > 10m3 T2", 364),
    ("Particuliers > 10m3 T3", 364),
    ("Sonel 870", 50),
    ("Sonel 871", 314),
    ("Sonel 872", 364),
    ("Sonel 873", 243),
    ("Cadre Eneo 890", 293),
    ("Cadre Eneo 891", 364),
    ("Cadre Eneo 892", 364),
    ("Cadre Eneo 880", 293),
    ("Cadre Eneo 881", 364),
    ("B.F. Payantes", 293),
    ("Dépasst agts CDE", 293),
    ("Dépasst Adm. CDE", 293),
    ("Ventes Directes", 0),
    ("Rappel T1", 293),
    ("Rappel T2", 364),
    ("Sinistres", 364),
    ("Partants <= 10m3", 293),
    ("Partants > 10m3", 364),
    ("Fraudes", 364),
]

CATEGORIES_GCO = ("GCO", 0)
CATEGORIES_ADM = ("Administrations", 382)
CATEGORIES_BC = ("Bâtiments communaux", 382)
CATEGORIES_BFC = ("B.F.C", 382)
CATEGORIES_CW = [
    ("Val Part Agent CDE", 293),
    ("Val Services CDE", 293),
    ("Val Part Adm CDE", 293),
    ("Val Part agts Camwater", 293),
]

# Rubriques encaissements
RUBRIQUES_ENC_CCIALE = [
    "Part. 1 & 2", "Enc. Électroniques", "Impayés CDE", "GCO",
    "Enc. Chèques", "Anticipations", "Hors site",
    "Clts douteux CDE", "Clts douteux CW", "Résil. à imp.",
    "Fact. CFD", "Frais imp tiers", "BEAC", "Aes sonel",
    "SCDP", "ASECNA", "CAMTEL", "CAMPOST", "CRTV",
    "CAMRAIL", "Université", "CHU", "Communes", "TVA eau", "Arrondi eau",
]

RUBRIQUES_ENC_ADM = [
    "Fraude", "Clients douteux", "Ventes en directe", "Résiliés avec imp.",
    "Fact sinistre", "Fact. CFD", "Litige", "Frais banque",
    "Chèque imp", "Communes", "TVA eau", "Profit arrondi",
]

RUBRIQUES_ENC_BANQUES = ["Domiciliés", "Non domiciliés"]

RUBRIQUES_ENC_TRVX_CCIALE = [
    "Enc fact fraude", "Dévis brts P.", "Dévis T.R. part", "Dévis T.R. Ext.",
    "Frais de coupures", "Frais pose cptrs", "Frais vérif/étalon.", "Mutation",
    "Dégrt° ch./rép. Cpt.", "Passage fusée", "Sinistres", "TVA tvxx", "Profit arrondi",
]

RUBRIQUES_ENC_TRVX_ADM = [
    "Enc fact fraude", "Sinistres", "Dévis brts P.", "Dévis T.R. part",
    "Dévis T.R. Ext.", "Dégrt° ch./rép. Cpt.", "Passage fusée", "TVA", "Profits et arrondi",
]

# Types de branchements
TYPES_BRANCHEMENTS = ["vendus", "exécutés", "pec", "moratoire"]

# Prix unitaires par catégorie (pour cumul CA auto)
CATEGORIES_PU = {
    "Particuliers <= 10m3": 293, "Particuliers > 10m3 T2": 364, "Particuliers > 10m3 T3": 364,
    "Sonel 870": 50, "Sonel 871": 314, "Sonel 872": 364, "Sonel 873": 243,
    "Cadre Eneo 890": 293, "Cadre Eneo 891": 364, "Cadre Eneo 892": 364,
    "Cadre Eneo 880": 293, "Cadre Eneo 881": 364,
    "B.F. Payantes": 293, "Dépasst agts CDE": 293, "Dépasst Adm. CDE": 293,
    "Ventes Directes": 0, "Rappel T1": 293, "Rappel T2": 364,
    "Sinistres": 364, "Partants <= 10m3": 293, "Partants > 10m3": 364, "Fraudes": 364,
    "GCO": 0, "Administrations": 382, "Bâtiments communaux": 382, "B.F.C": 382,
    "Val Part Agent CDE": 293, "Val Services CDE": 293, "Val Part Adm CDE": 293, "Val Part agts Camwater": 293,
}

TVA_RATE = 0.1925
MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
    -- Opérateurs (identification saisie)
    CREATE TABLE IF NOT EXISTS operateurs (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        matricule TEXT UNIQUE NOT NULL,
        date_creation TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS directions_regionales (
        id INTEGER PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        nom TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS agences (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        dr_id INTEGER NOT NULL,
        FOREIGN KEY (dr_id) REFERENCES directions_regionales(id),
        UNIQUE(nom, dr_id)
    );

    CREATE TABLE IF NOT EXISTS prix_unitaires (
        id INTEGER PRIMARY KEY,
        categorie TEXT NOT NULL,
        prix INTEGER NOT NULL,
        exercice INTEGER NOT NULL DEFAULT 2026,
        UNIQUE(categorie, exercice)
    );

    -- Fenêtre 1: Volumes mensuels par agence (m3)
    CREATE TABLE IF NOT EXISTS volumes (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        categorie TEXT NOT NULL,
        valeur REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice, categorie)
    );

    -- Fenêtre 2a: CA Vente Eau - saisies manuelles (ENEO 871/873, GCO, Loc cptrs)
    CREATE TABLE IF NOT EXISTS ca_specifiques (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        rubrique TEXT NOT NULL,
        montant REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice, rubrique)
    );

    -- Fenêtre 3: Encaissements mensuels par agence (FCFA)
    CREATE TABLE IF NOT EXISTS encaissements (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        section TEXT NOT NULL,
        rubrique TEXT NOT NULL,
        montant REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice, section, rubrique)
    );

    -- Fenêtre 2b: Compléments Travaux Remboursables (CA Travaux)
    CREATE TABLE IF NOT EXISTS complements_travaux (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        montant REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    -- Branchements par AGENCE (v2 : anciennement par DR)
    CREATE TABLE IF NOT EXISTS branchements (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        type TEXT NOT NULL,
        valeur INTEGER DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice, type)
    );

    -- Recettes par AGENCE (v2 : anciennement par DR)
    CREATE TABLE IF NOT EXISTS recettes (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        montant REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    -- Données historiques N-1
    CREATE TABLE IF NOT EXISTS historique_volumes (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL,
        exercice INTEGER NOT NULL,
        total REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    CREATE TABLE IF NOT EXISTS historique_ca (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL,
        exercice INTEGER NOT NULL,
        total REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    CREATE TABLE IF NOT EXISTS historique_encaissements (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL,
        exercice INTEGER NOT NULL,
        total REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    -- Objectifs (flexibles : national/dr/agence, annuel/mensuel)
    CREATE TABLE IF NOT EXISTS objectifs (
        id INTEGER PRIMARY KEY,
        exercice INTEGER NOT NULL,
        scope_type TEXT NOT NULL DEFAULT 'national',
        scope_id INTEGER,
        rubrique TEXT NOT NULL,
        mois INTEGER,
        montant REAL DEFAULT 0,
        UNIQUE(exercice, scope_type, scope_id, rubrique, mois)
    );

    -- Fichiers objectifs uploadés
    CREATE TABLE IF NOT EXISTS objectifs_fichiers (
        id INTEGER PRIMARY KEY,
        nom_fichier TEXT NOT NULL,
        date_upload TEXT DEFAULT (datetime('now','localtime')),
        exercice INTEGER NOT NULL,
        operateur_nom TEXT,
        operateur_matricule TEXT,
        nb_lignes_importees INTEGER DEFAULT 0
    );

    -- Statut de saisie (brouillon / définitif)
    CREATE TABLE IF NOT EXISTS saisie_statut (
        id INTEGER PRIMARY KEY,
        fenetre TEXT NOT NULL,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL,
        exercice INTEGER NOT NULL DEFAULT 2026,
        statut TEXT NOT NULL DEFAULT 'brouillon',
        operateur_nom TEXT,
        operateur_matricule TEXT,
        date_statut TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(fenetre, agence_id, mois, exercice)
    );

    -- Branchements quotidiens par agence (suivi journalier)
    CREATE TABLE IF NOT EXISTS branchements_jour (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        date_saisie TEXT NOT NULL,
        vendus_d40 INTEGER DEFAULT 0,
        vendus_d20 INTEGER DEFAULT 0,
        vendus INTEGER DEFAULT 0,
        executes_d40 INTEGER DEFAULT 0,
        executes_d20 INTEGER DEFAULT 0,
        executes INTEGER DEFAULT 0,
        pec_d40 INTEGER DEFAULT 0,
        pec_d20 INTEGER DEFAULT 0,
        pec_machine INTEGER DEFAULT 0,
        moratoire_d40 INTEGER DEFAULT 0,
        moratoire_d20 INTEGER DEFAULT 0,
        moratoire INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        observations TEXT,
        operateur_nom TEXT NOT NULL,
        operateur_matricule TEXT NOT NULL,
        verrouille INTEGER DEFAULT 0,
        date_creation TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, date_saisie)
    );

    -- Impayés par agence et mois (portefeuille des impayés)
    CREATE TABLE IF NOT EXISTS impayes (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        particuliers_actifs REAL DEFAULT 0,
        gco_actifs REAL DEFAULT 0,
        particuliers_resilies REAL DEFAULT 0,
        gco_resilies REAL DEFAULT 0,
        bf_actifs REAL DEFAULT 0,
        bfc_actifs REAL DEFAULT 0,
        bf_resilies REAL DEFAULT 0,
        bfc_resilies REAL DEFAULT 0,
        gestion_manuelle REAL DEFAULT 0,
        resiliers_crediteurs REAL DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    -- Paiements électroniques (chargés via fichier Excel)
    CREATE TABLE IF NOT EXISTS paiements_electroniques (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER,
        dr_code TEXT,
        agence_nom TEXT,
        mois INTEGER,
        exercice INTEGER NOT NULL DEFAULT 2026,
        mode_paiement TEXT,
        montant REAL DEFAULT 0,
        date_upload TEXT DEFAULT (datetime('now','localtime'))
    );

    -- Réalisations antérieures (N-1) importées par fichier
    CREATE TABLE IF NOT EXISTS realisations_anterieures (
        id INTEGER PRIMARY KEY,
        exercice INTEGER NOT NULL,
        dr_code TEXT,
        agence_nom TEXT,
        agence_id INTEGER,
        rubrique TEXT NOT NULL,
        mois INTEGER,
        valeur REAL DEFAULT 0,
        total_annuel REAL DEFAULT 0,
        date_upload TEXT DEFAULT (datetime('now','localtime'))
    );

    -- Recettes quotidiennes par agence (suivi journalier)
    CREATE TABLE IF NOT EXISTS recettes_jour (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        date_saisie TEXT NOT NULL,
        caisse_commerciale REAL DEFAULT 0,
        cheques REAL DEFAULT 0,
        hors_sites REAL DEFAULT 0,
        virements REAL DEFAULT 0,
        paiements_electroniques REAL DEFAULT 0,
        total REAL DEFAULT 0,
        type_piece TEXT,
        numero_piece TEXT,
        convoyeur TEXT,
        banque_depot TEXT,
        operateur_nom TEXT NOT NULL,
        operateur_matricule TEXT NOT NULL,
        verrouille INTEGER DEFAULT 0,
        date_creation TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, date_saisie)
    );
    """)

    # Peupler les DRs et agences
    for code_dr, agences_list in STRUCTURE_CW.items():
        c.execute("INSERT OR IGNORE INTO directions_regionales (code, nom) VALUES (?, ?)",
                  (code_dr, code_dr))
        dr_id = c.execute("SELECT id FROM directions_regionales WHERE code=?", (code_dr,)).fetchone()[0]
        for nom_agence in agences_list:
            c.execute("INSERT OR IGNORE INTO agences (nom, dr_id) VALUES (?, ?)",
                      (nom_agence, dr_id))

    # Peupler les prix unitaires
    all_cats = CATEGORIES_VOLUMES + [CATEGORIES_GCO, CATEGORIES_ADM, CATEGORIES_BC, CATEGORIES_BFC] + CATEGORIES_CW
    for cat, prix in all_cats:
        c.execute("INSERT OR IGNORE INTO prix_unitaires (categorie, prix) VALUES (?, ?)",
                  (cat, prix))

    # Supprimer l'ancien objectif hardcodé encaissements 73B (si présent)
    c.execute("DELETE FROM objectifs WHERE exercice=2026 AND scope_type='national' AND rubrique='Encaissements' AND montant=73565872665")

    # Tables paiements électroniques CSV (données brutes + validées)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS paiements_elec_csv (
        id INTEGER PRIMARY KEY,
        exercice INTEGER NOT NULL DEFAULT 2026,
        date_transaction TEXT,
        operateur TEXT,
        reference_client TEXT,
        nom_client TEXT,
        montant REAL DEFAULT 0,
        centre TEXT,
        dr_code TEXT,
        agence_id INTEGER,
        statut TEXT,
        comptabilise TEXT,
        mois INTEGER,
        ligne_brute TEXT,
        fichier_source TEXT,
        date_upload TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (agence_id) REFERENCES agences(id)
    );

    CREATE TABLE IF NOT EXISTS paiements_elec_definitif (
        id INTEGER PRIMARY KEY,
        exercice INTEGER NOT NULL DEFAULT 2026,
        mois_debut INTEGER NOT NULL,
        mois_fin INTEGER NOT NULL,
        dr_code TEXT,
        agence_id INTEGER,
        agence_nom TEXT,
        operateur TEXT NOT NULL,
        montant_total REAL DEFAULT 0,
        nb_transactions INTEGER DEFAULT 0,
        date_validation TEXT DEFAULT (datetime('now','localtime')),
        operateur_nom TEXT,
        operateur_matricule TEXT,
        FOREIGN KEY (agence_id) REFERENCES agences(id)
    );
    """)

    # Migration : ajouter colonnes ⌀40/⌀20 à branchements_jour si absentes
    try:
        cols = [row[1] for row in c.execute("PRAGMA table_info(branchements_jour)").fetchall()]
        for col in ['vendus_d40', 'vendus_d20', 'executes_d40', 'executes_d20',
                     'pec_d40', 'pec_d20', 'moratoire_d40', 'moratoire_d20']:
            if col not in cols:
                c.execute(f"ALTER TABLE branchements_jour ADD COLUMN {col} INTEGER DEFAULT 0")
    except Exception:
        pass

    # Migration : ajouter colonne mois à realisations_anterieures si absente
    try:
        cols_real = [row[1] for row in c.execute("PRAGMA table_info(realisations_anterieures)").fetchall()]
        if 'mois' not in cols_real:
            c.execute("ALTER TABLE realisations_anterieures ADD COLUMN mois INTEGER")
        if 'total_annuel' not in cols_real:
            c.execute("ALTER TABLE realisations_anterieures ADD COLUMN total_annuel REAL DEFAULT 0")
    except Exception:
        pass

    # Migration : ajouter colonnes vente_eau/penalite à paiements_elec_csv si absentes
    try:
        cols_pe = [row[1] for row in c.execute("PRAGMA table_info(paiements_elec_csv)").fetchall()]
        for col, coltype in [('vente_eau', 'REAL DEFAULT 0'), ('penalite', 'REAL DEFAULT 0'),
                              ('pl_code', 'TEXT'), ('code_agence', 'TEXT')]:
            if col not in cols_pe:
                c.execute(f"ALTER TABLE paiements_elec_csv ADD COLUMN {col} {coltype}")
    except Exception:
        pass

    # ── Tables du module Monitoring (alertes automatisées) ────────────────────
    c.executescript("""
    -- Indicateur 1 : abonnés actifs / facturés par agence et mois
    CREATE TABLE IF NOT EXISTS facturation_abonnes (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        abonnes_actifs INTEGER DEFAULT 0,
        abonnes_factures INTEGER DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    -- Indicateur 4 : branchements réalisés dans les délais réglementaires (≤ 15 jours)
    CREATE TABLE IF NOT EXISTS branchements_delais (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        total_devis_payes INTEGER DEFAULT 0,
        dans_15j INTEGER DEFAULT 0,
        delai_moyen_jours REAL,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    -- Indicateur 6 : factures annulées/réémises vs total émises par agence et mois
    CREATE TABLE IF NOT EXISTS reemissions_factures (
        id INTEGER PRIMARY KEY,
        agence_id INTEGER NOT NULL,
        mois INTEGER NOT NULL CHECK(mois BETWEEN 1 AND 12),
        exercice INTEGER NOT NULL DEFAULT 2026,
        nb_factures_emises INTEGER DEFAULT 0,
        nb_reemissions INTEGER DEFAULT 0,
        FOREIGN KEY (agence_id) REFERENCES agences(id),
        UNIQUE(agence_id, mois, exercice)
    );

    -- Seuils paramétrables par la Direction Financière
    CREATE TABLE IF NOT EXISTS monitoring_params (
        id INTEGER PRIMARY KEY,
        exercice INTEGER NOT NULL DEFAULT 2026,
        cle TEXT NOT NULL,
        valeur REAL NOT NULL,
        libelle TEXT,
        UNIQUE(exercice, cle)
    );
    """)

    # Paramètres par défaut (uniquement si absents)
    params_defaut = [
        (2026, 'seuil_facturation',          0.95,  'Seuil critique taux de facturation (%)'),
        (2026, 'seuil_tarif_variation',       0.05,  'Variation max tarif m³ HT (%)'),
        (2026, 'seuil_reemissions',           0.02,  'Seuil critique réémissions factures (%)'),
        (2026, 'seuil_impayes_pct_recettes',  0.05,  'Seuil min encaissements impayés / recettes (%)'),
        (2026, 'seuil_delais_warn_jours',     12.0,  'Délai moyen warning branchements (jours)'),
    ]
    for exercice_p, cle, val, lib in params_defaut:
        c.execute("""INSERT OR IGNORE INTO monitoring_params (exercice, cle, valeur, libelle)
                     VALUES (?, ?, ?, ?)""", (exercice_p, cle, val, lib))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print(f"Base de données créée: {DB_PATH}")
