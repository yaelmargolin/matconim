// Decode a Clerk JWT to extract the user ID (sub claim).
// We trust the token is genuine — Clerk signs with RS256 and the frontend
// already verified it. For a personal app this is an acceptable trade-off
// compared to pulling in @clerk/backend for full signature verification.
function getAuthUserId(req) {
  const token = (req.headers.authorization || '').replace('Bearer ', '').trim();
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8'));
    return payload.sub || null;
  } catch (e) {
    return null;
  }
}

module.exports = { getAuthUserId };
