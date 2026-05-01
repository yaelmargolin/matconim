import json

with open('aNote_App/recipes-data.json') as f:
    recipes = json.load(f)

CORRECTIONS = {
    # ── False positives: incorrectly moved to meat from veggies ──────────────
    1777472223289: 'veggies',  # פטריות מוקפצות — corn/ginger/tofu, no meat
    1777472223512: 'veggies',  # כרובית בסגנון מיוחד — cauliflower dish
    1777472224111: 'veggies',  # מלנזיה חציל — eggplant dish
    1777472224437: 'veggies',  # כרוב אדום — red cabbage/apple dish
    1777472224493: 'salads',   # סלסה ישראלית — tomato/onion salsa
    1777472224502: 'veggies',  # פטריות עם שום ופירורי לחם — mushrooms
    1777472224193: 'veggies',  # תבשיל בצל שום ותימין — onion/garlic/thyme stew

    # ── False positives: incorrectly moved to chicken from veggies ──────────
    1777472223460: 'veggies',  # מוקפץ בוק צ'וי ופטריות — bok choy + mushrooms
    1777472225012: 'veggies',  # פטריות שיטאקי ובוק צ'וי — shiitake + bok choy
    1777472225476: 'veggies',  # נודלס ירקות — vegetable noodles

    # ── False positives: falafel/hummus/wonton moved to meat → savory ────────
    1777472223743: 'savory',   # מתכון לבצק וונטון — flour/water dough
    1777472223763: 'savory',   # חומוס ופלאפל — chickpeas
    1777472225060: 'savory',   # פלאפל חומוס
    1777472225061: 'savory',   # פלאפל חומוס של הדס

    # ── Meat dishes incorrectly moved to veggies ────────────────────────────
    1777472223361: 'meat',     # אוסובוקו — classic veal shank dish
    1777472224034: 'meat',     # קציצות בקר ברוטב עגבניות — beef meatballs

    # ── Vegetarian meatballs — not really meat ───────────────────────────────
    1777472223906: 'savory',   # קציצות פירורי חלה — breadcrumb balls (dairy+eggs)

    # ── Soups items that clearly don't belong there ──────────────────────────
    1777472223408: 'veggies',  # ירקות מוקפצים עם טופו — stir-fried veggies
    1777472223564: 'savory',   # הכנת קעריות מבצק שקם — pastry cups
    1777472223600: 'savory',   # גבינת שמנת — cream cheese making
    1777472223753: 'other',    # זה קל ומספק כל — empty, unidentifiable
    1777472223853: 'veggies',  # טופו ברוטב לימון חרדל ודבש — tofu dish
    1777472223863: 'veggies',  # בלונוז טופו פטנט — tofu recipe
    1777472223901: 'veggies',  # כדורי טופו ברוטב חמוץ מתוק — tofu balls
    1777472224149: 'chicken',  # המצרכים – — step mentions פרגיות (chicken thighs)
    1777472224150: 'savory',   # בלילה לפנקייקים — pancake batter
    1777472224196: 'veggies',  # פטריות מהירות — quick mushrooms
    1777472224278: 'savory',   # רוטב סויה לנודלס — soy noodle sauce
    1777472224335: 'desserts', # סופגניות ביס — bite-sized donuts
    1777472224859: 'desserts', # המצרכים- — pear cake (butter, sugar, eggs, pears)
    1777472224985: 'desserts', # פודינג שוקולד — chocolate pudding
    1777472225407: 'desserts', # ריצ'ארלי — almond cookies
    1777472224859: 'desserts', # (repeated, kept)

    # ── Salads items that don't belong there ─────────────────────────────────
    1777472224487: 'other',    # מערבבת … — empty/unidentifiable
    1777472225541: 'savory',   # ‏איך להפסיק לפחד ולהתחיל לאכול כוסמת — buckwheat guide

    # ── Other lingering wrong items in meat from this audit ──────────────────
    1777472223458: 'savory',   # קציצות בולט — likely vegetarian/savory based on title
}

lookup = {r['id']: r for r in recipes}
changed = 0
for rid, new_cat in CORRECTIONS.items():
    r = lookup.get(rid)
    if r and r.get('category') != new_cat:
        old = r.get('category')
        r['category'] = new_cat
        print(f"  [{rid}] {old!r:10} → {new_cat!r:10} | {r['title'][:55]}")
        changed += 1

print(f'\nTotal: {changed} corrections')

with open('aNote_App/recipes-data.json', 'w') as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2)
print('Saved.')

from collections import Counter
counts = Counter(r.get('category') for r in recipes)
print("\nCategory counts after corrections:")
for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {cat:12} {n}")
