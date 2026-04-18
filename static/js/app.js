/* === Saisie - Logique Frontend v2 === */

function getAgenceId() { return document.getElementById('sel-agence').value; }
function getMois() { return document.getElementById('sel-mois').value; }

let currentStatut = null;

function fmt(n) {
    if (!n && n !== 0) return '-';
    return Math.round(n).toLocaleString('fr-FR');
}

// --- Init ---
function initPage() {
    loadData();
}

function loadData() {
    let loadPromise = Promise.resolve();
    if (FENETRE === 'volumes') loadPromise = loadVolumes();
    else if (FENETRE === 'ca_ve') loadPromise = loadCaSpec();
    else if (FENETRE === 'ca_travaux') loadPromise = loadComplements();
    else if (FENETRE === 'encaissements') loadPromise = loadEnc();
    else if (FENETRE === 'impayes') loadPromise = loadImpayes();
    if (['ca_ve', 'ca_travaux'].includes(FENETRE)) loadCaTotalBanner();
    // Charger les cumuls de l'agence
    loadCumulBanner();
    // Vérifier le statut après chargement des données
    loadPromise.then(() => checkStatut());
}

// --- Cumul banners (valeurs historiques agence) ---
function loadCumulBanner() {
    const agId = getAgenceId();
    if (!agId) return;

    if (FENETRE === 'volumes') {
        fetch(`/api/cumul/volumes?agence_id=${agId}`)
            .then(r => r.json())
            .then(data => {
                const el1 = document.getElementById('cumul-vol-total');
                const el2 = document.getElementById('cumul-vol-ca');
                if (el1) el1.textContent = fmt(data.total_volumes || 0);
                if (el2) el2.textContent = fmt(data.total_ca || 0);
            }).catch(() => {});
    } else if (FENETRE === 'ca_ve' || FENETRE === 'ca_travaux') {
        fetch(`/api/cumul/ca?agence_id=${agId}`)
            .then(r => r.json())
            .then(data => {
                if (FENETRE === 'ca_ve') {
                    const e1 = document.getElementById('cumul-cave-total');
                    const e2 = document.getElementById('cumul-cave-trvx');
                    const e3 = document.getElementById('cumul-cave-global');
                    if (e1) e1.textContent = fmt(data.ca_ve || 0);
                    if (e2) e2.textContent = fmt(data.ca_trvx || 0);
                    if (e3) e3.textContent = fmt(data.ca_global || 0);
                } else {
                    const e1 = document.getElementById('cumul-trvx-total');
                    const e2 = document.getElementById('cumul-trvx-global');
                    if (e1) e1.textContent = fmt(data.ca_trvx || 0);
                    if (e2) e2.textContent = fmt(data.ca_global || 0);
                }
            }).catch(() => {});
    } else if (FENETRE === 'encaissements') {
        fetch(`/api/cumul/encaissements?agence_id=${agId}`)
            .then(r => r.json())
            .then(data => {
                const el = document.getElementById('cumul-enc-total');
                if (el) el.textContent = fmt(data.total || 0);
            }).catch(() => {});
    } else if (FENETRE === 'impayes') {
        fetch(`/api/cumul/impayes?agence_id=${agId}`)
            .then(r => r.json())
            .then(data => {
                const e1 = document.getElementById('cumul-imp-actifs');
                const e2 = document.getElementById('cumul-imp-resilies');
                const e3 = document.getElementById('cumul-imp-total');
                if (e1) e1.textContent = fmt(data.actifs || 0);
                if (e2) e2.textContent = fmt(data.resilies || 0);
                if (e3) e3.textContent = fmt(data.total || 0);
            }).catch(() => {});
    }
}

// --- CA Total Banner ---
function loadCaTotalBanner() {
    fetch(`/api/ca_global/${getAgenceId()}/${getMois()}`)
        .then(r => r.json())
        .then(data => {
            const bVe = document.getElementById('banner-ca-ve');
            const bTrvx = document.getElementById('banner-ca-trvx');
            const bTotal = document.getElementById('banner-ca-total');
            if (bVe) bVe.textContent = fmt(data.total_ve || 0) + ' FCFA';
            if (bTrvx) bTrvx.textContent = fmt(data.total_trvx_remb || 0) + ' FCFA';
            if (bTotal) bTotal.textContent = fmt(data.ca_global || 0) + ' FCFA';
        });
}

