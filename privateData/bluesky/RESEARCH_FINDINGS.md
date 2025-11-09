# Private Data on ATProto/Bluesky - Research Findings

## Executive Summary

ATProto (the protocol powering Bluesky) was initially designed for public content only. Private data support—including encrypted messaging, private posts, and private accounts—represents an entire "second phase" of protocol development currently in planning stages. The community has formed working groups and third-party solutions like Germ DM have emerged to fill gaps, but native protocol support is still being designed.

---

## 1. Core Concepts: Two Categories of Private Data

**Source:** Paul Frazee's Leaflet Articles
- https://pfrazee.leaflet.pub/3lzhmtognls2q
- https://pfrazee.leaflet.pub/3lzhui2zbxk2b

### Personal-Private Data
- **Definition:** Unshared data like preferences, bookmarks, favorites
- **Proposed Solution:** Mirror the public storage system with a private indicator in URIs
- **Implementation:** OAuth scopes grant app access, direct replication streams with PDSes
- **Status:** "Fairly straightforward" - no complex signing models required

### Shared-Private Data
- **Definition:** Multi-user but non-public content (DMs, private posts, group chats)
- **Challenge:** Much more complex, no single solution
- **Key Considerations:**
  - Scale handling (hundreds/thousands of participants)
  - Metadata leakage (can participants be enumerated?)
  - Security guarantees (E2E encryption support)
  - Use-case coverage (private accounts, large groups)
  - User administration (clear permission management)
  - Developer experience (intuitive compared to AT primitives)

---

## 2. Three Architectural Schemes for Shared-Private Data

**Concept:** "Arenas" = collection of records in shared-private experiences

### Hosted Arena
- Server hosts private data and mediates access
- Dynamic rules possible
- Requires trust in host
- Records must be cryptographically signed to prevent misrepresentation
- **Tradeoff:** Flexibility vs. trust requirements

### Mail
- Email-style immutable transactions
- Access rules fixed based on recipient lists
- No revocation possible
- Local edits don't propagate to previous recipients
- **Tradeoff:** Simplicity vs. limited control

### Synced Arena
- Sync channels propagate records across multiple servers
- Access controlled via viewer lists
- Functions as "private relay"
- Store-and-forward semantics
- Potentially gossip protocols
- **Tradeoff:** Complexity vs. resilience

**Implementation Options:**
- PDS level
- Application layer
- Hybrid models

---

## 3. Official ATProto Roadmap & Status

### Current State (as of 2025)
- ATProto currently supports **public data only**
- Current Bluesky DMs are **proprietary and outside the protocol**
- Not end-to-end encrypted
- Built to "get the feature out the door"

**Key Sources:**
- 2025 Protocol Roadmap: https://docs.bsky.app/blog/2025-protocol-roadmap-spring
- What's next for ATProto: https://techcrunch.com/2025/03/26/whats-next-for-atproto-the-protocol-powering-bluesky-and-other-apps/

### Timeline
1. **Phase 1 (Current):** Auth Scopes implementation
   - OAuth for AT Protocol: https://docs.bsky.app/blog/oauth-atproto
   - Progress on Auth Scopes (August 2025): https://github.com/bluesky-social/atproto/discussions/4118

2. **Phase 2 (Planned):** Shared data implementation
   - Depends on Auth Scopes completion
   - Design work expected to start after Phase 1

3. **Phase 3 (Future):** E2EE messaging and private content
   - On-protocol DMs
   - E2EE group chat
   - Private accounts
   - Not expected to start until after shared data

### Technology Choice
**MLS (Messaging Layer Security) is the leading candidate**
- IETF standardized protocol (RFC 9420)
- Emerging internet standard for encrypted messaging interoperability
- Already far along IETF standardization track
- Official MLS info: https://messaginglayersecurity.rocks/
- RFC: https://datatracker.ietf.org/doc/rfc9420/

**Why MLS?**
- Clear top candidate according to ATProto team
- Already being adopted by major platforms
- Designed for group messaging at scale
- Supports forward secrecy and post-compromise security

---

## 4. Current Third-Party Solutions

### Germ DM - E2EE Messaging for Bluesky

**Status:** Beta as of July 2025

