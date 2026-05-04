const { getSQL, ensureTable, rowToRecipe, setCORS } = require('./_db');
const { requireAuth } = require('./_auth');

module.exports = async function handler(req, res) {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    await ensureTable();
    const sql = getSQL();

    // ── GET all recipes ──────────────────────────────────────────────────────
    if (req.method === 'GET') {
      const rows = await sql`SELECT * FROM recipes ORDER BY title ASC`;
      return res.status(200).json(rows.map(rowToRecipe));
    }

    // ── POST create recipe ───────────────────────────────────────────────────
    if (req.method === 'POST') {
      if (!await requireAuth(req, res)) return;
      const r = req.body;
      if (!r || !r.id) return res.status(400).json({ error: 'missing id' });
      const rows = await sql`
        INSERT INTO recipes (id, title, category, ingredients, steps, notes, url, image, text_raw, created_at)
        VALUES (
          ${r.id},
          ${r.title || ''},
          ${r.category || 'other'},
          ${JSON.stringify(r.ingredients || [])},
          ${JSON.stringify(r.steps || [])},
          ${r.notes || ''},
          ${r.url || ''},
          ${r.image || null},
          ${r.text || ''},
          ${r.createdAt || r.id}
        )
        ON CONFLICT (id) DO UPDATE SET
          title       = EXCLUDED.title,
          category    = EXCLUDED.category,
          ingredients = EXCLUDED.ingredients,
          steps       = EXCLUDED.steps,
          notes       = EXCLUDED.notes,
          url         = EXCLUDED.url,
          image       = EXCLUDED.image,
          text_raw    = EXCLUDED.text_raw
        RETURNING *
      `;
      return res.status(201).json(rowToRecipe(rows[0]));
    }

    return res.status(405).json({ error: 'method not allowed' });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: e.message });
  }
};
