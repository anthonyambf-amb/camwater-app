# 📔 Journal de déploiement CAMWATER

> Ce document trace **tout ce qui a été fait automatiquement** sur cet ordinateur pour mettre en ligne la plateforme, et **ce qui reste à faire**. À transmettre au prochain administrateur technique en cas de besoin.

---

## ✅ ÉTAPE 1 — CODE SUR GITHUB (FAIT)

**Date :** 2026-04-18

### Outils installés sur le Mac
| Outil | Emplacement | Rôle |
|-------|-------------|------|
| `gh` (GitHub CLI) v2.90.0 | `~/bin/gh` | Authentification GitHub + credential helper pour git |

> **Note** : `gh` a été téléchargé en binaire direct depuis https://github.com/cli/cli/releases/v2.90.0 (pas d'Homebrew). Pour l'utiliser depuis le terminal, lancer : `~/bin/gh <commande>` — ou ajouter `~/bin` au `PATH` dans `~/.zshrc`.

### Configuration Git globale
Fichier `~/.gitconfig` (ou via `git config --global --list`) :
```
user.name = Anthony Amb
user.email = anthony.amb.f@gmail.com
init.defaultBranch = main
credential.https://github.com.helper = !/Users/macbookpro/bin/gh auth git-credential
credential.https://gist.github.com.helper = !/Users/macbookpro/bin/gh auth git-credential
```

### Authentification GitHub
- Méthode : **OAuth Device Flow** via `gh auth login --web`
- Compte : **anthonyambf-amb**
- Token stocké : dans le **trousseau macOS** (Keychain — chiffré système)
- **Jamais transmis en clair**, jamais écrit dans un fichier
- Révocation possible à tout moment : https://github.com/settings/applications → « GitHub CLI » → Revoke

### Dépôt GitHub
- URL : **https://github.com/anthonyambf-amb/camwater-app**
- Branche principale : `main`
- Visibilité : privée (à confirmer dans GitHub Settings)
- Commits poussés :
  1. `851156d` — *Premier déploiement CAMWATER — app Flask + config Render + guide déploiement* (36 fichiers)
  2. *Fusion* — merge du README.md initial de GitHub
  3. `2cc333a` — *Ignorer les fichiers auxiliaires SQLite (-shm/-wal)*

### Fichiers de déploiement ajoutés dans `camwater-app/`
| Fichier | Rôle |
|---------|------|
| `requirements.txt` | Dépendances Python pinées (Flask, gunicorn, openpyxl, Werkzeug) |
| `Procfile` | Commande de démarrage prod : `gunicorn app:app` |
| `runtime.txt` | Python 3.11.9 |
| `render.yaml` | Blueprint Render (service web + disque persistant 1 Go + variables d'env) |
| `.gitignore` | Exclut `data/*.db*`, `__pycache__`, `.DS_Store`, `.env`, `venv/` |
| `DEPLOIEMENT_EN_LIGNE.md` | Guide pas à pas complet |

### Adaptations du code (déjà poussées sur GitHub)
- `database.py` : chemin de la base lu depuis `CAMWATER_DATA_DIR` (env var) → persistance cloud
- `app.py` : clé secrète lue depuis `CAMWATER_SECRET_KEY` ; `UPLOAD_FOLDER` basé sur `CAMWATER_DATA_DIR`

---

## 🔜 ÉTAPE 2 — DÉPLOIEMENT RENDER (À FAIRE — ~10 minutes)

> ⚠️ Cette étape nécessite la **création d'un compte** (je ne peux pas le faire automatiquement pour raison de sécurité).

### 2.1 Créer le compte Render

1. Aller sur **https://render.com**
2. Cliquer **« Get Started »**
3. Choisir **« Sign up with GitHub »** → autoriser Render à lire vos dépôts

### 2.2 Déployer via Blueprint (automatique)

1. Tableau de bord Render → bouton **« New + »** (mauve, haut droit) → **« Blueprint »**
2. Sélectionner le dépôt **`anthonyambf-amb/camwater-app`** → **« Connect »**

   *(Si le dépôt n'apparaît pas, cliquer « Configure account » et autoriser Render à voir ce dépôt.)*

3. Render lit `render.yaml` et propose automatiquement :
   - Service web **camwater** (runtime Python, plan Free)
   - Disque persistant **camwater-data** (1 Go, monté sur `/var/data`)
   - Variables d'environnement (dont `CAMWATER_SECRET_KEY` générée aléatoirement)
4. Cliquer **« Apply »** → **« Create New Resources »**
5. Patienter 3-5 minutes (suivre les logs de build en direct)

### 2.3 Récupérer l'URL publique

En haut de la page du service, URL du type :
```
https://camwater.onrender.com
```
ou avec suffixe aléatoire si `camwater` est pris.

### 2.4 Tester les 3 URL

| Profil | URL de test |
|--------|-------------|
| Centralisation | `https://camwater.onrender.com/central` |
| Agents terrain | `https://camwater.onrender.com/agences` |
| Direction | `https://camwater.onrender.com/direction` |

---

## 🔜 ÉTAPE 3 — NOM DE DOMAINE (OPTIONNEL — ~5 €/an)

### 3.1 Vérifier la disponibilité + acheter

- **Porkbun** (https://porkbun.com) : ~6 € le `.com` la 1ʳᵉ année, ~10 €/an ensuite
- **OVH** (https://ovh.com) : acteur français, ~8 €/an le `.com`
- **Cloudflare Registrar** : prix coûtant (~9 €/an fixe)

### 3.2 Brancher sur Render

Sur Render → service `camwater` → Settings → **Custom Domains** → Add → entrer le nom.
Render fournit 1 CNAME + 1 A à configurer dans l'interface DNS du registrar.
HTTPS (Let's Encrypt) automatique, 5 min à 2 h.

---

## 🔄 METTRE À JOUR LE CODE À L'AVENIR

Depuis ce Mac :
```bash
cd "/Users/macbookpro/.../camwater-app"
git add .
git commit -m "Description du changement"
git push
```
→ Render redéploie automatiquement en 2 min.

L'authentification GitHub est **persistante** dans le trousseau macOS — aucune ressaisie nécessaire.

---

## 🆘 EN CAS DE PERTE D'ACCÈS

### Si vous perdez ce Mac
- Les commits sont sur GitHub → `git clone https://github.com/anthonyambf-amb/camwater-app.git` sur un autre Mac
- Les données de production sont sur Render (disque `/var/data/camwater.db`) → indépendantes du Mac
- Pour pousser depuis un nouveau Mac : réinstaller `gh` + `gh auth login --web` → trousseau reconstitué

### Si vous perdez le compte GitHub
- Le dépôt GitHub est détenu par `anthonyambf-amb@gmail` — récupération via support GitHub
- Plan B : les fichiers sont aussi présents localement dans le dossier de l'app (tous les commits sont en local via `.git/`)

### Si le site Render ne répond plus
- Vérifier https://status.render.com
- Ouvrir les logs du service sur render.com → onglet **Logs**
- Redémarrage manuel : onglet **Manual Deploy** → **Clear build cache & deploy**

---

## 📞 CONTACTS UTILES

| Ressource | Lien |
|-----------|------|
| Dépôt GitHub | https://github.com/anthonyambf-amb/camwater-app |
| Doc Render | https://render.com/docs |
| Support Render | https://render.com/support |
| Révoquer token GitHub | https://github.com/settings/applications |
| Statut Render | https://status.render.com |

---

*Ce journal a été généré automatiquement lors du premier déploiement. Mettez-le à jour manuellement à chaque changement d'architecture majeur (domaine, migration base, nouvel hébergeur, etc.).*
