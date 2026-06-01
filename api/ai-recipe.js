const Anthropic = require('@anthropic-ai/sdk');
const { setCORS } = require('./_db');
const { getAuthUserId } = require('./_auth');

function getYouTubeVideoId(url) {
  try {
    const u = new URL(url);
    if (u.hostname.includes('youtube.com')) return u.searchParams.get('v');
    if (u.hostname === 'youtu.be') return u.pathname.slice(1).split('?')[0];
    return null;
  } catch { return null; }
}

async function fetchYouTubeTranscript(videoId) {
  const pageRes = await fetch(`https://www.youtube.com/watch?v=${videoId}`, {
    headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' }
  });
  const html = await pageRes.text();

  const match = html.match(/"captionTracks":\s*(\[[\s\S]*?\])/);
  if (!match) return null;

  let tracks;
  try { tracks = JSON.parse(match[1]); } catch { return null; }
  if (!tracks.length) return null;

  const track = tracks.find(t => t.languageCode === 'he' || t.languageCode === 'iw')
    || tracks.find(t => t.kind === 'asr')
    || tracks[0];
  if (!track?.baseUrl) return null;

  const xmlRes = await fetch(track.baseUrl);
  const xml = await xmlRes.text();

  const lines = Array.from(xml.matchAll(/<text[^>]*>([\s\S]*?)<\/text>/g))
    .map(m => m[1]
      .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
      .replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/<[^>]+>/g, ''))
    .filter(t => t.trim());

  return lines.join(' ').trim() || null;
}

async function fetchWebpageText(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; RecipeBot/1.0)' },
    signal: AbortSignal.timeout(12000)
  });
  const html = await res.text();
  const text = html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<nav[\s\S]*?<\/nav>/gi, '')
    .replace(/<footer[\s\S]*?<\/footer>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  return text.slice(0, 14000);
}

module.exports = async function handler(req, res) {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });

  const userId = getAuthUserId(req);
  if (!userId) return res.status(401).json({ error: 'לא מחוברת. כנסי לחשבון תחילה.' });

  const { url } = req.body || {};
  if (!url) return res.status(400).json({ error: 'missing url' });

  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(503).json({ error: 'מפתח Anthropic API חסר בהגדרות השרת' });
  }

  try {
    let content;
    const videoId = getYouTubeVideoId(url);

    if (videoId) {
      content = await fetchYouTubeTranscript(videoId);
      if (!content) {
        return res.status(422).json({ error: 'לא נמצאו כתוביות לסרטון זה. נסי סרטון עם כתוביות מופעלות.' });
      }
    } else {
      content = await fetchWebpageText(url);
      if (!content || content.length < 50) {
        return res.status(422).json({ error: 'לא ניתן לטעון את הדף. נסי להדביק את הטקסט ידנית.' });
      }
    }

    const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

    const response = await client.messages.create({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 2048,
      system: `אתה עוזר שמחלץ מתכוני בישול. קרא את התוכן ומצא את המתכון.
החזר JSON תקין בלבד, ללא markdown, ללא הסבר נוסף:
{
  "title": "שם המרשם בעברית",
  "ingredients": ["כמות + מרכיב", "..."],
  "steps": ["שלב מפורט", "..."],
  "notes": "טיפים והערות (או מחרוזת ריקה)"
}
תרגם לעברית אם הטקסט באנגלית. כלול כמויות מדויקות במצרכים. כתוב שלבים ברורים.`,
      messages: [{ role: 'user', content: `חלץ מתכון מהתוכן הבא:\n\n${content}` }]
    });

    let recipe;
    try {
      const raw = response.content[0].text.trim().replace(/^```json?\n?/, '').replace(/\n?```$/, '');
      recipe = JSON.parse(raw);
    } catch {
      return res.status(500).json({ error: 'שגיאה בפענוח תשובת AI. נסי שוב.' });
    }

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
