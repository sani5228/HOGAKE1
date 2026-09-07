 const state = { name: '', phone: '', aadhaar: '', uid: '' };

  const steps = {
    1: document.getElementById('step1'),
    2: document.getElementById('step2'),
    3: document.getElementById('step3'),
    4: document.getElementById('step4'),
  };

  function goTo(n) {
    Object.values(steps).forEach(s => s.classList.remove('active'));
    steps[n].classList.add('active');
  }

  function setError(fieldEl, show) {
    fieldEl.classList.toggle('invalid', show);
  }

  // only allow digits in the aadhaar field as the user types
  document.getElementById('aadhaar').addEventListener('input', (e) => {
    e.target.value = e.target.value.replace(/\D/g, '').slice(0, 12);
  });
  document.getElementById('phone').addEventListener('input', (e) => {
    e.target.value = e.target.value.replace(/\D/g, '').slice(0, 10);
  });

  // ---- STEP 1 -> Get OTP ----
  document.getElementById('getOtpBtn').addEventListener('click', () => {
    const nameEl = document.getElementById('fullName');
    const aadhaarEl = document.getElementById('aadhaar');
    const phoneEl = document.getElementById('phone');
    const nameField = document.getElementById('nameField');
    const aadhaarField = document.getElementById('aadhaarField');
    const phoneField = document.getElementById('phoneField');

    const name = nameEl.value.trim();
    const aadhaar = aadhaarEl.value.trim();
    const phone = phoneEl.value.trim();

    const nameValid = name.length > 1;
    const aadhaarValid = /^[0-9]{12}$/.test(aadhaar);
    const phoneValid = /^[0-9]{10}$/.test(phone);

    setError(nameField, !nameValid);
    setError(aadhaarField, !aadhaarValid);
    setError(phoneField, !phoneValid);

    if (!nameValid || !aadhaarValid || !phoneValid) return;

    state.name = name;
    state.phone = phone;
    state.aadhaar = aadhaar;

    document.getElementById('phoneEcho').textContent = phone.replace(/(\d{6})(\d{4})/, 'XXXXXX$2');
    goTo(2);
  });

  // ---- STEP 2 -> Verify OTP ----
  document.getElementById('verifyOtpBtn').addEventListener('click', () => {
    const otpEl = document.getElementById('otp');
    const otpField = document.getElementById('otpField');
    const otp = otpEl.value.trim();
    const valid = /^[0-9]{6}$/.test(otp);

    setError(otpField, !valid);
    if (!valid) return;

    // auto-generate FARM ID: username (no spaces, lowercase) + first 4 digits of Aadhaar
    const namePart = state.name.replace(/\s+/g, '').toLowerCase();
    const firstFour = state.aadhaar.slice(0, 4);
    state.uid = namePart + firstFour;

    document.getElementById('uidText').textContent = state.uid;
    goTo(3);
  });

  document.getElementById('backTo1').addEventListener('click', () => goTo(1));

  // ---- STEP 3 -> Create account ----
  document.getElementById('createAccountBtn').addEventListener('click', () => {
    const pwEl = document.getElementById('password');
    const pwConfirmEl = document.getElementById('passwordConfirm');
    const pwField = document.getElementById('pwField');
    const pwConfirmField = document.getElementById('pwConfirmField');

    const pw = pwEl.value;
    const pwConfirm = pwConfirmEl.value;

    const pwValid = pw.length >= 6;
    const matchValid = pw === pwConfirm && pwConfirm.length > 0;

    setError(pwField, !pwValid);
    setError(pwConfirmField, pwValid && !matchValid);

    if (!pwValid || !matchValid) return;

    document.getElementById('nameEcho').textContent = state.name;
    document.getElementById('uidFinal').textContent = state.uid;
    goTo(4);
  });

  document.getElementById('doneBtn').addEventListener('click', () => {
    // reset flow back to step 1 for demo purposes
    goTo(1);
    document.getElementById('fullName').value = '';
    document.getElementById('aadhaar').value = '';
    document.getElementById('phone').value = '';
    document.getElementById('otp').value = '';
    document.getElementById('password').value = '';
    document.getElementById('passwordConfirm').value = '';
  });