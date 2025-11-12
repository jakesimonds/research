# Aztec Crypto + ATProto Keypair Validation - Feasibility Study

**Research Date:** 2025-11-12

## TL;DR - Is This Possible?

### ✅ YES, Your Use Case is FULLY SUPPORTED

Your proposed architecture of Aztec crypto validation + ATProto keypair + Bluesky labeler badges is **feasible and follows established patterns**.

---

## Your Proposed Flow

```
User → Web/App Flow → Aztec ZK Proof Generation
    ↓
Generate Smart Contract (proves something)
    ↓
Generate Keypair:
    • Public key → User's PDS/DID (visible to everyone)
    • Private key → Your validation server (secure storage)
    ↓
Labeler Service:
    • Scans firehose
    • Finds public key
    • Validates cryptographically
    • Applies "verified" badge
```

## What We Found

### 1. ✅ Public Keys in DIDs: FULLY SUPPORTED

**As of June 2025**, ATProto's PLC Directory allows custom verification keys:

- **Up to 10 verification methods** per DID
- **Any key type**: ed25519, p256, k256, etc.
- **Custom purposes**: Beyond just account signing
- **Example fragment**: `#aztec_verification`

**Real Example DID with multiple keys:**
- `did:plc:5eoo6tyoqrucebr43ws4zoff`
- Has both `#atproto` (standard) and `#ed25519test` (custom)
- View at: https://plc.directory/did:plc:5eoo6tyoqrucebr43ws4zoff

### 2. ✅ Split Keypair Pattern: ESTABLISHED

Labeler services **already use this exact pattern**:

- **Public key** in DID as `#atproto_label`
- **Private key** held server-side
- Labels cryptographically signed

**Example:** `did:plc:4wgmwsq4t3tg55ffl3r7ocec` (self-labeler.snarfed.org)

### 3. ❌ Finding Keys in Firehose: NOT ELEGANT

**The "needle in haystack" problem is REAL:**

- NO server-side filtering by DID properties
- Cannot query "find all users with #aztec_verification key"
- Must consume entire firehose (1000+ events/sec)
- One developer: "6TB of data in March, >99% ignored"

**The Solution: Don't Search, Track**

Instead of scanning for keys, maintain your own index:

```
User completes validation
    ↓
Your service records their DID
    ↓
Use Jetstream to filter for THOSE specific DIDs
    ↓
Reduces firehose by >99%
```

### 4. ⚠️ Labeler Concerns: YES, But Verification is Legitimate

**Paul Frazee / team concerns found:**
- Labelers being misused for harassment (Jesse Singal Watch, etc.)
- Community guidelines updated to prohibit label abuse
- Leadership controversies around moderation

**BUT: Verification labels are explicitly supported**
- Ozone moderation app supports verification
- This is an intended use case
- Just be transparent and provide appeals process

---

## Recommended Architecture

### Phase 1: Validation & Key Management

```javascript
// User completes Aztec validation
const proof = await generateAztecProof(userData);

// Verify proof
if (!verifyProof(proof)) throw new Error('Invalid proof');

// Generate keypair (k256 recommended for crypto compatibility)
const keypair = generateK256Keypair();

// Add public key to user's DID
await updateUserDID(userDID, {
  verificationMethod: {
    id: `${userDID}#aztec_verification`,
    type: "Multikey",
    controller: userDID,
    publicKeyMultibase: encodeDIDKey(keypair.publicKey)
  }
});

// Store private key securely (HSM recommended)
await storePrivateKey(keypair.privateKey, userDID);

// Index this DID as verified
await db.verifiedUsers.insert({ did: userDID, timestamp: now });
```

### Phase 2: Labeler Service

```javascript
// Subscribe to Jetstream with DID filter
const verifiedDIDs = await db.verifiedUsers.getAll();

