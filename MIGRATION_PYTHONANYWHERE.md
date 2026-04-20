# 🐍 Déploiement CAMWATER sur PythonAnywhere

> **Pourquoi PythonAnywhere ?** 100 % gratuit (jamais de carte bancaire), spécialisé Python/Flask depuis 2012, base **SQLite persistante** incluse, URL stable, pas de mise en veille brutale. Idéal pour une démo avec données réelles qui ne disparaissent pas.
>
> **Votre action totale** : ~8 minutes, dont 5 de clics et 3 d'attente.

---

## 🏁 Aperçu — vous allez faire 7 étapes simples

```
 1. Compte PA            2. Clone repo         3. Setup auto
    (2 min)                 (20 sec)              (1 min)
       │                       │                     │
       ▼                       ▼                     ▼
 4. Web App      5. Copier WSGI        6. Static      7. Reload
    wizard          (30 sec)           files          & test
    (1 min)                            (30 sec)       (30 sec)
```

---

## ÉTAPE 1 — Créer le compte PythonAnywhere

1. Allez sur **https://www.pythonanywhere.com**
2. Cliquez **« Pricing & signup »** en haut à droite
3. Sous la colonne **« Beginner »** (gratuit, 0 $), cliquez **« Create a Beginner account »**
4. Choisissez un **pseudo** — important : **minuscules, pas de tiret**
   - Exemple bon : `anthonyambf` ou `camwatercm` ou `anthonyamb`
   - ⚠️ **Notez-le**, vous en aurez besoin à l'étape 5 (il apparaîtra partout dans l'URL)
5. Email + mot de passe → **« Register »**
6. Validez via le lien reçu par email

✅ Votre espace : `https://www.pythonanywhere.com/user/<votre-pseudo>/`

---

## ÉTAPE 2 — Ouvrir une console Bash

1. Connecté sur PythonAnywhere → onglet **« Consoles »** (menu du haut)
2. Dans « Start a new console » → cliquez **« Bash »**
3. Un terminal noir s'ouvre → c'est votre shell Linux sur les serveurs PA

---

## ÉTAPE 3 — Installation automatique (une seule commande)

**Copiez-collez cette commande dans la console Bash** (tout fait d'un coup) :

```bash
curl -fsSL https://raw.githubusercontent.com/anthonyambf-amb/camwater-app/main/setup_pythonanywhere.sh | bash
```

Ce que le script fait (environ 1 minute) :
- Clone votre dépôt GitHub
- Crée un dossier de données persistantes dans `~/camwater-data/`
- Crée un virtualenv Python 3.11
- Installe Flask, openpyxl, etc.
- Prépare un fichier `wsgi_ready.py` avec votre pseudo pré-rempli

Quand c'est fini, il affiche un cadre avec les infos utiles pour les étapes suivantes.

---

## ÉTAPE 4 — Créer le Web App

1. Onglet **« Web »** (menu du haut)
2. Bouton bleu **« Add a new web app »**
3. « Next » (URL = `votre-pseudo.pythonanywhere.com` — pas de domaine personnalisé sur Free)
4. **« Manual configuration »** (PAS « Flask » — on veut le contrôle)
5. **Python 3.11**
6. « Next » → « Done » → la page de config apparaît

---

## ÉTAPE 5 — Configurer les chemins

Sur la page du web app, en remontant la liste des sections :

### Section « Code »

| Champ | Valeur à saisir (remplacez `<USERNAME>`) |
|---|---|
| **Source code** | `/home/<USERNAME>/camwater-app` |
| **Working directory** | `/home/<USERNAME>/camwater-app` |
| **WSGI configuration file** | (lien déjà là — cliquez-le, voir étape 5b) |

### Étape 5b — Coller le WSGI

1. Cliquez sur le lien bleu **WSGI configuration file** (ouvre un éditeur en ligne)
2. **Sélectionnez TOUT** (`Ctrl+A`) et **supprimez**
3. Dans la console Bash (onglet à côté), tapez :
   ```bash
   cat ~/camwater-app/wsgi_ready.py
   ```
4. Copiez toute la sortie affichée
5. Collez dans l'éditeur WSGI
6. **« Save »** (bouton vert en haut)

### Section « Virtualenv »

| Champ | Valeur |
|---|---|
| Virtualenv | `/home/<USERNAME>/camwater-venv` |

---

## ÉTAPE 6 — Mapping des fichiers statiques

Toujours sur la page du web app, section **« Static files »** :

Cliquez **« Enter URL »** / **« Enter path »** et ajoutez **une seule ligne** :

| URL | Directory |
|---|---|
| `/static/` | `/home/<USERNAME>/camwater-app/static` |

(Sauvegarde automatique à chaque ajout.)

---

## ÉTAPE 7 — Reload & test

1. Tout en haut de la page, gros bouton vert **« Reload `<votre-pseudo>.pythonanywhere.com` »** → cliquer
2. Attendre ~10 secondes
3. Ouvrir dans un nouvel onglet : **`https://<votre-pseudo>.pythonanywhere.com`**
4. La page d'accueil CAMWATER avec les 3 espaces doit s'afficher 🎉

Testez les 3 URL :
- `https://<pseudo>.pythonanywhere.com/central`
- `https://<pseudo>.pythonanywhere.com/agences`
- `https://<pseudo>.pythonanywhere.com/direction`

**Donnez-moi votre URL publique** et je lance les tests automatiques.

---

## 🔄 Comment mettre à jour plus tard (quand je pousse du nouveau code)

1. Console Bash PA :
   ```bash
   cd ~/camwater-app && git pull
   ```
2. Onglet **« Web »** → bouton **« Reload »**

Total : 15 secondes.

---

## 🆘 En cas d'erreur au chargement

| Symptôme | Cause probable | Remède |
|---|---|---|
| « Something went wrong :-( » | Erreur Python au démarrage | Onglet Web → « Error log » en bas → me copier les 10 dernières lignes |
| « Server error (500) » | Même chose | idem |
| CSS absent, page brute | Static files mal mappés | Refaire étape 6 |
| Page ne charge pas du tout | Web app non reloadée | Re-cliquer « Reload » |
| « ModuleNotFoundError » | Virtualenv mal lié | Vérifier étape 5 section Virtualenv |

---

## 📊 Ce que vous obtiendrez

| Point | Valeur |
|---|---|
| URL | `https://<votre-pseudo>.pythonanywhere.com` |
| Coût | 0 € à vie (tant que vous vous connectez ≥ 1×/3 mois) |
| Persistance données | ✅ SQLite dans `~/camwater-data/camwater.db` — **JAMAIS effacé** |
| Persistance objectifs Excel | ✅ `~/camwater-data/objectifs/` |
| HTTPS | ✅ Let's Encrypt auto |
| Limites Free | 512 Mo disque (~largement suffisant), 1 web app, CPU partagé |
| Mise en veille | Non (site toujours réactif tant que compte actif) |
| Carte bancaire | ❌ Jamais |

---

## 🎁 Bonus — Activer les redéploiements automatiques

(Optionnel, à faire plus tard si vous voulez.)

PA ne lit pas GitHub webhook directement, mais vous pouvez créer une **Scheduled Task** (onglet « Tasks ») qui fait :

```bash
cd ~/camwater-app && git pull && touch /var/www/<USERNAME>_pythonanywhere_com_wsgi.py
```

Fréquence : toutes les 1 heure (limite Free tier). Ainsi chaque `git push` que je fais est automatiquement tiré dans l'heure.

Dites-moi si vous voulez que je vous guide pour l'activer après le déploiement initial.
