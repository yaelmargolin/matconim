const { neon } = require('@neondatabase/serverless');
const { getAuthUserId } = require('./_auth');
const { setCORS } = require('./_db');

function getSQL() { return neon(process.env.DATABASE_URL); }

async function ensureTable(sql) {
  await sql`
    CREATE TABLE IF NOT EXISTS free_notes (
      id         BIGINT PRIMARY KEY,
      title      TEXT   DEFAULT '',
      content    TEXT   DEFAULT '',
      created_at BIGINT,
      owner_id   TEXT
    )
  `;
}

function rowToNote(r) {
  return {
    id:        Number(r.id),
    title:     r.title   || '',
    content:   r.content || '',
    createdAt: Number(r.created_at || r.id),
  };
}

module.exports = async function handler(req, res) {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const sql = getSQL();
    await ensureTable(sql);
    const userId = getAuthUserId(req);
    if (!userId) return res.status(401).json({ error: 'unauthorized' });

    if (req.method === 'GET') {
      const rows = await sql`
        SELECT * FROM free_notes WHERE owner_id = ${userId} ORDER BY created_at DESC
      `;
      return res.status(200).json(rows.map(rowToNote));
    }

    if (req.method === 'POST') {
      const { id, title, content } = req.body || {};
      if (!id) return res.status(400).json({ error: 'missing id' });
      const rows = await sql`
        INSERT INTO free_notes (id, title, content, created_at, owner_id)
        VALUES (${id}, ${title || ''}, ${content || ''}, ${id}, ${userId})
        ON CONFLICT (id) DO UPDATE
          SET title = EXCLUDED.title, content = EXCLUDED.content
        RETURNING *
      `;
      return res.status(201).json(rowToNote(rows[0]));
    }

    return res.status(405).json({ error: 'method not allowed' });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: e.message });
  }
};
