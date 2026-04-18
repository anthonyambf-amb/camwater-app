/* === Dashboard / Visualisation - Frontend v2 === */

let charts = {};

function fmt(n) {
    if (!n && n !== 0) return '-';
    return Math.round(n).toLocaleString('fr-FR');
}

function fmtMds(n) {
    if (!n) return '0';
    return Math.round(n).toLocaleString('fr-FR');
}

function fmtPct(n) {
    return (n * 100).toFixed(1) + '%';
}

function fmtEvol(taux) {
    const pct = (taux * 100).toFixed(1);
    if (taux > 0) return `+${pct}%`;
    if (taux < 0) return `${pct}%`;
    return '0%';
}

const COLORS = {
    primary: '#0056b3',
    secondary: '#003d82',
    accent: '#2980b9',
    danger: '#e74c3c',
    success: '#27ae60',
    teal: '#1a6bc4',
    drColors: [
        '#002b5c', '#003d82', '#0056b3', '#1a6bc4', '#2980b9', '#3498db',
        '#5dade2', '#1a3f6f', '#154c79', '#1b4f72', '#2471a3', '#85c1e9'
    ],
    clientColors: ['#002b5c', '#0056b3', '#2980b9', '#5dade2', '#85c1e9'],
    trendUp: '#27ae60',
    trendDown: '#e74c3c'
};

// --- Params helpers ---
function getDashParams() {
    const siteSel = document.getElementById('dash-site').value;
    const moisDebut = document.getElementById('dash-mois-debut').value;
    const moisFin = document.getElementById('dash-mois-fin').value;
    let site_type = 'national', site_id = '';
    if (siteSel.startsWith('dr:')) {
        site_type = 'dr';
        site_id = siteSel.replace('dr:', '');
    }
    return { site_type, site_id, mois_debut: moisDebut, mois_fin: moisFin };
}

function buildQS(params) {
    return Object.entries(params).filter(([,v]) => v !== '').map(([k,v]) => `${k}=${encodeURIComponent(v)}`).join('&');
}

// --- Main load ---
function loadDashboard() {
    const p = getDashParams();
    const label = p.site_type === 'national' ? 'Ensemble CAMWATER' : p.site_id;
    const mDebLabel = MOIS_NAMES[parseInt(p.mois_debut) - 1];
    const mFinLabel = MOIS_NAMES[parseInt(p.mois_fin) - 1];
    document.getElementById('dash-date').textContent =
        `${label} \u2014 ${mDebLabel} \u00e0 ${mFinLabel} 2026`;

    fetch(`/api/dashboard?${buildQS(p)}`)
        .then(r => r.json())
        .then(data => {
            renderKPIs(data);
            renderTauxEncaissement(data);
            renderCaDrChart(data);
            renderClientsPieChart(data);
            renderEncEvolutionChart(data);
            renderObjectifs(data);
            renderRecouvDrChart(data);
            renderBranchementsDrChart(data);
            renderVolEvolutionChart(data);
            renderDecomposition(data);
        });

    // Charger les stats impayés
    fetch(`/api/impayes/dashboard?${buildQS(p)}`)
        .then(r => r.json())
        .then(data => {
            renderImpayesKPIs(data);
            renderImpayesCategorieChart(data);
            renderImpayesDrChart(data);
            renderImpayesEvolChart(data);
        })
        .catch(() => {});

    // Charger les stats branchements quotidiens
    fetch(`/api/branchements-jour/dashboard-stats?${buildQS(p)}`)
        .then(r => r.json())
        .then(data => {
            renderBranchJourKPIs(data);
            renderBranchJourDrChart(data);
            renderBranchJourEvolChart(data);
        })
        .catch(() => {});

    // Charger les paiements électroniques par opérateur
    fetch(`/api/paiements-elec/dashboard-operators?${buildQS(p)}`)
        .then(r => r.json())
        .then(data => { renderDashPEOperators(data); })
        .catch(() => {});
}

