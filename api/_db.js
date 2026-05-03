const { neon } = require('@neondatabase/serverless');

let _sql = null;
function getSQL() {
  if (!_sql) _sql = neon(process.env.DATABASE_URL);
  return _sql;
}

async function ensureTable() {
  const sql = getSQL();
  await sql`
    CREATE TABLE IF NOT EXISTS recipes (
      id          BIGINT PRIMARY KEY,
      title       TEXT    NOT NULL DEFAULT '',
      category    TEXT             DEFAULT 'other',
      ingredients JSONB            DEFAULT '[]',
      steps       JSONB            DEFAULT '[]',
      notes       TEXT             DEFAULT '',
      url         TEXT             DEFAULT '',
      image       TEXT             DEFAULT '',
      text_raw    TEXT             DEFAULT '',
      created_at  BIGINT
    )
  `;
}

function rowToRecipe(r) {
  return {
    id:          Number(r.id),
    title:       r.title,
    category:    r.category,
    ingredients: r.ingredients || [],
    steps:       r.steps       || [],
    notes:       r.notes       || '',
    url:         r.url         || '',
    image:       r.image       || undefined,
    text:        r.text_raw    || '',
    createdAt:   Number(r.created_at || r.id),
  };
}

function setCORS(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

module.exports = { getSQL, ensureTable, rowToRecipe, setCORS };
