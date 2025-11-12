# ATProto Keypair + Labeler Research

**Research Date:** 2025-11-12
**Topic:** Using public/private keypairs with ATProto DIDs + Labeler services for Aztec-based validation

## Research Questions

1. **Keypair Storage Pattern:**
   - Can we store a public key in a user's PDS/DID?
   - Are there examples of private keys being held server-side while public keys are in DIDs?
   - What's the standard way to add custom public keys to ATProto identities?

2. **Labeler Service Mechanics:**
   - How do labeler services work in ATProto/Bluesky?
   - How do they scan the firehose?
   - Can they efficiently find specific public keys?
   - Is this a "needle in haystack" problem or is there indexing?

3. **Use Case Validation:**
   - User completes Aztec-powered validation (generates proof/smart contract)
   - Generate keypair: public → PDS, private → validation server
   - Labeler scans firehose, finds public key, validates with private key
   - Adds verification badge/label to user

4. **Labeler Concerns:**
   - Has Paul Frazee or Bluesky team expressed concerns about labeler misuse?
   - What are the limitations or concerns?

---

## Investigation Log

### Starting Point

From previous research, we know:
- DIDs contain public keys for signing (verificationMethod)
- DID documents are public and resolve via HTTPS
- ATProto uses did:plc (most common) and did:web
- DIDs are primarily used for account signing keys

Key question: Can we add CUSTOM public keys to a DID for non-signing purposes?

---

## FINDINGS

## 1. Can Custom Public Keys Be Added to DIDs?

### ✅ YES - As of June 2025

**Major Update:** The PLC Directory service was updated in June 2025 to relax verificationMethod constraints.

**What's Allowed:**
- Multiple verification methods per DID document (up to 10 maximum)
- Custom key types including ed25519, p256, k256, and other did:key formats
- Keys must be syntactically valid: `did:key:` prefix + base58-encoded multibase string
- Each key needs: `id`, `type` (Multikey), `controller`, and `publicKeyMultibase`

**Constraints:**
- Maximum of 10 verification methods per DID
- For ATProto repo authentication, only p256 and k256 are supported
- For PLC rotation keys, only p256 and k256 are supported
- Custom keys can be used for non-atproto purposes

**Source:** [GitHub Discussion #3928](https://github.com/bluesky-social/atproto/discussions/3928)

### Real Example: Multiple Keys in DID Document

**Example DID:** `did:plc:5eoo6tyoqrucebr43ws4zoff`

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/multikey/v1",
    "https://w3id.org/security/suites/secp256k1-2019/v1"
  ],
  "id": "did:plc:5eoo6tyoqrucebr43ws4zoff",
  "alsoKnownAs": ["at://bob.example.com"],
  "verificationMethod": [
    {
      "id": "did:plc:5eoo6tyoqrucebr43ws4zoff#atproto",
      "type": "Multikey",
      "controller": "did:plc:5eoo6tyoqrucebr43ws4zoff",
      "publicKeyMultibase": "zQ3shaxnaNhKA1zSvif5BzJWMc6yMTVKAFnxpyaLZaU2qharU"
    },
    {
      "id": "did:plc:5eoo6tyoqrucebr43ws4zoff#ed25519test",
      "type": "Multikey",
      "controller": "did:plc:5eoo6tyoqrucebr43ws4zoff",
      "publicKeyMultibase": "z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK"
    }
  ],
  "service": [
    {
      "id": "#atproto_pds",
      "type": "AtprotoPersonalDataServer",
      "serviceEndpoint": "https://pds.bob.example.com/"
    }
  ]
}
```

**Key Observations:**
- Two verification methods present: `#atproto` (standard signing key) and `#ed25519test` (custom key)
- Both use `Multikey` type
- Custom key uses different cryptographic algorithm (ed25519)
- DID document resolves publicly via PLC directory

---

## 2. Labeler Service Pattern: Split Keypair Architecture

### ✅ ESTABLISHED PATTERN EXISTS

ATProto has a **built-in pattern** for services (like labelers) that use separate signing keys:

**Standard Keys:**
- `#atproto` - Main account signing key for repository
- `#atproto_label` - Dedicated key for signing labels

**Example Labeler DID:** `did:plc:4wgmwsq4t3tg55ffl3r7ocec` (self-labeler.snarfed.org)