// --- Volumes ---
function loadVolumes() {
    const tbody = document.getElementById('volumes-body');
    if (!tbody) return Promise.resolve();
    return fetch(`/api/volumes?agence_id=${getAgenceId()}&mois=${getMois()}`)
        .then(r => r.json())
        .then(data => {
            tbody.innerHTML = '';
            CATEGORIES_VOL.forEach(([cat, pu]) => {
                const val = data[cat] || 0;
                const ca = val * pu;
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${cat}</td><td style="text-align:right">${fmt(pu)}</td>
                    <td><input type="number" data-cat="${cat}" value="${val || ''}" step="1" class="vol-input"></td>
                    <td style="text-align:right" class="vol-ca" data-pu="${pu}">${fmt(ca)}</td>`;
                tbody.appendChild(tr);
            });
            updateVolTotals();
            document.querySelectorAll('.vol-input').forEach(inp => {
                inp.addEventListener('input', updateVolTotals);
            });
        });
}

function updateVolTotals() {
    let totalVol = 0, totalCA = 0;
    document.querySelectorAll('.vol-input').forEach(inp => {
        const val = parseFloat(inp.value) || 0;
        const pu = parseFloat(inp.closest('tr').querySelector('.vol-ca').dataset.pu) || 0;
        const ca = val * pu;
        inp.closest('tr').querySelector('.vol-ca').textContent = fmt(ca);
        totalVol += val;
        totalCA += ca;
    });
    const elVol = document.getElementById('vol-total');
    const elCa = document.getElementById('ca-auto-total');
    if (elVol) elVol.textContent = fmt(totalVol);
    if (elCa) elCa.textContent = fmt(totalCA);
}

function saveVolumes() {
    const valeurs = {};
    document.querySelectorAll('.vol-input').forEach(inp => {
        valeurs[inp.dataset.cat] = parseFloat(inp.value) || 0;
    });
    return fetch('/api/volumes', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ agence_id: getAgenceId(), mois: getMois(), valeurs })
    }).then(r => {
        if (!r.ok) return r.json().then(d => Promise.reject(d.error || 'Erreur serveur'));
        return r.json();
    });
}

// --- CA Vente Eau (ex CA Sp\u00e9cifiques) ---
function loadCaSpec() {
    return fetch(`/api/ca_specifiques?agence_id=${getAgenceId()}&mois=${getMois()}`)
        .then(r => r.json())
        .then(data => {
            document.querySelectorAll('.ca-spec-input').forEach(inp => {
                inp.value = data[inp.dataset.key] || '';
            });
            updateCaSpecTotal();
            document.querySelectorAll('.ca-spec-input').forEach(inp => {
                inp.addEventListener('input', updateCaSpecTotal);
            });
        });
}

function updateCaSpecTotal() {
    let total = 0;
    document.querySelectorAll('.ca-spec-input').forEach(inp => {
        total += parseFloat(inp.value) || 0;
    });
    const el = document.getElementById('ca-spec-total');
    if (el) el.textContent = fmt(total);
}

function saveCaSpec() {
    const valeurs = {};
    document.querySelectorAll('.ca-spec-input').forEach(inp => {
        valeurs[inp.dataset.key] = parseFloat(inp.value) || 0;
    });
    return fetch('/api/ca_specifiques', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ agence_id: getAgenceId(), mois: getMois(), valeurs })
    }).then(r => {
        if (!r.ok) return r.json().then(d => Promise.reject(d.error || 'Erreur serveur'));
        return r.json();
    }).then(data => { loadCaTotalBanner(); return data; });
}

// --- Encaissements ---
function loadEnc() {
    return fetch(`/api/encaissements?agence_id=${getAgenceId()}&mois=${getMois()}`)
        .then(r => r.json())
        .then(data => {
            document.querySelectorAll('.enc-input').forEach(inp => {
                inp.value = data[inp.dataset.key] || '';
            });
            updateEncTotals();
            document.querySelectorAll('.enc-input').forEach(inp => {
                inp.addEventListener('input', updateEncTotals);
            });
        });
}

function updateEncTotals() {
    const sectionTotals = {};
    let grandTotal = 0;
    document.querySelectorAll('.enc-input').forEach(inp => {
        const val = parseFloat(inp.value) || 0;
        const section = inp.dataset.key.split('|')[0];
        sectionTotals[section] = (sectionTotals[section] || 0) + val;
        grandTotal += val;
    });
    document.querySelectorAll('.subtotal').forEach(el => {
        const section = el.dataset.section;
        el.textContent = fmt(sectionTotals[section] || 0);
    });
    const el = document.getElementById('enc-total');
    if (el) el.textContent = fmt(grandTotal);
}

function saveEnc() {
    const valeurs = {};
    document.querySelectorAll('.enc-input').forEach(inp => {
        valeurs[inp.dataset.key] = parseFloat(inp.value) || 0;
    });
    return fetch('/api/encaissements', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ agence_id: getAgenceId(), mois: getMois(), valeurs })
    }).then(r => {
        if (!r.ok) return r.json().then(d => Promise.reject(d.error || 'Erreur serveur'));
        return r.json();
    });
}

// --- CA Travaux (Compl\u00e9ments) ---
function loadComplements() {
    const tbody = document.getElementById('comp-body');
    if (!tbody) return Promise.resolve();
    return fetch(`/api/complements?agence_id=${getAgenceId()}`)
        .then(r => r.json())
        .then(data => {
            tbody.innerHTML = '';
            for (let m = 1; m <= 12; m++) {
                const d = data[m] || { frais_pose: 0, frais_verif: 0, mutation: 0, complement: 0 };
                const auto = d.frais_pose + d.frais_verif + d.mutation;
                const total = auto + d.complement;
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${MOIS_NAMES[m-1]}</td>
                    <td style="text-align:right">${fmt(d.frais_pose)}</td>
                    <td style="text-align:right">${fmt(d.frais_verif)}</td>
                    <td style="text-align:right">${fmt(d.mutation)}</td>
                    <td style="text-align:right">${fmt(auto)}</td>
                    <td class="highlight-col"><input type="number" data-mois="${m}" value="${d.complement || ''}" step="1" class="comp-input"></td>
                    <td style="text-align:right;font-weight:700" class="comp-total">${fmt(total)}</td>`;
                tbody.appendChild(tr);
            }
            updateCompTotals();
            document.querySelectorAll('.comp-input').forEach(inp => {
                inp.addEventListener('input', updateCompTotals);
            });
        });
}

function updateCompTotals() {
    let tPose = 0, tVerif = 0, tMut = 0, tAuto = 0, tManual = 0, tGrand = 0;
    document.querySelectorAll('#comp-body tr').forEach(tr => {
        const cells = tr.querySelectorAll('td');
        const pose = parseNum(cells[1].textContent);
        const verif = parseNum(cells[2].textContent);
        const mut = parseNum(cells[3].textContent);
        const auto = pose + verif + mut;
        const manual = parseFloat(tr.querySelector('.comp-input').value) || 0;
        const total = auto + manual;
        cells[6].textContent = fmt(total);
        tPose += pose; tVerif += verif; tMut += mut; tAuto += auto; tManual += manual; tGrand += total;
    });
    const ids = ['comp-pose-total', 'comp-verif-total', 'comp-mut-total', 'comp-auto-total', 'comp-manual-total', 'comp-grand-total'];
    const vals = [tPose, tVerif, tMut, tAuto, tManual, tGrand];
    ids.forEach((id, i) => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = i === 5 ? `<strong>${fmt(vals[i])}</strong>` : fmt(vals[i]);
    });
}

