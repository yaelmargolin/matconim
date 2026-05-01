import json

with open('aNote_App/recipes-data.json') as f:
    recipes = json.load(f)

def meaningful_list(lst):
    return [x for x in (lst or []) if x and x.strip()]

def meaningful_text(s):
    return bool(s and len(s.strip()) > 20)

def notes_to_steps(notes_text):
    lines = [l.strip() for l in notes_text.splitlines() if l.strip()]
    return lines if lines else []

kept = []
moved_count = 0
deleted_empty = 0
deleted_no_steps = 0

for r in recipes:
    ing   = meaningful_list(r.get('ingredients', []))
    steps = meaningful_list(r.get('steps', []))
    notes = r.get('notes', '')

    # ── completely empty: no ingredients AND no steps ──────────────────────
    if not ing and not steps:
        deleted_empty += 1
        continue

    # ── has ingredients but no steps ───────────────────────────────────────
    if ing and not steps:
        if meaningful_text(notes):
            # move notes → steps
            r['steps'] = notes_to_steps(notes)
            r['notes'] = ''
            moved_count += 1
            kept.append(r)
        else:
            # nothing to extract → delete
            deleted_no_steps += 1
            continue
    else:
        kept.append(r)

print(f'הועברו notes→steps:  {moved_count}')
print(f'נמחקו (ריקים):       {deleted_empty}')
print(f'נמחקו (אין שלבים):   {deleted_no_steps}')
print(f'נשארו:               {len(kept)}')
print(f'סה"כ לפני:           {len(recipes)}')

with open('aNote_App/recipes-data.json', 'w') as f:
    json.dump(kept, f, ensure_ascii=False, indent=2)
print('Saved.')
