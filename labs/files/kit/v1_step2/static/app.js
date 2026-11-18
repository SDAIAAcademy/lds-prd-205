// Shows the fare family of a booking code.
document.getElementById('form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const out = document.getElementById('out');
  const response = await fetch('/api/explain?ref=' + encodeURIComponent(document.getElementById('ref').value));
  const data = await response.json();
  out.textContent = data.ok ? 'الأجرة: ' + data.family + ' · ' + data.route : data.message;
});
