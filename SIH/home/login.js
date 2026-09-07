
  const form = document.getElementById('loginForm');
  const usernameField = document.getElementById('usernameField');
  const passwordField = document.getElementById('passwordField');

  // prefill FARM ID if arriving fresh from registration
  const prefill = new URLSearchParams(window.location.search).get('user');
  if (prefill) {
    document.getElementById('username').value = prefill;
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    const usernameValid = username.length > 0;
    const passwordValid = password.length > 0;

    usernameField.classList.toggle('invalid', !usernameValid);
    passwordField.classList.toggle('invalid', !passwordValid);

    if (!usernameValid || !passwordValid) return;

    // demo-only: no real auth backend, so any credentials pass
    window.location.href = 'dashboard.html?user=' + encodeURIComponent(username);
  });

