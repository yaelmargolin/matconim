import json, re

with open('aNote_App/recipes-data.json') as f:
    recipes = json.load(f)

# ── 1. FIX BAD TITLES ──────────────────────────────────────────────────────
TITLE_FIXES = {
    1777472223624: "כדורי גבינה רכים",
    1777472223713: "חלה של עינב",
    1777472224164: "דלעת קלויה בתנור",   # "צילום: דן פרץ, סטיילינג: נורית קריב"
    1777472224408: "סלט חסה ומלפפון",    # "הכנתי ויצא נהדר"
    1777472224603: "עוגיות מגולגלות",    # "~ מתכוניישן"
    1777472224958: "באו עם בקר מפורק",   # "~ מתכוניישן"
    1777472225462: "בצק שמרים מתוק",     # "המתכון של הדר פלדמן"
    1777472224431: "סלט כרוב ותפוח",     # "המצרכים-"
    1777472224474: "ירקות קורמלים בתנור",# "צרכים (ל-4-6..."
    1777472224597: "בצק אחד - 3 סוגי עוגיות",  # "שרה נגלר"
}

# Additional bad titles found from other scans
TITLE_FIXES.update({
    # Still has tilde / source tag
    1777472223965: "אלדושקיי - עוגיות יוגורט רוסיות",
})

# ── 2. CATEGORY REASSIGNMENT ──────────────────────────────────────────────
def best_category(r):
    title = r.get('title', '')
    t = title.lower()
    full = ' '.join([title,
                     r.get('notes', ''),
                     ' '.join(r.get('ingredients', [])),
                     ' '.join(r.get('steps', []))]).lower()

    # Soups — title must say מרק
    if re.match(r'^מרק\b', t):
        return 'soups'

    # Salads — title must say סלט
    if re.match(r'^סלט\b', t):
        return 'salads'

    # Jam/sweet spread — title starts with ריבת/ממרח
    if re.match(r'^ריבת?\b|^ממרח\b|^ריבה\b|^מרמלד', t):
        return 'sweet'

    # Chicken — title has clear chicken word
    if re.search(r'פרגיות|חזה עוף|עוף\b|שניצל|נאגטס עוף|קציצות עוף|עוף טחון|גיוזה עוף|קרפלך עוף', t):
        return 'chicken'

    # Meat — title has clear beef/meat word (not chicken)
    if re.search(r'\bבשר\b|סינטה|שייטל|אנטריקוט|פיקניה|אסאדו|בריסקט|קבב\b|ארעיס|כופתא|סטייק|המבורגר\b|קציצות בשר|כדורי בשר', t):
        return 'meat'

    # Fish
    if re.search(r'סלמון|טונה|דג |דגי |פילה דג|קוד\b|לוקוס|מוסר ים|גרבלקס|חריימה', t):
        return 'fish'

    # Bread/savory pastry — title keyword
    if re.search(r'^לחם\b|^חלה\b|^פיתות?\b|^פוקצ.ה|^ביגלה|^בייגל|^בורקס|^פרצל|^לחמניות|^מלאוואח|^מופלטה|^ג.חנון|^לאפה|^קרקרים|^פרנה\b|^בייגלס', t):
        return 'savory'

    # Desserts (sweet baked goods, sweets) — title keyword
    if re.search(r'^עוגת?\b|^עוגיות?\b|^טארט\b|^פחזניות|^כנאפה|^בקלווה|^גלידת?|^חלווה|^שטרודל|^טירמיסו|^תירמיסו|^מוס\b|^קרמבו|^קנאלה|^מוצ.י|^עוגת|^ברונ|^בראוני|^מקרון', t):
        return 'desserts'

    # Pasta/grains
    if re.search(r'^פסטה\b|^ניוקי|^לזניה|^ריזוטו|^אטריות|^קוגל\b', t):
        return 'pasta'

    return None  # no change

# Apply category fixes
cat_changes = 0
title_changes = 0

for r in recipes:
    rid = r['id']

    # Fix title
    if rid in TITLE_FIXES:
        r['title'] = TITLE_FIXES[rid]
        title_changes += 1

    # Fix category
    suggested = best_category(r)
    if suggested and suggested != r.get('category'):
        old_cat = r.get('category')
        r['category'] = suggested
        cat_changes += 1
        print(f"  [{rid}] cat: {old_cat!r:10} → {suggested!r:10} | {r['title'][:55]}")

print(f'\nTitles fixed: {title_changes}')
print(f'Categories fixed: {cat_changes}')

with open('aNote_App/recipes-data.json', 'w') as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2)
print('Saved.')
