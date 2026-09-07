const FASAL_LANGS = [
  { code: 'en', native: 'English' },
  { code: 'hi', native: 'हिन्दी' },
  { code: 'ta', native: 'தமிழ்' },
  { code: 'pa', native: 'ਪੰਜਾਬੀ' },
  { code: 'as', native: 'অসমীয়া' },
  { code: 'te', native: 'తెలుగు' },
];

function initFasalLanguageSwitcher(strings, defaultLang = 'en') {
  const langMenu = document.getElementById('langMenu');
  const mobileLangGrid = document.getElementById('mobileLangGrid'); // optional
  const langBtn = document.getElementById('langBtn');
  const langBtnLabel = document.getElementById('langBtnLabel');
  const langWrap = document.getElementById('langWrap');

  function applyLang(code) {
    const dict = strings[code] || strings.en;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) el.textContent = dict[key];
    });
    document.documentElement.setAttribute('lang', code);
    if (langBtnLabel) langBtnLabel.textContent = code.toUpperCase();
    document.querySelectorAll('#langMenu button, #mobileLangGrid button').forEach(b => {
      b.classList.toggle('active', b.dataset.code === code);
    });
  }

  if (langMenu) {
    FASAL_LANGS.forEach(l => {
      const item = document.createElement('button');
      item.dataset.code = l.code;
      item.innerHTML = `<span class="native">${l.native}</span><span class="code">${l.code.toUpperCase()}</span>`;
      item.addEventListener('click', () => {
        applyLang(l.code);
        langMenu.classList.remove('open');
        if (langBtn) langBtn.setAttribute('aria-expanded', 'false');
      });
      langMenu.appendChild(item);
    });
  }

  if (mobileLangGrid) {
    FASAL_LANGS.forEach(l => {
      const item = document.createElement('button');
      item.dataset.code = l.code;
      item.textContent = l.native;
      item.addEventListener('click', () => applyLang(l.code));
      mobileLangGrid.appendChild(item);
    });
  }

  if (langBtn && langMenu) {
    langBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = langMenu.classList.toggle('open');
      langBtn.setAttribute('aria-expanded', open);
    });
    document.addEventListener('click', (e) => {
      if (langWrap && !langWrap.contains(e.target)) {
        langMenu.classList.remove('open');
        langBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  applyLang(defaultLang);
}