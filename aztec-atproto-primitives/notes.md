# Research Notes: Aztec ATProto Primitives

## Investigation Process

### Initial Exploration
- Reviewed existing research in the repo (bluesky-did-research, privateData/bluesky)
- Created fresh directory: aztec-atproto-primitives
- Goal: Identify ATProto primitives that work well with Aztec for verification/identity

### ATProto Primitives Research

#### Web Searches Conducted
1. "ATProto labeller service how to create 2025"
2. "Bluesky ATProto badges verification labels"
3. "ATProto primitives developers Bluesky custom services"
4. "blue.badge ATProto Bluesky badge implementation"
5. "Aztec zero knowledge proof verification service"

#### Key Resources Found
- bsky-watch/labeler GitHub repo: Go-based labeler toolkit
- ATProto label specs: https://atproto.com/specs/label
- Blue Badge project: https://badge.blue/ (experimental badge system)
- Bluesky verification blog post (April 2025)
- GitHub discussion #3065: Badges vs Labels as first-class citizens

### Key Findings

#### 1. Labellers
- Main primitive for moderation AND identity verification
- Each labeler has a DID with signing keys
- Must implement two endpoints:
  - `com.atproto.label.subscribeLabels` (realtime subscription)
  - `com.atproto.label.queryLabels` (query labels)
- Can optionally implement `com.atproto.report.createReport` for reports
- bsky-watch/labeler provides working Go implementation

#### 2. Badges
- NOT a first-class primitive yet (under discussion)
- Currently implemented via positive labels or custom systems
- Blue Badge (badge.blue) is experimental implementation:
  - Uses `blue.badge.definition` and `blue.badge.award` records
  - Includes cryptographic signatures (JWS)
  - Can render as SVG via https://render.badge.blue/badge
  - Uses DID verification methods
- Community wants badges as distinct from moderation labels

#### 3. Other ATProto Primitives
- **Custom Feeds**: Algorithm-driven content curation
- **Firehose API**: Real-time stream of all network activity
- **PDSes (Personal Data Servers)**: User data storage
- **Relays**: Aggregate and index data from PDSes
- **DID System**: Decentralized identity (did:plc, did:web)

#### 4. Aztec Verification Capabilities
- **ACE (AZTEC Cryptography Engine)**: Validates ZK proofs
- **PLONK**: Universal trusted setup proof system
- **Noir Language**: Generate verifier contracts
- **On-chain Verification**: Solidity verifier contracts for Ethereum/EVM
- **Use Cases**: Age verification, identity attestation, credential verification

### Aztec + Labeller Concept

The integration idea:
1. User generates ZK proof via Aztec (e.g., age, credential, membership)
2. Verification service validates proof off-chain or on-chain
3. If valid, labeller subscribes user and applies verified badge/label
4. Badge appears on user's profile in Bluesky
5. Can be used for: KYC, age verification, accreditation, community membership, etc.

### Technical Architecture Possibilities

**Option A: On-chain Verification**
- User submits ZK proof to Ethereum smart contract
- Noir-generated verifier validates proof
- Service monitors blockchain for verified proofs
- Labeller automatically applies badge based on on-chain verification

**Option B: Off-chain Verification Service**
- User submits ZK proof directly to verification API
- Service uses Aztec ACE to validate proof
- Upon validation, service calls labeller API to apply badge
- Faster, cheaper, but requires trust in service operator

**Option C: Hybrid**
- High-value verifications go on-chain
- Low-value verifications stay off-chain
- Different badge types for each trust level

### Next Steps for Implementation
1. Set up basic labeler using bsky-watch/labeler
2. Define badge types (e.g., "age-verified", "credential-verified")
3. Build Aztec proof verification endpoint
4. Connect verification to labeler API
5. Create user flow for proof submission
6. Deploy and test on Bluesky

### Questions to Explore
- [ ] Can we use Blue Badge system alongside labeler?
- [ ] How to handle proof expiry/revocation?
- [ ] What Aztec circuits are most useful for identity?
- [ ] Should verification be subscription-based or one-time?
- [ ] Privacy considerations for ZK proofs + public labels?
