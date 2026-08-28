const $ = (id) => document.getElementById(id);
const show = (value) => { $('result').textContent = JSON.stringify(value, null, 2); };
$('preview').addEventListener('click', async () => {
  try {
    const response = await fetch('/api/preview');
    const data = await response.json();
    if (!response.ok) throw data;
    $('root-status').textContent = `ریشه: ${data.root}`;
    $('lists').textContent = `قابل حذف (${data.deletable.length}):\n${data.deletable.join('\n') || 'موردی نیست'}\n\nمستثنا (${data.excluded.length}):\n${data.excluded.join('\n') || 'موردی نیست'}`;
    $('preview-result').hidden = false; show(data);
  } catch (error) { show(error); }
});
$('confirm').addEventListener('change', (event) => { $('delete').disabled = !event.target.checked; });
$('delete').addEventListener('click', async () => {
  if (!$('confirm').checked) return;
  try {
    const response = await fetch('/api/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({confirmation:true})});
    const data = await response.json(); if (!response.ok) throw data; show(data);
  } catch (error) { show(error); }
});
