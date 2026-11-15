// OIL SIF Precursor Detection Engine - Client Application

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    
    // Page-specific initialization
    if (document.getElementById("dashboard-root")) {
        initDashboard();
    }
    if (document.getElementById("triage-root")) {
        initTriage();
    }
    if (document.getElementById("batch-root")) {
        initBatch();
    }
});

function initNavigation() {
    // Highlight active nav item
    const path = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-link");
    navLinks.forEach(link => {
        if (link.getAttribute("href") === path) {
            link.classList.add("bg-sky-500/20", "text-sky-400", "border-sky-500");
        }
    });
}

// -------------------------------------------------------------
// DASHBOARD VIEW
// -------------------------------------------------------------
async function initDashboard() {
    try {
        const resp = await fetch("/api/dashboard-stats");
        const data = await resp.json();
        
        // Update KPIs
        document.getElementById("kpi-total-reports").innerText = data.kpis.total_reports.toLocaleString();
        document.getElementById("kpi-sif-precursors").innerText = data.kpis.sif_precursors.toLocaleString();
        document.getElementById("kpi-sif-density").innerText = `${data.kpis.sif_precursor_rate_pct}%`;
        document.getElementById("kpi-high-risk-sites").innerText = data.kpis.high_risk_facilities_count;
        
        // Render Charts
        renderIOGPChart(data.iogp_distribution);
        renderTrendChart(data.monthly_trend);
        renderSiteDensityTable(data.site_rankings);
        
        // Render Leaflet Map
        renderOilfieldMap(data.site_rankings);
    } catch (err) {
        console.error("Failed to load dashboard data:", err);
    }
}

function renderIOGPChart(iogpDist) {
    const labels = Object.keys(iogpDist);
    const series = Object.values(iogpDist);
    
    const options = {
        chart: {
            type: 'polarArea',
            height: 320,
            background: 'transparent',
            toolbar: { show: false }
        },
        labels: labels,
        series: series,
        stroke: { colors: ['#1f2937'] },
        fill: { opacity: 0.85 },
        theme: { mode: 'dark' },
        colors: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316', '#6366f1'],
        legend: {
            position: 'right',
            labels: { colors: '#9ca3af' },
            fontSize: '12px'
        },
        tooltip: {
            theme: 'dark',
            y: { formatter: val => `${val} SIF Precursors` }
        }
    };
    
    const chartEl = document.getElementById("chart-iogp");
    if (chartEl) {
        chartEl.innerHTML = "";
        const chart = new ApexCharts(chartEl, options);
        chart.render();
    }
}

function renderTrendChart(trendData) {
    const options = {
        chart: {
            type: 'area',
            height: 320,
            background: 'transparent',
            toolbar: { show: false }
        },
        series: [
            { name: 'Total Safety Reports', data: trendData.total_reports },
            { name: 'SIF Precursors Detected', data: trendData.sif_precursors }
        ],
        xaxis: {
            categories: trendData.categories,
            labels: { style: { colors: '#9ca3af' } }
        },
        yaxis: {
            labels: { style: { colors: '#9ca3af' } }
        },
        colors: ['#0ea5e9', '#ef4444'],
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 2 },
        fill: {
            type: 'gradient',
            gradient: { opacityFrom: 0.55, opacityTo: 0.05 }
        },
        theme: { mode: 'dark' },
        legend: {
            position: 'top',
            horizontalAlign: 'right',
            labels: { colors: '#9ca3af' }
        }
    };
    
    const chartEl = document.getElementById("chart-trend");
    if (chartEl) {
        chartEl.innerHTML = "";
        const chart = new ApexCharts(chartEl, options);
        chart.render();
    }
}

