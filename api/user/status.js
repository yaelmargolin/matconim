const crypto = require('crypto');
const { getSQL, setCORS } = require('../_db');
const { getAuthUserId } = require('../_auth');

const ADMIN_EMAIL = 'yaelmar52@gmail.com';
const APP_URL = process.env.VERCEL_PROJECT_PRODUCTION_URL
  ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
  : 'https://matconim.vercel.app';

async function ensureUsersTable(sql) {
  await sql`
    CREATE TABLE IF NOT EXISTS users (
      id             SERIAL PRIMARY KEY,
      clerk_id       TEXT UNIQUE NOT NULL,
      email          TEXT DEFAULT '',
      name           TEXT DEFAULT '',
      status         TEXT DEFAULT 'pending',
      approval_token TEXT,
      created_at     BIGINT
    )
  `;
  // Add column if upgrading from old schema
  await sql`ALTER TABLE users ADD COLUMN IF NOT EXISTS approval_token TEXT`;
}

async function sendApprovalEmail(email, name, clerkId, token) {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.warn('RESEND_API_KEY not set — skipping email');
    return;
  }
  const approveUrl = `${APP_URL}/api/user/approve?token=${token}&action=approve`;
  const rejectUrl  = `${APP_URL}/api/user/approve?token=${token}&action=reject`;

  const html = `
    <div dir="rtl" style="font-family:sans-serif;max-width:500px;margin:auto;">
      <h2>בקשת גישה חדשה — מרשמים</h2>
      <p><strong>שם:</strong> ${name || '—'}</p>
      <p><strong>מייל:</strong> ${email}</p>
      <p><strong>מזהה Clerk:</strong> ${clerkId}</p>
      <br>
      <a href="${approveUrl}" style="background:#16a34a;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;margin-left:10px;display:inline-block;">✅ אישור</a>
      <a href="${rejectUrl}"  style="background:#dc2626;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;">❌ דחייה</a>
    </div>
  `;

  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: 'Matconim <onboarding@resend.dev>',
      to: ADMIN_EMAIL,
      subject: `בקשת גישה: ${name || email}`,
      html,
    }),
  });
}

module.exports = async function handler(req, res) {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  const userId = await getAuthUserId(req);
  if (!userId) return res.status(401).json({ error: 'unauthorized' });

  const sql = getSQL();
  await ensureUsersTable(sql);

  // GET — just return current status
  if (req.method === 'GET') {
    const rows = await sql`SELECT status FROM users WHERE clerk_id = ${userId}`;
    return res.status(200).json({ status: rows[0]?.status || 'unknown' });
  }

  // POST — register/check user
  if (req.method === 'POST') {
    const { email = '', name = '' } = req.body || {};

    // Check if already registered
    const existing = await sql`SELECT status, approval_token FROM users WHERE clerk_id = ${userId}`;
    if (existing.length) {
      return res.status(200).json({ status: existing[0].status });
    }

    // New user — insert as pending and send approval email
    const token = crypto.randomBytes(32).toString('hex');
    await sql`
      INSERT INTO users (clerk_id, email, name, status, approval_token, created_at)
      VALUES (${userId}, ${email}, ${name}, 'pending', ${token}, ${Date.now()})
      ON CONFLICT (clerk_id) DO NOTHING
    `;

    await sendApprovalEmail(email, name, userId, token).catch(e =>
      console.error('Email send error:', e.message)
    );

    return res.status(200).json({ status: 'pending' });
  }

  return res.status(405).json({ error: 'method not allowed' });
};