```json
{
  "id": "did:plc:4wgmwsq4t3tg55ffl3r7ocec",
  "alsoKnownAs": ["at://self-labeler.snarfed.org"],
  "verificationMethod": [
    {
      "id": "did:plc:4wgmwsq4t3tg55ffl3r7ocec#atproto",
      "type": "Multikey",
      "controller": "did:plc:4wgmwsq4t3tg55ffl3r7ocec",
      "publicKeyMultibase": "zQ3shugkhgdDVvxbRG37HRB5yLoiTegAUm8sarF8Ti4acuTe9"
    },
    {
      "id": "did:plc:4wgmwsq4t3tg55ffl3r7ocec#atproto_label",
      "type": "Multikey",
      "controller": "did:plc:4wgmwsq4t3tg55ffl3r7ocec",
      "publicKeyMultibase": "zQ3shMz2SoabkL1npH8yTR1GTeaBt4WFUVxe4MztoGY9zMKrg"
    }
  ],
  "service": [
    {
      "id": "#atproto_pds",
      "type": "AtprotoPersonalDataServer",
      "serviceEndpoint": "https://button.us-west.host.bsky.network"
    },
    {
      "id": "#atproto_labeler",
      "type": "AtprotoLabeler",
      "serviceEndpoint": "https://self-labeler.snarfed.org"
    }
  ]
}
```

**Key Pattern:**
1. Public key for labeling is stored in DID as `#atproto_label`
2. Private key held server-side by the labeler service
3. Service endpoint declared as `#atproto_labeler`
4. Labels are cryptographically signed with the `#atproto_label` key

