import json

with open('aNote_App/recipes-data.json') as f:
    recipes = json.load(f)

FIXES = {
    # 300 גר קמח → biscuit/cookie dough with cottage cheese filling, cut into squares, baked
    1777472223337: "ריבועי גבינה",
    # 1 קג קמח → yeast dough, shaped into bagels with sesame/poppy seed coating
    1777472223507: "ביגלה ביתית",
    # 1 קג קמח → basic bread: flour, water, yeast, salt
    1777472223540: "לחם בסיסי",
    # 325 גר מים → artisan bread with biga pre-ferment, white+whole wheat flour, 2-day process
    1777472223593: "לחם ביגה",
    # 600 ג' חזה עוף → chicken breast with zucchini, carrots, sweet chili stir-fry
    1777472223778: "מוקפץ עוף עם ירקות",
    # 70 גר יוגורט x10 → yogurt dough stuffed with mozzarella + Bulgarian + kashkaval cheese mix
    1777472223825: "לחם גבינות בבצק יוגורט",
    # 1 כוס זיתי קלמטה → marinated olives with garlic, lemon, oregano, parsley, capers
    1777472223886: "זיתים מתובלים",
    # 100 גר פרורי חלה → challah crumb patties with parmesan, eggs, in tomato sauce
    1777472223906: "קציצות פירורי חלה ברוטב עגבניות",
    # 1 כוס שיבולת שועל → oat and whole wheat flour cake/muffins with stewed plums
    1777472224070: "עוגת שיבולת שועל ושזיפים",
    # 5 מנות פטריות מהירות → has no content; just clean the quantity from title
    1777472224196: "פטריות מהירות",
    # 2כפות שמרים → enriched yeast dough with eggs, oil, brandy (challah-style)
    1777472224338: "בצק שמרים עשיר",
    # 100 ג"רחמאה → shortcrust tart with custard filling and sliced apples
    1777472224608: "טארט תפוחים",
    # 3 כפות קמח אורז → chocolate microwave mug cake (rice flour, cocoa, yogurt, egg)
    1777472224714: "עוגת ספל שוקולד",
    # 1 כוס אורז בסמטי → rice pudding with saffron, cardamom, milk, pistachios, cashews
    1777472224986: "פודינג אורז עם זעפרן",
    # 1.2 אונטריב טחון → ground meat with onions, celery, parsley, baharat stuffed in pita (aaras)
    1777472225274: "ארעיס - בשר טחון",
    # 2 כפות סויה8 → sesame, paprika, cumin, garlic, lemon spice blend (doubled portions)
    1777472225411: "תיבול שומשום וסויה",
    # 100 ג' חמאה → baked eggs with spinach, mushrooms, cherry tomatoes, cheese, cream
    1777472225491: "ביצים אפויות על תרד ופטריות",
}

changed = 0
lookup = {r['id']: r for r in recipes}
for rid, new_title in FIXES.items():
    r = lookup.get(rid)
    if r:
        old = r.get('title', '')
        r['title'] = new_title
        print(f"  {repr(old[:50])} → {repr(new_title)}")
        changed += 1

print(f'\nTotal: {changed} titles updated')

with open('aNote_App/recipes-data.json', 'w') as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2)
print('Saved.')
