const { createClerkClient } = require('@clerk/backend');

let _clerk = null;
function getClerk() {
  if (!_clerk) _clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY });
  return _clerk;
}

async function getAuthUserId(req) {
  const token = (req.headers.authorization || '').replace('Bearer ', '').trim();
  if (!token) return null;
  try {
    const payload = await getClerk().verifyToken(token);
    return payload.sub;
  } catch (e) {
    console.error('Auth token error:', e.message);
    return null;
  }
}

module.exports = { getAuthUserId };
