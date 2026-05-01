import json, re

with open('aNote_App/recipes-data.json') as f:
    recipes = json.load(f)

lookup = {r['id']: r for r in recipes}

def full_text(r):
    return ' '.join([
        r.get('title', ''),
        r.get('notes', ''),
        ' '.join(r.get('ingredients', [])),
        ' '.join(r.get('steps', []))
    ]).lower()

def has_meat(r):
    ft = full_text(r)
    return bool(re.search(
        r'בשר טחון|בשר בקר|בשר כבש|בשר עגל|סינטה|שייטל|אנטריקוט|פיקניה|אסאדו|בריסקט|'
        r'קצבייה|נקניק(?!ית)|קבב|ארעיס|כופתא|סטייק|המבורגר|'
        r'טחון(?! עוף| הודו| טורקי)|'
        r'\bבשר\b(?! עוף| הודו)',
        ft
    ))

def has_chicken(r):
    ft = full_text(r)
    return bool(re.search(
        r'פרגיות|חזה עוף|שוק עוף|כנפי עוף|עוף שלם|עוף טחון|עוף מפורק|'
        r'שניצל|נאגטס|קציצות עוף|גיוזה עוף|קרפלך עוף|כרעי עוף|'
        r'\bעוף\b',
        ft
    ))

def has_fish(r):
    ft = full_text(r)
    return bool(re.search(
        r'סלמון|טונה|דג |דגי |פילה דג|קוד\b|לוקוס|מוסר ים|גרבלקס|חריימה|'
        r'דג ים|אמנון|בורי|מוסר|פורל|הרינג|אנשובי',
        ft
    ))

def has_pasta(r):
    ft = full_text(r)
    return bool(re.search(
        r'פסטה|ספגטי|פנה|ריגטוני|פרפר(?:ות)?|לזניה|ניוקי|ריזוטו|אטריות|'
        r'אורז|קינואה|בולגור|בורגול|כוסמת|קוסקוס|עדשים|שעועית',
        ft
    ))

def is_veggie_only(r):
    """Has no meat/chicken/fish — pure veggie/dairy/egg dish"""
    return not has_meat(r) and not has_chicken(r) and not has_fish(r)

# ── AUDIT MEAT CATEGORY ───────────────────────────────────────────────────────
print("=== NON-MEAT recipes currently in 'meat' category ===")
meat_fixes = {}
for r in recipes:
    if r.get('category') != 'meat':
        continue
    if has_meat(r):
        continue
    # Check if it's actually chicken
    if has_chicken(r):
        meat_fixes[r['id']] = 'chicken'
        print(f"  → chicken: [{r['id']}] {r['title']}")
    elif has_fish(r):
        meat_fixes[r['id']] = 'fish'
        print(f"  → fish:    [{r['id']}] {r['title']}")
    else:
        # Decide savory vs veggies vs other
        t = r.get('title', '').lower()
        ft = full_text(r)
        if re.search(r'^סלט\b', t):
            meat_fixes[r['id']] = 'salads'
            print(f"  → salads:  [{r['id']}] {r['title']}")
        elif re.search(r'^מרק\b', t):
            meat_fixes[r['id']] = 'soups'
            print(f"  → soups:   [{r['id']}] {r['title']}")
        elif re.search(r'^עוגת?\b|^עוגיות?\b|^מוס\b|^גלידת?|^פחזניות|^טארט\b|^קאפ|^בראוני|^מקרון', t):
            meat_fixes[r['id']] = 'desserts'
            print(f"  → desserts:[{r['id']}] {r['title']}")
        elif re.search(r'^לחם\b|^חלה\b|^פיתות?\b|^פוקצ|^בורקס|^בייגל|^לחמניות|^בצק', t):
            meat_fixes[r['id']] = 'savory'
            print(f"  → savory:  [{r['id']}] {r['title']}")
        elif re.search(r'ביצ|גבינ|טופו|ירק|כרוב|תרד|עגבני|פטריה|כרובית|קישוא|דלעת|אפונ|תירס', ft):
            meat_fixes[r['id']] = 'veggies'
            print(f"  → veggies: [{r['id']}] {r['title']}")
        else:
            meat_fixes[r['id']] = 'savory'
            print(f"  → savory:  [{r['id']}] {r['title']}")