function renderSiteDensityTable(rankings) {
    const tbody = document.getElementById("table-site-rankings");
    if (!tbody) return;
    
    tbody.innerHTML = rankings.map((site, idx) => {
        let badgeClass = "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
        if (site.sif_density_pct >= 28.0) {
            badgeClass = "bg-rose-500/20 text-rose-400 border-rose-500/30 font-bold";
        } else if (site.sif_density_pct >= 22.0) {
            badgeClass = "bg-amber-500/20 text-amber-400 border-amber-500/30";
        }
        
        return `
            <tr class="border-b border-gray-800 hover:bg-gray-800/40 transition">
                <td class="px-4 py-3 text-xs font-mono text-gray-400">#${idx + 1}</td>
                <td class="px-4 py-3 font-medium text-gray-200">${site.site_name}</td>
                <td class="px-4 py-3 text-xs text-sky-400">${site.facility_type}</td>
                <td class="px-4 py-3 text-xs text-gray-400">${site.basin}</td>
                <td class="px-4 py-3 text-right font-mono text-gray-300">${site.total_reports}</td>
                <td class="px-4 py-3 text-right font-mono text-rose-400 font-semibold">${site.sif_precursors}</td>
                <td class="px-4 py-3 text-right">
                    <span class="inline-block px-2 py-0.5 text-xs rounded border ${badgeClass}">
                        ${site.sif_density_pct}%
                    </span>
                </td>
            </tr>
        `;
    }).join("");
}

function renderOilfieldMap(sites) {
    const mapEl = document.getElementById("oilfield-map");
    if (!mapEl || typeof L === "undefined") return;
    
    // Focus near Assam-Arakan Basin (Duliajan HQ)
    const map = L.map("oilfield-map").setView([27.3589, 95.3195], 7);
    
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a> | Oil India Limited HSE',
        maxZoom: 18
    }).addTo(map);
    
    sites.forEach(site => {
        if (!site.latitude || !site.longitude) return;
        
        let markerColor = "#10b981"; // Safe
        if (site.sif_density_pct >= 28.0) {
            markerColor = "#ef4444"; // High SIF
        } else if (site.sif_density_pct >= 22.0) {
            markerColor = "#f59e0b"; // Warning
        }
        
        const circle = L.circleMarker([site.latitude, site.longitude], {
            radius: Math.max(6, site.sif_precursors * 0.4),
            fillColor: markerColor,
            color: "#ffffff",
            weight: 1.5,
            opacity: 0.9,
            fillOpacity: 0.7
        }).addTo(map);
        
        circle.bindPopup(`
            <div class="p-2 text-sm font-sans">
                <div class="font-bold text-sky-400 mb-1">${site.site_name}</div>
                <div class="text-xs text-gray-300 mb-1"><b>Type:</b> ${site.facility_type} (${site.basin})</div>
                <div class="text-xs text-gray-300"><b>Total Reports:</b> ${site.total_reports}</div>
                <div class="text-xs text-rose-400 font-semibold"><b>SIF Precursors:</b> ${site.sif_precursors}</div>
                <div class="text-xs font-bold mt-1" style="color: ${markerColor}"><b>SIF Precursor Density:</b> ${site.sif_density_pct}%</div>
            </div>
        `);
    });
}

// -------------------------------------------------------------
// LIVE TRIAGE VIEW
// -------------------------------------------------------------
const PRESETS = [
    {
        title: "Monkey Board - Working at Height",
        text: "Floorman observed climbing the derrick ladder at 22m elevation without engaging fall arrest slider or safety harness lanyard while latching tubulars."
    },
    {
        title: "Separator Flange - Stored Pressure",
        text: "Maintenance fitter cracked flange bolts on crude discharge manifold under 600 psi residual pressure without verifying LOTO or bleed down."
    },
    {
        title: "H2S Sour Gas Alarm - Toxic Atmosphere",
        text: "Operator entered cellar pit at wellhead #4 where H2S gas detector alarm was beeping at 25 ppm without wearing SCBA escape set."
    },
    {
        title: "Crane Rigging - Heavy Suspended Load",
        text: "Near miss: synthetic web sling sheared on sharp edge while hoisting 3.5-ton casing pipe; load swung violently into drill floor rotary barrier."
    },
    {
        title: "Routine Non-SIF Observation",
        text: "Minor water spillage from drinking water cooler observed on floor of administrative corridor near tea dispenser."
    }
];

