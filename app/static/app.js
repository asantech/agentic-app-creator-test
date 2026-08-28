const previewButton = document.getElementById('preview');
const confirmButton = document.getElementById('confirm');
const statusBox = document.getElementById('status');
let previewId = null;
function renderList(id, values) { document.getElementById(id).innerHTML = (values || []).map(value => `<li>${escapeHtml(value)}</li>`).join(''); }
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
previewButton.addEventListener('click', async () => {
  confirmButton.disabled = true; previewId = null; statusBox.textContent = 'در حال تهیهٔ پیش‌نمایش...';
  try { const response = await fetch('/api/preview', {method:'POST'}); const data = await response.json();
    previewId = data.preview_id; renderList('deletable', data.deleted); renderList('excluded', data.excluded);
    confirmButton.disabled = data.status !== 'preview' || !previewId; statusBox.textContent = data.message;
  } catch (error) { statusBox.textContent = 'خطا در ارتباط با سرویس.'; }
});
confirmButton.addEventListener('click', async () => {
  if (!previewId || !window.confirm('آیا حذف واقعی را تأیید می‌کنید؟')) return;
  confirmButton.disabled = true; statusBox.textContent = 'در حال حذف...';
  const response = await fetch('/api/confirm', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({preview_id:previewId,confirm:true})});
  const data = await response.json(); renderList('deletable', data.deleted); renderList('excluded', data.excluded); statusBox.textContent = data.message; previewId = null;
});
