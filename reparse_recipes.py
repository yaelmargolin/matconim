import json, re, copy

with open('/Users/yaelmargolin/Desktop/matconim/aNote_App/recipes-data.json') as f:
    recipes = json.load(f)

# Same logic as JS parseRecipe, expanded
ING_KW  = re.compile(r'^(מצרכים|רכיבים|חומרים|מרכיבים|המרכיבים|רשימת\s+המרכיבים|חומרי\s+גלם|מה\s+צריך|נדרש|לבצק|למלית|לרוטב|לציפוי|לקישוט|לגנאש|לקרם|לסירופ|ingredients?|for\s+the)(\s|[:\-–—(]|$)', re.IGNORECASE)
STEP_KW = re.compile(r'^(הוראות(\s+הכנה)?|אופן\s+ה?הכנה|הכנה|שלבי(\s+הכנה)?|הוראות\s+הביצוע|דרך\s+ה?הכנה|שיטת\s+הכנה|ביצוע|הכנת|הוראות|preparation|instructions?|method|directions?)(\s|[:\-–—(]|$)', re.IGNORECASE)

def is_ing_header(l): return bool(ING_KW.match(l)) and len(l) < 60
def is_step_header(l): return bool(STEP_KW.match(l)) and len(l) < 60

def is_ing_line(l):
    return bool(re.match(r'^[\d½¼¾⅓⅔⅛⅜⅝⅞]', l) or
                re.match(r'^\d+[\/\d]*\s+', l) or
                re.match(r'^(כף|כפיות?|כוסות?|ק"ג|גרם|מ"ל|ליטר|חבילת?|קופסת?|ענפי?|שיני|שן|פרוסות?|מעט|קמצוץ|חצי|רבע|שליש)\s', l, re.IGNORECASE))

def clean_ing(l):
    return re.sub(r'^[-•*–·‐◾▢▸►→]+\s*', '', re.sub(r'^\d+[\.\)]\s*', '', l)).strip()

def parse_text(text):
    """Returns (ingredients, steps, notes) from raw text."""
    if not text or not text.strip():
        return [], [], ''
    lines = [l.strip() for l in text.replace('\r\n', '\n').split('\n')]

    title, ing_start, ing_end, step_start = '', -1, -1, -1
    title_idx = -1
    step_end = len(lines)

    for i, l in enumerate(lines):
        if not l: continue
        if not title and ing_start == -1 and step_start == -1:
            if not is_ing_header(l) and not is_step_header(l):
                title = l; title_idx = i; continue
        if is_ing_header(l):
            if ing_start == -1: ing_start = i + 1
            continue
        if is_step_header(l):
            if ing_start != -1 and ing_end == -1: ing_end = i
            step_start = i + 1

    if ing_start != -1 and ing_end == -1:
        ing_end = step_start - 1 if step_start != -1 else len(lines)

    ingredients = []
    if ing_start != -1:
        for l in lines[ing_start:ing_end]:
            if not l: continue
            c = clean_ing(l)
            if c: ingredients.append(c)

    # Fallback: auto-detect ingredients if none found
    if not ingredients:
        boundary = step_start - 1 if step_start != -1 else len(lines)
        for l in lines[(title_idx+1 if title_idx != -1 else 0):boundary]:
            if not l: continue
            if is_ing_header(l): continue
            if is_ing_line(l):
                c = clean_ing(l)
                if c: ingredients.append(c)

    steps = []
    if step_start != -1:
        buf = ''
        def flush():
            nonlocal buf
            t = buf.strip().rstrip('.')
            if len(t) > 2: steps.append(t)
            buf = ''
        for l in lines[step_start:step_end]:
            if not l: flush(); continue
            if re.match(r'^\d+[\.\)]\s+', l): flush(); buf = re.sub(r'^\d+[\.\)]\s+', '', l).rstrip('.'); flush()
            elif re.match(r'^[-•*–·‐]\s+', l): flush(); buf = re.sub(r'^[-•*–·‐]\s+', '', l).rstrip('.'); flush()
            else:
                buf += (' ' if buf else '') + l
                if l.endswith('.'): flush()
        flush()

    # Capture notes (between title and first section)
    note_start = (title_idx + 1) if title_idx != -1 else 0
    note_end   = ing_start if ing_start != -1 else (step_start if step_start != -1 else len(lines))
    notes_lines = [l for l in lines[note_start:note_end] if l and not is_ing_header(l) and not is_step_header(l)]
    notes = '\n'.join(notes_lines)

    return ingredients, steps, notes


fixed = 0
for r in recipes:
    if r.get('ingredients') and r.get('steps'):
        continue  # already good

    # Reconstruct text from what we have
    parts = []
    if r.get('title'): parts.append(r['title'])
    if r.get('notes','').strip(): parts.append(r['notes'])
    # Add steps back as raw text if no ingredients
    if not r.get('ingredients') and r.get('steps'):
        parts.extend(r['steps'])

    if not parts or len(parts) == 1:
        continue  # only title, nothing to do

    text = '\n'.join(parts)
    new_ing, new_steps, new_notes = parse_text(text)

    changed = False
    if new_ing and not r.get('ingredients'):
        r['ingredients'] = new_ing
        changed = True
    if new_steps and not r.get('steps'):
        r['steps'] = new_steps
        changed = True
    if changed:
        r['notes'] = new_notes
        fixed += 1

print(f'Fixed: {fixed} recipes')

# Verify
no_ing_no_steps = [r for r in recipes if not r.get('ingredients') and not r.get('steps')]
has_both = [r for r in recipes if r.get('ingredients') and r.get('steps')]
steps_no_ing = [r for r in recipes if not r.get('ingredients') and r.get('steps')]
ing_no_steps = [r for r in recipes if r.get('ingredients') and not r.get('steps')]
print(f'After fix:')
print(f'  יש מצרכים + שלבים: {len(has_both)}')
print(f'  יש שלבים, אין מצרכים: {len(steps_no_ing)}')
print(f'  יש מצרכים, אין שלבים: {len(ing_no_steps)}')
print(f'  ריקים לחלוטין: {len(no_ing_no_steps)}')

with open('/Users/yaelmargolin/Desktop/matconim/aNote_App/recipes-data.json', 'w') as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2)
print('Saved.')
