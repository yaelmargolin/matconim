#!/usr/bin/env python3
"""
Process notes-recipes.json → recipes-data.json
Replicates the JS import logic from index.html.
"""
import json, re, time

# ── helpers ──────────────────────────────────────────────────────────────────

def strip_anote_markup(body):
    if not body:
        return ''
    s = body
    s = re.sub(r'<@media[^>]*?/>', '', s)
    s = re.sub(r'<@font[^>]*>', '', s)
    s = re.sub(r'</@font>', '', s)
    s = re.sub(r'<@h[12]>([\s\S]*?)</@h[12]>', r'\1\n', s)
    s = re.sub(r'</?@[a-z0-9_]+(?::[^>]*)?>', '', s, flags=re.IGNORECASE)
    s = re.sub(r'  +', ' ', s)
    return s.strip()

def clean_import_title(title):
    if not title:
        return ''
    # take only the first line (strip URLs and extra lines)
    title = title.split('\n')[0].strip()
    if re.match(r'^https?://', title):
        return ''
    # strip phone numbers
    title = re.sub(r'\d{2,3}-\d{6,7}.*$', '', title).strip()
    # strip site-name suffix patterns: "Dish name - SiteName" or "Dish name | SiteName"
    title = re.sub(r'\s*[-–|]\s*[^-–|\n]{3,50}$', '', title).strip()
    # strip trailing punctuation
    title = title.rstrip('.,;:')
    return title.strip()

# ── categories ───────────────────────────────────────────────────────────────

KW = {
    'chicken':  ['עוף','חזה עוף','שוק עוף','כרעיים','כנפיים','פרגית','הודו','ברווז','אווז','קורניש','ביריאני','טיקה','מרינדה עוף','שניצל עוף','גריל עוף'],
    'meat':     ['בקר','כבש','עגל','נקניק','המבורגר','סטייק','צלי','קציצ','שניצל','כבד','אסאדו','ריב','בשר טחון','פילה בקר','קבב','ברבקיו','אנטריקוט','בשר בקר','ספריבס','ליבה','פולקה'],
    'fish':     ['דג','סלמון','טונה','בקלה','קרפיון','לוברה','מוסר','דניס','פורל','שרימפס','קלמרי','פירות ים','בס ים','גפילטע','כבד דג','אנשובי','הרינג'],
    'pasta':    ['פסטה','ספגטי','ריזוטו','קוסקוס','אטריות','לזניה','פנה','פוסילי',"פטוצ'יני",'ניוקי','אורז','פדאוס','בורגול','פארו'],
    'savory':   ['מאפה','לחם','בצק שמרים','פיצה',"פוקצ'ה",'קיש','בורקס',"ג'חנון",'בייגלה','פיתה','לחמניות','טארט מלוח','מאפה מלוח','כריך',"סנדוויץ",'באגט','לאפה','מסמן','כתיף'],
    'soups':    ['מרק','ציר','מינסטרונה','בורש','שקשוקה','פו ','רמן','נודלס','מרק עוף','מרק בצל',"גספצ'ו",'מרק ירקות','מרק עדשים','מרק שעועית'],
    'salads':   ['סלט','חסה','קפרזה','טבולה','כוסמת','קינואה','ירקות טריים','סלט ירק','סלט עגבניות','סלט חצילים','סלט גזר','וואלדורף'],
    'veggies':  ['ירקות','חציל','פטרייה','פטריות','קישוא','דלעת','שעועית','עדשים','תרד','ברוקולי','כרובית','אספרגוס','טופו','תפוח אדמה','פטטה','בטטה','גזר','כרוב','בצל','שום צלוי','ירקות קלויים','ירקות מוקפצים','ציד',"צ'ילי ירקות"],
    'hosting':  ['קנפה','ברוסקטה','ממרח','דיפ','פינגר','מזנון','נגיסים','לחם שום','גמבה','טפס','חומוס','טחינה','בבגנוש','גואקמולה','פסטו','ריקוטה'],
    'sweet':    ['עוגה','מאפין','בראוניז','עוגיות','רולד','חלה','קאפקייק','טארט מתוק','קינמון','סקונס',"שוקולד צ'יפס",'עוגת גבינה','עוגת שמרים','רוגלח','עלי בצק'],
    'desserts': ['קינוח','גלידה','מוס','פנקוטה','טירמיסו','קרם ברולה','פאי','פודינג','סורבה','קרפ','וופל','פרפה','חלבה',"מוצ'י",'טרופל','פרלין','שוקולד פונדו'],
}