function parseNum(str) {
    if (!str || str === '-') return 0;
    return parseFloat(str.replace(/\s/g, '').replace(/,/g, '.')) || 0;
}

function saveComplements() {
    const valeurs = {};
    document.querySelectorAll('.comp-input').forEach(inp => {
        valeurs[inp.dataset.mois] = parseFloat(inp.value) || 0;
    });
    return fetch('/api/complements', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ agence_id: getAgenceId(), valeurs })
    }).then(r => {
        if (!r.ok) return r.json().then(d => Promise.reject(d.error || 'Erreur serveur'));
        return r.json();
    }).then(data => { loadCaTotalBanner(); return data; });
}

// --- Branchements (par agence) ---
function getDrCode() {
    const sel = document.getElementById('sel-dr');
    return sel ? sel.value : '';
}

function loadBranchements() {
    return fetch(`/api/branchements?agence_id=${getAgenceId()}&mois=${getMois()}`)
        .then(r => r.json())
        .then(data => {
            document.querySelectorAll('.brch-input').forEach(inp => {
                inp.value = data[inp.dataset.type] || '';
            });
            updateBrchTotal();
            document.querySelectorAll('.brch-input').forEach(inp => {
                inp.addEventListener('input', updateBrchTotal);
            });
            loadBrchCumul();
        });
}

function updateBrchTotal() {
    let total = 0;
    document.querySelectorAll('.brch-input').forEach(inp => {
        total += parseInt(inp.value) || 0;
    });
    const el = document.getElementById('brch-total');
    if (el) el.textContent = fmt(total);
}

