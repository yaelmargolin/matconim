import json, psycopg2, psycopg2.extras, sys

DB_URL = open(f"{__import__('os').path.expanduser('~')}/neon.txt").read().strip()

with open('aNote_App/recipes-data.json') as f:
    recipes = json.load(f)

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print("Creating table if needed...")
cur.execute("""
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
""")
conn.commit()

print(f"Seeding {len(recipes)} recipes...")
inserted = 0
skipped  = 0

for r in recipes:
    try:
        cur.execute("""
            INSERT INTO recipes (id, title, category, ingredients, steps, notes, url, image, text_raw, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            r['id'],
            r.get('title') or '',
            r.get('category') or 'other',
            json.dumps(r.get('ingredients') or [], ensure_ascii=False),
            json.dumps(r.get('steps') or [], ensure_ascii=False),
            r.get('notes') or '',
            r.get('url') or '',
            r.get('image') or None,
            r.get('text') or '',
            r.get('createdAt') or r['id'],
        ))
        if cur.rowcount:
            inserted += 1
        else:
            skipped += 1
    except Exception as e:
        print(f"  Error on {r['id']}: {e}")
        conn.rollback()
        continue

    if (inserted + skipped) % 100 == 0:
        conn.commit()
        print(f"  {inserted + skipped}/{len(recipes)} (inserted: {inserted}, skipped: {skipped})")

conn.commit()
cur.close()
conn.close()
print(f"\nDone. Inserted: {inserted}, Skipped (already exist): {skipped}")
