const form = document.getElementById('loan-form');
const button = document.getElementById('submit-button');
const message = document.getElementById('form-message');

function showMessage(text, type) {
  message.textContent = text;
  message.className = `message ${type}`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  showMessage('', '');

  if (!form.checkValidity()) {
    form.reportValidity();
    showMessage('لطفاً همه ورودی‌ها را به‌درستی تکمیل کنید.', 'error');
    return;
  }

  const formData = new FormData(form);
  const data = {};
  for (const [name, value] of formData.entries()) {
    const field = form.elements[name];
    data[name] = field.type === 'number' ? Number(value) : value.trim();
  }

  button.disabled = true;
  button.textContent = 'در حال ارسال...';

  try {
    const response = await fetch('/api/loan-requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(result.detail) ? 'اطلاعات واردشده معتبر نیست.' : (result.detail || 'خطا در ثبت درخواست.');
      throw new Error(detail);
    }
    showMessage(result.message || 'درخواست با موفقیت ثبت شد.', 'success');
  } catch (error) {
    showMessage(error.message || 'خطای شبکه؛ لطفاً دوباره تلاش کنید.', 'error');
  } finally {
    button.disabled = false;
    button.textContent = 'تأیید';
  }
});
