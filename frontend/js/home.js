  const LANGS = [
    { code: 'en', native: 'English' },
    { code: 'hi', native: 'हिन्दी' },
    { code: 'ta', native: 'தமிழ்' },
    { code: 'pa', native: 'ਪੰਜਾਬੀ' },
    { code: 'as', native: 'অসমীয়া' },
    { code: 'te', native: 'తెలుగు' },
  ];

  const STRINGS = {
    en: {
      nav_home: "Home", nav_about: "About", nav_contact: "Contact", nav_help: "Help", nav_register: "Registration",
      lang_label: "Choose language",
      hero_kicker: "For growers, by growers",
      hero_title: "Plan your harvest with clarity",
      hero_body: "FASAL brings weather, soil, and market data into one place, so you can decide what to sow, when to water, and where to sell — without the guesswork.",
      hero_cta_primary: "Create your account",
      hero_cta_ghost: "Learn more",
      features_title: "Everything your field needs, in one dashboard",
      features_sub: "From sowing to selling, FASAL keeps your decisions grounded in real data rather than habit alone.",
      feature1_title: "Weather forecasts",
      feature1_body: "7-day, field-level forecasts so irrigation and spraying happen at the right moment.",
      feature2_title: "Soil health tracking",
      feature2_body: "Log soil tests over seasons and get simple recommendations for the next crop cycle.",
      feature3_title: "Market prices",
      feature3_body: "Compare mandi prices nearby before you decide where and when to sell your harvest.",
      cta_title: "Ready to plan your next season?",
      cta_body: "Setting up takes less than two minutes — just your name and phone number to begin.",
      cta_button: "Register now",
    },
    hi: {
      nav_home: "होम", nav_about: "हमारे बारे में", nav_contact: "संपर्क", nav_help: "सहायता", nav_register: "पंजीकरण",
      lang_label: "भाषा चुनें",
      hero_kicker: "किसानों के लिए, किसानों द्वारा",
      hero_title: "अपनी फसल की योजना स्पष्टता से बनाएं",
      hero_body: "FASAL मौसम, मिट्टी और बाज़ार का डेटा एक ही जगह लाता है, ताकि आप बिना अंदाज़े के तय कर सकें कि क्या बोना है, कब सिंचाई करनी है, और कहाँ बेचना है।",
      hero_cta_primary: "अपना खाता बनाएं",
      hero_cta_ghost: "और जानें",
      features_title: "आपके खेत की हर ज़रूरत, एक ही डैशबोर्ड में",
      features_sub: "बुवाई से लेकर बिक्री तक, FASAL आपके फैसलों को अनुमान की बजाय असली डेटा पर आधारित रखता है।",
      feature1_title: "मौसम पूर्वानुमान",
      feature1_body: "7-दिन का, खेत-स्तर का पूर्वानुमान ताकि सिंचाई और छिड़काव सही समय पर हो।",
      feature2_title: "मिट्टी स्वास्थ्य ट्रैकिंग",
      feature2_body: "हर मौसम की मिट्टी जांच दर्ज करें और अगली फसल के लिए आसान सुझाव पाएं।",
      feature3_title: "बाज़ार भाव",
      feature3_body: "बेचने से पहले नज़दीकी मंडियों के भाव आपस में तुलना करें।",
      cta_title: "अगले सीज़न की योजना बनाने के लिए तैयार हैं?",
      cta_body: "शुरू करने में दो मिनट से भी कम समय लगता है — बस अपना नाम और फ़ोन नंबर दें।",
      cta_button: "अभी पंजीकरण करें",
    },
    ta: {
      nav_home: "முகப்பு", nav_about: "எங்களைப் பற்றி", nav_contact: "தொடர்பு", nav_help: "உதவி", nav_register: "பதிவு",
      lang_label: "மொழியைத் தேர்ந்தெடுக்கவும்",
      hero_kicker: "விவசாயிகளுக்காக, விவசாயிகளால்",
      hero_title: "உங்கள் அறுவடையை தெளிவாகத் திட்டமிடுங்கள்",
      hero_body: "FASAL வானிலை, மண் மற்றும் சந்தை தரவை ஒரே இடத்தில் தருகிறது, எதை விதைக்க வேண்டும், எப்போது நீர்ப்பாசனம் செய்ய வேண்டும், எங்கு விற்க வேண்டும் என்பதை நீங்கள் யூகமின்றி முடிவு செய்யலாம்.",
      hero_cta_primary: "உங்கள் கணக்கை உருவாக்குங்கள்",
      hero_cta_ghost: "மேலும் அறிக",
      features_title: "உங்கள் வயலுக்கு தேவையான அனைத்தும், ஒரே டாஷ்போர்டில்",
      features_sub: "விதைப்பது முதல் விற்பது வரை, FASAL உங்கள் முடிவுகளை பழக்கத்திற்குப் பதிலாக உண்மையான தரவின் அடிப்படையில் வைத்திருக்கிறது.",
      feature1_title: "வானிலை முன்னறிவிப்பு",
      feature1_body: "7-நாள், வயல்-நிலை முன்னறிவிப்பு, நீர்ப்பாசனமும் தெளிப்பும் சரியான நேரத்தில் நடக்க.",
      feature2_title: "மண் ஆரோக்கிய கண்காணிப்பு",
      feature2_body: "பருவங்கள் தோறும் மண் பரிசோதனைகளை பதிவு செய்து, அடுத்த பயிருக்கான எளிய பரிந்துரைகளைப் பெறுங்கள்.",
      feature3_title: "சந்தை விலைகள்",
      feature3_body: "விற்பதற்கு முன் அருகிலுள்ள சந்தை விலைகளை ஒப்பிடுங்கள்.",
      cta_title: "அடுத்த பருவத்தைத் திட்டமிட தயாரா?",
      cta_body: "தொடங்குவது இரண்டு நிமிடங்களுக்கும் குறைவாகும் — உங்கள் பெயரும் தொலைபேசி எண்ணும் மட்டும் போதும்.",
      cta_button: "இப்போது பதிவு செய்யுங்கள்",
    },
    pa: {
      nav_home: "ਹੋਮ", nav_about: "ਸਾਡੇ ਬਾਰੇ", nav_contact: "ਸੰਪਰਕ", nav_help: "ਮਦਦ", nav_register: "ਰਜਿਸਟ੍ਰੇਸ਼ਨ",
      lang_label: "ਭਾਸ਼ਾ ਚੁਣੋ",
      hero_kicker: "ਕਿਸਾਨਾਂ ਲਈ, ਕਿਸਾਨਾਂ ਵੱਲੋਂ",
      hero_title: "ਆਪਣੀ ਫ਼ਸਲ ਦੀ ਯੋਜਨਾ ਸਪਸ਼ਟਤਾ ਨਾਲ ਬਣਾਓ",
      hero_body: "FASAL ਮੌਸਮ, ਮਿੱਟੀ ਅਤੇ ਮੰਡੀ ਦਾ ਡਾਟਾ ਇੱਕੋ ਥਾਂ 'ਤੇ ਲਿਆਉਂਦਾ ਹੈ, ਤਾਂ ਜੋ ਤੁਸੀਂ ਬਿਨਾਂ ਅੰਦਾਜ਼ੇ ਦੇ ਫੈਸਲਾ ਕਰ ਸਕੋ ਕਿ ਕੀ ਬੀਜਣਾ ਹੈ, ਕਦੋਂ ਪਾਣੀ ਦੇਣਾ ਹੈ, ਅਤੇ ਕਿੱਥੇ ਵੇਚਣਾ ਹੈ।",
      hero_cta_primary: "ਆਪਣਾ ਖਾਤਾ ਬਣਾਓ",
      hero_cta_ghost: "ਹੋਰ ਜਾਣੋ",
      features_title: "ਤੁਹਾਡੇ ਖੇਤ ਦੀ ਹਰ ਲੋੜ, ਇੱਕੋ ਡੈਸ਼ਬੋਰਡ ਵਿੱਚ",
      features_sub: "ਬਿਜਾਈ ਤੋਂ ਲੈ ਕੇ ਵਿਕਰੀ ਤੱਕ, FASAL ਤੁਹਾਡੇ ਫੈਸਲਿਆਂ ਨੂੰ ਅੰਦਾਜ਼ੇ ਦੀ ਬਜਾਏ ਅਸਲ ਡਾਟਾ 'ਤੇ ਆਧਾਰਿਤ ਰੱਖਦਾ ਹੈ।",
      feature1_title: "ਮੌਸਮ ਪੂਰਵ ਅਨੁਮਾਨ",
      feature1_body: "7-ਦਿਨਾਂ ਦਾ, ਖੇਤ-ਪੱਧਰ ਦਾ ਪੂਰਵ ਅਨੁਮਾਨ ਤਾਂ ਜੋ ਸਿੰਚਾਈ ਅਤੇ ਛਿੜਕਾਅ ਸਹੀ ਸਮੇਂ 'ਤੇ ਹੋਵੇ।",
      feature2_title: "ਮਿੱਟੀ ਸਿਹਤ ਟਰੈਕਿੰਗ",
      feature2_body: "ਹਰ ਮੌਸਮ ਦੀ ਮਿੱਟੀ ਜਾਂਚ ਦਰਜ ਕਰੋ ਅਤੇ ਅਗਲੀ ਫ਼ਸਲ ਲਈ ਆਸਾਨ ਸੁਝਾਅ ਪਾਓ।",
      feature3_title: "ਮੰਡੀ ਭਾਅ",
      feature3_body: "ਵੇਚਣ ਤੋਂ ਪਹਿਲਾਂ ਨੇੜਲੀਆਂ ਮੰਡੀਆਂ ਦੇ ਭਾਅ ਦੀ ਤੁਲਨਾ ਕਰੋ।",
      cta_title: "ਅਗਲੇ ਸੀਜ਼ਨ ਦੀ ਯੋਜਨਾ ਬਣਾਉਣ ਲਈ ਤਿਆਰ ਹੋ?",
      cta_body: "ਸ਼ੁਰੂ ਕਰਨ ਵਿੱਚ ਦੋ ਮਿੰਟ ਤੋਂ ਵੀ ਘੱਟ ਸਮਾਂ ਲੱਗਦਾ ਹੈ — ਬਸ ਆਪਣਾ ਨਾਮ ਅਤੇ ਫ਼ੋਨ ਨੰਬਰ ਦਿਓ।",
      cta_button: "ਹੁਣੇ ਰਜਿਸਟਰ ਕਰੋ",
    },
    as: {
      nav_home: "গৃহ", nav_about: "আমাৰ বিষয়ে", nav_contact: "যোগাযোগ", nav_help: "সহায়", nav_register: "পঞ্জীয়ন",
      lang_label: "ভাষা বাছক",
      hero_kicker: "কৃষকৰ বাবে, কৃষকৰ দ্বাৰা",
      hero_title: "স্পষ্টতাৰে আপোনাৰ শস্যৰ পৰিকল্পনা কৰক",
      hero_body: "FASAL-এ বতৰ, মাটি আৰু বজাৰৰ তথ্য এক ঠাইতে আনি দিয়ে, যাতে আপুনি অনুমানৰ বিনাই কি সিচিব, কেতিয়া পানী দিব আৰু ক'ত বিক্ৰী কৰিব সেয়া ঠিক কৰিব পাৰে।",
      hero_cta_primary: "আপোনাৰ একাউণ্ট সৃষ্টি কৰক",
      hero_cta_ghost: "অধিক জানক",
      features_title: "আপোনাৰ পথাৰৰ প্ৰতিটো প্ৰয়োজন, এটা ডেশ্ববৰ্ডত",
      features_sub: "সিঁচাৰ পৰা বিক্ৰীলৈকে, FASAL-এ আপোনাৰ সিদ্ধান্তসমূহ অভ্যাসৰ পৰিৱৰ্তে প্ৰকৃত তথ্যৰ ওপৰত আধাৰিত ৰাখে।",
      feature1_title: "বতৰৰ পূৰ্বানুমান",
      feature1_body: "৭-দিনীয়া, পথাৰ-স্তৰৰ পূৰ্বানুমান যাতে জলসিঞ্চন আৰু স্প্ৰে সঠিক সময়ত হয়।",
      feature2_title: "মাটিৰ স্বাস্থ্য ট্ৰেকিং",
      feature2_body: "প্ৰতি ঋতুৰ মাটি পৰীক্ষা লিপিবদ্ধ কৰক আৰু পৰৱৰ্তী শস্যৰ বাবে সহজ পৰামৰ্শ লাভ কৰক।",
      feature3_title: "বজাৰ দাম",
      feature3_body: "বিক্ৰী কৰাৰ আগতে কাষৰীয়া বজাৰৰ দাম তুলনা কৰক।",
      cta_title: "পৰৱৰ্তী বতৰটোৰ পৰিকল্পনা কৰিবলৈ যুগুত?",
      cta_body: "আৰম্ভ কৰিবলৈ দুমিনিটতকৈও কম সময় লাগে — কেৱল আপোনাৰ নাম আৰু ফোন নম্বৰ দিয়ক।",
      cta_button: "এতিয়াই পঞ্জীয়ন কৰক",
    },
    te: {
      nav_home: "హోమ్", nav_about: "మా గురించి", nav_contact: "సంప్రదించండి", nav_help: "సహాయం", nav_register: "నమోదు",
      lang_label: "భాషను ఎంచుకోండి",
      hero_kicker: "రైతుల కోసం, రైతుల చేత",
      hero_title: "మీ పంటను స్పష్టతతో ప్రణాళిక చేయండి",
      hero_body: "FASAL వాతావరణం, నేల మరియు మార్కెట్ డేటాను ఒకే చోట తీసుకువస్తుంది, తద్వారా మీరు ఏమి విత్తాలో, ఎప్పుడు నీరు పెట్టాలో, ఎక్కడ అమ్మాలో ఊహాగానాలు లేకుండా నిర్ణయించుకోవచ్చు.",
      hero_cta_primary: "మీ ఖాతాను సృష్టించండి",
      hero_cta_ghost: "మరింత తెలుసుకోండి",
      features_title: "మీ పొలానికి కావలసినవన్నీ, ఒకే డాష్‌బోర్డ్‌లో",
      features_sub: "విత్తనం నుండి అమ్మకం వరకు, FASAL మీ నిర్ణయాలను అలవాటుకు బదులుగా నిజమైన డేటాపై ఆధారపడేలా ఉంచుతుంది.",
      feature1_title: "వాతావరణ సూచనలు",
      feature1_body: "7-రోజుల, పొలం-స్థాయి సూచనలతో నీటిపారుదల, పిచికారీ సరైన సమయంలో జరుగుతాయి.",
      feature2_title: "నేల ఆరోగ్య ట్రాకింగ్",
      feature2_body: "ప్రతి సీజన్ నేల పరీక్షలను నమోదు చేసి, తదుపరి పంట కోసం సులభమైన సూచనలు పొందండి.",
      feature3_title: "మార్కెట్ ధరలు",
      feature3_body: "అమ్మే ముందు సమీప మార్కెట్ ధరలను పోల్చి చూడండి.",
      cta_title: "తదుపరి సీజన్‌ను ప్రణాళిక చేయడానికి సిద్ధమేనా?",
      cta_body: "ప్రారంభించడానికి రెండు నిమిషాల కంటే తక్కువ సమయం పడుతుంది — మీ పేరు మరియు ఫోన్ నంబర్ మాత్రమే అవసరం.",
      cta_button: "ఇప్పుడే నమోదు చేసుకోండి",
    },
  };

  let currentLang = 'en';

  function applyLang(code) {
    const dict = STRINGS[code] || STRINGS.en;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) el.textContent = dict[key];
    });
    document.getElementById('htmlRoot').setAttribute('lang', code);
    document.getElementById('langBtnLabel').textContent = code.toUpperCase();
    currentLang = code;

    document.querySelectorAll('#langMenu button, #mobileLangGrid button').forEach(b => {
      b.classList.toggle('active', b.dataset.code === code);
    });
  }

  // build desktop dropdown
  const langMenu = document.getElementById('langMenu');
  const mobileLangGrid = document.getElementById('mobileLangGrid');

  LANGS.forEach(l => {
    const item = document.createElement('button');
    item.dataset.code = l.code;
    item.innerHTML = `<span class="native">${l.native}</span><span class="code">${l.code.toUpperCase()}</span>`;
    item.addEventListener('click', () => {
      applyLang(l.code);
      langMenu.classList.remove('open');
      langBtn.setAttribute('aria-expanded', 'false');
      dismissTooltip();
    });
    langMenu.appendChild(item);

    const mItem = document.createElement('button');
    mItem.dataset.code = l.code;
    mItem.textContent = l.native;
    mItem.addEventListener('click', () => applyLang(l.code));
    mobileLangGrid.appendChild(mItem);
  });

  applyLang('en');

  // ---- dropdown toggle ----
  const langWrap = document.getElementById('langWrap');
  const langBtn = document.getElementById('langBtn');

  langBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const open = langMenu.classList.toggle('open');
    langBtn.setAttribute('aria-expanded', open);
    dismissTooltip();
  });

  document.addEventListener('click', (e) => {
    if (!langWrap.contains(e.target)) {
      langMenu.classList.remove('open');
      langBtn.setAttribute('aria-expanded', 'false');
    }
  });

  // ---- attention highlight + tooltip ----
  function dismissTooltip() {
    langWrap.classList.remove('show-tooltip');
    langWrap.classList.remove('needs-attention');
  }

  setTimeout(() => {
    langWrap.classList.add('show-tooltip');
  }, 1200);

  setTimeout(() => {
    dismissTooltip();
  }, 9000);

  // ---- hamburger (mobile) ----
  const hamburger = document.getElementById('hamburger');
  const panel = document.getElementById('mobilePanel');

  hamburger.addEventListener('click', () => {
    const isOpen = panel.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', isOpen);
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 900 && panel.classList.contains('open')) {
      panel.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
    }
  });

  panel.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      panel.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
    });
  });