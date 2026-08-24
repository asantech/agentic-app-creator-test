const form = document.querySelector('#cleanup-form');
const result = document.querySelector('#result');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form).entries());
  for (const key of ['delete_working_files', 'delete_hidden_files', 'preserve_git_metadata', 'preserve_app_skeleton', 'explicit_confirmation']) {
    data[key] = form.elements[key].checked;
  }

  result.textContent = 'در حال تهیه پیش‌نمایش...';
  try {
    const response = await fetch('/api/preview', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    const body = await response.json();
    const included = body.included.length ? body.included.join('، ') : 'هیچ موردی';
    const preserved = body.preserved.length ? body.preserved.join('، ') : 'هیچ موردی';
    result.innerHTML = `<strong>${body.message}</strong>\n\nمشمول دامنه: ${included}\nحفظ‌شده: ${preserved}`;
  } catch (error) {
    result.textContent = 'تهیه پیش‌نمایش انجام نشد. لطفاً دوباره تلاش کنید.';
  }
});