function initTriage() {
    // Populate Presets
    const presetContainer = document.getElementById("preset-buttons");
    if (presetContainer) {
        presetContainer.innerHTML = PRESETS.map((p, idx) => `
            <button onclick="loadPreset(${idx})" class="text-left px-3 py-2 text-xs rounded bg-gray-800/80 hover:bg-gray-700/80 text-gray-300 border border-gray-700 transition">
                <span class="font-semibold text-sky-400 block mb-0.5">${p.title}</span>
                <span class="truncate block text-gray-400 opacity-80">${p.text.substring(0, 50)}...</span>
            </button>
        `).join("");
    }
    
    const analyzeBtn = document.getElementById("btn-analyze-incident");
    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", runTriageAnalysis);
    }
}

function loadPreset(idx) {
    const input = document.getElementById("incident-input-text");
    if (input) {
        input.value = PRESETS[idx].text;
    }
}

async function runTriageAnalysis() {
    const input = document.getElementById("incident-input-text");
    const text = input ? input.value.trim() : "";
    if (!text) {
        alert("Please enter or select an incident report text to triage.");
        return;
    }
    
    const resultsContainer = document.getElementById("triage-results");
    const loader = document.getElementById("triage-loader");
    if (loader) loader.classList.remove("hidden");
    if (resultsContainer) resultsContainer.classList.add("hidden");
    
    try {
        const resp = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text: text,
                site_id: "OIL-RIG-01",
                report_type: "Unsafe Act"
            })
        });
        
        const data = await resp.json();
        renderTriageResults(data, text);
    } catch (err) {
        alert("Failed to analyze incident: " + err.message);
    } finally {
        if (loader) loader.classList.add("hidden");
        if (resultsContainer) resultsContainer.classList.remove("hidden");
    }
}

function renderTriageResults(data, originalText) {
    const isSif = data.sif_evaluation.is_sif_precursor;
    const prob = Math.round(data.sif_evaluation.sif_probability * 100);
    const tier = data.sif_evaluation.risk_tier;
    const rule = data.iogp_tagging.primary_iogp_rule;
    
    // Status Badge & Gauge
    const badge = document.getElementById("res-sif-badge");
    const gaugeBar = document.getElementById("res-sif-gauge-bar");
    const probVal = document.getElementById("res-sif-prob-val");
    const tierVal = document.getElementById("res-sif-tier");
    
    if (gaugeBar) gaugeBar.style.width = `${prob}%`;
    if (probVal) probVal.innerText = `${prob}%`;
    if (tierVal) tierVal.innerText = tier;
    
    if (isSif) {
        badge.className = "px-3 py-1 rounded text-sm font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse";
        badge.innerText = "CRITICAL SIF PRECURSOR DETECTED";
        if (gaugeBar) gaugeBar.className = "h-full bg-gradient-to-r from-amber-500 to-rose-600 rounded gauge-meter";
    } else {
        badge.className = "px-3 py-1 rounded text-sm font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
        badge.innerText = "ROUTINE NON-SIF OBSERVATION";
        if (gaugeBar) gaugeBar.className = "h-full bg-gradient-to-r from-sky-500 to-emerald-500 rounded gauge-meter";
    }
    
    // Rule & Confidence
    document.getElementById("res-iogp-rule").innerText = rule;
    document.getElementById("res-iogp-desc").innerText = data.iogp_tagging.rule_description;
    
    // XAI Highlighted Tokens
    const xaiContainer = document.getElementById("res-xai-tokens");
    if (xaiContainer) {
        xaiContainer.innerHTML = data.explainable_ai.highlighted_html;
    }
    
    // Engineering Rationale
    const rationaleSummary = document.getElementById("res-rationale-summary");
    if (rationaleSummary) {
        rationaleSummary.innerHTML = data.explainable_ai.summary.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
    }
    
    // Bowtie Diagram
    renderBowtieDiagram(data.bowtie_analysis);
    
    // CAPA Checklist
    renderCAPA(data.capa_actions);
    
    // Store data for briefing generation
    window.lastTriageResult = {
        data: data,
        text: originalText
    };
}

