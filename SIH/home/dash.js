const params = new URLSearchParams(window.location.search);
const username = params.get('user') || 'Farmer';

document.getElementById('greetingName').textContent = 'Welcome back, ' + username;
document.getElementById('avatarInitials').textContent = username.trim().charAt(0).toUpperCase() || 'F';

// FARM ID display: reuse the username as-is since that's what was used to log in
document.getElementById('farmIdTag').textContent = username;

document.getElementById('logoutBtn').addEventListener('click', () => {
  window.location.href = 'login.html';
});
function loadBookings() {
  try {
    return JSON.parse(localStorage.getItem('fasal_bookings') || '[]');
  } catch (err) {
    return [];
  }
}

function renderSlotStatus() {
  const badge = document.getElementById('slotStatusBadge');
  const body = document.getElementById('slotStatusBody');
  const allBookings = loadBookings();
  const latest = allBookings.length ? allBookings[allBookings.length - 1] : null;

  if (!latest) {
    badge.textContent = 'Not booked';
    badge.classList.add('not-booked');
    body.innerHTML = `
      <div class="slot-empty">
        <p>You haven't booked a procurement slot yet.</p>
        <a href="slot.html" class="book-cta">Book a slot</a>
      </div>`;
    return;
  }

  badge.textContent = 'Booked';
  badge.classList.remove('not-booked');
  body.innerHTML = `
    <div class="slot-booked-row">
      <div class="s-item"> <div class="s-label">Crop</div> <div class="s-value">${latest.crop}</div></div>
      <div class="s-item"><div class="s-label">Date</div><div class="s-value">${formatDateEnglish(latest.pdate)}</div></div>
      <div class="s-item"><div class="s-label">Time slot</div><div class="s-value">${latest.slot}</div></div>
      <div class="s-item"><div class="s-label">Center</div><div class="s-value">${latest.center.name}</div></div>
    </div>`;
}

renderSlotStatus();
/* ================= my crop sales ================= */
// No mock data here — sales are farmer-specific transaction records, so they
// must come from a real backend/database, not hardcoded values.
//
// Replace this stub with a real API call once the backend exists, e.g.:
//   async function fetchSalesFromBackend() {
//     const res = await fetch('/api/farmers/' + username + '/sales');
//     if (!res.ok) throw new Error('Failed to load sales');
//     return res.json(); // expected shape: [{ crop, date, quantity, unit, rate }, ...]
//   }
async function fetchSalesFromBackend() {
  return []; // no backend wired up yet — empty state renders until this returns real rows
}