**Key Links:**
- Germ Network Official: https://www.germnetwork.com/blog/germdm-atproto-now-beta
- TechCrunch Coverage: https://techcrunch.com/2025/07/30/germ-brings-end-to-end-encrypted-messages-to-bluesky/
- Beta Waitlist: https://www.germnetwork.com/beta-waitlist
- Bluesky Profile: https://bsky.app/profile/germnetwork.com

**Architecture:**
- **Technology:** Messaging Layer Security (MLS) - IETF standard
- **Authentication:** Integrates with ATProto identity system
- **No Phone Number Required:** Uses ATProto DIDs and handles instead
- **Pairing Keys:** Cryptographic keys authenticate ATProto identity
- **Cross-Platform:** Works with Bluesky, Flashes, Skylight, and other ATProto apps

**Features:**
- End-to-end encrypted direct messages
- Authenticated handoff to E2EE DMs
- User controls (accept DMs from followers, initiate-only mode)
- Cross-platform blocking (Germ-only or across all ATProto apps)
- Handle authentication verification

**Open Source:**
- Much of Germ's technology is open sourced
- Could enable Bluesky to add encrypted messaging to official app
- Community can build on their work

---

## 5. Community Efforts & Working Groups

### AT Protocol Community Wiki
**Main Hub:** https://atproto.wiki/en/working-groups

### Active Working Groups:

#### E2EE Messaging Working Group
- **Link:** https://atproto.wiki/en/working-groups/e2ee
- **Focus:** DMs and group chat
- **Goal:** Make in-protocol/protocol-compatible mechanism for group E2EE messaging
- **Standard:** Building on MLS IETF standard
- **Formed:** March 2025 at AtmosphereConf in Seattle

#### Private Data Working Group
- **Link:** https://atproto.wiki/en/working-groups (listed)
- **Goal:** Learn together about cryptographic primitives, security & usability trade-offs, prototyping approaches
- **Status:** Active community discussions

### Community Specifications

#### ATMessaging Proto
- **Repository:** https://github.com/ATProtocol-Community/atmessaging-proto
- **Description:** Draft specification for E2EE direct and group messaging in AT Protocol apps
- **Technology:** MLS (Messaging Layer Security) Protocol
- **Status:** Draft, seeking community contributions

**Key Features:**
- **Security Properties:**
  - Privacy: Prevent observers from identifying communication patterns
  - Confidentiality: Only intended recipients can read messages

- **Cryptographic Guarantees:**
  - Forward secrecy
  - Post-compromise security

- **Scalability:**
  - Efficient large-group messaging
  - Multi-device support

- **Decentralization:**
  - Decentralized MLS Delivery and Authentication Service
  - No centralized service dependency

---

## 6. Cryptographic Approaches & Technical Proposals

### Soatok's "Private Airspaces for Bluesky"
**Article:** https://soatok.blog/2024/11/29/imagining-private-airspaces-for-bluesky/

**Main Proposals:**

#### 1. Limited Audience/Non-Public Content
- Posts accessible only to selected followers or custom "circles"
- Content encrypted while remaining on existing relays
- Ciphertext exists in same channels as public messages
- Only followers can decrypt and read

#### 2. Protocol-Native Direct Messages
- Encrypted messaging between users
- Stronger privacy guarantees than public posts

**Cryptographic Technologies:**

##### MLS (Messaging Layer Security)
- Establishes shared encryption keys for groups
- Bandwidth scales logarithmically to group size
- For 1 million users: only "21 KEMs invocations" per operation
- Extremely efficient at scale

##### HPKE (Hybrid Public Key Encryption)
- Combines key encapsulation with symmetric encryption
- Protects message contents
- Modern cryptographic standard

##### Digital Signatures
- Uses public keys from Bluesky's existing Decentralized Identifiers (DIDs)
- Authenticates participants
- Leverages existing infrastructure

**Implementation Approach:**
- Don't redesign architecture
- Encrypt content on existing infrastructure
- Secret keys remain on users' devices
- Key transparency protocols prevent relay operator access

**Secondary Opportunities:**
- Premium subscriptions
- Post-quantum cryptography protection
- Alternative payment mechanisms for creators

---

## 7. Personal Data & OAuth Implementation

