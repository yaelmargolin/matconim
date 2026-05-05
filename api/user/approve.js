const { getSQL, setCORS } = require('../_db');

module.exports = async function handler(req, res) {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  const { token, action } = req.query;
  if (!token || !['approve', 'reject'].includes(action)) {
    return res.status(400).send('Invalid request');
  }

  const sql = getSQL();
  const rows = await sql`SELECT id, email, name FROM users WHERE approval_token = ${token}`;
  if (!rows.length) return res.status(404).send('Token not found or already used');

  const newStatus = action === 'approve' ? 'approved' : 'rejected';
  await sql`UPDATE users SET status = ${newStatus}, approval_token = NULL WHERE approval_token = ${token}`;

  const user = rows[0];
  const emoji = action === 'approve' ? '✅' : '❌';
  const label = action === 'approve' ? 'אושר' : 'נדחה';

  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(200).send(`
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head><meta charset="UTF-8"><title>אישור גישה</title>
    <style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f0f7ff;}
    .card{background:#fff;border-radius:16px;padding:40px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,.08);max-width:400px;}
    h1{font-size:1.4em;margin:12px 0 8px;}</style>
    </head>
    <body><div class="card">
      <div style="font-size:3em">${emoji}</div>
      <h1>המשתמש ${label}</h1>
      <p>${user.name || user.email}</p>
      <p style="color:#64748b;font-size:.9em">${user.email}</p>
    </div></body>
    </html>
  `);
};
