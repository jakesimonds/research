# Quick Answers to Your Questions

## Q1: Can we put a public key in a user's PDS?

**YES.** As of June 2025, you can add up to 10 custom verification methods to a user's DID document.

**Example fragment:** `#aztec_verification`

**View real example:** https://plc.directory/did:plc:5eoo6tyoqrucebr43ws4zoff

---

## Q2: Is there a keypair pattern (public in PDS, private on server)?

**YES.** This is the **exact pattern labeler services already use**:

- Public key in DID as `#atproto_label`
- Private key held server-side
- Labels cryptographically signed

**Example labeler DID:** https://plc.directory/did:plc:4wgmwsq4t3tg55ffl3r7ocec

---

## Q3: Can labeler find public keys? Is it needle in haystack or elegant?

**NEEDLE IN HAYSTACK.**

**The Problem:**
- No server-side filtering by DID properties
- Cannot query "all DIDs with custom key X"
- Must consume entire firehose: 1000+ events/sec
- Developer quote: "6TB in March, >99% ignored"

**The Solution:**
1. Don't search for keys
2. Maintain your own database of verified DIDs
3. Use **Jetstream** to filter for THOSE specific DIDs
4. Reduces bandwidth by >99%

**Code pattern:**
```javascript
// After user validates, record their DID
await db.verifiedUsers.insert({ did: userDID });

// Subscribe to Jetstream for ONLY those DIDs
const verifiedDIDs = await db.verifiedUsers.getAll();
jetstream.subscribe({ dids: verifiedDIDs }, handleEvent);
```

---

## Q4: Did Paul Frazee say something about labelers being misused?

**YES.** There have been controversies:

**Real incidents:**
1. **Jesse Singal Watch** - Tracked followers, applied warning badges, shut down
2. **Follow Tracker** - Operator: "some of you can't be trusted to use this information reasonably"
3. **Private School Labeler** - Tagged people without consent

**Leadership issues:**
- **"Waffles" incident (Oct 2025)**: CEO Jay Graber mocked moderation concerns
- **Slow response to racist usernames (July 2023)**: Led to user "posting strike"

**BUT:**
- Bluesky updated Community Guidelines to prohibit label abuse
- **Verification labels are explicitly supported and legitimate**
- Just be transparent and provide appeals process

---

## Q5: Is your Aztec use case feasible?

**✅ YES, FULLY SUPPORTED.**

**Architecture that works:**

```
User → Aztec validation → Generate ZK proof
    ↓
Validation server verifies proof
    ↓
Generate keypair (k256/p256):
    • Public key → User's DID #aztec_verification
    • Private key → HSM on validation server
    ↓
Record DID in verified users database
    ↓
Labeler monitors via Jetstream (DID filter)
    ↓
Apply "aztec-verified" label
    ↓
Badge appears on user's profile
```

**Advantages:**
- Cryptographically sound
- Privacy preserving (only public key revealed, not proof)
- Standard ATProto pattern
- Proven at scale (5.5M labels in 2024)

**Challenges:**
- Must maintain your own index of verified users
- Can't discover existing verified users by scanning
- Need clear UX for multi-step flow
- HSM recommended for private key storage

---

## Key Links

**Specs:**
- DID Spec: https://atproto.com/specs/did
- Labels: https://atproto.com/specs/label
- Jetstream: https://docs.bsky.app/blog/jetstream

**Examples:**
- Multiple keys DID: https://plc.directory/did:plc:5eoo6tyoqrucebr43ws4zoff
- Labeler DID: https://plc.directory/did:plc:4wgmwsq4t3tg55ffl3r7ocec

**Tools:**
- Self-labeler: https://github.com/snarfed/self-labeler
- ATProto SDK (Python): https://github.com/MarshalX/atproto

**Discussions:**
- Custom keys (June 2025): https://github.com/bluesky-social/atproto/discussions/3928
- Firehose filtering: https://github.com/bluesky-social/atproto/discussions/2418
- Label abuse: https://github.com/bluesky-social/proposals/issues/19

---

**Research Date:** 2025-11-12
**Status:** ✅ Your use case is feasible and follows established patterns
