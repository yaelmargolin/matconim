import json, re

with open('/Users/yaelmargolin/Desktop/matconim/aNote_App/recipes-data.json') as f:
    recipes = json.load(f)

# id → new title (based on manual review of content)
FIXES = {
    1777472223219: "מסעדת גולדיס",
    1777472223225: "מאלאי קופטה",
    1777472223282: "קבבים מגוונים",
    1777472223304: "סלט סלק עם גבינה",
    1777472223375: "טיפים לבישול אורז",
    1777472223408: "ירקות מוקפצים עם טופו",
    1777472223437: "לחמניות רכות",
    1777472223463: "בורקס פילו עם גבינה בולגרית",
    1777472223487: "בורקס גבינה",
    1777472223492: "מרק ירקות",
    1777472223499: "ביגלה ירושלמית",
    1777472223502: "פרצל",
    1777472223504: "ביגלה מתוקה",
    1777472223573: "סלט ברוקולי ברוטב טחינה",
    1777472223577: "בריוש ממולא בקרם שקדים ותפוחים",
    1777472223595: "גבינה ביתית",
    1777472223604: "בצק עשיר (חמאה וחלב)",
    1777472223620: "בצק למאפה",
}

# Additional fixes by scanning all recipes
def has_bad_title(t):
    if not t or t == 'מתכון ללא שם': return True
    if 'http' in t or 'www.' in t: return True
    if len(t) <= 5: return True
    if '|' in t: return True
    return False

# Manual fixes for remaining 72 recipes (by position in output)
MANUAL = {
    # id: new_title  — derived from content
}

# Let's build from the full list
all_fixable = [(r['id'], r) for r in recipes if has_bad_title(r.get('title','').strip()) and (r.get('ingredients') or r.get('steps') or r.get('notes','').strip())]
print(f"Fixable: {len(all_fixable)}")
for rid, r in all_fixable:
    if rid not in FIXES:
        print(f"  MISSING: {rid} | {repr(r.get('title','')[:50])}")
