# 🚀 Déploiement CAMWATER sur Koyeb (remplace Render)

> **Pourquoi Koyeb ?** Datacenter Paris (~80 ms de latence depuis le Cameroun vs ~200 ms USA pour Render), interface plus rapide, déploiement plus fiable sur plan gratuit.

---

## ⚡ Étape unique — Déployer en 3 clics

1. **Cliquez sur ce lien** (ouvre Koyeb pré-configuré avec votre dépôt GitHub) :

   👉 **[DEPLOY CAMWATER ON KOYEB](https://app.koyeb.com/deploy?type=git&repository=github.com%2Fanthonyambf-amb%2Fcamwater-app&branch=main&name=camwater&service_type=web&regions=par&instance_type=free&builder=buildpack&run_command=gunicorn+app%3Aapp+--bind+0.0.0.0%3A%24PORT+--workers+2+--timeout+120&ports=8000%3Bhttp%3B%2F&env%5BCAMWATER_DEBUG%5D=0&env%5BCAMWATER_DATA_DIR%5D=%2Ftmp%2Fcamwater&env%5BPYTHON_VERSION%5D=3.11.9&autodeploy=true)**

2. **Si c'est votre première fois sur Koyeb** :
   - « Sign up with GitHub » → autorisez Koyeb à voir `anthonyambf-amb/camwater-app`
   - Aucune carte bancaire requise pour le plan Free

3. **Sur la page de déploiement qui s'affiche** :
   - Tout est déjà rempli (repo, branche, commande, région Paris, instance Free)
   - Cliquez **« Deploy »** en bas

4. **Patientez 3-5 minutes** (build + start), puis Koyeb affiche une URL du type :
   ```
   https://camwater-<pseudo>.koyeb.app
   ```

5. **Testez** :
   - `https://camwater-<pseudo>.koyeb.app/` → page d'accueil (3 espaces)
   - `https://camwater-<pseudo>.koyeb.app/central` → login Centralisation
   - `https://camwater-<pseudo>.koyeb.app/agences` → login agents terrain
   - `https://camwater-<pseudo>.koyeb.app/direction` → dashboard Direction lecture seule

6. **Donnez-moi l'URL publique** une fois le service « Healthy » → je lance les tests automatiques.

---

## 🔧 Configuration appliquée (pour info)

| Paramètre | Valeur |
|---|---|
| Nom du service | `camwater` |
| Type | Web (HTTP) |
| Région | Paris (`par`) |
| Instance | Free (0,1 vCPU, 256 Mo RAM) — sleep après 30 min idle |
| Dépôt | `github.com/anthonyambf-amb/camwater-app` |
| Branche | `main` |
| Build | Buildpack Python (lit `runtime.txt` + `requirements.txt` automatiquement) |
| Run command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| Port exposé | 8000 (HTTP, path `/`) |
| Auto-deploy | ✅ (re-déploie à chaque `git push`) |
| Env `CAMWATER_DEBUG` | `0` |
| Env `CAMWATER_DATA_DIR` | `/tmp/camwater` (éphémère) |
| Env `PYTHON_VERSION` | `3.11.9` |

---

## ⚠️ Limitations plan Free (identiques à Render)

| Point | Détail |
|---|---|
| **Stockage** | Éphémère — `/tmp/camwater/camwater.db` perdu à chaque redéploiement |
| **Mise en veille** | Après 30 min sans trafic, le service s'endort. 1ᵉʳ visiteur = ~20 s de réveil |
| **RAM** | 256 Mo — suffisant pour cette app Flask |
| **Concurrence** | 1 instance, 2 workers gunicorn |

### Pour passer en production (données persistantes)
- **Plan eco** (~2,7 $/mois) + volume attaché (~0,30 $/Go/mois) : 1 Go persistant ≈ **2 000 FCFA/mois total**
- OU migration SQLite → Postgres sur **Neon** (free tier 0,5 Go permanent) + Koyeb Free : **0 FCFA/mois** — nécessite adaptation du code (je peux la faire)

---

## 🔄 Mise à jour du code (identique à Render)

```bash
cd "/Users/macbookpro/.../camwater-app"
git add .
git commit -m "Description"
git push
```
→ Koyeb détecte le push et redéploie automatiquement en 2-3 min.

---

## 🆘 Si le déploiement échoue

1. Sur Koyeb → votre service → onglet **« Deployments »**
2. Cliquez sur le déploiement en échec → onglet **« Build logs »** ou **« Runtime logs »**
3. Copiez-moi les **5-10 dernières lignes** contenant « ERROR » ou « Traceback »

Je diagnostique et corrige immédiatement.

---

## 📝 Et Render ?

Vous pouvez laisser le service Render tel quel (il n'accepte pas le déploiement de toute façon) — ou le supprimer depuis `dashboard.render.com`. Les fichiers `render.yaml` et `Procfile` restent compatibles, vous pourrez revenir sur Render plus tard si vous le souhaitez.