### OAuth Scopes
**Specs:**
- Official OAuth Spec: https://atproto.com/specs/oauth
- Community Wiki: https://atproto.wiki/en/wiki/reference/networking/oauth
- OAuth for AT Protocol: https://docs.bsky.app/blog/oauth-atproto

**Current Scopes (Transitional):**
- `atproto` - Required for all atproto OAuth sessions (like `openid`)
- `transition:generic` - Broad permissions (similar to App Passwords)
  - Write access to create/update/delete any repository record type
  - Access to most Lexicon endpoints
- `transition:chat.bsky` - Access to direct messaging features

**Future:** Complete system of granular permission scopes planned

### Personal Data Server (PDS)
**Wiki:** https://atproto.wiki/en/wiki/reference/core-architecture/pds

**Purpose:**
- Main entry point and "digital home" for users
- Stores user's data repository and blobs
- Manages user identity
- Provides APIs for data queries and network interactions

**Functionality:**
- Hosts and manages user repositories
- Maintains Merkle Search Tree data structure
- Handles mutations and generates diffs

### Bookmarks Example
**PR:** https://github.com/bluesky-social/atproto/pull/4163

**Current Implementation:**
- Designed as private feature
- Only user can see their own bookmarks
- Stored **off-protocol** (not in ATProto repos)
- Will move on-protocol once private data support exists

---

## 8. Decentralized Identity & DIDs

### Identity Architecture
**Specs:**
- DID Spec: https://atproto.com/specs/did
- Identity Guide: https://atproto.com/guides/identity
- Community Wiki: https://atproto.wiki/en/wiki/reference/identifiers/did

### Dual Identifier System
1. **Handle:** Mutable, domain name format
2. **DID (Decentralized Identifier):** Immutable, W3C standard

**Resolution Flow:**
```
Handle → DID → DID Document → Signing Key + Hosting Service
```

### Supported DID Methods

#### DID:PLC
- Novel method developed by Bluesky Social
- Designed specifically for AT Protocol
- Features:
  - Key rotation
  - Account recovery
  - Service migration

#### DID:Web
- Standard W3C DID method
- Uses DNS/web infrastructure
- Migration discussion: https://github.com/bluesky-social/atproto/discussions/2705

### Verification & Attestation
**Structure:**
- Public signing key in `verificationMethod` array
- Object with `id` ending in `#atproto`
- `controller` matches the DID
- `type` is `"Multikey"`

**Benefits:**
- Maintain identity across handles or service providers
- Cryptographically verify content
- Migrate between PDSes while preserving identity and social graph

**SDKs:**
- TypeScript: https://www.npmjs.com/package/@atproto/identity
- Python: https://atproto.blue/en/latest/atproto_identity/index.html

---

## 9. Blockchain & Smart Contract Verification

### Key Finding: ATProto is NOT a Blockchain

**FAQ:** https://atproto.com/guides/faq

**Clarification:**
- ATProto is a **federated protocol**
- NOT a blockchain
- Does NOT use blockchain technology
- Uses cryptography but not cryptocurrency

**Verification Approach:**
- Domains map to cryptographic URLs
- User data in signed data repositories
- Service auth tokens as asymmetrically signed JWTs
- Native ATProto verification systems (not blockchain-based)

### Age Verification (Current Implementation)

**Articles:**
- Working with UK Government: https://bsky.social/about/blog/07-10-2025-age-assurance
- Approach to Age Assurance: https://bsky.social/about/blog/09-10-2025-age-assurance-approach
- TechCrunch (Ohio): https://techcrunch.com/2025/09/29/bluesky-rolls-out-age-verification-for-users-in-ohio/

**Current Solution:**
- Uses **Epic Games' Kids Web Services (KWS)**
- Methods: Credit card verification, ID scans, face scans
- Enabled in: UK, South Dakota, Wyoming, Ohio

