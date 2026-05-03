#!/usr/bin/env node
// Run once: node scripts/seed.js
// Requires DATABASE_URL env var (copy from Vercel dashboard or .env.local)
require('dotenv').config({ path: '.env.local' });

const { neon } = require('@neondatabase/serverless');
const recipes = require('../aNote_App/recipes-data.json');

async function seed() {
  const sql = neon(process.env.DATABASE_URL);

  console.log('Creating table if needed...');
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

  console.log(`Seeding ${recipes.length} recipes in batches...`);
  let inserted = 0;

  for (const r of recipes) {
    await sql`
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
      ON CONFLICT (id) DO NOTHING
    `;
    inserted++;
    if (inserted % 50 === 0) console.log(`  ${inserted}/${recipes.length}`);
  }

  console.log(`Done. ${inserted} recipes seeded.`);
}

seed().catch(e => { console.error(e); process.exit(1); });
