# Aztec ATProto Primitives Research

## Overview

This research identifies the key ATProto/Bluesky primitives that can be leveraged for an Aztec-based verification system. The goal is to create a service that uses Aztec's zero-knowledge proofs to verify attributes about users, then display verified badges via Bluesky's labeling system.

## ATProto Primitives

### 1. Labellers (Primary Focus)

**What are they?**
Labelers are the main component of ATProto's composable moderation system. While designed for content moderation, they can also serve informational purposes like verification badges, user attributes, or positive identity markers.

**Key Characteristics:**
- Each labeler has its own DID (Decentralized Identifier)
- Signs labels with cryptographic keys (#atproto_label)
- Can be subscribed to by users who want those labels
- Appears as the source (src) field in labels
- Can be used for moderation OR verification/badges

**Technical Requirements:**
Must implement these XRPC endpoints:
- `com.atproto.label.subscribeLabels` - Realtime subscription of all labels
- `com.atproto.label.queryLabels` - Query labels published on content
- `com.atproto.report.createReport` (optional) - Receive user reports

**Architecture:**
- Service endpoint in DID document (ID: #atproto_labeler, type: AtprotoLabeler)
- Labels can be applied to profiles, posts, or any content URI
- Users subscribe to labelers they trust
- Labels appear based on user's subscriptions and preferences

### 2. Badges (Experimental)

**Current State:**
Badges are NOT yet a first-class primitive in ATProto. There's active community discussion (GitHub #3065) about making "positive labels" into distinct "badges" separate from moderation labels.

**Blue Badge Implementation:**
An experimental badge system exists at https://badge.blue/

**Technical Structure:**
- `blue.badge.definition` - Defines the badge (name, description, image)
- `blue.badge.award` (or `blue.badge.collection`) - Award records in user repositories
- Includes cryptographic signatures (JWS format)
- References DID verification methods
- Can render as SVG: `https://render.badge.blue/badge?uri=<badge-uri>`

**Key Difference from Labels:**
- Badges are for positive identity expression
- Labels are for content filtering/moderation
- Badges should be visually rich (icons, colors)
- Badges are user-chosen to display

**Current Approach:**
Use labelers with "positive" labels as de facto badges until badges become first-class.

### 3. Other Useful Primitives

**Custom Feeds:**
- Algorithm-driven content curation
- Could surface verified users or verified content
- Typescript SDKs available

**Firehose API:**
- Real-time stream of all network activity
- Useful for monitoring verification requests
- Can trigger automated verification workflows

**DID System:**
- did:plc (PLC directory) and did:web (web-based)
- Already researched in your repo (see did-web-examples.md)
- Can be used for service identity and verification

**Personal Data Servers (PDS):**
- Store user data and repositories
- Where badge records would be stored
- Can be self-hosted or use shared infrastructure

## How to Create Your Own Labeller

### Prerequisites
- Go programming knowledge (for bsky-watch/labeler)
- OR ability to implement XRPC endpoints in your language of choice
- Docker & Docker Compose
- Domain name (for service endpoint)
- ATProto account (DID + password)

### Step-by-Step Guide

#### 1. Choose Implementation Approach

**Option A: Use bsky-watch/labeler (Recommended for Beginners)**
```bash
git clone https://github.com/bsky-watch/labeler.git
cd labeler
```

**Option B: Build from Scratch**
Import the labeler module in your Go project:
```go
import "bsky.watch/labeler"
```

**Option C: Different Language**
Implement the required XRPC endpoints using ATProto SDK for your language (Python, TypeScript, Dart, etc.)

#### 2. Configuration Setup

**Create .env file:**
```bash
cp example.env .env
# Edit DATA_DIR and other environment variables
```

**Create config.yaml:**
```bash
cp example_config.yaml config.yaml
```

**Generate Private Key:**
You need a private key for signing labels. Add it to config.yaml:
```yaml
signing_key: "your-private-key-here"
did: "did:plc:your-did-here"
password: "your-app-password"
```

**Define Your Labels:**
```yaml
labels:
  - name: "age-verified"
    description: "User has verified their age using zero-knowledge proof"
  - name: "credential-verified"
    description: "User has verified professional credentials"
  - name: "aztec-verified"
    description: "User has completed Aztec ZK verification"
```

#### 3. Deploy the Service

**Using Docker:**
```bash
docker compose up --build -d
```

**Enable Admin API (Optional):**
```bash
cp docker-compose.override.example.yaml docker-compose.override.yaml
docker compose up -d
```

This exposes an endpoint for creating labels via API:
```bash
curl -X POST --json '{"uri": "did:plc:user-did", "val": "age-verified"}' \
  http://127.0.0.1:8081/label
```

#### 4. Register Your Labeler

**Update PLC Directory:**
```bash
docker compose exec labeler ./update-plc --config=/config.yaml
```

This registers your labeler's DID and service endpoint in the PLC directory.

**Update Labeler Record:**
The service automatically updates labeler records on startup when `did`, `password`, and `labels` are configured in config.yaml.

#### 5. Make It Public

**Requirements:**
- Public HTTPS endpoint for your labeler service
- Domain name pointing to your service
- SSL/TLS certificate (Let's Encrypt recommended)

**Update Service Endpoint:**
Ensure your DID document points to your public endpoint with type `AtprotoLabeler`.

#### 6. Users Subscribe

Users can find and subscribe to your labeler through:
- Bluesky settings > Moderation > Labelers
- Direct link to your labeler's profile (did:plc:your-did)
- Third-party labeler directories like https://www.bluesky-labelers.io/

## Aztec + Labeller Verification System

### Concept

Create a verification service that combines:
1. **Aztec ZK Proofs** - Users prove attributes without revealing private data
2. **Verification Service** - Validates proofs and issues verification tokens
3. **Labeller Service** - Applies badges to verified users on Bluesky

### Use Cases

**Age Verification:**
- User proves they're over 18 without revealing birthdate
- Labeller applies "age-verified" badge
- No personal data stored or shared

**Professional Credentials:**
- Prove you're a licensed doctor/lawyer/engineer
- Prove you have a degree from specific university
- Verify certifications without exposing personal details

**Community Membership:**
- Prove membership in organization without doxxing
- Verify event attendance (e.g., DevConnect)
- Confirm group affiliation privately

**Financial Attestations:**
- Prove creditworthiness without revealing finances
- Verify accredited investor status
- Confirm token holdings without exposing wallet

### Technical Architecture

#### Architecture Option 1: Off-Chain Verification (Fastest)

```
┌─────────┐                  ┌──────────────┐                  ┌──────────┐
│  User   │                  │ Verification │                  │ Labeller │
│         │                  │   Service    │                  │ Service  │
└─────────┘                  └──────────────┘                  └──────────┘
     │                              │                                │
     │  1. Generate ZK Proof        │                                │
     │     (via Aztec/Noir)         │                                │
     │──────────────────────────────>                                │
     │                              │                                │
     │                              │  2. Validate Proof             │
     │                              │     (ACE/Noir Verifier)        │
     │                              │                                │
     │  3. Return Verification      │                                │
     │     Token                    │                                │
     │<──────────────────────────────                                │
     │                              │                                │
     │  4. Request Badge            │                                │
     │     (with token)             │                                │
     │─────────────────────────────────────────────────────────────>│
     │                              │                                │
     │                              │  5. Verify Token               │
     │                              │<────────────────────────────────│
     │                              │                                │
     │                              │  6. Confirm                    │
     │                              │─────────────────────────────────>
     │                              │                                │
     │  7. Apply Label              │                                │
     │<─────────────────────────────────────────────────────────────│
```

**Pros:**
- Fast verification (no blockchain confirmation)
- Low/no cost
- Better privacy (proofs not on-chain)

**Cons:**
- Requires trust in verification service
- Centralized proof validation
- Token could be stolen/replayed (needs security measures)

#### Architecture Option 2: On-Chain Verification (Most Trustless)

```
┌─────────┐         ┌──────────┐         ┌─────────────┐         ┌──────────┐
│  User   │         │Ethereum  │         │  Monitoring │         │ Labeller │
│         │         │Verifier  │         │   Service   │         │ Service  │
└─────────┘         └──────────┘         └─────────────┘         └──────────┘
     │                    │                      │                      │
     │  1. Generate       │                      │                      │
     │     ZK Proof       │                      │                      │
     │                    │                      │                      │
     │  2. Submit to      │                      │                      │
     │     Smart Contract │                      │                      │
     │───────────────────>│                      │                      │
     │                    │                      │                      │
     │                    │  3. Validate Proof   │                      │
     │                    │     (Noir Verifier)  │                      │
     │                    │                      │                      │
     │  4. Emit Event     │                      │                      │
     │    (if valid)      │                      │                      │
     │                    │──────────────────────>                      │
     │                    │                      │                      │
     │                    │                      │  5. Apply Label      │
     │                    │                      │     to user DID      │
     │                    │                      │─────────────────────>│
     │                    │                      │                      │
     │  6. Label appears on profile              │                      │
     │<──────────────────────────────────────────────────────────────────│
```

**Pros:**
- Trustless verification (anyone can audit)
- Permanent proof record
- No centralized service risk

**Cons:**
- Gas costs for on-chain verification
- Slower (blockchain confirmation time)
- Proofs are public (may leak metadata)

#### Architecture Option 3: Hybrid (Recommended)

- **High-value verifications** (credentials, identity) → On-chain
- **Low-value verifications** (preferences, interests) → Off-chain
- Different badge tiers indicate verification method
- Users choose based on privacy/cost/trust tradeoffs

### Implementation Steps

#### 1. Design Your Verification Circuit (Noir)

Example: Age Verification
```noir
fn main(
    birthdate: Field,
    current_date: Field,
    min_age: Field,
    public_commitment: pub Field
) {
    // Verify commitment matches birthdate
    let commitment = hash(birthdate);
    assert(commitment == public_commitment);

    // Calculate age
    let age = (current_date - birthdate) / 365;

    // Assert minimum age
    assert(age >= min_age);
}
```

#### 2. Generate Verifier Contract

```bash
noire compile circuit.nr
noire codegen-verifier
```

This creates a Solidity contract that can verify proofs on Ethereum.

#### 3. Deploy Verification Service

**Off-Chain Option:**
```javascript
// Express API endpoint
app.post('/verify', async (req, res) => {
  const { proof, publicInputs, userDid } = req.body;

  // Validate proof using Noir verifier
  const isValid = await verifier.verify(proof, publicInputs);

  if (isValid) {
    // Generate verification token
    const token = jwt.sign({ did: userDid, verified: true }, secret);
    res.json({ token });
  }
});
```

**On-Chain Option:**
```solidity
// Solidity contract
contract AztecVerifier {
    event Verified(address indexed user, string did, bytes32 proofHash);

    function verify(bytes calldata proof, bytes32[] calldata publicInputs, string calldata did)
        external
        returns (bool)
    {
        bool isValid = verifier.verify(proof, publicInputs);
        require(isValid, "Invalid proof");

        emit Verified(msg.sender, did, keccak256(proof));
        return true;
    }
}
```

#### 4. Connect to Labeller

**API Integration:**
```javascript
// After successful verification
async function applyLabel(userDid, labelValue) {
  await fetch('http://labeller-service:8081/label', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      uri: userDid,
      val: labelValue
    })
  });
}
```

**Event Monitoring (On-Chain):**
```javascript
// Monitor blockchain for verification events
verifierContract.on('Verified', async (user, did, proofHash) => {
  console.log(`User ${did} verified!`);
  await applyLabel(did, 'aztec-verified');
});
```

#### 5. Create User Interface

**Verification Flow:**
1. User visits your verification portal
2. Connects wallet (for on-chain) or generates proof client-side
3. Submits proof + ATProto DID
4. Receives confirmation
5. Badge appears on Bluesky profile (if subscribed to labeller)

**Frontend Example:**
```javascript
// Generate proof (client-side)
const proof = await noir.generateProof(witnessInputs);

// Submit to verification service
const response = await fetch('/verify', {
  method: 'POST',
  body: JSON.stringify({
    proof: proof.proof,
    publicInputs: proof.publicInputs,
    userDid: 'did:plc:user-id'
  })
});
```

### Security Considerations

**Proof Replay Prevention:**
- Include timestamp in public inputs
- Store proof hashes to prevent reuse
- Time-limit verification tokens

**Privacy Protection:**
- Minimize public inputs
- Don't store unnecessary data
- Consider what labels reveal about users

**Sybil Resistance:**
- One verification per DID
- Proof must commit to specific DID
- Monitor for suspicious patterns

**Label Revocation:**
- Implement expiry for time-sensitive verifications
- Allow users to request removal
- Handle compromised credentials

### Badge Design

**Label Naming:**
- Use clear, descriptive names: `age-verified`, `credential-verified`
- Consider hierarchy: `verified-basic`, `verified-enhanced`, `verified-premium`
- Indicate verification method: `onchain-verified`, `zk-verified`

**Visual Design (for Blue Badge style):**
- Create SVG icons for each badge type
- Use colors that align with verification level
- Make badges distinguishable from official Bluesky badges

**Metadata:**
```yaml
labels:
  - name: "aztec-age-verified"
    description: "User has verified their age using Aztec zero-knowledge proof"
    severity: "none"  # Not a moderation label
    blurs: "none"
    defaultSetting: "show"
    adultOnly: false
```

## Next Steps

### Immediate Actions
1. Set up test labeller using bsky-watch/labeler
2. Create simple Noir circuit for age verification
3. Build minimal verification API
4. Test end-to-end flow on Bluesky testnet

### Medium-Term Goals
1. Deploy production labeller with HTTPS endpoint
2. Implement multiple verification types
3. Build user-friendly verification portal
4. Integrate with Aztec mainnet

### Long-Term Vision
1. Explore Blue Badge integration for richer display
2. Build verification marketplace (multiple proof types)
3. Enable third-party proof providers
4. Create developer toolkit for custom verifications

## Resources

### ATProto/Bluesky
- ATProto Specs: https://atproto.com/specs/label
- Bluesky Docs: https://docs.bsky.app/
- bsky-watch/labeler: https://github.com/bsky-watch/labeler
- Blue Badge: https://badge.blue/
- Labeler Directory: https://www.bluesky-labelers.io/

### Aztec
- Aztec Docs: https://aztec.network/
- Noir Language: https://noir-lang.org/
- Aztec GitHub: https://github.com/AztecProtocol/aztec-packages

### Community
- ATProto Discussion #3065 (Badges): https://github.com/bluesky-social/atproto/discussions/3065
- Bluesky Developer Discord
- Aztec Developer Discord

## Conclusion

The combination of Aztec's zero-knowledge proofs and ATProto's labeling system creates powerful possibilities for privacy-preserving verification on Bluesky. By building a labeller that accepts ZK proofs, you can create a verification service that respects user privacy while providing trustworthy attestations.

The key is choosing the right architecture for your use case:
- **Off-chain** for speed and privacy
- **On-chain** for trustlessness and auditability
- **Hybrid** for flexibility and user choice

Start simple with a basic labeller and age verification, then expand to more complex use cases as you validate the concept.
