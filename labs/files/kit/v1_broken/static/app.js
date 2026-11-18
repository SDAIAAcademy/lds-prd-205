// Shows the fare family, the rule and the change fee of a booking code.
document.getElementById('form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const out = document.getElementById('out');
  const response = await fetch('/api/explain?ref=' + encodeURIComponent(document.getElementById('ref').value));
  const data = await response.json();
  out.textContent = '';
  if (!data.ok) { out.textContent = data.message; return; }
  const head = document.createElement('p');
  head.textContent = data.allowed ? 'رسوم التغيير بالريال: ' + data.fee : 'لا يمكن تغيير هذا الحجز الآن';
  const rule = document.createElement('p');
  rule.textContent = 'القاعدة ' + data.rule_id + ': ' + data.rule_text;
  const meta = document.createElement('p');
  meta.textContent = 'الأجرة: ' + data.family + ' · ' + data.route;
  out.append(head, rule, meta);
});
