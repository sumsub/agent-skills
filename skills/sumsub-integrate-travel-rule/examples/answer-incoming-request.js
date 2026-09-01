/**
 * Stage 5 — answering an incoming Travel Rule request.
 *
 * Two responses, in order, each skippable via its own flag. Response two on
 * its own returns 200 but leaves the exchange pinned at onHold forever, so the
 * ordering here is not stylistic.
 *
 * Budget: the counterparty's confirmation timeout can be as short as 10
 * seconds, and that covers webhook delivery plus both calls. Do the work on
 * the request path, not on a queue you drain every minute.
 */

const crypto = require('crypto');

const BASE = process.env.SUMSUB_BASE || 'https://api.sumsub.com';
const APP_TOKEN = process.env.SUMSUB_APP_TOKEN;
const SECRET = process.env.SUMSUB_SECRET_KEY;

function sign(method, pathWithQuery, body = '') {
  const ts = Math.floor(Date.now() / 1000);
  const sig = crypto
    .createHmac('sha256', SECRET)
    .update(ts + method.toUpperCase() + pathWithQuery + body)
    .digest('hex');
  return {
    'X-App-Token': APP_TOKEN,
    'X-App-Access-Ts': String(ts),
    'X-App-Access-Sig': sig,
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };
}

async function call(method, pathWithQuery, payload) {
  const body = payload === undefined ? '' : JSON.stringify(payload);
  const res = await fetch(BASE + pathWithQuery, {
    method,
    headers: sign(method, pathWithQuery, body),
    body: body || undefined,
  });
  if (!res.ok) throw new Error(`${method} ${pathWithQuery} -> ${res.status} ${await res.text()}`);
  return res.json();
}

const getTransaction = (txnId) => call('GET', `/resources/kyt/txns/${txnId}/one`);

/** Response one — is this wallet ours? Also unmasks the counterparty's data. */
const confirmAddress = (txnId, isOurs) =>
  call('POST', `/resources/kyt/txns/${txnId}/ownership/${isOurs ? 'confirmed' : 'unconfirmed'}`);

/** Response two — whose is it? Send applicantId, or the participant inline. */
const identifyUser = (txnId, owner) =>
  call('POST', `/resources/kyt/txns/${txnId}/travelRuleOwnership`, owner);

/**
 * Look the address up in your own systems.
 * Returning { ours: false } rejects the exchange — only do that when the
 * address genuinely is not yours. Rejecting to avoid the work stops your
 * user's transfer.
 */
async function resolveOwner(address /*, memo */) {
  // return { ours: true, applicantId: '...' }             // known applicant
  // return { ours: true, participant: { firstNameEn: ... } } // not a Sumsub applicant
  // return { ours: false }
  throw new Error('implement resolveOwner against your address book');
}

async function handleIncomingRequest(txnId) {
  let txn = await getTransaction(txnId);

  // Not for us to answer — we started this one.
  if (!txn.travelRuleInfo) return { skipped: 'not a Travel Rule transaction' };

  const address = txn.data?.applicant?.paymentMethod?.accountId;
  const memo = txn.data?.applicant?.paymentMethod?.memo;
  const owner = await resolveOwner(address, memo);

  // Response one — skip when already answered (automation, or a retry).
  if (txn.needMasking) {
    txn = await confirmAddress(txnId, owner.ours);
    if (!owner.ours) return { answered: 'unconfirmedOwnership' };
  }

  // Response two — required only in the strictest ownership validation mode.
  if (txn.travelRuleInfo?.needApplicantOwnershipConfirmation) {
    txn = await identifyUser(
      txnId,
      owner.applicantId
        ? { applicantId: owner.applicantId }
        : { applicantParticipant: owner.participant },
    );
  }

  return { answered: txn.travelRuleInfo?.status };
}

/**
 * Webhook receiver. Verify the signature against your webhook secret before
 * trusting the payload — omitted here for brevity, see
 * https://docs.sumsub.com/docs/verify-webhook-payload-signatures
 *
 * Ack fast and do the work inline: a 10-second budget does not survive a queue.
 * Deliveries are not guaranteed to be unique — make this idempotent, which the
 * two flags already give you for free.
 */
async function onWebhook(req, res) {
  // kytTxnId is Sumsub's transaction id — the one the API paths take.
  // kytDataTxnId is the txnId you supplied when the transaction was created.
  const { type, kytTxnId, kytDataTxnId } = req.body;
  if (type !== 'applicantKytTxnCreated' || !kytTxnId) return res.sendStatus(200);

  try {
    const result = await handleIncomingRequest(kytTxnId);
    console.log('travel rule answered', kytDataTxnId, result);
  } catch (err) {
    // Alert on this. Nothing re-delivers the request, and the counterparty is
    // holding a transfer while you are silent.
    console.error('travel rule answer failed', kytDataTxnId, err);
  }
  res.sendStatus(200);
}

module.exports = { handleIncomingRequest, onWebhook };