function loadBrchCumul() {
    const dr = getDrCode();
    if (!dr) return;
    fetch(`/api/branchements/cumul?dr=${encodeURIComponent(dr)}&mois=${getMois()}`)
        .then(r => r.json())
        .then(data => {
            const el = id => document.getElementById(id);
            if (el('brch-cumul-vendus')) el('brch-cumul-vendus').textContent = fmt(data['vendus'] || 0);
            if (el('brch-cumul-executes')) el('brch-cumul-executes').textContent = fmt(data['exécutés'] || 0);
            if (el('brch-cumul-pec')) el('brch-cumul-pec').textContent = fmt(data['pec'] || 0);
            if (el('brch-cumul-moratoire')) el('brch-cumul-moratoire').textContent = fmt(data['moratoire'] || 0);
        });
}

function saveBranchements() {
    const valeurs = {};
    document.querySelectorAll('.brch-input').forEach(inp => {
        valeurs[inp.dataset.type] = parseInt(inp.value) || 0;
    });
    return fetch('/api/branchements', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ agence_id: getAgenceId(), mois: parseInt(getMois()), valeurs })
    }).then(r => {
        if (!r.ok) return r.json().then(d => Promise.reject(d.error || 'Erreur serveur'));
        return r.json();
    });
}

// --- Recettes (par agence) ---
function loadRecettes() {
    return fetch(`/api/recettes?agence_id=${getAgenceId()}&mois=${getMois()}`)
        .then(r => r.json())
        .then(data => {
            const inp = document.getElementById('recette-montant');
            if (inp) inp.value = data.montant || '';
            loadRecCumul();
        });
}

function loadRecCumul() {
    const dr = getDrCode();
    if (!dr) return;
    fetch(`/api/recettes/cumul?dr=${encodeURIComponent(dr)}&mois=${getMois()}`)
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById('rec-cumul-total');
            if (el) el.textContent = fmt(data.total || 0) + ' FCFA';
        });
}

function saveRecettes() {
    return fetch('/api/recettes', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            agence_id: getAgenceId(),
            mois: parseInt(getMois()),
            montant: parseFloat(document.getElementById('recette-montant').value) || 0
        })
    }).then(r => {
        if (!r.ok) return r.json().then(d => Promise.reject(d.error || 'Erreur serveur'));
        return r.json();
    });
}

// --- Impay\u00e9s ---
function loadImpayes() {
    return fetch(`/api/impayes?agence_id=${getAgenceId()}&mois=${getMois()}`)
        .then(r => r.json())
        .then(data => {
            document.querySelectorAll('.imp-input').forEach(inp => {
                inp.value = data[inp.dataset.key] || '';
            });
            updateImpayesComputeds();
            document.querySelectorAll('.imp-input').forEach(inp => {
                inp.addEventListener('input', updateImpayesComputeds);
            });
        });
}

function updateImpayesComputeds() {
    const v = k => parseFloat(document.querySelector(`.imp-input[data-key="${k}"]`).value) || 0;

    const totalActifs = v('particuliers_actifs') + v('gco_actifs');
    const totalResilies = v('particuliers_resilies') + v('gco_resilies');
    const totalComActifs = v('bf_actifs') + v('bfc_actifs');
    const totalComResilies = v('bf_resilies') + v('bfc_resilies') + v('gestion_manuelle');
    const totalImpayes = totalActifs + totalResilies + totalComActifs + totalComResilies;

    document.getElementById('imp-total-actifs').textContent = fmt(totalActifs);
    document.getElementById('imp-total-resilies').textContent = fmt(totalResilies);
    document.getElementById('imp-total-com-actifs').textContent = fmt(totalComActifs);
    document.getElementById('imp-total-com-resilies').textContent = fmt(totalComResilies);
    document.getElementById('imp-total-impayes').textContent = fmt(totalImpayes);
}

function saveImpayes() {
    const valeurs = {};
    document.querySelectorAll('.imp-input').forEach(inp => {
        valeurs[inp.dataset.key] = parseFloat(inp.value) || 0;
    });
    return fetch('/api/impayes', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ agence_id: getAgenceId(), mois: getMois(), valeurs })
    }).then(r => {
        if (!r.ok) return r.json().then(d => Promise.reject(d.error || 'Erreur serveur'));
        return r.json();
    });
}

// === Statut Saisie (Brouillon / D\u00e9finitif) ===

