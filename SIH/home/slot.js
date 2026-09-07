
/* ================= data ================= */
const CROPS = [
    { name: "Rice", hindi: "चावल", season: "kharif" },
    { name: "Maize", hindi: "मक्का", season: "kharif" },
    { name: "Cotton", hindi: "कपास", season: "kharif" },
    { name: "Soybean", hindi: "सोयाबीन", season: "kharif" },
    { name: "Sugarcane", hindi: "गन्ना", season: "kharif" },
    { name: "Groundnut", hindi: "मूंगफली", season: "kharif" },
    { name: "Bajra (Pearl Millet)", hindi: "बाजरा", season: "kharif" },
    { name: "Wheat", hindi: "गेहूं", season: "rabi" },
    { name: "Mustard", hindi: "सरसों", season: "rabi" },
    { name: "Gram (Chickpea)", hindi: "चना", season: "rabi" },
    { name: "Barley", hindi: "जौ", season: "rabi" },
    { name: "Peas", hindi: "मटर", season: "rabi" },
    { name: "Watermelon", hindi: "तरबूज", season: "zaid" },
    { name: "Cucumber", hindi: "खीरा", season: "zaid" },
    { name: "Moong (Green Gram)", hindi: "मूंग", season: "zaid" },
    { name: "Muskmelon", hindi: "खरबूजा", season: "zaid" },
];

const SEASON_LABELS = {
    kharif: "Kharif season (June – October)",
    rabi: "Rabi season (November – March)",
    zaid: "Zaid season (April – May)",
};

const CENTERS = {
    "Prayagraj": { name: "Prayagraj Mandi Procurement Center", address: "Naini Industrial Area, Prayagraj", distanceKm: 6 },
    "Kaushambi": { name: "Kaushambi APMC Center", address: "Manjhanpur Road, Kaushambi", distanceKm: 22 },
    "Pratapgarh": { name: "Pratapgarh Krishi Mandi", address: "Civil Lines, Pratapgarh", distanceKm: 35 },
    "Fatehpur": { name: "Fatehpur Procurement Center", address: "GT Road, Fatehpur", distanceKm: 48 },
    "Varanasi": { name: "Varanasi Regional Mandi", address: "Cantonment, Varanasi", distanceKm: 90 },
};

const TIME_SLOTS = ["9:00 AM – 11:00 AM", "12:00 PM – 2:00 PM", "3:00 PM – 5:00 PM"];

const HINDI_MONTHS = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"];

/* in-memory only — resets on reload, since there's no backend yet */
const bookings = [];
const slotCounters = {}; // key: date+center -> next slot index

/* ================= season + crop filtering ================= */
function getSeason(date) {
    const m = date.getMonth() + 1;
    if (m >= 6 && m <= 10) return "kharif";
    if (m === 4 || m === 5) return "zaid";
    return "rabi";
}

const today = new Date();
const currentSeason = getSeason(today);

document.getElementById('seasonNote').textContent =
    "Showing crops for the " + SEASON_LABELS[currentSeason] + ".";
const cropChipGrid = document.getElementById('cropChipGrid');
let selectedCrops = [];

CROPS.filter(c => c.season === currentSeason).forEach(c => {
    const chip = document.createElement('label');
    chip.className = 'crop-chip';
    chip.innerHTML = `
    <input type="checkbox" value="${c.name}">
    <span class="chip-check">
      <svg viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </span>
    ${c.name}
  `;
    const checkbox = chip.querySelector('input');
    chip.addEventListener('click', (e) => {
        e.preventDefault();
        checkbox.checked = !checkbox.checked;
        chip.classList.toggle('selected', checkbox.checked);
        selectedCrops = Array.from(cropChipGrid.querySelectorAll('input:checked')).map(i => i.value);
        document.getElementById('f-crop').classList.remove('invalid');
    });
    cropChipGrid.appendChild(chip);
});

const districtSelect = document.getElementById('district');
Object.keys(CENTERS).forEach(d => {
    const opt = document.createElement('option');
    opt.value = d;
    opt.textContent = d;
    districtSelect.appendChild(opt);
});

// default the date input to today, minimum today
const dateInput = document.getElementById('pdate');
const todayStr = today.toISOString().split('T')[0];
dateInput.min = todayStr;
dateInput.value = todayStr;

