const { GoogleGenerativeAI } = require('@google/generative-ai');
const { setCORS } = require('./_db');

function getUrlType(url) {
  try {
    const u = new URL(url);
    if (u.hostname.includes('youtube.com') || u.hostname === 'youtu.be') return 'youtube';
    if (u.hostname.includes('instagram.com')) return 'instagram';
    return 'webpage';
  } catch { return 'webpage'; }
}

async function fetchPageMeta(url) {
  const res = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
      'Accept-Language': 'he-IL,he;q=0.9,en;q=0.8',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    },
    signal: AbortSignal.timeout(12000)
  });
  const html = await res.text();

  // Extract og:description (Instagram caption lives here)
  const ogDesc = html.match(/<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']{10,})["']/i)
    || html.match(/<meta[^>]+content=["']([^"']{10,})["'][^>]+property=["']og:description["']/i);
  const ogTitle = html.match(/<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']+)["']/i)
    || html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:title["']/i);

  const description = ogDesc ? ogDesc[1].replace(/&amp;/g, '&').replace(/&#39;/g, "'").replace(/&quot;/g, '"').trim() : '';
  const title = ogTitle ? ogTitle[1].replace(/&amp;/g, '&').replace(/&#39;/g, "'").trim() : '';

  // Also grab visible text
  const bodyText = html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 8000);

  return { description, title, bodyText };
}

const PROMPT = `אתה עוזר שמחלץ מתכוני בישול. מצא את המתכון וחלץ אותו.
החזר JSON תקין בלבד, ללא markdown, ללא הסבר נוסף:
{
  "title": "שם המרשם בעברית",
  "ingredients": ["כמות + מרכיב", "..."],
  "steps": ["שלב מפורט", "..."],
  "notes": "טיפים והערות (או מחרוזת ריקה)"
}
תרגם לעברית אם הטקסט באנגלית. כלול כמויות מדויקות במצרכים. כתוב שלבים ברורים.`;

module.exports = async function handler(req, res) {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });

  const { url } = req.body || {};
  if (!url) return res.status(400).json({ error: 'missing url' });

  const apiKey = process.env.MATKONIM_AI || process.env.GEMINI_API_KEY;
  if (!apiKey) return res.status(503).json({ error: 'מפתח Gemini API חסר בהגדרות השרת' });

  try {
    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash-8b' });

    const urlType = getUrlType(url);
    let contentParts;

    if (urlType === 'youtube') {
      contentParts = [
        { fileData: { mimeType: 'video/mp4', fileUri: url } },
        { text: PROMPT }
      ];
    } else {
      // Instagram + web pages: extract text/caption from the page
      const { description, title, bodyText } = await fetchPageMeta(url);

      const combined = [
        title ? `כותרת: ${title}` : '',
        description ? `תיאור/כיתוב:\n${description}` : '',
        bodyText ? `תוכן הדף:\n${bodyText}` : ''
      ].filter(Boolean).join('\n\n');

      if (!combined || combined.length < 30) {
        return res.status(422).json({ error: 'לא ניתן לקרוא את הדף. אם זה אינסטגרם — הוא דורש כניסה. נסי להדביק את הטקסט ידנית.' });
      }

      contentParts = [{ text: PROMPT + '\n\n' + combined }];
    }

    const result = await model.generateContent(contentParts);
    const raw = result.response.text().trim().replace(/^```json?\n?/, '').replace(/\n?```$/, '');

    let recipe;
    try { recipe = JSON.parse(raw); }
    catch { return res.status(500).json({ error: 'שגיאה בפענוח תשובת AI. נסי שוב.' }); }

    const ingredients = Array.isArray(recipe.ingredients) ? recipe.ingredients : [];
    const steps = Array.isArray(recipe.steps) ? recipe.steps : [];
    const notes = recipe.notes || '';

    const text = [
      recipe.title || '',
      '',
      'מצרכים:',
      ...ingredients.map(i => `- ${i}`),
      '',
      'אופן ההכנה:',
      ...steps.map((s, i) => `${i + 1}. ${s}`),
      ...(notes ? ['', notes] : [])
    ].join('\n');

    return res.status(200).json({ title: recipe.title || '', ingredients, steps, notes, text });

  } catch (e) {
    console.error('ai-recipe error:', e);
    return res.status(500).json({ error: 'שגיאה בניתוח: ' + (e.message || 'שגיאה לא ידועה') });
  }
};
