const { createClerkClient } = require('@clerk/backend');

let _clerk = null;
function getClerk() {
  if (!_clerk) _clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY });
  return _clerk;
}

async function requireAuth(req, res) {
  const token = (req.headers.authorization || '').replace('Bearer ', '').trim();
  if (!token) {
    res.status(401).json({ error: 'unauthorized' });
    return null;
  }
  try {
    const payload = await getClerk().verifyToken(token);
    return payload.sub; // userId
  } catch (e) {
    res.status(401).json({ error: 'invalid token' });
    return null;
  }
}

module.exports = { requireAuth };
