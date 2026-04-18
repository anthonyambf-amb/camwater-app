# 🚀 Mettre CAMWATER en ligne — Guide ultra-simple

> **Objectif** : votre plateforme accessible 24h/24, même quand votre PC est éteint, avec données sauvegardées en ligne. Coût : **0 €/mois** au démarrage.
>
> **Temps total** : ~30 minutes la première fois.
>
> **Pré-requis** : juste un navigateur internet et votre adresse email.

---

## ✅ Tout ce qui est déjà fait pour vous

J'ai préparé tous les fichiers techniques nécessaires dans le dossier `camwater-app/` :

| Fichier | Rôle |
|---------|------|
| `requirements.txt` | Liste des composants Python à installer |
| `Procfile` | Commande de démarrage en production |
| `runtime.txt` | Version de Python |
| `render.yaml` | Configuration automatique pour Render.com |
| `.gitignore` | Empêche d'envoyer la base locale en ligne |
| `app.py` (modifié) | Lit la clé de sécurité et le chemin des données depuis l'environnement |
| `database.py` (modifié) | La base SQLite va automatiquement vers le disque persistant cloud |

**Vous n'avez RIEN à toucher dans le code.** Suivez juste les étapes ci-dessous.

---

## 📋 Vue d'ensemble — 3 grandes étapes

```
[1] Mettre votre code sur GitHub  ────►  [2] Connecter à Render  ────►  [3] Partager les URL
   (15 min, 1 fois)                       (10 min, 1 fois)               (1 min)
```

---

# 🅰️ ÉTAPE 1 — Créer un compte GitHub et y déposer votre code

GitHub = un coffre-fort en ligne pour votre code. Render ira y chercher l'app.

## 1.1 Créer le compte GitHub

1. Ouvrez votre navigateur → allez sur **https://github.com**
2. Cliquez **« Sign up »** (en haut à droite)
3. Entrez votre **email**, choisissez un **mot de passe**, choisissez un **nom d'utilisateur** (ex. `camwater-cm`)
4. Confirmez votre email (un lien vous est envoyé)

✅ Vous avez un compte GitHub.

## 1.2 Créer un dépôt (« repository »)

1. Une fois connecté, cliquez le bouton vert **« New »** ou le `+` en haut à droite → **« New repository »**
2. Remplissez :
   - **Repository name** : `camwater-app`
   - **Description** : `Plateforme commerciale CAMWATER`
   - Cochez **« Private »** (important — vos données sont confidentielles)
   - **Ne cochez RIEN d'autre** (pas de README, pas de .gitignore, pas de licence — j'ai déjà tout préparé)
3. Cliquez **« Create repository »**

GitHub vous montre une page avec des commandes. **Gardez cet onglet ouvert.**

## 1.3 Envoyer votre code sur GitHub

Ouvrez l'application **Terminal** sur votre Mac (touche `cmd + espace`, tapez « terminal », entrée).

Copiez-collez les commandes suivantes **une par une** (remplacez `VOTRE-PSEUDO` par le pseudo GitHub que vous venez de créer) :

```bash
cd "/Users/macbookpro/Library/CloudStorage/GoogleDrive-anthony.amb.f@gmail.com/Autres ordinateurs/My Laptop/CW/ACTUEL/2026/SQSC 2026/camwater-app"

git init
git add .
git commit -m "Premier déploiement CAMWATER"
git branch -M main
git remote add origin https://github.com/VOTRE-PSEUDO/camwater-app.git
git push -u origin main
```

À la dernière commande, GitHub vous demandera votre identifiant + un **« Personal Access Token »** (pas votre mot de passe).

### Comment créer ce token (1 fois pour la vie) :
1. Sur GitHub → cliquez votre photo (haut droit) → **« Settings »**
2. Tout en bas du menu gauche → **« Developer settings »**
3. **« Personal access tokens »** → **« Tokens (classic) »**
4. **« Generate new token »** → **« Generate new token (classic) »**
5. **Note** : `camwater-deploy` — **Expiration** : `90 days` — Cochez la case **`repo`**
6. Bouton vert **« Generate token »** en bas
7. **Copiez le token immédiatement** (vous ne le reverrez jamais) et collez-le quand le terminal le demande à la place du mot de passe

✅ Votre code est sur GitHub. Vérifiez en rafraîchissant la page de votre dépôt : tous les fichiers doivent apparaître.

---

# 🅱️ ÉTAPE 2 — Déployer sur Render.com

## 2.1 Créer un compte Render

1. Allez sur **https://render.com**
2. Cliquez **« Get Started »** ou **« Sign Up »**
3. Choisissez **« Sign up with GitHub »** ← le plus simple
4. Autorisez Render à voir vos dépôts GitHub

✅ Compte Render créé, lié à GitHub.

## 2.2 Créer le service web

