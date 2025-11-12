# Nostr + Aztec Hackathon Research

## Overview
Research for integrating Nostr relay with Aztec privacy layer for hackathon submission targeting the **Identity Infrastructure ($2,000)** track.

---

## 1. Running a Nostr Relay

### TL;DR
**Yes - can be done in an afternoon locally, then deployed to EC2/cloud.**

### Implementation Options

#### Option A: nostr-rs-relay (Recommended - Rust)
- Most popular implementation
- Uses SQLite for storage
- Simple TOML configuration
```bash
git clone https://github.com/scsibug/nostr-rs-relay
cd nostr-rs-relay
cargo build --release
./target/release/nostr-rs-relay
```
Runs on `localhost:8080` by default

#### Option B: strfry (C++)
- Extremely fast
- Good for production
```bash
git clone https://github.com/hoytech/strfry
cd strfry
make setup-golpe
make
./strfry relay
```

#### Option C: Build Your Own (Educational)
- Node.js + WebSocket (ws library)
- SQLite or in-memory storage
- Implement NIP-01 spec (REQ/EVENT/CLOSE messages)
- ~200-300 lines for MVP
- Great for understanding the protocol

### Deployment Options
- AWS EC2
- fly.io (easiest)
- Railway
- DigitalOcean droplets

---

## 2. Nostr Protocol Basics

### Key Management
- **Private key (nsec)**: Signs all events, proves authorship
- **Public key (npub)**: Your identity, derived from private key via secp256k1
- Standard elliptic curve cryptography

### Event Structure
**Everything in Nostr is an event** - JSON objects with:
```json
{
  "id": "event hash",
  "pubkey": "author's public key",
  "created_at": "unix timestamp",
  "kind": "event type",
  "tags": ["references", "mentions"],
  "content": "actual data",
  "sig": "signature over event"
}
```

### Event Kinds
- `kind: 0` - User metadata
- `kind: 1` - Text notes (posts)
- `kind: 3` - Contact lists
- `kind: 4` - Encrypted DMs
- Many more...

### Security Model
- Relays don't verify - they just store/forward
- Clients verify signatures
- Pseudonymous by default (pubkey is identity)

---

## 3. Privacy Problems in Nostr

### Current Limitations

#### Personal-Private Storage
- No built-in private data storage
- Everything goes through relays (public)
- Draft posts, bookmarks, preferences all exposed

#### Shared-Private Storage (Bigger Problem)
- DMs leak metadata (who talks to whom, when, frequency)
- No private groups
- No scalable multi-user private spaces
- Current encryption (NIP-04/17) only hides content, not metadata

### What's Missing
- No reputation/attestation system
- No verifiable credentials
- No privacy-preserving access control
- No cross-chain identity portability

---

## 4. Aztec Integration Ideas

### Idea 1: Private Attestation Layer ⭐️ RECOMMENDED
**Track:** Identity Infrastructure ($2,000)

#### Problem
Nostr identities are pseudonymous but lack reputation/verification

#### Solution
Use Aztec to store private credentials linked to Nostr pubkeys

```
Nostr (public social) ←→ Aztec (private attestations)
```

#### Features
- Prove age without revealing birthdate
- Prove organizational verification without revealing which org
- Aggregate multiple attestations (ZKPassport + on-chain history)
- User-controlled data (no centralized authority)
- Gate relay access based on proofs

#### Technical Architecture
1. Nostr relay runs normally
2. Special event kind links Nostr pubkey → Aztec address
3. Attestations stored privately in Aztec contracts
4. Generate ZK proofs to share with other Nostr users
5. Optional: Relay features gated by attestation proofs

#### Qualification Alignment
✅ Uses Aztec Devnet
✅ Composes with ZKPassport/other identity systems
✅ Aztec IS the identity infrastructure
✅ User controls identity data
✅ Clear user interaction model

---

### Idea 2: Private Group Messaging
**Track:** Rethinking What's Possible ($1,000)