# ── AUDIT CHICKEN CATEGORY ────────────────────────────────────────────────────
print("\n=== NON-CHICKEN recipes currently in 'chicken' category ===")
chicken_fixes = {}
for r in recipes:
    if r.get('category') != 'chicken':
        continue
    if has_chicken(r):
        continue
    if has_meat(r):
        chicken_fixes[r['id']] = 'meat'
        print(f"  → meat:    [{r['id']}] {r['title']}")
    elif has_fish(r):
        chicken_fixes[r['id']] = 'fish'
        print(f"  → fish:    [{r['id']}] {r['title']}")
    else:
        t = r.get('title', '').lower()
        ft = full_text(r)
        if re.search(r'^סלט\b', t):
            chicken_fixes[r['id']] = 'salads'
            print(f"  → salads:  [{r['id']}] {r['title']}")
        elif re.search(r'^מרק\b', t):
            chicken_fixes[r['id']] = 'soups'
            print(f"  → soups:   [{r['id']}] {r['title']}")
        elif re.search(r'^עוגת?\b|^עוגיות?\b|^מוס\b|^גלידת?', t):
            chicken_fixes[r['id']] = 'desserts'
            print(f"  → desserts:[{r['id']}] {r['title']}")
        elif re.search(r'^לחם\b|^חלה\b|^פיתות?\b|^פוקצ|^בורקס|^בצק', t):
            chicken_fixes[r['id']] = 'savory'
            print(f"  → savory:  [{r['id']}] {r['title']}")
        else:
            chicken_fixes[r['id']] = 'savory'
            print(f"  → savory:  [{r['id']}] {r['title']}")

# ── AUDIT FISH CATEGORY ───────────────────────────────────────────────────────
print("\n=== NON-FISH recipes currently in 'fish' category ===")
fish_fixes = {}
for r in recipes:
    if r.get('category') != 'fish':
        continue
    if has_fish(r):
        continue
    if has_chicken(r):
        fish_fixes[r['id']] = 'chicken'
        print(f"  → chicken: [{r['id']}] {r['title']}")
    elif has_meat(r):
        fish_fixes[r['id']] = 'meat'
        print(f"  → meat:    [{r['id']}] {r['title']}")
    else:
        fish_fixes[r['id']] = 'veggies'
        print(f"  → veggies: [{r['id']}] {r['title']}")

# ── AUDIT SOUPS CATEGORY ──────────────────────────────────────────────────────
print("\n=== Non-soup recipes in 'soups' category ===")
for r in recipes:
    if r.get('category') != 'soups':
        continue
    t = r.get('title', '').lower()
    ft = full_text(r)
    if not re.search(r'מרק|נזיד|יורשקה|בישול|שורבה|בישקי|מינסטרוני|ציר', ft):
        print(f"  ? [{r['id']}] {r['title']}")

# ── AUDIT SALADS CATEGORY ─────────────────────────────────────────────────────
print("\n=== Non-salad recipes in 'salads' category ===")
for r in recipes:
    if r.get('category') != 'salads':
        continue
    t = r.get('title', '').lower()
    if not re.search(r'סלט|סלסה|טעחינה|ממרח|שקשוקה|חומוס|מטבוחה|ג.וואנ|תוספת|ירקות', t):
        ft = full_text(r)
        if not re.search(r'ירקות|עגבני|מלפפון|חסה|כרוב|גזר|פלפל|אבוקד|גרגיר|רוקט', ft):
            print(f"  ? [{r['id']}] {r['title']}")

