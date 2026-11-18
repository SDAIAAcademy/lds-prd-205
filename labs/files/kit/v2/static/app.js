// Calls the prototype's own server. No key here: the server holds it.
document.getElementById('form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const out = document.getElementById('out');
  const ref = document.getElementById('ref').value;
  out.textContent = 'جارٍ التحميل...';
  const response = await fetch('/api/explain?ref=' + encodeURIComponent(ref));
  const data = await response.json();
  out.textContent = '';
  if (!data.ok) {
    const p = document.createElement('p');
    p.textContent = data.message;
    out.append(p);
    return;
  }
  const head = document.createElement('p');
  head.className = 'fee';
  head.textContent = data.allowed
    ? 'رسوم التغيير بالريال: ' + data.fee
    : 'لا يمكن تغيير هذا الحجز الآن';
  const body = document.createElement('p');
  body.textContent = data.explanation;
  const meta = document.createElement('p');
  meta.className = 'note';
  meta.textContent = 'الأجرة: ' + data.family + ' · القاعدة ' + data.rule_id + ' · ' + data.route;
  if (data.source === 'model' && data.mode === 'stub') {
    meta.textContent += ' · الشرح من بديل مكتوب مسبقًا (stub)، لا من نموذج';
  }
  out.append(head, body, meta);
});