def auto_category(title, text):
    t = title.lower()
    if re.search('עוף|פרגית|הודו|ביריאני|טיקה', t): return 'chicken'
    if re.search('דג|סלמון|טונה|שרימפס|פירות ים', t): return 'fish'
    if re.search('פסטה|ספגטי|ריזוטו|קוסקוס|לזניה|אורז', t): return 'pasta'
    if re.search('מרק|ציר|שקשוקה', t): return 'soups'
    if re.search('סלט', t): return 'salads'
    if re.search('קינוח|גלידה|מוס|טירמיסו|סורבה', t): return 'desserts'
    if re.search('עוגה|עוגיות|מאפין|בראוניז|קאפקייק', t): return 'sweet'
    if re.search('לחם|פיצה|פוקצ|בורקס|קיש|בייגלה|פיתה|מאפה מלוח|כריך|סנדוויץ', t): return 'savory'
    if re.search('ממרח|דיפ|חומוס|טחינה|בבגנוש|גואקמולה', t): return 'hosting'
    if re.search('קבב|סטייק|בשר|שניצל|המבורגר|קציצ|אסאדו', t): return 'meat'
    if re.search('ירקות|חציל|פטרייה|קישוא|בטטה|כרובית|ברוקולי', t): return 'veggies'
    full = (title + ' ' + text[:400]).lower()
    order = ['chicken','meat','fish','pasta','soups','salads','veggies','hosting','desserts','sweet','savory']
    for cat in order:
        for kw in KW[cat]:
            if kw.lower() in full:
                return cat
    return 'other'

# ── recipe parser ─────────────────────────────────────────────────────────────

ING_KW  = re.compile(r'^(מצרכים|רכיבים|חומרים|מרכיבים|חומרי\s+גלם|מה\s+צריך|נדרש|לבצק|למלית|לרוטב|לציפוי|לקישוט|לגנאש|לקרם|לסירופ|ingredients?)(\s|[:\-–—(]|$)', re.IGNORECASE)
STEP_KW = re.compile(r'^(הוראות(\s+הכנה)?|אופן\s+ה?הכנה|הכנה|שלבי(\s+הכנה)?|הוראות\s+הביצוע|דרך\s+ה?הכנה|שיטת\s+הכנה|ביצוע|הכנת|הוראות|preparation|instructions?|method|directions?)(\s|[:\-–—(]|$)', re.IGNORECASE)

def is_ing_header(l):
    return bool(ING_KW.match(l)) and len(l) < 60

def is_step_header(l):
    return bool(STEP_KW.match(l)) and len(l) < 60