/* radio highlight */
document.querySelectorAll('.radio-option').forEach(opt => {
    opt.addEventListener('click', () => {
        document.querySelectorAll('.radio-option').forEach(o => o.classList.remove('selected'));
        opt.classList.add('selected');
        opt.querySelector('input').checked = true;
        document.getElementById('f-storage').classList.remove('invalid');
    });
});

document.getElementById('phone').addEventListener('input', e => {
    e.target.value = e.target.value.replace(/\D/g, '').slice(0, 10);
});
document.getElementById('statusPhone').addEventListener('input', e => {
    e.target.value = e.target.value.replace(/\D/g, '').slice(0, 10);
});

/* ================= tabs ================= */
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    });
});

/* ================= helpers ================= */
function formatDateHindi(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.getDate() + ' ' + HINDI_MONTHS[d.getMonth()] + ' ' + d.getFullYear();
}

function formatDateEnglish(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' });
}

function nextSlot(dateStr, centerName) {
    const key = dateStr + '|' + centerName;
    const idx = slotCounters[key] || 0;
    slotCounters[key] = idx + 1;
    return TIME_SLOTS[idx % TIME_SLOTS.length];
}

function generateBookingId() {
    return 'FSL' + Math.floor(100000 + Math.random() * 900000);
}

function cropHindiName(name) {
    const match = CROPS.find(c => c.name === name);
    return match ? match.hindi : name;
}
function cropHindiList(commaJoinedNames) {
    return commaJoinedNames.split(', ').map(cropHindiName).join(', ');
}

/* ================= form submit ================= */
document.getElementById('bookingForm').addEventListener('submit', (e) => {
    e.preventDefault();

    const phone = document.getElementById('phone').value.trim();
    const district = districtSelect.value;
    const pdate = dateInput.value;
    const crop = selectedCrops.join(', ');
    const qty = document.getElementById('qty').value.trim();
    const unit = document.getElementById('unit').value;
    const storageEl = document.querySelector('input[name="storage"]:checked');

    let valid = true;

    const phoneValid = /^[0-9]{10}$/.test(phone);
    document.getElementById('f-phone').classList.toggle('invalid', !phoneValid);
    if (!phoneValid) valid = false;

    const districtValid = district !== '';
    document.getElementById('f-district').classList.toggle('invalid', !districtValid);
    if (!districtValid) valid = false;

    const dateValid = pdate !== '' && pdate >= todayStr;
    document.getElementById('f-date').classList.toggle('invalid', !dateValid);
    if (!dateValid) valid = false;

    const cropValid = selectedCrops.length > 0;
    document.getElementById('f-crop').classList.toggle('invalid', !cropValid);
    if (!cropValid) valid = false;

    const qtyValid = qty !== '' && Number(qty) > 0;
    document.getElementById('f-qty').classList.toggle('invalid', !qtyValid);
    if (!qtyValid) valid = false;

    const storageValid = !!storageEl;
    document.getElementById('f-storage').classList.toggle('invalid', !storageValid);
    if (!storageValid) valid = false;

    if (!valid) return;

    const center = CENTERS[district];
    const slot = nextSlot(pdate, center.name);
    const bookingId = generateBookingId();
    const storageAnswer = storageEl.value;

    const booking = {
        id: bookingId, phone, district, pdate, crop, qty, unit, storageAnswer,
        center, slot, createdAt: new Date(),
    };
    bookings.push(booking);

    // ---- populate result card ----
    document.getElementById('rCrop').textContent = crop;
    document.getElementById('rQty').textContent = qty + ' ' + unit;
    document.getElementById('rDate').textContent = formatDateEnglish(pdate);
    document.getElementById('rSlot').textContent = slot;
    document.getElementById('rCenterName').textContent = center.name;
    document.getElementById('rCenterAddr').textContent = center.address;
    document.getElementById('rCenterDist').textContent = '~' + center.distanceKm + ' km from ' + district;

    const smsText =
        'प्रिय किसान, आपकी स्लॉट बुकिंग सफल रही। ' +
        'फसल: ' + cropHindiList(crop) + ', ' +
        'मात्रा: ' + qty + ' ' + unit + ', ' +
        'दिनांक: ' + formatDateHindi(pdate) + ', ' +
        'समय: ' + slot + ', ' +
        'केंद्र: ' + center.name + ', ' +
        'पता: ' + center.address + '। ' +
        'बुकिंग आईडी: ' + bookingId + '। धन्यवाद — FASAL';

    document.getElementById('smsBubble').textContent = smsText;
    document.getElementById('smsMeta').textContent = 'Sent to +91 ' + phone.replace(/(\d{5})(\d{5})/, '$1 $2');

    document.getElementById('resultCard').classList.add('show');
    document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
});

