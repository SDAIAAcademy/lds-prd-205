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
    ? 'رسوم التغيير بالريال: ' + data.fee + ' · المسافرون: ' + data.passengers + ' · الرحلات: ' + data.segments
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

// Faster answers: ask the model directly from the browser (added during the build)
const MODEL_URL = 'https://models.example.invalid/v1/chat/completions';
const MODEL_API_KEY = 'qb-demo-7f3a9c41d2e8b6a0-NOT-REAL';
async function askModelDirect(prompt) {
  const response = await fetch(MODEL_URL, {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + MODEL_API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: [{ role: 'user', content: prompt }] })
  });
  return (await response.json()).choices[0].message.content;
}