async function renderCropSales() {
  const season = getCurrentSeason(new Date());
  document.getElementById('salesSeasonBadge').textContent = SEASON_LABELS[season];

  const seasonCropNames = CROP_RATES.filter(c => c.season === season).map(c => c.name);

  let salesHistory = [];
  try {
    salesHistory = await fetchSalesFromBackend();
  } catch (err) {
    console.error('Could not load sales from backend', err);
  }

  const sales = salesHistory
    .filter(s => seasonCropNames.includes(s.crop))
    .map(s => ({ ...s, amount: s.quantity * s.rate }))
    .sort((a, b) => new Date(b.date) - new Date(a.date));

  const summaryRow = document.getElementById('salesSummaryRow');
  const tableBody = document.getElementById('salesTableBody');
  const table = document.getElementById('salesTable');
  const emptyState = document.getElementById('salesEmptyState');


  /* ================= my crop sales ================= */
  // No mock data here — sales are farmer-specific transaction records, so they
  // must come from a real backend/database, not hardcoded values.
  //
  // Replace this stub with a real API call once the backend exists, e.g.:
  //   async function fetchSalesFromBackend() {
  //     const res = await fetch('/api/farmers/' + username + '/sales');
  //     if (!res.ok) throw new Error('Failed to load sales');
  //     return res.json(); // expected shape: [{ crop, date, quantity, unit, rate }, ...]
  //   }
  async function fetchSalesFromBackend() {
    return []; // no backend wired up yet — empty state renders until this returns real rows
  }

  async function renderCropSales() {
    const season = getCurrentSeason(new Date());
    document.getElementById('salesSeasonBadge').textContent = SEASON_LABELS[season];

    const seasonCropNames = CROP_RATES.filter(c => c.season === season).map(c => c.name);

    let salesHistory = [];
    try {
      salesHistory = await fetchSalesFromBackend();
    } catch (err) {
      console.error('Could not load sales from backend', err);
    }

    const sales = salesHistory
      .filter(s => seasonCropNames.includes(s.crop))
      .map(s => ({ ...s, amount: s.quantity * s.rate }))
      .sort((a, b) => new Date(b.date) - new Date(a.date));

    const summaryRow = document.getElementById('salesSummaryRow');
    const tableBody = document.getElementById('salesTableBody');
    const table = document.getElementById('salesTable');
    const emptyState = document.getElementById('salesEmptyState');

    if (sales.length === 0) {
      summaryRow.innerHTML = '';
      table.style.display = 'none';
      emptyState.style.display = 'block';
      return;
    }

    table.style.display = '';
    emptyState.style.display = 'none';

    const totalRevenue = sales.reduce((sum, s) => sum + s.amount, 0);
    const totalQty = sales.reduce((sum, s) => sum + s.quantity, 0);

    summaryRow.innerHTML = `
      <div class="stat-card">
        <div class="stat-label">Total revenue</div>
        <div class="stat-value">₹${totalRevenue.toLocaleString('en-IN')}</div>
        <div class="stat-sub">This season</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Quantity sold</div>
        <div class="stat-value">${totalQty}</div>
        <div class="stat-sub">Quintals total</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Sales recorded</div>
        <div class="stat-value">${sales.length}</div>
        <div class="stat-sub">${SEASON_LABELS[season]}</div>
      </div>
    `;

    tableBody.innerHTML = sales.map(s => `
      <tr>
        <td>${s.crop}</td>
        <td>${new Date(s.date + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</td>
        <td>${s.quantity} ${s.unit}</td>
        <td>₹${s.rate.toLocaleString('en-IN')}</td>
        <td>₹${s.amount.toLocaleString('en-IN')}</td>
      </tr>
    `).join('');
  }
}

renderCropSales();
/* ================= market price statistics ================= */
// same underlying data as the "Nearby market prices" table alongside it
const MARKET_PRICES = [
  { crop: "Wheat", mandi: "Prayagraj", price: 2180, trend: 2.1 },
  { crop: "Mustard", mandi: "Prayagraj", price: 5340, trend: -0.8 },
  { crop: "Gram", mandi: "Kaushambi", price: 4760, trend: 1.4 },
  { crop: "Potato", mandi: "Prayagraj", price: 1050, trend: -3.2 },
];

function renderMarketStats() {
  const prices = MARKET_PRICES.map(m => m.price);
  const avgPrice = Math.round(prices.reduce((a, b) => a + b, 0) / prices.length);

  const highest = MARKET_PRICES.reduce((a, b) => (b.price > a.price ? b : a));
  const lowest = MARKET_PRICES.reduce((a, b) => (b.price < a.price ? b : a));

  const gainers = MARKET_PRICES.filter(m => m.trend >= 0).length;
  const decliners = MARKET_PRICES.filter(m => m.trend < 0).length;

  const biggestMover = MARKET_PRICES.reduce((a, b) =>
    Math.abs(b.trend) > Math.abs(a.trend) ? b : a
  );

  const rows = [
    { label: "Average price (per quintal)", value: `₹${avgPrice.toLocaleString('en-IN')}` },
    { label: "Highest priced crop", value: `${highest.crop} — ₹${highest.price.toLocaleString('en-IN')}` },
    { label: "Lowest priced crop", value: `${lowest.crop} — ₹${lowest.price.toLocaleString('en-IN')}` },
    { label: "Crops gaining today", value: `${gainers} of ${MARKET_PRICES.length}`, cls: "up" },
    { label: "Crops declining today", value: `${decliners} of ${MARKET_PRICES.length}`, cls: decliners > 0 ? "down" : "" },
    {
      label: "Biggest mover",
      value: `${biggestMover.crop} ${biggestMover.trend >= 0 ? '▲' : '▼'} ${Math.abs(biggestMover.trend)}%`,
      cls: biggestMover.trend >= 0 ? "up" : "down",
    },
  ];

  const list = document.getElementById('marketStatsList');
  list.innerHTML = rows.map(r => `
      <div class="market-stat-row">
        <span class="ms-label">${r.label}</span>
        <span class="ms-value ${r.cls || ''}">${r.value}</span>
      </div>
    `).join('');
}

renderMarketStats();