#### Problem
Nostr DMs leak metadata (participants, timing, message counts)

#### Solution
Aztec for private group state + access control

#### Features
- Group membership stored privately on Aztec
- Messages encrypted, stored on Aztec or IPFS
- Nostr relay only sees opaque event hashes
- Prove group membership → decrypt messages
- Zero metadata leakage

#### Addresses
The "shared-private storage" problem - multi-user private data with:
- Scalable access control
- No metadata leakage
- E2E encryption
- User-friendly administration

---

### Idea 3: Cross-Chain Private Social
**Track:** Privacy Across Chains ($2,000)

#### Problem
Nostr identities siloed to Nostr ecosystem

#### Solution
Bridge Nostr identity across chains privately

#### Features
- Use Wormhole/Substance Labs for bridging
- Nostr event → private action on Ethereum/other chain
- Prove Nostr reputation → access gated content elsewhere
- Aztec as privacy layer between ecosystems

#### Examples
- Post on Nostr → trigger private payment on Ethereum
- Nostr follower count → unlock features on another chain
- Cross-chain private reputation system

---

## 5. Recommended Approach

### Target: Identity Infrastructure Track ($2,000)

### Timeline
- **Afternoon 1**: Spin up `nostr-rs-relay` locally, learn protocol
- **Day 1-2**: Build Aztec contracts
  - Attestation storage (private)
  - Link Nostr pubkey → Aztec address
  - ZK proof functions (prove facts without revealing data)
- **Day 2-3**: Build integration layer
  - Nostr client extension or standalone app
  - UI to manage attestations
  - Proof generation/verification
- **Day 3-4**: Demo + documentation

### Why This Wins
✅ **Clear use case**: Nostr desperately needs identity infrastructure
✅ **Only possible with privacy**: Can't do private attestations without Aztec
✅ **User controls data**: Fully decentralized
✅ **Actually useful**: Real value for Nostr ecosystem
✅ **Composable**: Works with ZKPassport, Anon Aadhaar, etc.
✅ **Doable timeframe**: Realistic for hackathon

### Technical Stack
- **Relay**: nostr-rs-relay (or minimal custom implementation)
- **Smart contracts**: Aztec.nr
- **Client**: TypeScript/JavaScript
- **Bridge libraries**: Aztec SDK
- **Frontend**: React (optional, for demo)

---

## 6. Key Differentiators

### Why Aztec + Nostr Makes Sense

1. **Nostr lacks private state storage**
   - Aztec provides private contract storage
   - Natural fit for attestations, credentials

2. **Nostr is pseudonymous, not privacy-preserving**
   - Can link identity across relays
   - Can analyze social graphs
   - Aztec adds true privacy layer

3. **Nostr needs reputation without centralization**
   - Attestations on Aztec are user-controlled
   - No trusted third party
   - Prove facts without revealing everything

4. **Composability**
   - Nostr pubkey is universal identifier
   - Aztec attestations portable across apps
   - Real identity infrastructure

---

## Next Steps

1. Set up local Nostr relay
2. Design Aztec contract architecture for attestations
3. Sketch proof system (what facts to prove?)
4. Build minimal integration
5. Create compelling demo

---

## Resources

### Nostr
- [NIP-01: Basic Protocol](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [nostr-rs-relay](https://github.com/scsibug/nostr-rs-relay)
- [Nostr Dev Resources](https://nostr.how/en/developers)

### Aztec
- [Aztec Docs](https://docs.aztec.network/)
- [Aztec.nr](https://docs.aztec.network/developers/contracts/main)
- [ZKPassport Docs](https://docs.zkpassport.id/intro)
- [Anon Aadhaar](https://github.com/anon-aadhaar/anon-aadhaar-noir)

### Hackathon Tracks
- Identity Infrastructure: $2,000
- Privacy Across Chains: $2,000
- Rethinking What's Possible: $1,000
