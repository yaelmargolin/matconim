const { getSQL, ensureTable, rowToRecipe, setCORS } = require('../_db');
const { getAuthUserId } = require('../_auth');

module.exports = async function handler(req, res) {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  const id = Number(req.query.id);
  if (!id) return res.status(400).json({ error: 'missing id' });

  try {
    await ensureTable();
    const sql = getSQL();

    // ── PUT update recipe ────────────────────────────────────────────────────
    if (req.method === 'PUT') {
      const userId = getAuthUserId(req);
      if (!userId) return res.status(401).json({ error: 'unauthorized' });

      // Only the recipe owner can edit (owner_id = NULL means original/protected)
      const check = await sql`SELECT owner_id FROM recipes WHERE id = ${id}`;
      if (!check.length) return res.status(404).json({ error: 'not found' });
      if (check[0].owner_id !== userId)
        return res.status(403).json({ error: 'forbidden' });

      const r = req.body;
      const rows = await sql`
        UPDATE recipes SET
          title       = ${r.title || ''},
          category    = ${r.category || 'other'},
          ingredients = ${JSON.stringify(r.ingredients || [])},
          steps       = ${JSON.stringify(r.steps || [])},
          notes       = ${r.notes || ''},
          url         = ${r.url || ''},
          image       = ${r.image || null},
          text_raw    = ${r.text || ''}
        WHERE id = ${id}
        RETURNING *
      `;
      return res.status(200).json(rowToRecipe(rows[0]));
    }

    // ── DELETE recipe ────────────────────────────────────────────────────────
    if (req.method === 'DELETE') {
      const userId = getAuthUserId(req);
      if (!userId) return res.status(401).json({ error: 'unauthorized' });

      const check = await sql`SELECT owner_id FROM recipes WHERE id = ${id}`;
      if (!check.length) return res.status(404).json({ error: 'not found' });
      if (check[0].owner_id !== userId)
        return res.status(403).json({ error: 'forbidden' });

      await sql`DELETE FROM recipes WHERE id = ${id}`;
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ error: 'method not allowed' });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: e.message });
  }
};
