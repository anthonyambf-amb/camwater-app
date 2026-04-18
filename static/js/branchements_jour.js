/* === Branchements du Jour - Logique Frontend (v2 ⌀40/⌀20) === */

const opData = JSON.parse(localStorage.getItem('camwater_bj_op') || '{}');

// Rediriger si pas identifie
if (!opData.agence_id) {
    window.location.href = '/branchements-jour';
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
document.getElementById('bj-agence-nom').textContent = opData.agence_nom || '--';
document.getElementById('bj-dr-code').textContent = opData.dr_code || '--';
document.getElementById('bj-date-display').textContent = fmtDate(opData.date_saisie) || '--';

// Calcul automatique des totaux par catégorie et total général
var CATS = ['vendus', 'executes', 'pec', 'moratoire'];

document.querySelectorAll('.bj-input').forEach(function(inp) {
    inp.addEventListener('input', updateBjTotals);
});

function updateBjTotals() {
    var totalD40 = 0, totalD20 = 0, grandTotal = 0;
    CATS.forEach(function(cat) {
        var d40 = parseInt(document.getElementById('bj-' + cat + '-d40').value) || 0;
        var d20 = parseInt(document.getElementById('bj-' + cat + '-d20').value) || 0;
        var catTotal = d40 + d20;
        var el = document.getElementById('bj-' + cat + '-total');
        if (el) el.innerHTML = '<strong>' + fmt(catTotal) + '</strong>';
        totalD40 += d40;
        totalD20 += d20;
        grandTotal += catTotal;
    });
    var elD40 = document.getElementById('bj-total-d40');
    var elD20 = document.getElementById('bj-total-d20');
    var elTotal = document.getElementById('bj-total');
    if (elD40) elD40.textContent = fmt(totalD40);
    if (elD20) elD20.textContent = fmt(totalD20);
    if (elTotal) elTotal.textContent = fmt(grandTotal);
}

// Charger le cumul des branchements pour cette agence
function loadCumul() {
    fetch('/api/branchements-jour/cumul?agence_id=' + opData.agence_id)
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var el = document.getElementById('bj-cumul-total');
            if (el) el.textContent = fmt(data.cumul || 0);
        })
        .catch(function() {
            var el = document.getElementById('bj-cumul-total');
            if (el) el.textContent = '--';
        });
}

// Charger les donnees existantes
function loadExisting() {
    fetch('/api/branchements-jour?agence_id=' + opData.agence_id + '&date=' + opData.date_saisie)
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
    document.getElementById('bj-vendus-d40').value = data.vendus_d40 || '';
    document.getElementById('bj-vendus-d20').value = data.vendus_d20 || '';
    document.getElementById('bj-executes-d40').value = data.executes_d40 || '';
    document.getElementById('bj-executes-d20').value = data.executes_d20 || '';
    document.getElementById('bj-pec-d40').value = data.pec_d40 || '';
    document.getElementById('bj-pec-d20').value = data.pec_d20 || '';
    document.getElementById('bj-moratoire-d40').value = data.moratoire_d40 || '';
    document.getElementById('bj-moratoire-d20').value = data.moratoire_d20 || '';
    document.getElementById('bj-observations').value = data.observations || '';
    updateBjTotals();
}

function lockForm(data) {
    fillForm(data);
    document.getElementById('bj-lock-status').style.display = 'block';
    var inputs = document.querySelectorAll('.bj-input, #bj-observations');
    inputs.forEach(function(el) {
        el.disabled = true;
        el.classList.add('locked');
    });
    document.getElementById('bj-submit-btn').style.display = 'none';
}

function submitBranchementJour() {
    // Verifier qu'au moins une valeur est renseignee
    var hasValue = false;
    document.querySelectorAll('.bj-input').forEach(function(inp) {
        if (parseInt(inp.value)) hasValue = true;
    });
    if (!hasValue) {
        document.getElementById('bj-save-status').textContent = 'Veuillez renseigner au moins une valeur.';
        document.getElementById('bj-save-status').style.color = '#e74c3c';
        return;
    }

    if (!confirm('Enregistrer les branchements du jour ?\n\nATTENTION : Les donn\u00e9es seront verrouill\u00e9es apr\u00e8s enregistrement.\nVous ne pourrez plus modifier cette saisie.')) {
        return;
    }

    var gv = function(id) { return parseInt(document.getElementById(id).value) || 0; };

    var payload = {
        agence_id: parseInt(opData.agence_id),
        date_saisie: opData.date_saisie,
        vendus_d40: gv('bj-vendus-d40'),
        vendus_d20: gv('bj-vendus-d20'),
        vendus: gv('bj-vendus-d40') + gv('bj-vendus-d20'),
        executes_d40: gv('bj-executes-d40'),
        executes_d20: gv('bj-executes-d20'),
        executes: gv('bj-executes-d40') + gv('bj-executes-d20'),
        pec_d40: gv('bj-pec-d40'),
        pec_d20: gv('bj-pec-d20'),
        pec_machine: gv('bj-pec-d40') + gv('bj-pec-d20'),
        moratoire_d40: gv('bj-moratoire-d40'),
        moratoire_d20: gv('bj-moratoire-d20'),
        moratoire: gv('bj-moratoire-d40') + gv('bj-moratoire-d20'),
        observations: document.getElementById('bj-observations').value.trim(),
        operateur_nom: '',
        operateur_matricule: opData.matricule
    };

    fetch('/api/branchements-jour', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(function(r) { return r.json().then(function(d) { return { ok: r.ok, data: d }; }); })
    .then(function(result) {
        var statusEl = document.getElementById('bj-save-status');
        if (!result.ok) {
            statusEl.textContent = result.data.error || 'Erreur';
            statusEl.style.color = '#e74c3c';
            return;
        }
        statusEl.textContent = 'Branchements enregistr\u00e9s et verrouill\u00e9s avec succ\u00e8s';
        statusEl.style.color = '#27ae60';
        lockForm(payload);
        loadCumul();
    });
}

// Initialisation
loadExisting();