**Methods:**
- Facial recognition (age estimation)
- Government-issued ID uploads (passport, driver's license)
- Payment card checks with age eligibility databases

**Privacy Concerns:**
- Requires sharing full identity (not just proof of age)
- Third-party service involvement
- No cryptographic proofs found

**Missing:** No evidence of privacy-preserving age verification methods like:
- Zero-knowledge proofs
- Cryptographic age attestations
- Blockchain-based badges/credentials
- Smart contract verification

### Potential Future: Cryptographic Attestations

**Related Technology (not ATProto-specific):**
- Ethereum Attestation Service (EAS): https://attest.org/
- Could theoretically bridge to ATProto DIDs in future
- No current integration or proposals found

---

## 10. Comparison with Other Protocols

### ActivityPub/Mastodon

**Discussion:** https://github.com/bluesky-social/atproto/discussions/1716

**Key Differences:**

#### Architecture
- **ActivityPub:** Traditional message-passing (like email, XMPP)
- **ATProto:** "Shared heap" - data in one global pool

#### Private Messages
- **ActivityPub/Mastodon:** "About as private as email"
  - Admin can read DMs (but hopefully doesn't)
  - Not end-to-end encrypted
- **Bluesky:** Currently centralized, not E2EE, not federated

#### Account Portability
- **ATProto:** Core feature via signed data repositories + DIDs
- **ActivityPub:** Difficult to retrofit (major reason for new protocol)

**Further Reading:**
- First impressions of AT Protocol: https://educatedguesswork.org/posts/atproto-firstlook/
- Tim Bray's analysis: https://www.tbray.org/ongoing/When/202x/2023/04/28/Bluesky
- How decentralized is Bluesky: https://dustycloud.org/blog/how-decentralized-is-bluesky/

### Matrix & XMPP

**Comparison Resources:**
- XMPP vs Matrix: https://www.process-one.net/blog/xmpp-matrix/
- Matrix FAQ: https://matrix.org/faq/

**Encryption:**
- **Matrix:** Built-in E2EE (Olm and Megolm libraries)
- **XMPP:** TLS + SASL, E2EE via OMEMO extension

**ATProto Position:**
- Considering MLS as foundation
- Matrix working to become MLS-compatible
- Potential: "Linearized Matrix running on top of MLS"

---

## 11. Key Technical Resources

### Official Specifications
- AT Protocol Main: https://atproto.com/
- Full Specs: https://atproto.com/specs/atp
- Repository Spec: https://atproto.com/specs/repository
- Cryptography Spec: https://atproto.com/specs/cryptography
- Official Docs: https://docs.bsky.app/docs/advanced-guides/atproto

### Wikipedia & Overview Articles
- AT Protocol Wikipedia: https://en.wikipedia.org/wiki/AT_Protocol
- AT Protocol Bluesky Paper: https://dl.acm.org/doi/abs/10.1145/3694809.3700740

### GitHub Discussions (Essential Reading)

#### Encryption & Private Content
- **Main Discussion:** https://github.com/bluesky-social/atproto/discussions/121
  - Core discussion on encryption for private content
  - Team's thinking on not putting encrypted data in public repos
  - MLS as leading candidate

#### Private Accounts
- **Discussion #1409:** https://github.com/bluesky-social/atproto/discussions/1409
  - Support for private accounts
  - Technical challenges with decentralization

#### Direct Messages
- **Discussion #1728:** https://github.com/bluesky-social/atproto/discussions/1728
  - Direct messages proposals and discussion

#### Private Non-Shared Data
- **Discussion #3363:** https://github.com/bluesky-social/atproto/discussions/3363
  - Private, non-shared data in repo
  - Personal-private vs shared-private distinction

#### Developer Projects
- **Discussion #3049:** https://github.com/bluesky-social/atproto/discussions/3049
  - Call for developer projects
  - Community building on ATProto

#### Verification
- **Discussion #3795:** https://github.com/bluesky-social/atproto/discussions/3795
  - Building verification for self-hosted instances

### Python SDK
- Direct Messages (Chats): https://atproto.blue/en/latest/dm.html
- DID Document: https://atproto.blue/en/latest/atproto_core/did_doc.html

### Community Resources
- ATProto Community Wiki: https://atproto.wiki/
- AtmosphereConf 2025 Discussions: https://atprotocol.dev/atmosphereconf-2025-discussions/
- AT Protocol Community Fund: https://atprotocol.dev/introducing-at-protocol-community-fund/

### OpenMLS Implementation
- OpenMLS: https://openmls.tech/
- Open Tech Fund Article: https://www.opentech.fund/news/messaging-layer-security-protocol-the-next-generation-of-secure-messaging-technology/

---

## 12. Current Gaps & Opportunities

### What's Missing

#### No Privacy-Preserving Verification
- No zero-knowledge proofs for age/credential verification
- No cryptographic attestations that preserve privacy
- No blockchain-based badges (by design - ATProto doesn't use blockchain)
- Current age verification requires full identity disclosure

#### No Native Private Content Yet
- All private features currently off-protocol or proprietary
- DMs not part of ATProto specification
- No private posts or limited-audience posts
- No private accounts

#### Limited Personal Data Support
- Bookmarks and preferences stored off-protocol
- Waiting for OAuth scopes + shared data implementation
- No standard for client-side encryption of personal data

### Opportunities for Innovation

#### Privacy-Preserving Attestations
- **Opportunity:** Build ZKP-based credential system that works with ATProto DIDs
- **Use Cases:** Age verification, professional credentials, membership badges
- **Approach:** External attestation service that verifies without revealing identity
- **Challenge:** Integration with DID system and resolver infrastructure

#### Encrypted Personal Data Layer
- **Opportunity:** Client-side encrypted storage for bookmarks, preferences, drafts
- **Approach:** Encrypt data before storing in PDS, keys derived from user credentials
- **Challenge:** Key management, recovery, multi-device sync

#### Privacy-Preserving Social Graph
- **Opportunity:** Hidden follows, private blocklists, encrypted friend lists
- **Approach:** Cryptographic commitments, selective disclosure
- **Challenge:** Balance privacy with protocol transparency requirements

#### Group Chat Innovation
- **Opportunity:** Build on MLS for feature-rich group messaging
- **Use Cases:** Private communities, paid subscriber groups, ephemeral groups
- **Approach:** Leverage upcoming ATMessaging Proto spec
- **Challenge:** Integration with existing ATProto infrastructure

#### Cross-Protocol Bridges
- **Opportunity:** Bridge ATProto E2EE messaging with Matrix, Signal, etc.
- **Approach:** MLS as common foundation
- **Challenge:** Identity mapping, trust boundaries

---

## 13. Implementation Recommendations

### For Developers Building on ATProto

#### Short-Term (Now - Q2 2025)
1. **Monitor OAuth Scopes Implementation**
   - Track: https://github.com/bluesky-social/atproto/discussions/4118
   - Prepare apps to adopt granular permissions
   - Plan migration from App Passwords

2. **Explore Third-Party E2EE**
   - Integrate with Germ DM or similar
   - Build messaging features with future migration path
   - Use MLS if building custom solution

3. **Store Private Data Off-Protocol**
   - Follow Bluesky's bookmarks approach
   - Encrypt client-side if needed
   - Plan migration to on-protocol when available

#### Medium-Term (Q2-Q4 2025)
1. **Participate in Working Groups**
   - Join E2EE Messaging WG: https://atproto.wiki/en/working-groups/e2ee
   - Join Private Data WG
   - Contribute to ATMessaging Proto spec

2. **Prepare for Shared Data Support**
   - Design features assuming future private data support
   - Consider OAuth scope requirements
   - Plan for eventual migration

3. **Experiment with Cryptographic Primitives**
   - MLS implementations (OpenMLS)
   - HPKE for hybrid encryption
   - Key transparency systems

#### Long-Term (2026+)
1. **Native E2EE Integration**
   - Adopt official ATProto E2EE when available
   - Migrate from third-party solutions
   - Leverage protocol-native features

2. **Private Content Features**
   - Limited-audience posts
   - Private accounts
   - Encrypted communities

3. **Advanced Privacy Features**
   - Zero-knowledge credentials
   - Privacy-preserving verification
   - Selective disclosure systems

---

## 14. Open Questions & Research Areas

### Protocol Design Questions

1. **Metadata Protection**
   - How to prevent enumeration of private group participants?
   - Can metadata be protected while maintaining discoverability?
   - What's the tradeoff between privacy and moderation?

2. **Key Management**
   - How to handle key rotation for large groups?
   - What recovery mechanisms for lost keys?
   - Multi-device sync without key exposure?

3. **Moderation in Private Spaces**
   - How to enable reporting of private content?
   - Can moderation work without breaking E2EE?
   - What's the role of server operators?

### Technical Challenges

1. **Scale of Private Groups**
   - Can MLS scale to millions of participants?
   - What's the performance impact on mobile devices?
   - How to optimize for bandwidth-constrained networks?

2. **Cross-Service Private Content**
   - How do private posts work across different ATProto apps?
   - Can E2EE messages work between different PDS implementations?
   - What happens when services federate private content?

3. **Backwards Compatibility**
   - How to migrate existing DMs to new E2EE system?
   - Can old clients view private content after protocol upgrade?
   - What's the transition plan?

### Privacy Innovation

1. **Zero-Knowledge Credentials**
   - Can ZKPs integrate with ATProto DIDs?
   - What's the user experience for proof generation?
   - How to prevent replay attacks?

2. **Private Discovery**
   - How to find private groups without exposing membership?
   - Can search work over encrypted content?
   - What about algorithmic feeds for private posts?

3. **Forward-Looking Privacy**
   - Post-quantum cryptography timeline?
   - How to future-proof key formats?
   - What about quantum-resistant signatures?

---

## 15. Summary of Resources by Category

### Must-Read Articles
1. Paul Frazee's Private Data Concepts: https://pfrazee.leaflet.pub/3lzhmtognls2q
2. Paul Frazee's Three Schemes: https://pfrazee.leaflet.pub/3lzhui2zbxk2b
3. Soatok's Private Airspaces: https://soatok.blog/2024/11/29/imagining-private-airspaces-for-bluesky/
4. 2025 Protocol Roadmap: https://docs.bsky.app/blog/2025-protocol-roadmap-spring

### GitHub Discussions (Priority)
1. Encryption for private content: https://github.com/bluesky-social/atproto/discussions/121
2. Support for Private Accounts: https://github.com/bluesky-social/atproto/discussions/1409
3. Private, non-shared data in repo: https://github.com/bluesky-social/atproto/discussions/3363
4. Progress on Auth Scopes: https://github.com/bluesky-social/atproto/discussions/4118
5. Direct Messages: https://github.com/bluesky-social/atproto/discussions/1728

### Community Projects
1. ATMessaging Proto: https://github.com/ATProtocol-Community/atmessaging-proto
2. Germ DM: https://www.germnetwork.com/blog/germdm-atproto-now-beta
3. AT Protocol Community Wiki: https://atproto.wiki/

### Official Specifications
1. AT Protocol: https://atproto.com/
2. OAuth: https://atproto.com/specs/oauth
3. DID: https://atproto.com/specs/did
4. Cryptography: https://atproto.com/specs/cryptography

### Standards & Protocols
1. MLS RFC 9420: https://datatracker.ietf.org/doc/rfc9420/
2. MLS Overview: https://messaginglayersecurity.rocks/
3. OpenMLS: https://openmls.tech/

### Media Coverage
1. Germ DM Launch (TechCrunch): https://techcrunch.com/2025/07/30/germ-brings-end-to-end-encrypted-messages-to-bluesky/
2. What's Next for ATProto (TechCrunch): https://techcrunch.com/2025/03/26/whats-next-for-atproto-the-protocol-powering-bluesky-and-other-apps/
3. Bluesky Age Verification: https://bsky.social/about/blog/07-10-2025-age-assurance

---

## Conclusion

Private data on ATProto is in a transitional phase. The protocol was designed for public content first, with private data as a second phase. The community is actively working on solutions:

**Current State:**
- Third-party E2EE solutions (Germ DM) filling the gap
- Community specifications under development (ATMessaging Proto)
- Working groups forming and collaborating
- Official roadmap has clear phases

**Near Future (2025-2026):**
- OAuth scopes completion
- Shared data implementation
- MLS-based E2EE messaging
- Private accounts and content

**Key Technology:** MLS (Messaging Layer Security) is the clear winner for encrypted messaging, with broad community and protocol team support.

**Innovation Opportunities:** Privacy-preserving credentials, ZKP-based verification, encrypted personal data layers, and cross-protocol bridges remain largely unexplored in the ATProto ecosystem.

**Note on Blockchain:** ATProto explicitly does NOT use blockchain or cryptocurrency. All cryptographic verification uses standard public-key cryptography, DIDs, and signed data repositories. Any blockchain-based verification would need to be a separate layer that bridges to ATProto DIDs.

---

**Research Compiled:** November 9, 2025
**Next Steps:** Monitor working group progress, test Germ DM beta, contribute to ATMessaging Proto specification