def parse_recipe(text):
    res = {'title': '', 'ingredients': [], 'steps': [], 'notes': ''}
    if not text or not text.strip():
        return res
    lines = [l.strip() for l in text.replace('\r\n', '\n').split('\n')]
    title = ''
    title_idx = -1
    ing_start = ing_end = step_start = -1
    step_end = len(lines)

    for i, l in enumerate(lines):
        if not l:
            continue
        if not title and ing_start == -1 and step_start == -1:
            if not is_ing_header(l) and not is_step_header(l):
                title = l
                title_idx = i
                continue
        if is_ing_header(l):
            if ing_start == -1:
                ing_start = i + 1
            continue
        if is_step_header(l):
            if ing_start != -1 and ing_end == -1:
                ing_end = i
            step_start = i + 1

    if ing_start != -1 and ing_end == -1:
        ing_end = (step_start - 1) if step_start != -1 else len(lines)

    res['title'] = title

    if ing_start != -1:
        for i in range(ing_start, ing_end):
            r = lines[i]
            if not r:
                continue
            c = re.sub(r'^[-•*–·‐]+\s*', '', r)
            c = re.sub(r'^\d+[\.\)]\s*', '', c).strip()
            if c:
                res['ingredients'].append(c)

    if step_start != -1:
        buf = ''
        def flush():
            nonlocal buf
            t = buf.strip().rstrip('.')
            if len(t) > 2:
                res['steps'].append(t)
            buf = ''

        for i in range(step_start, step_end):
            r = lines[i]
            if not r:
                flush()
                continue
            if re.match(r'^\d+[\.\)]\s+', r):
                flush()
                buf = re.sub(r'^\d+[\.\)]\s+', '', r).rstrip('.')
                flush()
            elif re.match(r'^[-•*–·‐]\s+', r):
                flush()
                buf = re.sub(r'^[-•*–·‐]\s+', '', r).rstrip('.')
                flush()
            else:
                buf += (' ' if buf else '') + r
                if r.endswith('.'):
                    flush()
        flush()

        # split steps on sentence boundaries
        if res['steps']:
            split_steps = []
            for step in res['steps']:
                parts = re.split(r'\.(?=\s*[א-תA-Za-z])', step)
                for p in parts:
                    t = p.strip().rstrip('.')
                    if len(t) > 3:
                        split_steps.append(t)
            if split_steps:
                res['steps'] = split_steps

    # notes: text between title and first section header
    note_start = (title_idx + 1) if title_idx != -1 else 0
    note_end = (ing_start - 1) if ing_start != -1 else ((step_start - 1) if step_start != -1 else len(lines))
    note_lines = [lines[i] for i in range(note_start, note_end) if lines[i]]
    res['notes'] = '\n'.join(note_lines).strip()

    return res

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    src = '/Users/yaelmargolin/Documents/private_notes/notes-recipes.json'
    with open(src, encoding='utf-8') as f:
        data = json.load(f)

    base = int(time.time() * 1000)
    recipes = []

    for i, note in enumerate(data['notes']):
        raw_body = note.get('body', '')
        clean = strip_anote_markup(raw_body)

        # extract first URL
        url_match = re.search(r'https?://[^\s<\n]+', raw_body)
        url = ''
        if url_match:
            url = re.sub(r'[.,;:!?)]+$', '', url_match.group(0))

        # title
        title = clean_import_title(note.get('title', ''))
        if not title:
            for line in clean.split('\n'):
                l = line.strip()
                if not l or re.match(r'^https?://', l):
                    continue
                candidate = clean_import_title(l) or l
                if len(candidate) > 2:
                    title = candidate
                    break

        title = title or 'מתכון ללא שם'

        # filter: strip URLs and check if there's real content
        text_no_urls = re.sub(r'https?://[^\s]+', '', clean)
        text_no_urls = re.sub(r'\s+', ' ', text_no_urls).strip()
        if len(text_no_urls) < 30:
            continue

        # cleaned text for parsing (remove URLs)
        cleaned_text = re.sub(r'https?://[^\s\n]+', '', clean)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()

        parsed = parse_recipe(cleaned_text)
        parsed_title_clean = clean_import_title(parsed['title'])
        final_title = title if title != 'מתכון ללא שם' else (parsed_title_clean or 'מתכון ללא שם')

        cat = auto_category(final_title, cleaned_text)

        recipes.append({
            'id':          base + i,
            'noteId':      note['id'],
            'title':       final_title,
            'category':    cat,
            'ingredients': parsed['ingredients'],
            'steps':       parsed['steps'],
            'notes':       parsed['notes'],
            'url':         url,
            'createdAt':   base,
        })

    with open('aNote_App/recipes-data.json', 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, separators=(',', ':'))

    print(f'Done: {len(recipes)} recipes written to aNote_App/recipes-data.json')

    # category breakdown
    from collections import Counter
    cats = Counter(r['category'] for r in recipes)
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f'  {cat}: {count}')

if __name__ == '__main__':
    main()
