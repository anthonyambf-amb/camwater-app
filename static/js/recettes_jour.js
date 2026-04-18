/* === Recettes du Jour - Logique Frontend === */

const opData = JSON.parse(localStorage.getItem('camwater_rj_op') || '{}');

// Rediriger si pas identifié
if (!opData.agence_id) {
    window.location.href = '/recettes-jour';
}

function fmt(n) {
    if (!n && n !== 0) return '0';
    return Math.round(n).toLocaleString('fr-FR');
}

function fmtDate(d) {
    if (!d) return '';
    var parts = d.split('-');
    if (parts.length === 3) return parts[2] + '/' + parts[1] + '/' + parts[0];
    return d;
}

// Remplir la barre d'info
document.getElementById('rj-agence-nom').textContent = opData.agence_nom || '--';
document.getElementById('rj-dr-code').textContent = opData.dr_code || '--';
document.getElementById('rj-date-display').textContent = fmtDate(opData.date_saisie) || '--';

// Calcul automatique du total
document.querySelectorAll('.rj-input').forEach(function(inp) {
    inp.addEventListener('input', updateRjTotal);
});

function updateRjTotal() {
    var fields = ['rj-caisse', 'rj-cheques', 'rj-hors-sites', 'rj-virements', 'rj-elec'];
    var total = 0;
    fields.forEach(function(id) {
        total += parseFloat(document.getElementById(id).value) || 0;
    });
    document.getElementById('rj-total').textContent = fmt(total);
}

// Afficher/masquer le champ convoyeur "Autre"
document.getElementById('rj-convoyeur').addEventListener('change', function() {
    var wrap = document.getElementById('rj-convoyeur-autre-wrap');
    if (this.value === 'Autre') {
        wrap.style.display = 'block';
        document.getElementById('rj-convoyeur-autre').focus();
    } else {
        wrap.style.display = 'none';
        document.getElementById('rj-convoyeur-autre').value = '';
    }
});

// Charger le cumul des recettes pour cette agence
function loadCumul() {
    fetch('/api/recettes-jour/cumul?agence_id=' + opData.agence_id)
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var el = document.getElementById('rj-cumul-total');
            if (el) {
                el.textContent = fmt(data.cumul || 0) + ' FCFA';
            }
        })
        .catch(function() {
            var el = document.getElementById('rj-cumul-total');
            if (el) el.textContent = '-- FCFA';
        });
}

// Charger les données existantes
function loadExisting() {
    fetch('/api/recettes-jour?agence_id=' + opData.agence_id + '&date=' + opData.date_saisie)
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.verrouille) {
                lockForm(data);
            } else if (data.id) {
                fillForm(data);
            }
            loadCumul();
        });
}

function fillForm(data) {
    document.getElementById('rj-caisse').value = data.caisse_commerciale || '';
    document.getElementById('rj-cheques').value = data.cheques || '';
    document.getElementById('rj-hors-sites').value = data.hors_sites || '';
    document.getElementById('rj-virements').value = data.virements || '';
    document.getElementById('rj-elec').value = data.paiements_electroniques || '';
    if (data.type_piece) document.getElementById('rj-type-piece').value = data.type_piece;
    document.getElementById('rj-num-piece').value = data.numero_piece || '';
    // Convoyeur
    var convSel = document.getElementById('rj-convoyeur');
    var convoyeur = data.convoyeur || '';
    if (convoyeur === 'Cotrava' || convoyeur === 'Transval') {
        convSel.value = convoyeur;
    } else if (convoyeur) {
        convSel.value = 'Autre';
        document.getElementById('rj-convoyeur-autre-wrap').style.display = 'block';
        document.getElementById('rj-convoyeur-autre').value = convoyeur;
    }
    // Banque
    if (data.banque_depot) document.getElementById('rj-banque-depot').value = data.banque_depot;
    updateRjTotal();
}

function lockForm(data) {
    fillForm(data);
    // Afficher le statut verrouillé
    document.getElementById('rj-lock-status').style.display = 'block';
    // Désactiver tous les champs
    var inputs = document.querySelectorAll('.rj-input, #rj-type-piece, #rj-num-piece, #rj-convoyeur, #rj-convoyeur-autre, #rj-banque-depot');
    inputs.forEach(function(el) {
        el.disabled = true;
        el.classList.add('locked');
    });
    // Masquer le bouton
    document.getElementById('rj-submit-btn').style.display = 'none';
}

function getConvoyeurValue() {
    var sel = document.getElementById('rj-convoyeur').value;
    if (sel === 'Autre') {
        return document.getElementById('rj-convoyeur-autre').value.trim() || 'Autre';
    }
    return sel;
}

function submitRecetteJour() {
    // Vérifier qu'au moins un montant est renseigné
    var fields = ['rj-caisse', 'rj-cheques', 'rj-hors-sites', 'rj-virements', 'rj-elec'];
    var hasValue = false;
    fields.forEach(function(id) {
        if (parseFloat(document.getElementById(id).value)) hasValue = true;
    });
    if (!hasValue) {
        document.getElementById('rj-save-status').textContent = 'Veuillez renseigner au moins un montant.';
        document.getElementById('rj-save-status').style.color = '#e74c3c';
        return;
    }

    // Vérifier justificatif
    if (!document.getElementById('rj-type-piece').value) {
        document.getElementById('rj-save-status').textContent = 'Veuillez sélectionner le type de pièce.';
        document.getElementById('rj-save-status').style.color = '#e74c3c';
        return;
    }

    // Vérifier convoyeur
    if (!document.getElementById('rj-convoyeur').value) {
        document.getElementById('rj-save-status').textContent = 'Veuillez sélectionner le convoyeur de fonds.';
        document.getElementById('rj-save-status').style.color = '#e74c3c';
        return;
    }

    // Vérifier banque
    if (!document.getElementById('rj-banque-depot').value) {
        document.getElementById('rj-save-status').textContent = 'Veuillez sélectionner la banque de dépôt.';
        document.getElementById('rj-save-status').style.color = '#e74c3c';
        return;
    }

    if (!confirm('Enregistrer la recette du jour ?\n\nATTENTION : Les données seront verrouillées après enregistrement.\nVous ne pourrez plus modifier cette saisie.')) {
        return;
    }

    var payload = {
        agence_id: parseInt(opData.agence_id),
        date_saisie: opData.date_saisie,
        caisse_commerciale: parseFloat(document.getElementById('rj-caisse').value) || 0,
        cheques: parseFloat(document.getElementById('rj-cheques').value) || 0,
        hors_sites: parseFloat(document.getElementById('rj-hors-sites').value) || 0,
        virements: parseFloat(document.getElementById('rj-virements').value) || 0,
        paiements_electroniques: parseFloat(document.getElementById('rj-elec').value) || 0,
        type_piece: document.getElementById('rj-type-piece').value,
        numero_piece: document.getElementById('rj-num-piece').value,
        convoyeur: getConvoyeurValue(),
        banque_depot: document.getElementById('rj-banque-depot').value,
        operateur_nom: '',
        operateur_matricule: opData.matricule
    };

    fetch('/api/recettes-jour', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(function(r) { return r.json().then(function(d) { return { ok: r.ok, data: d }; }); })
    .then(function(result) {
        var statusEl = document.getElementById('rj-save-status');
        if (!result.ok) {
            statusEl.textContent = result.data.error || 'Erreur';
            statusEl.style.color = '#e74c3c';
            return;
        }
        statusEl.textContent = 'Recette enregistrée et verrouillée avec succès';
        statusEl.style.color = '#27ae60';
        lockForm(payload);
        loadCumul();
    });
}

// Initialisation
loadExisting();