**Source:** [ATProto Label Spec](https://atproto.com/specs/label)

---

## 3. How Labeler Services Work

### Architecture

**Key Components:**
1. **Service Identity:** Labeler has its own DID document
2. **Signing Key:** `#atproto_label` key in verificationMethod array
3. **Service Endpoint:** `#atproto_labeler` in service array with URL
4. **Declaration Record:** Defines what labels the service can apply

**Label Structure:**
- **source:** The labeler's DID
- **subject:** Content URI or account DID being labeled
- **value:** Label string (max 128 bytes, like a tag)
- **timestamp:** When label was created
- **expiration:** Optional expiry date
- **signature:** Cryptographic signature using `#atproto_label` key

### Distribution Mechanisms

**1. Event Stream:** `com.atproto.label.subscribeLabels`
   - WebSocket endpoint broadcasting new labels
   - Supports backfill for historical labels
   - Real-time label distribution

**2. Query Endpoint:** `com.atproto.label.queryLabels`
   - Flexible filtering by subject, source, etc.
   - Not required to be publicly enumerable (access controls possible)

**3. Cryptographic Verification:**
   - Labels are signed with labeler's private key
   - Recipients validate signature using public key from DID document
   - Supports key rotation via DID document updates

---

## 4. Firehose Scanning & Finding Specific DIDs

### Current State (2025)

**❌ No Server-Side Filtering**
- The firehose does NOT support server-side filtering by DID or account properties
- Services must consume the entire firehose and filter client-side
- This is a known limitation discussed in GitHub #2418

**Performance Challenges:**
- One developer reported 6TB of bandwidth in March 2024
- Over 99% of firehose data was irrelevant to their use case
- "Needle in haystack" problem is REAL for finding specific accounts

**Solutions:**

**1. Jetstream (Official, January 2025)**
   - Shrinks firehose by >99% by providing lightweight JSON/CBOR streams
   - Supports filtering by:
     - Specific collections (e.g., only posts)
     - Specific repos/DIDs (list of accounts to watch)
   - 4 public instances available
   - [Jetstream Announcement](https://docs.bsky.app/blog/jetstream)

**2. DID-Based Sharding**
   - ATProto has natural sharding key (account DID)
   - Related events routed to correct shard
   - Allows concurrent processing while maintaining order per repo

**3. Client-Side Indexing**
   - Build local index of DIDs of interest
   - Subscribe to firehose and filter for matching DIDs
   - Keep sync status table for encountered accounts

**Best Practice for Your Use Case:**
- Use Jetstream to filter for specific DIDs (users with your custom key)
- Maintain local database of DIDs that have completed Aztec validation
- Subscribe to Jetstream with DID filter for those specific accounts
- This avoids scanning entire network

---

## 5. Split Keypair Pattern for Verification

### ✅ YOUR USE CASE IS SUPPORTED

Based on the research, here's how the Aztec validation pattern would work:

**Architecture:**

```
User completes Aztec validation
    ↓
Generate keypair (p256 or k256 for ATProto compatibility)
    ↓
Public key → Add to user's DID verificationMethod
    └─ Fragment: #aztec_verification (or custom name)
    └─ Type: Multikey
    └─ Public key in multibase format
    ↓
Private key → Stored on validation server
    ↓
Labeler service configuration:
    - Maintains list of DIDs with Aztec verification keys
    - Subscribes to Jetstream filtered for those DIDs
    - When user activity detected, applies verification label
    - Labels signed with labeler's #atproto_label key
    ↓
Verification badge appears on user's profile
```

**Technical Implementation:**

1. **Key Generation:**
   ```javascript
   // Generate p256 or k256 keypair
   // Encode public key as did:key format
   // Example: did:key:zQ3sh...
   ```

2. **Add to DID Document:**
   ```json
   {
     "id": "did:plc:userDID#aztec_verification",
     "type": "Multikey",
     "controller": "did:plc:userDID",
     "publicKeyMultibase": "zQ3sh..."
   }
   ```

3. **Labeler Tracking:**
   - Maintain database of verified DIDs
   - Subscribe to Jetstream with DID filter
   - Apply label when verified account has activity

4. **Label Application:**
   ```json
   {
     "source": "did:plc:labelerDID",
     "subject": "did:plc:userDID",
     "value": "aztec-verified",
     "timestamp": "2025-11-12T...",
     "signature": "..."
   }
   ```

**Advantages:**
- Public key is publicly verifiable via DID document
- Private key never leaves validation server
- Cryptographically sound verification
- Labels are also cryptographically signed
- Standard ATProto pattern

---

## 6. Examples of Application-Specific Keys

### Documented Use Cases:

**1. Labeler Services**
- Pattern: `#atproto_label` key for signing labels
- Example: self-labeler.snarfed.org
- Public key in DID, private key server-side

**2. Custom Verification (2025)**
- New as of June 2025 relaxation of constraints
- ed25519 keys for non-atproto services
- Example: did:plc:5eoo6tyoqrucebr43ws4zoff#ed25519test

**3. Cross-Protocol Compatibility**
- Store keys for other systems in ATProto DIDs
- Enables identity bridging between protocols
- Keys must be valid did:key format

**4. HPKE (Hybrid Public Key Encryption)**
- From previous research on private data in Bluesky
- Public keys from DIDs used for encryption
- Pattern for encrypted messaging and DMs

**NOT YET DOCUMENTED:**
- Zero-knowledge proof verification keys
- Smart contract verification keys
- Credential verification keys
- But the infrastructure NOW SUPPORTS these use cases!

---

## 7. Technical Limitations & Considerations

### Key Type Constraints

**For Custom Keys (Your Use Case):**
- ✅ Any key type supported (as of June 2025)
- ✅ Ed25519, p256, k256, others
- ✅ Must be valid did:key format
- ⚠️ Maximum 10 verification methods per DID
- ⚠️ Cannot be used for ATProto repo signing (only p256/k256)

**For ATProto Core Functions:**
- Only p256 and k256 for repository signing
- Only p256 and k256 for PLC rotation keys

### Performance Limitations

**Firehose Scanning:**
- ❌ No server-side filtering by DID properties
- ❌ Cannot query "all DIDs with key fragment #aztec_verification"
- ✅ Can use Jetstream to filter for known DIDs
- ⚠️ Must maintain separate index of verified accounts

**Implication for Your Use Case:**
- You'll need to track verified DIDs in your own database
- Cannot discover new verified users by scanning all DID documents
- Users must complete verification flow that registers their DID with your service
- Labeler then monitors those specific DIDs via Jetstream

### DID Document Updates

**Key Rotation:**
- DID documents can be updated
- Keys can be added/removed (up to 10 total)
- Updates propagate via PLC directory
- Services must handle key rotation gracefully

**Cost:**
- Free to update DID documents
- No blockchain fees (ATProto is not blockchain-based)
- Updates happen via PLC directory HTTP API

---

## 8. Labeler Concerns & Limitations

### From Bluesky Team

**Paul Frazee (CTO) Concerns:**
- Labelers operating without proper notification systems
- Users on external PDSes not being notified of bans
- Federation features still experimental (as of 2024-2025)
- Centralization concerns with Ozone moderation software

**Key Quote:**
> "At the relay level, users depend on filtering decisions without choice afterward, so the focus should be on legal concerns to allow applications downstream to make their own moderation choices."

**Known Issues:**
- Ozone (labeling software) has technical issues
- Alternative services remain dependent on Bluesky's infrastructure
- Decentralization goals not fully achieved yet

### Scale Considerations

**2024 Bluesky Stats:**
- Grew from 2.89M to 25.94M users
- Applied 5.5M labels
- Shows labeling at scale is real and active

**Implications:**
- Labeling infrastructure is proven
- Your use case would be small scale initially
- Pattern is established and supported

### Best Practices for Labelers

**From Community:**
1. Declare your labeling criteria transparently
2. Provide appeals process for incorrect labels
3. Don't misuse labels for non-moderation purposes (controversial)
4. Respect user privacy (labels are public)
5. Provide clear documentation of label meanings

**For Verification Labels:**
- Verification labels are explicitly supported
- Ozone moderation app will support verification
- This is an intended use case, not an abuse

---

## 9. Lexicon Schemas & Conventions

### DID Documents Are NOT Defined by Lexicon

**Important Distinction:**
- **Lexicon:** Schema system for ATProto RPC methods and record types
- **DID Documents:** Follow W3C DID specification standards
- These are separate systems

**No Lexicon Schema for:**
- verificationMethod fields
- service endpoint types
- Custom DID document properties

**Convention-Based Fragments:**
- `#atproto` - Standard repo signing key
- `#atproto_label` - Label signing key
- `#atproto_pds` - PDS service endpoint
- `#atproto_labeler` - Labeler service endpoint

**For Custom Keys:**
- Choose meaningful fragment identifier
- Example: `#aztec_verification` or `#zkp_key`
- Document your convention
- No official registry of fragment names (yet)

### Service Mapping Convention

**Fixed Mappings:**
- Service `atproto_labeler` maps to key `atproto_label`
- This is hardcoded convention in ATProto spec
- When issuing JWT tokens, service identifier determines signing key

**Example:**
```
Token issuer: did:web:label.example.com#atproto_labeler
Signing key: did:web:label.example.com#atproto_label
```

**For Custom Services:**
- No established pattern yet for custom service→key mapping
- Would need to define your own convention
- Document clearly for interoperability

---

## 10. Cryptographic Details

### Supported Curves

**ATProto Standard:**
1. **k256** (secp256k1)
   - Default for new accounts
   - Used by Bitcoin and cryptocurrencies
   - Not in WebCrypto API

2. **p256** (NIST P-256, secp256r1, prime256v1)
   - Included in WebCrypto API
   - Supported by TPMs, Secure Enclaves, cloud HSMs

**Both Required:**
- Implementations must support both curves
- For custom verification, either works
- k256 is more common in crypto space (relevant for Aztec)

### Key Encoding

**Format:**
```
did:key:z<multibase-encoded-key>
```

**Components:**
1. Multibase prefix (z = base58btc)
2. Multicodec prefix (identifies curve)
   - p256: 0x1200 (varint: [0x80, 0x24])
   - k256: 0xE7 (varint: [0xE7, 0x01])
3. Compressed public key (33 bytes)

**For DID Documents:**
- Remove `did:key:` prefix
- Just use the multibase string in `publicKeyMultibase` field

### Signing Practice

**Standard Pattern:**
1. Encode data in DAG-CBOR
2. Hash with SHA-256
3. Sign hash bytes with private key
4. Use "low-S" signature variant (prevents malleability)

**For Your Use Case:**
- If signing verification proofs, follow this pattern
- Ensures compatibility with ATProto tools
- Standard cryptographic best practices

---

## 11. Practical Implementation Roadmap

### Phase 1: Keypair Generation & DID Update

1. **Generate Compatible Keypair**
   ```javascript
   // Use k256 for crypto compatibility
   // Or p256 for broader hardware support
   // Encode as did:key format
   ```

2. **Update User's DID Document**
   - Use PLC directory API
   - Add verificationMethod with custom fragment
   - User must authorize the update (requires their credentials)

3. **Store Private Key Securely**
   - Hardware Security Module (HSM) if possible
   - Encrypted at rest
   - Limited access controls
   - Regular rotation policy

### Phase 2: Labeler Service Setup

1. **Create Labeler Identity**
   - Get DID (did:plc or did:web)
   - Generate `#atproto_label` keypair
   - Add to DID document
   - Set up service endpoint

2. **Deploy Labeler Service**
   - Reference implementation: github.com/snarfed/self-labeler
   - Or use @skyware/labeler package
   - Configure label definitions

3. **Connect to Jetstream**
   - Subscribe to filtered firehose
   - Maintain list of verified DIDs
   - Monitor for user activity

### Phase 3: Verification Flow

1. **User Completes Aztec Validation**
   - Generates ZK proof
   - Submits to your validation server

2. **Validation Server Processes**
   - Verifies proof is valid
   - Generates keypair
   - Updates user's DID (with permission)
   - Stores DID in verified users database

3. **Labeler Monitors & Labels**
   - Adds DID to Jetstream filter
   - Waits for user activity (post, profile update, etc.)
   - Applies verification label
   - Label appears in user's profile

### Phase 4: Verification Display

1. **In Bluesky App**
   - Labels appear as badges/indicators
   - Users can click to see labeler info
   - Labeler's declaration explains meaning

2. **Custom Clients**
   - Can query for labels via com.atproto.label.queryLabels
   - Filter by labeler DID and label value
   - Display custom verification UI

---

## 12. Code References & Tools

### Official Repositories

**ATProto Core:**
- Main repo: github.com/bluesky-social/atproto
- Identity package: github.com/bluesky-social/indigo/atproto/identity
- PDS: github.com/bluesky-social/pds

**Labeler Tools:**
- Self-labeler example: github.com/snarfed/self-labeler
- Skyware labeler: @skyware/labeler (npm)

**DID Tools:**
- PLC Directory: plc.directory (API docs: web.plc.directory/api/redoc)
- DID:web setup: atproto-did-web.lukeacl.com

### Python SDK

```python
# For working with ATProto from Python
pip install atproto
```

**Features:**
- Firehose subscription
- DID resolution
- Label queries
- Repository operations

### Jetstream

**Public Instances (2025):**
- 4 official instances available
- Supports WebSocket connections
- Filter by DID, collection, or both
- JSON and CBOR output

**Documentation:**
- jazco.dev/2024/09/24/jetstream
- docs.bsky.app/blog/jetstream

---

## 13. Alternative Approaches Considered

### Approach 1: Store Key in User Profile Record

**Idea:** Add public key to app.bsky.actor.profile record

❌ **Problems:**
- Profile records are mutable by user
- Less trustworthy than DID document
- Not cryptographically tied to identity
- Would need separate trust mechanism

### Approach 2: Blockchain-Based Verification

**Idea:** Store verification on Ethereum/other chain, reference in Bluesky

❌ **Problems:**
- ATProto explicitly does NOT use blockchain
- Would be separate system requiring bridge
- Extra complexity and cost
- Not native to protocol

### Approach 3: OAuth-Style Flow

**Idea:** User authenticates to validation service, service stores verification

❌ **Problems:**
- Centralized trust in validation service
- Not verifiable by third parties
- Doesn't leverage ATProto's cryptographic identity
- Labels would be opaque

### Approach 4: Custom App-Specific Record

**Idea:** Create Lexicon schema for verification records

⚠️ **Considerations:**
- Could work alongside DID approach
- Records are signed by user's key
- Visible in repository
- Labels still needed for display

✅ **Recommended: DID + Labels**
- Most native to ATProto architecture
- Leverages existing labeler infrastructure
- Publicly verifiable
- Cryptographically sound
- Standard pattern

---

## SUMMARY & RECOMMENDATIONS

### ✅ YES, Your Use Case Is Fully Supported

**What's Possible:**
1. Store custom public keys in user DIDs (up to 10 total)
2. Use any key type (ed25519, p256, k256, etc.)
3. Create labeler service with dedicated signing key
4. Apply verification badges via labels
5. All cryptographically verifiable and public

**The Pattern:**

```
┌─────────────────────────────────────────────────────┐
│ User Completes Aztec Validation                     │
│ (ZK proof generation)                               │
└─────────────┬───────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│ Validation Server                                    │
│ - Verifies proof                                    │
│ - Generates keypair (p256/k256)                     │
│ - Public key → User's DID #aztec_verification       │
│ - Private key → Secure storage                      │
│ - Records DID in verified users DB                  │
└─────────────┬───────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│ Labeler Service                                      │
│ - Subscribes to Jetstream (filtered by DIDs)        │
│ - Monitors verified users' activity                 │
│ - Applies "aztec-verified" label                    │
│ - Signed with labeler's #atproto_label key          │
└─────────────┬───────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│ User's Profile                                       │
│ ✓ Verification badge appears                        │
│ ✓ Publicly verifiable via DID document              │
│ ✓ Label explains verification source                │
└─────────────────────────────────────────────────────┘
```

### Key Advantages

1. **Cryptographically Sound**
   - Public key verifiable via DID document
   - Labels signed with labeler's key
   - Chain of trust is clear

2. **Privacy Preserving**
   - Only public key is published
   - ZK proof details stay off-chain
   - Verification fact is public, details are private

3. **Standard Pattern**
   - Uses established ATProto conventions
   - Labeler pattern is documented and supported
   - Not inventing new protocols

4. **Decentralized**
   - No central verification authority required
   - Anyone can verify the public key
   - Users can run their own labelers

### Challenges to Address

1. **No DID Discovery**
   - Cannot query "find all DIDs with #aztec_verification key"
   - Must maintain separate database of verified users
   - Users must actively register with your service

2. **Firehose Performance**
   - Must use Jetstream for efficient filtering
   - Monitor only specific DIDs, not entire network
   - Build and maintain local index

3. **User Experience**
   - DID updates require user authorization
   - Multi-step process (validate → update DID → get labeled)
   - Need clear UX flow

4. **Key Management**
   - Securing private keys is critical
   - Need rotation policy
   - HSM recommended for production

### Recommended Tech Stack

**For Validation Server:**
- Language: Python or TypeScript
- ATProto SDK: `atproto` (Python) or `@atproto/*` (JS/TS)
- Database: PostgreSQL for verified users index
- Key Storage: AWS KMS, HashiCorp Vault, or similar HSM

**For Labeler Service:**
- Reference: github.com/snarfed/self-labeler
- Framework: @skyware/labeler (TypeScript)
- Firehose: Jetstream subscription
- Hosting: Any cloud provider (AWS, GCP, etc.)

**For Key Generation:**
- Crypto library: noble-curves (JS) or cryptography (Python)
- Curves: k256 recommended for Aztec compatibility
- Encoding: @atproto/crypto for did:key format

### Next Steps

1. **Prototype Key Generation**
   - Write code to generate compatible keypairs
   - Test encoding as did:key format
   - Verify multibase encoding

2. **Test DID Update**
   - Create test account
   - Add custom verificationMethod
   - Verify appears in PLC directory

3. **Deploy Test Labeler**
   - Use self-labeler as starting point
   - Configure custom label definitions
   - Test label application and display

4. **Build Validation Flow**
   - Integrate Aztec proof verification
   - Connect to DID update process
   - Test end-to-end with test accounts

5. **Monitor Performance**
   - Test Jetstream filtering
   - Measure latency for label application
   - Optimize index queries

---

## Resources & Links

### Official Specifications
- DID Spec: https://atproto.com/specs/did
- Cryptography: https://atproto.com/specs/cryptography
- Labels: https://atproto.com/specs/label
- Identity Guide: https://atproto.com/guides/identity

### Key Discussions
- Relaxing verificationMethod constraints: https://github.com/bluesky-social/atproto/discussions/3928
- Firehose filtering: https://github.com/bluesky-social/atproto/discussions/2418
- DID document changes (2023): https://github.com/bluesky-social/atproto/discussions/1510

### Tools & Services
- PLC Directory: https://plc.directory
- PLC API Docs: https://web.plc.directory/api/redoc
- Jetstream: https://docs.bsky.app/blog/jetstream
- Self-labeler: https://github.com/snarfed/self-labeler

### Example DIDs
- Multiple keys: https://plc.directory/did:plc:5eoo6tyoqrucebr43ws4zoff
- Labeler: https://plc.directory/did:plc:4wgmwsq4t3tg55ffl3r7ocec

### Community
- ATProto SDK (Python): https://github.com/MarshalX/atproto
- ATProto SDK (TypeScript): https://github.com/bluesky-social/atproto
- ATProto Community Wiki: https://atproto.wiki

---

**Research completed:** 2025-11-12
**Last updated:** 2025-11-12
**Status:** ✅ Use case is fully feasible and supported

---

## 14. Additional Research: Labeler Concerns & Controversies (2025-11-12)

### Privacy & Misuse Issues Discovered

#### A. Harassment via Labelers
**GitHub Proposal #19:** "How to prevent labels being used to target abuse?"

**Real incidents:**
1. **Jesse Singal Watch Labeler**
   - Tracked followers of controversial figure
   - Applied badge "for informational purposes"
   - Badge interpreted as warning about tolerance of bigotry
   - Currently "TEMPORARILY CLOSED FOR MAINTENANCE"
   - Users unaware of how labels affected reputation

2. **Follow Tracker Shutdown**
   - Tracked followers of "prominent racists, transphobes, and alt-right figures"
   - Operator shut it down: *"because some of you can't be trusted to use this information reasonably and responsibly"*
   - Shows real concern about misuse

3. **Private School Labeler**
   - Tagged British public figures with private school info
   - Included annual tuition fees
   - Some labeled individuals expressed discomfort
   - Raised questions about consent

**Bluesky's Response:**
- Updated Community Guidelines prohibit:
  - Using labels for harassment
  - Accepting compensation for specific labeling actions
  - Abusing features like lists and labels
  - Bad-faith mass reporting

#### B. Leadership Controversies

**The "Waffles" Incident (October 2025):**
1. User asked CEO Jay Graber about banning Jesse Singal
2. Graber replied: "WAFFLES!" with waffle picture
3. CTO Paul Frazee: "if the guy doesn't break the rules we don't ban"
4. When users suggested apology: "You could try a poster's strike. I hear that works"

**Impact:**
- Seen as minimizing marginalized users' concerns
- Mocking those wanting transphobia-free platform
- Damaged trust in leadership

**Earlier Crisis (July 2023):**
- Trolls created accounts with racial slurs as usernames
- Admin response seen as slow
- Graber silent for 10 days
- Led to user "posting strike"

#### C. Data Scraping Concerns

**2024 Incident:**
- Hugging Face employee scraped 1M public posts for AI research
- Highlighted firehose enables massive data collection
- Bluesky acknowledged limitations
- Working on consent preferences, but **enforcement outside ecosystem impossible**

**Fundamental Issue:**
- All public data is REALLY public
- Firehose exposes everything
- No way to opt-out (by design)
- Privacy concerns ongoing

#### D. Moderation at Scale

**2024 Statistics:**
- **1.75M harassment reports** (largest category)
- **17x increase** in moderation reports overall
- Grew from 2.89M to 25.94M users
- Applied 5.5M labels

**Challenges:**
- Platform growing faster than moderation capacity
- Moderation team: ~100 people
- Need for automated detection systems
- Toxicity in replies, group harassment

### Efficiency Analysis Reinforced

**Developer Complaints:**
- ">99% of the data from the firehose is completely ignored"
- "6TB of data usage in March" for one developer
- "Subscribing to a torrential full-network firehose (over a thousand events per second), just to pluck out a handful of individual events"

**Current Stats:**
- ~100 posts/second
- 1000+ total events/second
- Exponentially growing

**What This Means for Finding Public Keys:**
- ❌ EXTREMELY inefficient
- ❌ Cannot query existing profiles
- ❌ Only catches new/updated profiles
- ❌ High bandwidth costs
- ❌ "Needle in haystack" confirmed

### Technical Issues Found

**GitHub Issues:**
1. **#3134:** Need automated spam labeler (Nov 2024)
2. **#2803:** Large label sets hit size limits (Sep 2024)
3. **#2367:** Labels taking effect from wrong labelers (Mar 2024)
4. **#2614:** Cannot add labelers to starter packs
5. **#2885:** Custom self-labels limitations

### Conclusion on Concerns

**For Your Use Case:**
- ✅ Labelers are legitimate for verification
- ✅ Community guidelines support verification use
- ⚠️ Be transparent about what you're tracking
- ⚠️ Provide appeals process
- ⚠️ Document clearly

**Privacy Considerations:**
- Users with verification keys will be publicly identifiable
- Your labeler will track specific users (via Jetstream)
- This is less invasive than tracking follows
- But still public data collection

**Reputational Risk:**
- Labeler controversies are real
- Leadership responses sometimes problematic
- Platform still maturing
- Monitor community sentiment

**Technical Recommendation Stands:**
- Use Jetstream for efficiency
- Maintain your own index
- Don't scan entire firehose
- Be selective about what you track

---

**Full detailed research:** See `labeler-research-findings.md` for comprehensive 12-section analysis
**Quick reference:** See `quick-reference.md` for key links and facts