1. Sur le tableau de bord Render, cliquez **« New + »** (bouton mauve, en haut à droite) → **« Blueprint »**

   *(« Blueprint » = Render lit le fichier `render.yaml` que j'ai préparé et configure tout automatiquement)*

2. Render affiche la liste de vos dépôts GitHub. Cliquez **« Connect »** à côté de `camwater-app`.

   Si vous ne voyez pas le dépôt → cliquez **« Configure account »** → autorisez l'accès au dépôt `camwater-app`.

3. Render lit `render.yaml` et vous propose de créer le service **camwater** + le disque **camwater-data**.

4. Cliquez **« Apply »** (ou **« Create New Resources »**).

5. **Patientez 3-5 minutes.** Render :
   - télécharge votre code
   - installe Python + Flask + openpyxl + gunicorn
   - réserve le disque persistant 1 Go
   - démarre le serveur

   Vous pouvez suivre les logs en direct (texte qui défile). Quand vous voyez `==> Your service is live 🎉`, c'est terminé.

## 2.3 Récupérer votre URL publique

En haut de la page de votre service, vous verrez une URL du type :

```
https://camwater.onrender.com
```

(Le nom exact dépend de la disponibilité — Render peut ajouter des chiffres, ex. `camwater-x7k2.onrender.com`.)

✅ **Votre plateforme est en ligne, accessible à tout le monde, 24h/24.**

---

# 🅲 ÉTAPE 3 — Partager les 3 URL aux utilisateurs

Communiquez ces 3 liens selon le profil :

| Profil | URL à envoyer |
|--------|---------------|
| **Centralisation** (siège) | `https://camwater.onrender.com/central` |
| **Agents terrain** (DR / agences) | `https://camwater.onrender.com/agences` |
| **Direction** (responsables — lecture seule) | `https://camwater.onrender.com/direction` |

**C'est tout.** Vous pouvez fermer votre Mac, le débrancher, partir en vacances — la plateforme tourne sur les serveurs Render.

---

## 🔄 Comment mettre à jour la plateforme plus tard

Quand vous (ou moi) modifiez le code :

```bash
cd "/Users/macbookpro/.../camwater-app"
git add .
git commit -m "Ce que vous avez changé"
git push
```

Render détecte automatiquement le `push` et redéploie en 2 minutes. **Aucun clic requis.**

---

## ⚠️ À savoir sur le plan gratuit Render

| Point | Détail |
|-------|--------|
| **Mise en veille** | Si personne ne visite pendant 15 min, le service s'endort. Le 1er visiteur après attend ~30 secondes le réveil. Les visites suivantes sont instantanées. |
| **Bande passante** | 100 Go/mois gratuits — largement suffisant |
| **Disque** | 1 Go gratuit → ~500 000 lignes en base, des années de données |
| **Données persistantes** | ✅ Sauvegardées sur le disque Render même après redéploiement |
| **HTTPS** | ✅ Inclus automatiquement |

### Si vous voulez supprimer la mise en veille (recommandé pour usage pro)
→ Passer le service au plan **Starter ($7/mois ≈ 4 200 FCFA)** : aucune mise en veille, plus de RAM. Un clic sur la page du service → **« Settings »** → **« Instance Type »** → **Starter**.

---

## 💾 Sauvegarde de votre base de données

La base SQLite est stockée sur le disque persistant Render à `/var/data/camwater.db`. Pour faire une sauvegarde sur votre PC :

1. Sur Render, ouvrez votre service → onglet **« Shell »** (terminal en ligne)
2. Tapez : `cat /var/data/camwater.db | base64 > /tmp/backup.txt && cat /tmp/backup.txt`
3. Copiez le texte affiché → collez dans un fichier sur votre Mac → décodez avec `base64 -d > camwater_backup.db`

Ou plus simple : utilisez **« Render Backups »** (option payante du disque, $0.25/Go/mois).

---

## 🆘 Si ça ne marche pas

| Problème | Solution |
|----------|----------|
| Erreur sur `git push` : « permission denied » | Token GitHub mal créé ou expiré → recommencez l'étape 1.3 |
| Render dit « Build failed » | Ouvrez les logs sur Render → cherchez le mot `Error` → envoyez-moi la ligne |
| Site charge à blanc | Attendez 30 s (réveil après mise en veille) puis rafraîchissez |
| « Application Error » | Logs Render onglet « Logs » → cherchez `Traceback` |

En cas de blocage, copiez-moi la dernière dizaine de lignes des **Logs Render** et je vous dis quoi faire.

---

## 🎯 Récapitulatif visuel

```
Aujourd'hui                              Après ce guide
─────────────                            ──────────────
Mac allumé en permanence  ❌             Mac éteint = OK ✅
URL Cloudflare qui change  ❌             URL fixe permanente ✅
Données sur disque local   ❌             Données sur cloud Render ✅
Tunnel à relancer          ❌             Démarrage automatique ✅
Coût : électricité 24/7    ❌             0 €/mois ✅
```

**Bonne mise en ligne ! 🚀**
