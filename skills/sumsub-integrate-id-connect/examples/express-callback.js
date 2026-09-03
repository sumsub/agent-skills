// Self-contained Express server that drives the full Sumsub ID Connect flow:
//   Stage 2: OIDC code -> access_token  (client_secret_basic, id.sumsub.com/api/snsId/oauth/token)
//   Stage 3: access_token -> share token (App Token + HMAC)
//     If sharingAllowed=false, Stage 3b mints a shareLink and redirects the
//     user; on consent callback we retry Stage 3a.
//   Stage 4: reuse/preview -> reuse/commit -> applicant materialised in your workspace
//
// Pairs with examples/oidc-redirect.html served from /public.
//
// Run:
//   npm install express
//   SUMSUB_APP_TOKEN=sbx:... SUMSUB_SECRET_KEY=... \
//     SUMSUB_CLIENT_ID=<your-clientId> \
//     SUMSUB_OIDC_CLIENT_SECRET=<your-oidc-client-secret> \
//     SUMSUB_LEVEL=<level-name> \
//     node express-callback.js
//
// package.json needs `"type": "module"` for the ESM imports below.

import express from 'express';
import crypto  from 'node:crypto';
import path    from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const PORT          = Number(process.env.PORT || 3000);
const CLIENT_ID     = process.env.SUMSUB_CLIENT_ID;
const CLIENT_SECRET = process.env.SUMSUB_OIDC_CLIENT_SECRET;   // Stage 2 code->token (server-side only)
const LEVEL_NAME    = process.env.SUMSUB_LEVEL;
// PUBLIC_BASE_URL overrides ORIGIN when running behind a TLS proxy or custom
// domain — the browser's redirect_uri (window.location.origin) and the
// server-side shareLink redirectUri must agree byte-for-byte, which means
// they must derive from the SAME public URL.
const ORIGIN       = process.env.PUBLIC_BASE_URL || `http://localhost:${PORT}`;
const SHARE_RETURN = `${ORIGIN}/share-complete`;   // must be in OIDC client redirect_uri allowlist
const API_BASE     = 'https://api.sumsub.com';
const ID_BASE      = 'https://id.sumsub.com';

for (const k of ['SUMSUB_APP_TOKEN', 'SUMSUB_SECRET_KEY', 'SUMSUB_CLIENT_ID', 'SUMSUB_OIDC_CLIENT_SECRET', 'SUMSUB_LEVEL']) {
  if (!process.env[k]) { console.error(`missing env: ${k}`); process.exit(1); }
}

// In-memory store keeping access_token alive between the two browser redirects
// (Stage 3b mint shareLink -> user consents -> /share-complete). Dies on
// restart; for prod use a real session store (Redis, encrypted cookie, etc).
const pendingShare = new Map();

// --- HMAC-signed request helper (Sumsub App-Token auth) ----------------------

async function sumsubHmac(method, pathQ, body, extraHeaders = {}) {
  const bodyStr = body ? JSON.stringify(body) : '';
  const ts = Math.floor(Date.now() / 1000);
  const sig = crypto.createHmac('sha256', process.env.SUMSUB_SECRET_KEY)
    .update(`${ts}${method}${pathQ}${bodyStr}`).digest('hex');
  const headers = {
    'X-App-Token':        process.env.SUMSUB_APP_TOKEN,
    'X-App-Access-Ts':    String(ts),
    'X-App-Access-Sig':   sig,
    'X-Agent-Source':     'sumsub-skills',
    'X-Agent-Source-Ver': '1.4.1',
    Accept:               'application/json',
    ...extraHeaders,
  };
  if (bodyStr) headers['Content-Type'] = 'application/json';
  const r = await fetch(`${API_BASE}${pathQ}`, { method, headers, body: bodyStr || undefined });
  const text = await r.text();
  let json; try { json = JSON.parse(text); } catch { json = { raw: text }; }
  if (!r.ok) {
    const err = new Error(json.description || json.message || `Sumsub ${pathQ} failed: ${r.status}`);
    err.status = r.status; err.body = json;
    throw err;
  }
  return json;
}

// --- Stage 2/3/4 wrappers ----------------------------------------------------

// Stage 2 — exchange the authorization code on the OIDC token endpoint
// (client_secret_basic). The code came from the browser authorize flow, so its
// counterpart is this endpoint, not the HMAC route. redirect_uri MUST equal the
// value used at authorize in Stage 1 byte-for-byte — here `${ORIGIN}/`, the same
// value oidc-redirect.html builds from `window.location.origin + '/'`.
async function exchangeCodeForAccessToken(code, codeVerifier) {
  const basic = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');
  const form = new URLSearchParams({
    grant_type:    'authorization_code',
    code,
    redirect_uri:  `${ORIGIN}/`,
    code_verifier: codeVerifier,
  });
  const r = await fetch(`${ID_BASE}/api/snsId/oauth/token`, {
    method:  'POST',
    headers: { Authorization: `Basic ${basic}`, 'Content-Type': 'application/x-www-form-urlencoded', Accept: 'application/json' },
    body:    form.toString(),
  });
  const text = await r.text();
  let json; try { json = JSON.parse(text); } catch { json = { raw: text }; }
  if (!r.ok) throw Object.assign(new Error(json.error_description || json.error || `token endpoint ${r.status}`), { status: r.status, body: json });
  return json;
}

const mintShareToken = (accessToken) =>
  sumsubHmac('POST', '/resources/accessTokens/sumsubIdShareToken', {
    sumsubIdConnectToken: accessToken,
    forClientId:          CLIENT_ID,
    ttlInSecs:            1800,
  });