function renderBowtieDiagram(bt) {
    const container = document.getElementById("res-bowtie-diagram");
    if (!container) return;
    
    const prevBarriersHtml = bt.preventative_barriers.map(b => `
        <div class="p-2 mb-1.5 rounded text-xs text-left ${b.is_failed ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'bg-gray-800 text-gray-300 border border-gray-700'}">
            <div class="font-semibold">${b.name}</div>
            <div class="text-[10px] opacity-75">${b.type} &bull; <b>${b.status}</b></div>
        </div>
    `).join("");
    
    const mitBarriersHtml = bt.mitigative_barriers.map(b => `
        <div class="p-2 mb-1.5 rounded text-xs text-left ${b.is_failed ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'bg-blue-500/20 text-blue-300 border border-blue-500/40'}">
            <div class="font-semibold">${b.name}</div>
            <div class="text-[10px] opacity-75">${b.type} &bull; <b>${b.status}</b></div>
        </div>
    `).join("");
    
    container.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-5 gap-3 items-center text-center">
            <!-- Threat -->
            <div class="bowtie-node bowtie-threat">
                <span class="text-[10px] uppercase font-bold text-rose-400 block mb-1">Threat / Cause</span>
                <p class="text-xs">${bt.threat}</p>
            </div>
            
            <!-- Preventative Barriers -->
            <div class="bowtie-node bowtie-preventative">
                <span class="text-[10px] uppercase font-bold text-amber-400 block mb-1">Preventative Barriers</span>
                ${prevBarriersHtml}
            </div>
            
            <!-- Top Event -->
            <div class="bowtie-node bowtie-top-event">
                <span class="text-[10px] uppercase font-bold text-white block mb-1">CRITICAL TOP EVENT</span>
                <p class="text-xs">${bt.top_event}</p>
            </div>
            
            <!-- Mitigative Barriers -->
            <div class="bowtie-node bowtie-mitigative">
                <span class="text-[10px] uppercase font-bold text-sky-400 block mb-1">Mitigative Barriers</span>
                ${mitBarriersHtml}
            </div>
            
            <!-- Consequence -->
            <div class="bowtie-node bowtie-consequence">
                <span class="text-[10px] uppercase font-bold text-rose-400 block mb-1">SIF Potential Consequence</span>
                <p class="text-xs">${bt.consequence}</p>
            </div>
        </div>
    `;
}

function renderCAPA(capa) {
    const capaList = document.getElementById("res-capa-list");
    const priorityBadge = document.getElementById("res-capa-priority");
    if (priorityBadge) priorityBadge.innerText = capa.priority;
    
    if (capaList) {
        capaList.innerHTML = capa.hierarchy.map(item => `
            <div class="p-3 rounded bg-gray-800/60 border border-gray-700/60 flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center shrink-0 text-xs font-bold">
                    <i class="fa-solid fa-shield-halved"></i>
                </div>
                <div>
                    <div class="text-xs font-bold text-sky-300 uppercase tracking-wide mb-0.5">
                        ${item.level} ${item.tag ? `<span class="ml-2 text-[10px] px-1.5 py-0.2 rounded bg-gray-700 text-gray-300 font-normal">${item.tag}</span>` : ''}
                    </div>
                    <p class="text-sm text-gray-200">${item.action}</p>
                </div>
            </div>
        `).join("");
    }
}

async function generateSafetyBriefingModal() {
    if (!window.lastTriageResult) return;
    const res = window.lastTriageResult.data;
    const text = window.lastTriageResult.text;
    
    const resp = await fetch("/api/briefing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            report_id: "OIL-TRIAGE-" + Math.floor(1000 + Math.random() * 9000),
            site_name: "Oil India Field Unit",
            incident_text: text,
            iogp_rule: res.iogp_tagging.primary_iogp_rule,
            sif_probability: res.sif_evaluation.sif_probability,
            risk_tier: res.sif_evaluation.risk_tier
        })
    });
    
    const data = await resp.json();
    const modal = document.getElementById("briefing-modal");
    const modalContent = document.getElementById("briefing-text-content");
    if (modalContent) modalContent.innerText = data.briefing_text;
    if (modal) modal.classList.remove("hidden");
}

function closeBriefingModal() {
    const modal = document.getElementById("briefing-modal");
    if (modal) modal.classList.add("hidden");
}

function printBriefing() {
    const content = document.getElementById("briefing-text-content").innerText;
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<pre style="font-family: monospace; font-size: 13px; line-height: 1.4; padding: 20px;">' + content + '</pre>');
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
}

// -------------------------------------------------------------
// BATCH VIEW
// -------------------------------------------------------------
function initBatch() {
    const fileInput = document.getElementById("batch-file-input");
    const dropZone = document.getElementById("batch-drop-zone");
    
    if (dropZone && fileInput) {
        dropZone.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", handleBatchFileUpload);
        
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("border-sky-500", "bg-sky-500/10");
        });
        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("border-sky-500", "bg-sky-500/10");
        });
        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("border-sky-500", "bg-sky-500/10");
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleBatchFileUpload();
            }
        });
    }
}

async function handleBatchFileUpload() {
    const fileInput = document.getElementById("batch-file-input");
    if (!fileInput.files.length) return;
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);
    
    const loader = document.getElementById("batch-loader");
    const statsContainer = document.getElementById("batch-stats-container");
    const tableContainer = document.getElementById("batch-table-container");
    
    if (loader) loader.classList.remove("hidden");
    if (statsContainer) statsContainer.classList.add("hidden");
    if (tableContainer) tableContainer.classList.add("hidden");
    
    try {
        const resp = await fetch("/api/batch-upload", {
            method: "POST",
            body: formData
        });
        const data = await resp.json();
        
        // Populate stats
        document.getElementById("batch-total").innerText = data.total_records;
        document.getElementById("batch-sif-count").innerText = data.sif_precursors_detected;
        document.getElementById("batch-density").innerText = `${data.sif_density_pct}%`;
        
        // Render batch results table
        const tbody = document.getElementById("batch-table-body");
        if (tbody) {
            tbody.innerHTML = data.sample_results.map(row => {
                const isSif = row.is_sif_precursor;
                const badge = isSif 
                    ? '<span class="px-2 py-0.5 rounded text-xs bg-rose-500/20 text-rose-400 border border-rose-500/40 font-bold">SIF Precursor</span>'
                    : '<span class="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">Routine</span>';
                
                return `
                    <tr class="border-b border-gray-800 hover:bg-gray-800/40 transition">
                        <td class="px-4 py-3 text-xs font-mono text-gray-400">#${row.row_index}</td>
                        <td class="px-4 py-3 text-sm text-gray-200">${row.text}</td>
                        <td class="px-4 py-3">${badge}</td>
                        <td class="px-4 py-3 text-xs text-sky-400">${row.iogp_rule}</td>
                        <td class="px-4 py-3 text-right font-mono text-xs text-gray-300">${Math.round(row.sif_probability * 100)}%</td>
                    </tr>
                `;
            }).join("");
        }
        
        if (statsContainer) statsContainer.classList.remove("hidden");
        if (tableContainer) tableContainer.classList.remove("hidden");
    } catch (err) {
        alert("Batch processing failed: " + err.message);
    } finally {
        if (loader) loader.classList.add("hidden");
    }
}