/* ================= status lookup ================= */
document.getElementById('statusSearchBtn').addEventListener('click', () => {
    const phone = document.getElementById('statusPhone').value.trim();
    const resultsEl = document.getElementById('statusResults');

    if (!/^[0-9]{10}$/.test(phone)) {
        resultsEl.innerHTML = '<div class="empty-state">Enter a valid 10-digit phone number.</div>';
        return;
    }

    const matches = bookings.filter(b => b.phone === phone);

    if (matches.length === 0) {
        resultsEl.innerHTML = '<div class="empty-state">No bookings found for this number in the current session.</div>';
        return;
    }

    resultsEl.innerHTML = '';
    const list = document.createElement('div');
    list.className = 'booking-list';

    matches.forEach(b => {
        const item = document.createElement('div');
        item.className = 'booking-item';
        item.innerHTML = `
        <div class="b-top">
          <span class="b-id">${b.id}</span>
          <span class="status-pill">Confirmed</span>
        </div>
        <div class="b-grid">
          <div><span class="lbl">Crop:</span> ${b.crop}</div>
          <div><span class="lbl">Quantity:</span> ${b.qty} ${b.unit}</div>
          <div><span class="lbl">Date:</span> ${formatDateEnglish(b.pdate)}</div>
          <div><span class="lbl">Slot:</span> ${b.slot}</div>
          <div><span class="lbl">Center:</span> ${b.center.name}</div>
          <div><span class="lbl">Storage facility:</span> ${b.storageAnswer === 'yes' ? 'Yes' : 'No'}</div>
        </div>
      `;
        list.appendChild(item);
    });

    resultsEl.appendChild(list);
});
function saveBookingToStorage(booking) {
    try {
        const existing = JSON.parse(localStorage.getItem('fasal_bookings') || '[]');
        existing.push(booking);
        localStorage.setItem('fasal_bookings', JSON.stringify(existing));
    } catch (err) {
        console.error('Could not save booking to storage', err);
    }
}

const LOGIN_STRINGS = {
                en: { login_title: "Welcome back", login_sub: "Log in to view your profile and farm dashboard.", login_username_label: "FARM ID / Username", login_btn: "Log in" },
                hi: { login_title: "वापसी पर स्वागत है", login_sub: "अपनी प्रोफ़ाइल और डैशबोर्ड देखने के लिए लॉग इन करें।", login_username_label: "फार्म आईडी / उपयोगकर्ता नाम", login_btn: "लॉग इन करें" },
                ta: { login_title: "மீண்டும் வரவேற்கிறோம்", login_sub: "உங்கள் சுயவிவரம் மற்றும் டாஷ்போர்டைப் பார்க்க உள்நுழையவும்.", login_username_label: "பண்ணை ஐடி / பயனர்பெயர்", login_btn: "உள்நுழை" },
                pa: { login_title: "ਵਾਪਸ ਸੁਆਗਤ ਹੈ", login_sub: "ਆਪਣੀ ਪ੍ਰੋਫਾਈਲ ਅਤੇ ਡੈਸ਼ਬੋਰਡ ਵੇਖਣ ਲਈ ਲੌਗ ਇਨ ਕਰੋ।", login_username_label: "ਫਾਰਮ ਆਈਡੀ / ਯੂਜ਼ਰਨੇਮ", login_btn: "ਲੌਗ ਇਨ" },
                as: { login_title: "পুনৰ স্বাগতম", login_sub: "আপোনাৰ প্ৰ'ফাইল আৰু ডেশ্ববৰ্ড চাবলৈ লগইন কৰক।", login_username_label: "ফাৰ্ম আইডি / ব্যৱহাৰকাৰীৰ নাম", login_btn: "লগইন" },
                te: { login_title: "తిరిగి స్వాగతం", login_sub: "మీ ప్రొఫైల్ మరియు డాష్‌బోర్డ్‌ను చూడటానికి లాగిన్ అవ్వండి.", login_username_label: "ఫారమ్ ఐడీ / యూజర్‌నేమ్", login_btn: "లాగిన్" },
            };
            initFasalLanguageSwitcher(LOGIN_STRINGS, 'en');
