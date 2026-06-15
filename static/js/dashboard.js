// ── TAB SWITCHING ──
function switchTab(id, btn) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + id).classList.add('active');
    btn.classList.add('active');
    window.scrollTo(0, 0);
}

// ── CAROUSEL DOTS ──
(function () {
    const track = document.getElementById('carousel');
    const dotsEl = document.getElementById('carousel-dots');
    if (!track || !dotsEl) return;
    const cards = track.querySelectorAll('.sensor-card');
    if (cards.length <= 1) { dotsEl.style.display = 'none'; return; }

    cards.forEach((_, i) => {
        const d = document.createElement('div');
        d.className = 'dot' + (i === 0 ? ' active' : '');
        dotsEl.appendChild(d);
    });

    track.addEventListener('scroll', () => {
        const idx = Math.round(track.scrollLeft / 280);
        dotsEl.querySelectorAll('.dot').forEach((d, i) => {
            d.classList.toggle('active', i === idx);
        });
    }, { passive: true });
})();

// ── TIMESTAMPS ──
document.querySelectorAll('.timestamp').forEach(el => {
    const raw = el.textContent.replace('Updated', '').trim();
    const d = new Date(raw);
    if (!isNaN(d)) {
        el.textContent = 'Updated ' + d.toLocaleString('en-AU', {
            month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', hour12: true
        });
    }
});

// ── AIRBAND ──
async function checkAirbandStatus() {
    try {
        const res = await fetch('/api/airband');
        const data = await res.json();
        const dot = document.getElementById('airband-dot');
        const status = document.getElementById('airband-status');
        const cfg = document.getElementById('airband-config-display');
        const isActive = data.status === 'active';
        dot.className = 'status-dot ' + (isActive ? 'active' : 'error');
        status.textContent = isActive ? 'Active' : 'Inactive';
        if (data.config && cfg) cfg.textContent = data.config;
    } catch (e) {
        document.getElementById('airband-status').textContent = 'Unavailable';
    }
}

async function switchPreset() {
    const val = document.getElementById('preset-select').value;
    const fb = document.getElementById('airband-feedback');
    if (!val) { fb.textContent = 'Select a preset first'; return; }
    fb.textContent = 'Loading ' + val + '...';
    try {
        const res = await fetch('/api/airband', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config: val })
        });
        const data = await res.json();
        fb.textContent = data.status === 'success' ? 'Loaded ' + val : 'Error: ' + data.message;
        setTimeout(checkAirbandStatus, 3000);
    } catch (e) { fb.textContent = 'Request failed'; }
}

async function switchCustom() {
    const freq = document.getElementById('custom-freq').value;
    const label = document.getElementById('custom-label').value;
    const fb = document.getElementById('airband-feedback');
    if (!freq) { fb.textContent = 'Enter a frequency first'; return; }
    fb.textContent = 'Tuning to ' + freq + '...';
    try {
        const res = await fetch('/api/airband/custom', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ freq, label })
        });
        const data = await res.json();
        fb.textContent = data.status === 'success' ? 'Tuned to ' + freq : 'Error: ' + data.message;
        setTimeout(checkAirbandStatus, 3000);
    } catch (e) { fb.textContent = 'Request failed'; }
}

// ── ATC RENDER ──
function renderATC() {
    const container = document.getElementById('atc-calls');
    if (!container) return;

    const cls  = document.getElementById('atc-class').value;
    const type = document.getElementById('atc-type').value;

    const filtered = ATC_DATA.filter(item => {
        const classMatch = !cls  || item.classes.includes(cls);
        const typeMatch  = !type || item.type === type;
        return classMatch && typeMatch;
    });

    if (!filtered.length) {
        container.innerHTML = '<div class="atc-empty">No calls match this filter.</div>';
        return;
    }

    container.innerHTML = filtered.map((item, idx) => `
        <div class="atc-card ${item.type}" id="atc-item-${idx}">
            <div class="atc-card-header" onclick="toggleATC(${idx})">
                <div>
                    <div style="font-family:var(--mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;">
                        ${item.classes.join(' / ')} · ${item.type}
                    </div>
                    <div class="atc-card-title">${item.title}</div>
                </div>
                <div class="atc-chevron">▼</div>
            </div>
            <div class="atc-card-body">
                ${item.note ? `<div class="atc-note">${item.note}</div>` : ''}
                <div class="atc-format">
                    <div class="atc-format-label">Format</div>
                    <div class="atc-format-text">${item.format.replace(/\[([^\]]+)\]/g, '<span class="placeholder">[$1]</span>').replace(/\n/g, '<br>')}</div>
                </div>
                ${item.examples.map(ex => `
                    <div class="atc-example">
                        <div class="atc-example-label">${ex.label}</div>
                        <div class="atc-example-text">"${ex.text}"</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function toggleATC(idx) {
    document.getElementById('atc-item-' + idx).classList.toggle('open');
}

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
    checkAirbandStatus();
    renderATC();
});