// --- KPI Cards ---
function renderKPIs(data) {
    const c = data.cumul || {};
    const evol = data.evolutions || {};

    document.getElementById('kpi-ca').textContent = fmtMds(c.ca_global || 0);
    setTrend('kpi-ca-trend', evol.ca_global);

    document.getElementById('kpi-enc').textContent = fmtMds(c.total_encaissements || 0);
    setTrend('kpi-enc-trend', evol.total_encaissements);

    document.getElementById('kpi-taux').textContent = fmtPct(c.taux_recouvrement_ef || 0);
    setTrend('kpi-taux-trend', evol.taux_recouvrement_ef, true);

    // Paiements électroniques (depuis module PE dédié)
    const pctElec = data.pct_paiements_elec || 0;
    document.getElementById('kpi-elec').textContent = fmtPct(pctElec);
    const peTotal = data.pe_total || 0;
    document.getElementById('kpi-elec-sub').textContent = fmtMds(peTotal) + ' FCFA';
}

function setTrend(elId, evolData, isDiff) {
    const el = document.getElementById(elId);
    if (!el || !evolData) return;
    const taux = evolData.taux || 0;
    const cls = taux >= 0 ? 'up' : 'down';
    const arrow = taux >= 0 ? '\u25B2' : '\u25BC';
    if (isDiff) {
        const pts = (taux * 100).toFixed(1);
        el.innerHTML = `<span class="kpi-trend ${cls}">${arrow} ${pts >= 0 ? '+' : ''}${pts} pts vs N-1</span>`;
    } else {
        el.innerHTML = `<span class="kpi-trend ${cls}">${arrow} ${fmtEvol(taux)} vs N-1</span>`;
    }
}

// --- Taux d'encaissement & évolution N/N-1 ---
function renderTauxEncaissement(data) {
    const c = data.cumul || {};
    const evol = data.evolutions || {};

    setKpiMini('kpi-taux-ve', fmtPct(c.taux_enc_ve || 0));
    setKpiMini('kpi-taux-trvx', fmtPct(c.taux_enc_trvx || 0));
    setKpiMini('kpi-taux-global', fmtPct(c.taux_enc_global || 0));
    setKpiMini('kpi-taux-ef', fmtPct(c.taux_recouvrement_ef || 0));

    // Evolutions N/N-1
    setEvolMini('kpi-evol-vol', evol.total_volumes);
    setEvolMini('kpi-evol-ca', evol.ca_global);
    setEvolMini('kpi-evol-enc', evol.total_encaissements);
}

function setKpiMini(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}

function setEvolMini(id, evolData) {
    const el = document.getElementById(id);
    if (!el || !evolData) return;
    const taux = evolData.taux || 0;
    const cls = taux >= 0 ? 'up' : 'down';
    el.innerHTML = `<span class="kpi-trend ${cls}">${fmtEvol(taux)}</span>`;
}

// --- CA par DR (bar chart) ---
function renderCaDrChart(data) {
    const ctx = document.getElementById('chart-ca-dr');
    if (!ctx) return;
    if (charts.caDr) charts.caDr.destroy();

    const kpis = data.kpis_dr || {};
    const labels = DR_LIST.filter(dr => kpis[dr]);
    const values = labels.map(dr => kpis[dr].ca_global || 0);

    charts.caDr = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'CA Global (FCFA)',
                data: values,
                backgroundColor: COLORS.drColors.slice(0, labels.length),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { ticks: { callback: v => fmtMds(v) } } }
        }
    });
}

