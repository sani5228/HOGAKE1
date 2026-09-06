const state = { name: '', phone: '', aadhaar: '', uid: '', verifiedOtp: false };

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
document.getElementById('getOtpBtn').addEventListener('click', async () => {
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

  const btn = document.getElementById('getOtpBtn');
  btn.disabled = true;
  btn.textContent = 'Requesting OTP...';

  try {
    const res = await api.sendOtp(phone, 'REGISTRATION');
    state.name = name;
    state.phone = phone;
    state.aadhaar = aadhaar;

    document.getElementById('phoneEcho').textContent = phone.replace(/(\d{6})(\d{4})/, 'XXXXXX$2');
    showToast('OTP sent via simulated SMS! (Check backend terminal)', 'info');

    // In demo mode, prefill demo_otp if provided in API response for convenience
    if (res.data && res.data.demo_otp) {
      document.getElementById('otp').value = res.data.demo_otp;
    }

    goTo(2);
  } catch (err) {
    showToast(err.message || 'Failed to send OTP.', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Get OTP';
  }
});

// ---- STEP 2 -> Verify OTP ----
document.getElementById('verifyOtpBtn').addEventListener('click', async () => {
  const otpEl = document.getElementById('otp');
  const otpField = document.getElementById('otpField');
  const otp = otpEl.value.trim();
  const valid = /^[0-9]{6}$/.test(otp);

  setError(otpField, !valid);
  if (!valid) return;

  const btn = document.getElementById('verifyOtpBtn');
  btn.disabled = true;
  btn.textContent = 'Verifying...';

  try {
    const res = await api.verifyOtp(state.phone, otp);
    state.verifiedOtp = true;

    // Generate preliminary display ID
    const namePart = state.name.replace(/\s+/g, '').toLowerCase();
    const firstFour = state.aadhaar.slice(0, 4);
    state.uid = namePart + firstFour;
    document.getElementById('uidText').textContent = state.uid;

    showToast('OTP verified successfully!', 'success');
    goTo(3);
  } catch (err) {
    showToast(err.message || 'Invalid or expired OTP.', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Verify & continue';
  }
});

document.getElementById('backTo1').addEventListener('click', () => goTo(1));

// ---- STEP 3 -> Create account ----
document.getElementById('createAccountBtn').addEventListener('click', async () => {
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

  const btn = document.getElementById('createAccountBtn');
  btn.disabled = true;
  btn.textContent = 'Creating Account...';

  try {
    const regRes = await api.registerFarmer({
      name: state.name,
      mobile_number: state.phone,
      aadhaar: state.aadhaar,
      password: pw,
      state: 'Madhya Pradesh',
      district: 'Indore',
      village_town: 'Mhow',
      crop_ids: [1, 2] // Soybean and Rice by default
    });

    const farmerData = regRes.data.farmer;
    const finalId = farmerData.farmer_id || state.uid;

    document.getElementById('nameEcho').textContent = state.name;
    document.getElementById('uidFinal').textContent = finalId;

    showToast('Account created successfully!', 'success');
    goTo(4);
  } catch (err) {
    showToast(err.message || 'Account registration failed.', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create account';
  }
});

document.getElementById('doneBtn').addEventListener('click', () => {
  // If token is stored, navigate straight to dashboard, otherwise login
  if (api.getToken() && api.getCurrentUser()) {
    window.location.href = '/farmer/dashboard.html';
  } else {
    window.location.href = '/farmer/login.html';
  }
});