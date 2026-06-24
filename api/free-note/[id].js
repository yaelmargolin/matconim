const { neon } = require('@neondatabase/serverless');
const { getAuthUserId } = require('../_auth');
const { setCORS } = require('../_db');

function getSQL() { return neon(process.env.DATABASE_URL); }

module.exports = async function handler(req, res) {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const sql = getSQL();
    const id  = req.query.id;
    const userId = getAuthUserId(req);
    if (!userId) return res.status(401).json({ error: 'unauthorized' });

    if (req.method === 'PUT') {
      const { title, content } = req.body || {};
      await sql`
        UPDATE free_notes
        SET title = ${title || ''}, content = ${content || ''}
        WHERE id = ${id} AND owner_id = ${userId}
      `;
      return res.status(200).json({ ok: true });
    }

    if (req.method === 'DELETE') {
      await sql`DELETE FROM free_notes WHERE id = ${id} AND owner_id = ${userId}`;
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ error: 'method not allowed' });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: e.message });
  }
};