// --- Répartition clients (pie chart) ---
function renderClientsPieChart(data) {
    const ctx = document.getElementById('chart-clients-pie');
    if (!ctx) return;
    if (charts.clientsPie) charts.clientsPie.destroy();

    const rep = data.repartition_clients || {};
    const labels = Object.keys(rep);
    const values = Object.values(rep);

    charts.clientsPie = new Chart(ctx, {
        type: 'pie',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.clientColors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right', labels: { font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = total ? ((ctx.raw / total) * 100).toFixed(1) : 0;
                            return `${ctx.label}: ${fmtMds(ctx.raw)} FCFA (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

// --- Encaissements evolution (horizontal bar chart : mois en Y, valeurs en X) ---
function renderEncEvolutionChart(data) {
    const ctx = document.getElementById('chart-enc-evol');
    if (!ctx) return;
    if (charts.encEvol) charts.encEvol.destroy();

    const evol = data.evolution_mensuelle || [];
    const labels = evol.map(e => MOIS_NAMES[e.mois - 1].substring(0, 3));

    charts.encEvol = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                { label: 'CA Global', data: evol.map(e => e.ca_global), backgroundColor: COLORS.primary, borderRadius: 4 },
                { label: 'Encaissements', data: evol.map(e => e.encaissements), backgroundColor: COLORS.accent, borderRadius: 4 }
            ]
        },
        options: {
            indexAxis: 'y',          // → barres horizontales (mois en vertical)
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
                x: { ticks: { callback: v => fmtMds(v) } },
                y: { ticks: { font: { size: 11 } } }
            }
        }
    });
}

// --- Objectifs vs Réalisations ---
function renderObjectifs(data) {
    var tbody = document.getElementById('obj-vs-real-body');
    if (!tbody) return;

    var items = data.objectifs_vs_real || [];

    if (items.length === 0) {
        // Fallback : ancienne logique avec objectif_enc seul
        var obj = data.objectif_enc || 0;
        var real = (data.cumul || {}).total_encaissements || 0;
        var taux = data.taux_realisation || 0;
        if (obj > 0) {
            items = [{ rubrique: 'Encaissements', objectif: obj, realise: real, taux: taux }];
        } else {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#888;">Aucun objectif d\u00e9fini pour cet exercice</td></tr>';
            return;
        }
    }

    var html = '';
    items.forEach(function(item) {
        var pct = item.taux || 0;
        var pctDisplay = (pct * 100).toFixed(1) + '%';
        var barWidth = Math.min(pct * 100, 100).toFixed(1);
        var barColor = pct >= 1 ? '#27ae60' : pct >= 0.7 ? '#f39c12' : pct >= 0.4 ? '#e67e22' : '#e74c3c';
        html += '<tr>';
        html += '<td><strong>' + item.rubrique + '</strong></td>';
        html += '<td style="text-align:right">' + fmtMds(item.objectif || 0) + '</td>';
        html += '<td style="text-align:right">' + fmtMds(item.realise || 0) + '</td>';
        html += '<td style="text-align:right;font-weight:bold;color:' + barColor + '">' + pctDisplay + '</td>';
        html += '<td><div class="progress-bar" style="height:14px;margin:0;"><div class="progress-fill" style="width:' + barWidth + '%;background:' + barColor + ';"></div></div></td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

// --- Recouvrement par DR (horizontal bar) ---
function renderRecouvDrChart(data) {
    const ctx = document.getElementById('chart-recouv-dr');
    if (!ctx) return;
    if (charts.recouvDr) charts.recouvDr.destroy();

    const kpis = data.kpis_dr || {};
    const sorted = DR_LIST
        .filter(dr => kpis[dr])
        .sort((a, b) => (kpis[b].taux_recouvrement_ef || 0) - (kpis[a].taux_recouvrement_ef || 0));
    const values = sorted.map(dr => (kpis[dr].taux_recouvrement_ef || 0) * 100);
    const bgColors = values.map(v => v >= 70 ? COLORS.success : v >= 50 ? COLORS.accent : COLORS.danger);

    charts.recouvDr = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted,
            datasets: [{
                label: 'Taux recouvrement E.F. (%)',
                data: values,
                backgroundColor: bgColors,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { x: { max: 100, ticks: { callback: v => v + '%' } } }
        }
    });
}

// --- Branchements par DR ---
function renderBranchementsDrChart(data) {
    const ctx = document.getElementById('chart-brch-dr');
    if (!ctx) return;
    if (charts.brchDr) charts.brchDr.destroy();

    const brchDr = data.branchements_par_dr || {};
    const labels = DR_LIST;

    charts.brchDr = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                { label: 'Vendus', data: labels.map(dr => (brchDr[dr] || {}).vendus || 0), backgroundColor: '#002b5c', borderRadius: 3 },
                { label: 'Exécutés', data: labels.map(dr => (brchDr[dr] || {})['exécutés'] || 0), backgroundColor: '#0056b3', borderRadius: 3 },
                { label: 'PEC', data: labels.map(dr => (brchDr[dr] || {}).pec || 0), backgroundColor: '#5dade2', borderRadius: 3 },
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

// --- Volumes evolution mensuelle (line chart) ---
function renderVolEvolutionChart(data) {
    const ctx = document.getElementById('chart-vol-evol');
    if (!ctx) return;
    if (charts.volEvol) charts.volEvol.destroy();

    const evol = data.evolution_mensuelle || [];
    const labels = evol.map(e => MOIS_NAMES[e.mois - 1].substring(0, 3));

    charts.volEvol = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Volumes facturés (m3)',
                data: evol.map(e => e.volumes),
                borderColor: COLORS.primary,
                backgroundColor: 'rgba(0,86,179,0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true, ticks: { callback: v => fmtMds(v) } } }
        }
    });
}

// --- CA Global Decomposition ---
function renderDecomposition(data) {
    const c = data.cumul || {};
    const caAuto = (c.total_ve || 0) - (c.total_ca_spec || 0);

    document.getElementById('dec-ca-auto').textContent = fmtMds(caAuto) + ' FCFA';
    document.getElementById('dec-ca-spec').textContent = fmtMds(c.total_ca_spec || 0) + ' FCFA';
    document.getElementById('dec-total-ve').textContent = fmtMds(c.total_ve || 0) + ' FCFA';
    document.getElementById('dec-brchts').textContent = fmtMds(c.brchts_neufs || 0) + ' FCFA';
    document.getElementById('dec-penal').textContent = fmtMds(c.penalites || 0) + ' FCFA';
    document.getElementById('dec-devis').textContent = fmtMds(c.devis_ext || 0) + ' FCFA';
    document.getElementById('dec-autres').textContent = fmtMds(c.autres_trvx || 0) + ' FCFA';
    document.getElementById('dec-comp').textContent = fmtMds(c.complement || 0) + ' FCFA';
    document.getElementById('dec-fraudes').textContent = fmtMds(c.fraudes_trvx || 0) + ' FCFA';
    document.getElementById('dec-total-trvx').textContent = fmtMds(c.total_trvx_remb || 0) + ' FCFA';
    document.getElementById('dec-ca-global').textContent = fmtMds(c.ca_global || 0) + ' FCFA';
}

// --- Exports ---
function exportConsolidation() {
    const p = getDashParams();
    window.location.href = `/api/export/consolidation?${buildQS(p)}`;
}

function exportData(type) {
    const p = getDashParams();
    window.location.href = `/api/export/${type}?${buildQS(p)}`;
    document.getElementById('export-menu').classList.remove('show');
}

function toggleExportMenu() {
    document.getElementById('export-menu').classList.toggle('show');
}

// Close menu on outside click
document.addEventListener('click', e => {
    const menu = document.getElementById('export-menu');
    if (menu && !e.target.closest('.export-dropdown') && !e.target.closest('.btn-export-more')) {
        menu.classList.remove('show');
    }
});

// --- Branchements Quotidiens (dashboard) ---
function renderBranchJourKPIs(data) {
    const t = data.totaux || {};
    const el = id => document.getElementById(id);
    if (el('bj-centres')) el('bj-centres').textContent = data.centres || '0 / 0';
    if (el('bj-vendus')) el('bj-vendus').textContent = fmt(t.vendus || 0);
    if (el('bj-executes')) el('bj-executes').textContent = fmt(t.executes || 0);
    if (el('bj-pec')) el('bj-pec').textContent = fmt(t.pec_machine || 0);
    if (el('bj-moratoire')) el('bj-moratoire').textContent = fmt(t.moratoire || 0);
}

function renderBranchJourDrChart(data) {
    const ctx = document.getElementById('chart-bj-dr');
    if (!ctx) return;
    if (charts.bjDr) charts.bjDr.destroy();

    const parDr = data.par_dr || {};
    const labels = Object.keys(parDr).sort();
    if (labels.length === 0) {
        charts.bjDr = new Chart(ctx, {
            type: 'bar', data: { labels: ['Aucune donnée'], datasets: [{ data: [0] }] },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
        return;
    }

    charts.bjDr = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                { label: 'Vendus', data: labels.map(dr => parDr[dr].vendus), backgroundColor: '#002b5c', borderRadius: 3 },
                { label: 'Exécutés', data: labels.map(dr => parDr[dr].executes), backgroundColor: '#0056b3', borderRadius: 3 },
                { label: 'PEC', data: labels.map(dr => parDr[dr].pec_machine), backgroundColor: '#5dade2', borderRadius: 3 }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

function renderBranchJourEvolChart(data) {
    const ctx = document.getElementById('chart-bj-evol');
    if (!ctx) return;
    if (charts.bjEvol) charts.bjEvol.destroy();

    const evol = data.evolution || [];
    if (evol.length === 0) {
        charts.bjEvol = new Chart(ctx, {
            type: 'line', data: { labels: ['Aucune donnée'], datasets: [{ data: [0] }] },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
        return;
    }
    const labels = evol.map(e => {
        const parts = e.date.split('-');
        return parts[2] + '/' + parts[1];
    });

    charts.bjEvol = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: 'Vendus', data: evol.map(e => e.vendus), borderColor: '#002b5c', backgroundColor: 'rgba(0,43,92,0.1)', fill: false, tension: 0.3 },
                { label: 'Exécutés', data: evol.map(e => e.executes), borderColor: '#0056b3', backgroundColor: 'rgba(0,86,179,0.1)', fill: false, tension: 0.3 },
                { label: 'PEC', data: evol.map(e => e.pec_machine), borderColor: '#5dade2', backgroundColor: 'rgba(93,173,226,0.1)', fill: false, tension: 0.3 }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

// === Impayés Dashboard ===

function renderImpayesKPIs(data) {
    const t = data.totaux || {};
    const el = id => document.getElementById(id);
    if (el('imp-dash-total')) el('imp-dash-total').textContent = fmtMds(t.total_impayes || 0);
    // Afficher le mois de référence (fin de période) à côté du total
    const moisLabel = el('imp-dash-mois-label');
    if (moisLabel) {
        const evol = data.evolution_mensuelle || [];
        const last = evol.filter(e => e.in_range !== false).pop();
        if (last) moisLabel.textContent = `— ${MOIS_NAMES[last.mois - 1]}`;
        else moisLabel.textContent = '';
    }
}

function renderImpayesCategorieChart(data) {
    const ctx = document.getElementById('chart-imp-categorie');
    if (!ctx) return;
    if (charts.impCategorie) charts.impCategorie.destroy();

    const pc = data.par_categorie || {};
    const labels = Object.keys(pc);
    const values = Object.values(pc);

    if (values.every(v => v === 0)) {
        charts.impCategorie = new Chart(ctx, {
            type: 'pie', data: { labels: ['Aucune donnée'], datasets: [{ data: [1], backgroundColor: ['#ddd'] }] },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
        return;
    }

    charts.impCategorie = new Chart(ctx, {
        type: 'pie',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: ['#0056b3', '#e67e22', '#16a085', '#8e44ad'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right', labels: { font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = total ? ((ctx.raw / total) * 100).toFixed(1) : 0;
                            return `${ctx.label}: ${fmtMds(ctx.raw)} FCFA (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

function renderImpayesDrChart(data) {
    const ctx = document.getElementById('chart-imp-dr');
    if (!ctx) return;
    if (charts.impDr) charts.impDr.destroy();

    const parDr = data.par_dr || {};
    const labels = Object.keys(parDr).sort();

    if (labels.length === 0) {
        charts.impDr = new Chart(ctx, {
            type: 'bar', data: { labels: ['Aucune donnée'], datasets: [{ data: [0] }] },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
        return;
    }

    charts.impDr = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                { label: 'Actifs', data: labels.map(dr => parDr[dr].actifs), backgroundColor: '#0056b3', borderRadius: 3 },
                { label: 'Résiliés', data: labels.map(dr => parDr[dr].resilies), backgroundColor: '#c0392b', borderRadius: 3 }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: {
                x: { stacked: true },
                y: { stacked: true, ticks: { callback: v => fmtMds(v) } }
            }
        }
    });
}

function renderImpayesEvolChart(data) {
    const ctx = document.getElementById('chart-imp-evol');
    if (!ctx) return;
    if (charts.impEvol) charts.impEvol.destroy();

    const evol = data.evolution_mensuelle || [];
    // On a besoin d'au moins 2 mois (un mois de référence + un mois dans la plage)
    // pour calculer la variation % vs M-1.
    const inRange = evol.filter(e => e.in_range !== false);
    if (inRange.length === 0) {
        charts.impEvol = new Chart(ctx, {
            type: 'line', data: { labels: ['Aucune donnée'], datasets: [{ data: [0] }] },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
        return;
    }

    // 8 catégories clients + couleurs
    const CATS = [
        { key: 'particuliers_actifs',   label: 'Particuliers Actifs',   color: '#2980b9' },
        { key: 'gco_actifs',            label: 'GCO Actifs',            color: '#27ae60' },
        { key: 'particuliers_resilies', label: 'Particuliers Résiliés', color: '#c0392b' },
        { key: 'gco_resilies',          label: 'GCO Résiliés',          color: '#e67e22' },
        { key: 'bf_actifs',             label: 'BF Actifs',             color: '#16a085' },
        { key: 'bfc_actifs',            label: 'BFC Actifs',            color: '#8e44ad' },
        { key: 'bf_resilies',           label: 'BF Résiliés',           color: '#d35400' },
        { key: 'bfc_resilies',          label: 'BFC Résiliés',          color: '#7f8c8d' },
    ];

    // Labels = uniquement les mois de la plage sélectionnée
    const labels = inRange.map(e => MOIS_NAMES[e.mois - 1].substring(0, 3));

    // Pour chaque mois dans la plage, on trouve le précédent dans evol (même s'il est
    // hors plage — on l'a demandé à l'API exprès) et on calcule (m - m_prev) / m_prev × 100
    function pctDelta(key, idxInFull) {
        if (idxInFull === 0) return null;
        const prev = evol[idxInFull - 1][key] || 0;
        const curr = evol[idxInFull][key] || 0;
        if (prev === 0) return curr === 0 ? 0 : null;  // pas de base → non calculable
        return ((curr - prev) / prev) * 100;
    }

    const datasets = CATS.map(c => ({
        label: c.label,
        data: inRange.map(e => {
            const idx = evol.findIndex(x => x.mois === e.mois);
            return pctDelta(c.key, idx);
        }),
        borderColor: c.color,
        backgroundColor: c.color + '33',
        fill: false,
        tension: 0.25,
        borderWidth: 2,
        pointRadius: 3,
        spanGaps: true,
    }));

    charts.impEvol = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 12 } },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const v = ctx.raw;
                            if (v === null || v === undefined) return ctx.dataset.label + ' : n/a';
                            const sign = v > 0 ? '+' : '';
                            return `${ctx.dataset.label} : ${sign}${v.toFixed(1)} %`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: { display: true, text: 'Variation % vs M-1' },
                    ticks: { callback: v => v + ' %' }
                }
            }
        }
    });
}