const mintShareLink = (accessToken, state) =>
  sumsubHmac('POST', '/resources/snsId/oauth/shareLink', {
    redirectUri: SHARE_RETURN,
    forClientId: CLIENT_ID,
    displayMode: 'page',
    state,
  }, { Authorization: `Bearer ${accessToken}` });

async function reuseApplicant(shareToken, userId) {
  const qs = `?shareToken=${encodeURIComponent(shareToken)}` +
             `&levelName=${encodeURIComponent(LEVEL_NAME)}` +
             `&userId=${encodeURIComponent(userId)}`;
  const preview   = await sumsubHmac('GET',  `/resources/api/reusableIdentity/reuse/preview${qs}`);
  const applicant = await sumsubHmac('POST', `/resources/api/reusableIdentity/reuse${qs}`);
  return { preview, applicant };
}

// --- HTTP wiring -------------------------------------------------------------

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public'))); // serve oidc-redirect.html here

// Frontend reads config from here so AUTH_URL / CLIENT_ID aren't duplicated.
app.get('/config', (_req, res) => {
  res.json({
    authUrl:   `${ID_BASE}/api/snsId/oauth/authorize`,
    clientId:  CLIENT_ID,
    scopes:    'openid share name',
    levelName: LEVEL_NAME,
  });
});

// Frontend POSTs { code, codeVerifier } here after the authorize callback. We
// run Stages 2-4 inline; if Stage 3 needs consent, we return
// { needsConsent, shareUrl } and the frontend redirects.
app.post('/api/sumsub/id-connect/exchange', async (req, res) => {
  const { code, codeVerifier } = req.body || {};
  if (!code || !codeVerifier) return res.status(400).json({ error: 'code, codeVerifier required' });
  const userId = `user-${crypto.randomUUID()}`;
  try {
    const { access_token } = await exchangeCodeForAccessToken(code, codeVerifier);
    const share = await mintShareToken(access_token);

    if (!share.sharingAllowed) {
      const state = crypto.randomBytes(16).toString('hex');
      pendingShare.set(state, { accessToken: access_token, userId, createdAt: Date.now() });
      const { link } = await mintShareLink(access_token, state);
      return res.json({ needsConsent: true, shareUrl: link, state });
    }

    const { applicant } = await reuseApplicant(share.token, userId);
    res.json({ ok: true, userId, applicantId: applicant.id, reviewStatus: applicant.review?.reviewStatus });
  } catch (e) {
    res.status(e.status || 500).json({ error: e.message, body: e.body });
  }
});

// Stage 3b callback — Sumsub redirects here after the user grants sharing
// consent. We look up the access_token by `state`, retry share token (now
// sharingAllowed=true), and run Stage 4. Renders an HTML result page.
app.get('/share-complete', async (req, res) => {
  // Sumsub redirects here as ?token=<JWT>. The state is INSIDE the JWT payload,
  // NOT a top-level ?state= query param. Decode it to correlate. (Prod: verify
  // the JWT signature against the jwks_uri before trusting any claim.)
  const claims = decodeJwtPayload(String(req.query.token || ''));
  const state  = String(claims.state || req.query.state || '');
  const session = pendingShare.get(state);
  if (!session) return renderResult(res, { error: 'unknown or expired state', state }, false);
  pendingShare.delete(state);
  try {
    const share = await mintShareToken(session.accessToken);
    if (!share.sharingAllowed) return renderResult(res, { error: 'share still not allowed after consent', share }, false);
    const { applicant } = await reuseApplicant(share.token, session.userId);
    renderResult(res, { ok: true, userId: session.userId, applicantId: applicant.id, reviewStatus: applicant.review?.reviewStatus });
  } catch (e) {
    renderResult(res, { error: e.message, body: e.body }, false);
  }
});

// Decode (NOT verify) a JWT payload — prod must verify the signature against
// the id.sumsub.com jwks_uri (use `jose`) before trusting any claim.
function decodeJwtPayload(jwt) {
  try {
    const part = jwt.split('.')[1];
    if (!part) return {};
    return JSON.parse(Buffer.from(part.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8'));
  } catch { return {}; }
}

const htmlEscape = (s) => String(s).replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

function renderResult(res, payload, ok = true) {
  const colour = ok ? '#047857' : '#b91c1c';
  // payload can include user-controllable fields (e.g. req.query.state) — escape
  // before injecting into HTML, otherwise '</pre><script>...' breaks out.
  const safe = htmlEscape(JSON.stringify(payload, null, 2));
  res.set('Content-Type', 'text/html').send(`<!doctype html><html><head>
<meta charset="utf-8"/><title>Result</title>
<style>body{font-family:system-ui;max-width:640px;margin:4rem auto;padding:0 1rem}
pre{background:#f3f4f6;padding:1rem;border-radius:6px;white-space:pre-wrap;word-break:break-word;color:${colour}}</style>
</head><body><h1>${ok ? 'Done' : 'Failed'}</h1>
<pre>${safe}</pre>
<a href="/">back</a></body></html>`);
}

app.listen(PORT, () => {
  console.log(`id-connect-demo on ${ORIGIN}`);
  console.log(`  OIDC client_id   ${CLIENT_ID}`);
  console.log(`  Level for reuse  ${LEVEL_NAME}`);
  console.log(`  Allowlist these redirect_uris on the OIDC client:`);
  console.log(`    ${ORIGIN}/         (authorize callback)`);
  console.log(`    ${SHARE_RETURN}    (shareLink callback)`);
});