# ── AUDIT SAVORY CATEGORY ─────────────────────────────────────────────────────
print("\n=== Likely misplaced in 'savory' ===")
savory_fixes = {}
for r in recipes:
    if r.get('category') != 'savory':
        continue
    t = r.get('title', '').lower()
    ft = full_text(r)
    # Desserts masquerading as savory
    if re.search(r'^עוגת?\b|^עוגיות?\b|^מוס\b|^גלידת?|^פחזניות|^טארט\b|^קאפ|^בראוני|^מקרון|^שטרודל|^קרמבו|^טירמיסו', t):
        savory_fixes[r['id']] = 'desserts'
        print(f"  → desserts:[{r['id']}] {r['title']}")
    elif re.search(r'^מרק\b', t):
        savory_fixes[r['id']] = 'soups'
        print(f"  → soups:   [{r['id']}] {r['title']}")
    elif re.search(r'^סלט\b', t):
        savory_fixes[r['id']] = 'salads'
        print(f"  → salads:  [{r['id']}] {r['title']}")

# ── AUDIT DESSERTS CATEGORY ───────────────────────────────────────────────────
print("\n=== Likely misplaced in 'desserts' ===")
desserts_fixes = {}
for r in recipes:
    if r.get('category') != 'desserts':
        continue
    t = r.get('title', '').lower()
    if re.search(r'^מרק\b', t):
        desserts_fixes[r['id']] = 'soups'
        print(f"  → soups:   [{r['id']}] {r['title']}")
    elif re.search(r'^סלט\b', t):
        desserts_fixes[r['id']] = 'salads'
        print(f"  → salads:  [{r['id']}] {r['title']}")
    elif re.search(r'^לחם\b|^חלה\b|^פיתות?\b|^פוקצ|^בורקס|^לחמניות', t):
        desserts_fixes[r['id']] = 'savory'
        print(f"  → savory:  [{r['id']}] {r['title']}")
    elif has_meat(r) and not re.search(r'שוקולד|סוכר|קרמל|ריבה|מתוק|דבש|וניל|קינמון', full_text(r)):
        desserts_fixes[r['id']] = 'meat'
        print(f"  → meat:    [{r['id']}] {r['title']}")

# ── AUDIT VEGGIES CATEGORY ────────────────────────────────────────────────────
print("\n=== Likely misplaced in 'veggies' ===")
veggies_fixes = {}
for r in recipes:
    if r.get('category') != 'veggies':
        continue
    t = r.get('title', '').lower()
    if re.search(r'^מרק\b', t):
        veggies_fixes[r['id']] = 'soups'
        print(f"  → soups:   [{r['id']}] {r['title']}")
    elif re.search(r'^סלט\b', t):
        veggies_fixes[r['id']] = 'salads'
        print(f"  → salads:  [{r['id']}] {r['title']}")
    elif re.search(r'^עוגת?\b|^עוגיות?\b', t):
        veggies_fixes[r['id']] = 'desserts'
        print(f"  → desserts:[{r['id']}] {r['title']}")
    elif has_meat(r):
        veggies_fixes[r['id']] = 'meat'
        print(f"  → meat:    [{r['id']}] {r['title']}")
    elif has_chicken(r):
        veggies_fixes[r['id']] = 'chicken'
        print(f"  → chicken: [{r['id']}] {r['title']}")

# ── APPLY ALL FIXES ───────────────────────────────────────────────────────────
all_fixes = {}
all_fixes.update(meat_fixes)
all_fixes.update(chicken_fixes)
all_fixes.update(fish_fixes)
all_fixes.update(savory_fixes)
all_fixes.update(desserts_fixes)
all_fixes.update(veggies_fixes)

print(f"\n=== SUMMARY ===")
print(f"meat fixes:     {len(meat_fixes)}")
print(f"chicken fixes:  {len(chicken_fixes)}")
print(f"fish fixes:     {len(fish_fixes)}")
print(f"savory fixes:   {len(savory_fixes)}")
print(f"desserts fixes: {len(desserts_fixes)}")
print(f"veggies fixes:  {len(veggies_fixes)}")
print(f"TOTAL:          {len(all_fixes)}")

if all_fixes:
    for r in recipes:
        if r['id'] in all_fixes:
            r['category'] = all_fixes[r['id']]

    with open('aNote_App/recipes-data.json', 'w') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    print('Saved.')
else:
    print('No changes needed.')

# Final count per category
from collections import Counter
counts = Counter(r.get('category') for r in recipes)
print("\nCategory counts after fix:")
for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {cat:12} {n}")