function exportImpayes() {
    const p = getDashParams();
    window.location.href = `/api/export/impayes?${buildQS(p)}`;
    document.getElementById('export-menu').classList.remove('show');
}

// === Paiements Électroniques - Opérateurs (Dashboard) ===

function renderDashPEOperators(data) {
    const container = document.getElementById('dash-pe-bubbles');
    if (!container) return;

    const operators = data.operators || [];
    const total = data.montant_total || 0;

    if (operators.length === 0) {
        container.innerHTML = '<p style="color:#888;font-size:0.85rem;">Aucune donn\u00e9e de paiement \u00e9lectronique disponible</p>';
        // Masquer la section si pas de données
        const section = document.getElementById('section-pe-operators');
        if (section) section.style.display = 'none';
        return;
    }

    // Afficher la section
    const section = document.getElementById('section-pe-operators');
    if (section) section.style.display = '';

    const colors = ['#0056b3', '#27ae60', '#e67e22', '#8e44ad', '#e74c3c', '#1abc9c', '#f39c12', '#3498db', '#2c3e50', '#d35400'];
    let html = '';
    operators.forEach(function(op, idx) {
        const montant = op.montant || 0;
        const pct = op.taux || 0;
        const color = colors[idx % colors.length];
        html += '<div class="pe-bubble" style="border-left-color:' + color + ';">';
        html += '<div class="pe-bubble-name">' + op.operateur + '</div>';
        html += '<div class="pe-bubble-amount">' + fmtMds(montant) + ' FCFA</div>';
        html += '<div class="pe-bubble-pct" style="color:' + color + ';">' + fmtPct(pct) + '</div>';
        html += '<div class="pe-bubble-bar"><div style="width:' + (pct * 100).toFixed(1) + '%;background:' + color + ';"></div></div>';
        html += '</div>';
    });

    // Total général
    html += '<div class="pe-bubble pe-bubble-total">';
    html += '<div class="pe-bubble-name">TOTAL PAIEMENTS \u00c9LECTRONIQUES</div>';
    html += '<div class="pe-bubble-amount" style="font-size:1.3rem;">' + fmtMds(total) + ' FCFA</div>';
    html += '<div class="pe-bubble-pct">100%</div>';
    html += '</div>';

    container.innerHTML = html;
}

// --- Impression PDF ---
function printDashboardPDF() {
    window.print();
}