function getStatutParams() {
    return {
        fenetre: FENETRE,
        agence_id: getAgenceId(),
        mois: FENETRE === 'ca_travaux' ? 0 : getMois()
    };
}

function checkStatut() {
    const p = getStatutParams();
    fetch(`/api/statut?fenetre=${p.fenetre}&agence_id=${p.agence_id}&mois=${p.mois}`)
        .then(r => r.json())
        .then(data => {
            currentStatut = data.statut || null;
            updateStatutUI();
        });
}

function updateStatutUI() {
    const badge = document.getElementById('statut-badge');
    const btns = document.getElementById('save-btns');

    if (currentStatut === 'definitif') {
        if (badge) {
            badge.className = 'statut-badge statut-definitif';
            badge.textContent = 'Enregistrement d\u00e9finitif \u2014 Donn\u00e9es verrouill\u00e9es';
        }
        if (btns) btns.style.display = 'none';
        document.querySelectorAll('input[type="number"]').forEach(inp => {
            inp.readOnly = true;
            inp.classList.add('locked');
        });
    } else if (currentStatut === 'brouillon') {
        if (badge) {
            badge.className = 'statut-badge statut-brouillon';
            badge.textContent = 'Sauvegarde temporaire \u2014 Donn\u00e9es modifiables';
        }
        if (btns) btns.style.display = 'flex';
        document.querySelectorAll('input[type="number"]').forEach(inp => {
            inp.readOnly = false;
            inp.classList.remove('locked');
        });
    } else {
        if (badge) {
            badge.className = 'statut-badge statut-vide';
            badge.textContent = 'Aucune sauvegarde';
        }
        if (btns) btns.style.display = 'flex';
        document.querySelectorAll('input[type="number"]').forEach(inp => {
            inp.readOnly = false;
            inp.classList.remove('locked');
        });
    }
}

function getSaveFn() {
    const map = {
        'volumes': saveVolumes,
        'ca_ve': saveCaSpec,
        'ca_travaux': saveComplements,
        'encaissements': saveEnc,
        'branchements': saveBranchements,
        'recettes': saveRecettes,
        'impayes': saveImpayes
    };
    return map[FENETRE];
}

function doSaveBrouillon() {
    if (currentStatut === 'definitif') return;
    const saveFn = getSaveFn();
    if (!saveFn) return;
    saveFn()
        .then(() => updateStatut('brouillon'))
        .then(() => {
            showSaveMsg('Sauvegarde temporaire effectu\u00e9e');
            if (typeof resetSelection === 'function') resetSelection();
        })
        .catch(err => showSaveMsg(typeof err === 'string' ? err : (err.message || 'Erreur'), true));
}

function doSaveDefinitif() {
    if (currentStatut === 'definitif') return;
    if (!confirm('ATTENTION : L\'enregistrement d\u00e9finitif verrouille les donn\u00e9es.\nVous ne pourrez plus modifier ces donn\u00e9es apr\u00e8s validation.\n\nConfirmer l\'enregistrement d\u00e9finitif ?')) {
        return;
    }
    const saveFn = getSaveFn();
    if (!saveFn) return;
    saveFn()
        .then(() => updateStatut('definitif'))
        .then(() => {
            showSaveMsg('Enregistrement d\u00e9finitif effectu\u00e9 \u2014 Donn\u00e9es verrouill\u00e9es');
            if (typeof resetSelection === 'function') resetSelection();
        })
        .catch(err => showSaveMsg(typeof err === 'string' ? err : (err.message || 'Erreur'), true));
}

function updateStatut(statut) {
    const p = getStatutParams();
    const operateur = JSON.parse(localStorage.getItem('camwater_operateur') || '{}');
    return fetch('/api/statut', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            fenetre: p.fenetre,
            agence_id: parseInt(p.agence_id),
            mois: parseInt(p.mois),
            exercice: 2026,
            statut: statut,
            operateur_nom: operateur.nom || '',
            operateur_matricule: operateur.matricule || ''
        })
    }).then(r => {
        if (!r.ok) return r.json().then(d => Promise.reject(d.error || 'Erreur'));
        return r.json();
    });
}

function showSaveMsg(msg, isError) {
    const el = document.getElementById('save-status');
    if (el) {
        el.textContent = msg;
        el.style.color = isError ? '#e74c3c' : '#27ae60';
        setTimeout(() => { el.textContent = ''; }, 5000);
    }
}

// --- Helpers (legacy) ---
function showStatus(id) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = 'Enregistr\u00e9 !';
        setTimeout(() => el.textContent = '', 3000);
    }
}