jetstream.subscribe({
  dids: verifiedDIDs,
  collections: ['app.bsky.feed.post', 'app.bsky.actor.profile']
}, (event) => {
  // User with verification key had activity
  applyLabel({
    source: labelerDID,
    subject: event.did,
    value: 'aztec-verified',
    signature: signWithLabelerKey(labelData)
  });
});
```

### Phase 3: Display

- Badge appears in Bluesky UI
- Publicly verifiable via DID document
- Custom clients can query labels

---

## Key Advantages

1. **Cryptographically Sound**
   - Public key verifiable via DID
   - Labels signed by labeler
   - Chain of trust is clear

2. **Privacy Preserving**
   - Only public key is published
   - ZK proof details stay private
   - Verification fact is public, method is not

3. **Standard Pattern**
   - Uses established ATProto conventions
   - Not inventing new protocols
   - Proven at scale (5.5M labels in 2024)

4. **Decentralized**
   - No central authority needed
   - Anyone can verify the public key
   - Users can choose which labelers to trust

---

## Key Limitations

1. **No Discovery**
   - Cannot scan all DIDs to find custom keys
   - Must maintain your own database of verified users
   - Users must actively register with your service

2. **Firehose Efficiency**
   - Don't scan entire firehose (too expensive)
   - Use Jetstream with DID filtering
   - Build and maintain local index

3. **User Experience**
   - Multi-step process (validate → update DID → get labeled)
   - DID updates require user authorization
   - Need clear UX flow

4. **Key Management**
   - Private key security is critical
   - HSM recommended for production
   - Need rotation policy

---

## Implementation Roadmap

### Step 1: Prototype (1-2 weeks)
- Generate compatible keypairs (k256/p256)
- Test DID document updates
- Verify keys appear in PLC directory

### Step 2: Test Labeler (2-3 weeks)
- Deploy labeler using github.com/snarfed/self-labeler
- Configure custom label definitions
- Test label application and display

### Step 3: Validation Flow (3-4 weeks)
- Integrate Aztec proof verification
- Connect to DID update process
- Build user registration database
- Test end-to-end with test accounts

### Step 4: Production (ongoing)
- Deploy to production infrastructure
- Set up HSM for key storage
- Connect to Jetstream
- Monitor performance and costs

---

## Cost Estimates

**Infrastructure:**
- Validation server: $20-100/month (depending on scale)
- Database: $10-50/month
- HSM/KMS: $50-200/month (AWS KMS, Vault, etc.)
- Jetstream: Free (public instances) or self-hosted

**Bandwidth:**
- Jetstream (filtered): <100GB/month
- Full firehose (DON'T): 6TB+/month

**Total:** ~$100-400/month for production system

---

## Tech Stack Recommendations

**Validation Server:**
- Python or TypeScript
- ATProto SDK: `atproto` (Python) or `@atproto/*` (JS/TS)
- Database: PostgreSQL
- Key Storage: AWS KMS / HashiCorp Vault

**Labeler Service:**
- Framework: @skyware/labeler (TypeScript)
- Reference: github.com/snarfed/self-labeler
- Firehose: Jetstream subscription

**Cryptography:**
- noble-curves (JS) or cryptography (Python)
- k256 curve recommended for Aztec compatibility
- @atproto/crypto for did:key encoding

---

## Answers to Your Specific Questions

### Q: Can we put a public key in the PDS?

**A: YES.** As of June 2025, you can add up to 10 custom verification methods to any DID. The public key goes in the DID document (which is publicly resolvable), not directly "in the PDS" but associated with the user's identity.

### Q: Is there a keypair pattern (public in PDS, private on server)?

**A: YES.** This is the **exact pattern labeler services use**. They have `#atproto_label` key in their DID (public) and hold the private key server-side to sign labels.

### Q: Can labeler find the public key? Is it a needle in haystack?

**A: YES to needle in haystack, NO to elegant discovery.**

The firehose is extremely inefficient for discovery:
- 1000+ events/sec, growing exponentially
- No server-side filtering by DID properties
- Cannot query "all DIDs with custom key X"

**SOLUTION:** Don't search for keys. Instead:
1. Users register with your service during validation
2. You maintain database of verified DIDs
3. Use Jetstream to monitor ONLY those specific DIDs
4. This reduces bandwidth by >99%

### Q: Did Paul Frazee say something about labelers being misused?

**A: YES.** There have been labeler controversies:

1. **Harassment via Labelers**: Jesse Singal Watch, Follow Tracker, etc.
2. **Community Guidelines Updated**: Now prohibit using labels for harassment
3. **Leadership Controversies**: "Waffles" incident (Oct 2025) where CEO mocked moderation concerns

**BUT:** Verification labels are a legitimate, supported use case. Just be transparent and provide appeals.

---

## Bottom Line

Your Aztec crypto + ATProto keypair + labeler validation architecture is:

- ✅ **Technically feasible** (fully supported as of June 2025)
- ✅ **Follows established patterns** (labelers already work this way)
- ✅ **Cryptographically sound** (public key verification + signed labels)
- ✅ **Privacy preserving** (only public key revealed, not proof details)
- ⚠️ **Requires index maintenance** (can't discover via scanning)
- ⚠️ **Need clear UX** (multi-step process)
- ⚠️ **Be transparent** (labeler controversies are real)

**Recommended approach:**
1. Store public key in user's DID as `#aztec_verification`
2. Keep private key in HSM on validation server
3. Maintain database of verified DIDs
4. Use Jetstream to monitor those specific DIDs
5. Apply verification labels when users are active
6. Be transparent about your labeling criteria

---

## Resources

**Key Specs:**
- DID Spec: https://atproto.com/specs/did
- Labels: https://atproto.com/specs/label
- Cryptography: https://atproto.com/specs/cryptography

**Tools:**
- PLC Directory: https://plc.directory
- Jetstream: https://docs.bsky.app/blog/jetstream
- Self-labeler: https://github.com/snarfed/self-labeler
- ATProto SDK (Python): https://github.com/MarshalX/atproto

**Key Discussions:**
- Custom keys (June 2025): https://github.com/bluesky-social/atproto/discussions/3928
- Firehose filtering: https://github.com/bluesky-social/atproto/discussions/2418
- Label abuse prevention: https://github.com/bluesky-social/proposals/issues/19

**Example DIDs:**
- Multiple keys: https://plc.directory/did:plc:5eoo6tyoqrucebr43ws4zoff
- Labeler: https://plc.directory/did:plc:4wgmwsq4t3tg55ffl3r7ocec

---

**Full detailed research:** See `notes.md` for comprehensive technical findings
**Research date:** 2025-11-12
**Status:** ✅ Feasible and recommended
