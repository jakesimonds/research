# ATProto/Bluesky Labeler Services - Comprehensive Research Report

**Research Date:** 2025-11-12
**Focus:** Understanding labeler capabilities, firehose scanning, data access, and controversies

---

## Executive Summary

ATProto labelers are moderation/annotation services that consume the network firehose and apply labels to content and accounts. While powerful for moderation, they face significant challenges around efficiency ("needle in haystack" problem), privacy concerns, and potential for misuse. Finding specific data patterns like public keys in the firehose is **technically possible but highly inefficient** without proper indexing.

---

## 1. What Are Labelers in ATProto?

### Definition
Labelers produce "self-authenticating string annotations" on accounts or content for moderation and other purposes. They are a new type of server in the ATProto network architecture.

### Core Characteristics
- Each labeler has its own **service identity (DID)** that appears in the label source field
- Labels can be applied to:
  - Posts
  - Images/media
  - User accounts
  - Profile data
  - Any repository record

### Use Cases
**Moderation:**
- Identifying spam
- Marking inappropriate content
- Account-level warnings

**Informational/Entertainment:**
- Labeling post topics
- User pronouns
- GitHub repositories contributed to
- Elements/categories (Earth, Fire, Water, Air)
- Any custom metadata

### Key Technical Detail
The `val` field is core to each label. The protocol keeps semantics flexible, with current recommendation being lower-case kebab-syntax (e.g., `spam-account`, `nsfw-content`), max 128 bytes.

---

## 2. How Labeler Services Work

### Architecture

```
Firehose (Relay) → Labeler Service → Signed Labels → App Views / PDS
```

1. **Service Identity:**
   - Labeler DID document contains:
     - `#atproto_label` - signing key (distinct from repo signing key)
     - `#atproto_labeler` - service endpoint URL

2. **Label Signing:**
   - Labels use public-key cryptography
   - Signature process:
     - Construct complete label using schema fields
     - Encode in CBOR (DAG-CBOR normalization)
     - Hash with SHA-256
     - Sign hash bytes with `#atproto_label` key
   - Signatures validated when transferred between services

3. **Label Distribution:**
   - Two required endpoints:
     - `com.atproto.label.subscribeLabels` - realtime subscription
     - `com.atproto.label.queryLabels` - query interface
   - App Views and PDSes consume labels
   - Users subscribe to labelers (max 20 per user in Bluesky app)

4. **Setup Process:**
   - Publish an `app.bsky.labeler.service` record
   - "Converts" account into a labeler
   - Becomes discoverable to users

### Implementation Options

**Ozone (Official):**
- Bluesky's open-source labeler service
- Professional-grade tooling
- Web interface for manual labeling
- Supports automated rules

**Lightweight Alternatives:**
- `skyware-js/labeler` - TypeScript/Node.js
- Custom implementations using ATProto SDK

---

## 3. How Labelers Scan the Firehose

### Firehose Basics

The firehose is the network-wide stream of all repository updates, available at:
- **Relay endpoint:** `wss://bsky.network` (Bluesky's main relay)
- **Protocol:** `com.atproto.sync.subscribeRepos`

### Data Flow

```
PDS → Relay → Firehose → Labelers/Feed Generators/Apps
```

Relays continuously:
1. Crawl network by fetching repository updates from PDSes
2. Aggregate and index updates
3. Forward into network-wide data stream (firehose)

### What Events Are Included

**Event Types:**
1. **#commit** - Repository mutations
   - Create/update/delete operations on records
   - Examples: "create post", "create like", "delete follow"

2. **#identity** - Identity updates
   - Handle changes
   - Signing key updates
   - PDS hosting endpoint changes

3. **#account** - Account status changes
   - Takendown, suspended, deleted, deactivated

**Commit Event Structure:**
```json
{
  "seq": 123456,
  "time": "2024-...",
  "did": "did:plc:...",
  "commit": {
    "ops": [
      {
        "action": "create|update|delete",
        "path": "app.bsky.feed.post/...",
        "cid": "...",
      }
    ],
    "blocks": "CAR file bytes"
  }
}
```

### Collections Labelers Can Monitor

- `app.bsky.feed.post` - Posts
- `app.bsky.feed.like` - Likes
- `app.bsky.graph.follow` - Follows
- `app.bsky.actor.profile` - User profiles
- `app.bsky.feed.repost` - Reposts
- Any other repository record type

### Example Code (Python)

```python
from atproto import FirehoseSubscribeReposClient, parse_subscribe_repos_message

client = FirehoseSubscribeReposClient()

def on_message_handler(message) -> None:
    parsed = parse_subscribe_repos_message(message)
    # Process repository operations
    # Apply labels as needed

client.start(on_message_handler)
```

### Example Code (TypeScript/Node.js)

```typescript
import { subscribeRepos } from 'atproto-firehose'

const client = subscribeRepos(`wss://bsky.network`, {
  decodeRepoOps: true
})

client.on('commit', (evt) => {
  // Process commit events
  // Scan for patterns
  // Apply labels
})
```

---

## 4. Can Labelers Query/Search for Specific Data Patterns?

### Short Answer: **No efficient search mechanism exists**

### The "Needle in Haystack" Problem

#### Current Reality

Labelers must **consume the entire firehose** and filter client-side:
- ✗ No server-side filtering (as of 2024-2025)
- ✗ No query API for specific patterns
- ✗ No indexing of content by default

#### Real-World Impact

From developer reports:
- **">99% of the data from the firehose is completely ignored"** for most use cases
- One developer: **"6TB of data usage in March"** just to extract relevant events
- Developers "subscribing to a torrential full-network firehose (**over a thousand events per second**), just to pluck out a handful of individual events"

#### Volume Stats
- ~100 posts per second (as of recent data)
- Hundreds to thousands of combined events per second
- Exponentially growing as network scales

### Partial Solution: Jetstream

**Problem it addresses:** Inefficient consumption of full firehose

**How Jetstream helps:**
- Server-side Jetstream consumes firehose
- Fans out to many subscribers
- **Supports filtering** by:
  - Collections (e.g., only `app.bsky.feed.post`)
  - Specific repos/DIDs
- Surfaces events as simple JSON (vs binary format)

**Limitations:**
- Still requires knowing what to filter for
- Not suitable for "find any profile containing X pattern"
- Must define filters upfront

### For Finding Public Keys

**Scenario:** Labeler wants to find users with specific public key patterns in their profiles

**Challenges:**
1. **No profile content indexing** - Must process every profile update
2. **Profile fields available:**
   - `displayName` - User's display name
   - `description` - Free-form text bio
   - `avatar` - Image blob
   - Custom fields would need to be in description text

3. **Detection approach:**
   ```python
   def on_message_handler(message):
       parsed = parse_subscribe_repos_message(message)
       for op in parsed.ops:
           if op.path.startswith('app.bsky.actor.profile'):
               # Check if description contains public key pattern
               if 'pubkey:' in op.record.get('description', ''):
                   # Found potential match
                   apply_label(parsed.did, 'has-public-key')
   ```

4. **Problems:**
   - Must scan **every profile creation/update** event
   - Cannot query "show me all profiles with public keys"
   - **Extremely inefficient** for existing accounts
   - Only catches changes going forward, not existing state

### Accessing DID Documents

**Better approach for public keys:**

DID documents already contain public keys in `verificationMethod`:

```json
{
  "id": "did:plc:abc123",
  "verificationMethod": [{
    "id": "did:plc:abc123#atproto",
    "type": "Multikey",
    "controller": "did:plc:abc123",
    "publicKeyMultibase": "..."
  }]
}
```

**But:**
- These are for **account signing**, not custom application keys
- Adding custom keys to DID docs is not standard practice
- Would require PDS cooperation

---

## 5. Efficiency Assessment: Finding Specific Content

### Overall Rating: ⭐ (Very Inefficient)

### Breakdown by Scenario

| Scenario | Efficiency | Notes |
|----------|-----------|-------|
| Moderate new posts in real-time | ⭐⭐⭐⭐ | Good - primary use case |
| Find patterns in new content as it's created | ⭐⭐⭐ | Okay - with Jetstream filtering |
| Search existing content/profiles | ⭐ | Very poor - must process everything |
| Find specific users with data patterns | ⭐ | Very poor - no indexing |
| Query historical data | ⭐ | Very poor - need separate index |

### Why It's Inefficient

1. **Volume Problem:**
   - Network produces hundreds of events/second
   - Growing exponentially with adoption
   - Most data irrelevant to most labelers

2. **No Query Interface:**
   - Can't ask "show me profiles with X"
   - Can't filter by content patterns server-side
   - Must consume and filter locally

3. **Bandwidth Costs:**
   - 6TB/month reported by one developer
   - 99%+ wasted bandwidth for targeted use cases

4. **Latency:**
   - Can't immediately find if something exists
   - Must wait for it to appear in stream
   - Or process entire history

### Developer Feedback

From GitHub discussion #2418:
> "Server-side firehose/stream filtering is desired for the future, though it's not yet available in a comprehensive way."

This is a **known limitation** acknowledged by the ATProto team.

---

## 6. What Data Can Labelers Access?

### From Firehose Events

**User Profile Data (`app.bsky.actor.profile`):**
- Display name
- Description/bio (free text)
- Avatar image (as blob reference)
- Banner image (as blob reference)
- Profile creation/update timestamps

**Post Data (`app.bsky.feed.post`):**
- Post text
- Embedded media references
- Reply/quote metadata
- Creation timestamp
- Author DID

**Social Graph Data:**
- Follows (`app.bsky.graph.follow`)
- Blocks (`app.bsky.graph.block`)
- Lists (`app.bsky.graph.list`)
- Likes (`app.bsky.feed.like`)

**Account Metadata:**
- DID
- Handle
- Timestamps

### From DID Documents

Labelers can resolve any DID to get:
- Public signing keys (`verificationMethod`)
- Service endpoints
- Handle verification
- PDS location

**Resolution methods:**
- `did:plc` → HTTPS request to PLC directory
- `did:web` → HTTPS request to domain `/.well-known/did.json`

### What Labelers CANNOT Access

- ✗ Private messages/DMs
- ✗ Encrypted data
- ✗ User passwords/credentials
- ✗ Server-side private data
- ✗ Non-public repository records (if they exist)

### Privacy Note

**Everything in the firehose is PUBLIC:**
- All posts, profiles, follows are public by design
- No expectation of privacy for public actions
- Labels themselves are also public

---

## 7. Concerns and Controversies About Labelers

### Major Concerns Identified

#### A. Harassment and Targeting (GitHub Proposal #19)

**The Problem:**
> "How to prevent labels being used to target abuse?"

**Scenario:**
- Hostile group creates labeler
- Algorithmically labels all posts/members of targeted group
- Uses label to coordinate harassment
- Groups tag users with derogatory labels

**Example:**
- "Jesse Singal Watch" labeler tagged followers of controversial figure
- Badge interpreted as "warning" about tolerance of bigotry
- Users unaware of how labels affected their reputation
- Labeler description: "TEMPORARILY CLOSED FOR MAINTENANCE" (as of research date)

**Official Response:**
Updated Community Guidelines now prohibit:
- Using labels for harassment
- Accepting compensation for specific labeling actions
- Abusing Bluesky features like lists and labels
- Bad-faith mass reporting

#### B. Privacy and Tracking

**Follow Tracking:**
- Labelers can track who follows whom
- Create networks of associations
- Tag users based on their follows
- Users may not consent to this surveillance

**Quote from earlier search:**
> "A labeler tool called 'Follow Tracker' that showed who was following prominent racists, transphobes, and alt-right figures shut down, with its operator claiming this was 'because some of you can't be trusted to use this information reasonably and responsibly'."

#### C. Data Scraping Concerns

**The "Private School Labeler" Case:**
- Tagged British public figures with private school info
- Included annual tuition fees
- Some labeled individuals expressed discomfort
- Questions about consent and boundaries

**Broader Issue:**
- Firehose API enables massive data scraping
- 2024: Hugging Face employee scraped 1M posts for AI research
- Bluesky acknowledged limitations
- Working on consent preferences, but **enforcement outside ecosystem is impossible**

#### D. Scale and Volume Issues

**From GitHub:**

**Issue #2803:** "Request entity too large"
- Labelers with 500+ label definitions hit size limits
- Can't add new labels or translations
- Affects internationalization

**Issue #3134:** "Need automated spam labeler"
- Spammers show up en masse
- Respond to keywords (GoFundMe URLs, etc.)
- Manual moderation can't keep up

#### E. Leadership Response Controversies

**The "Waffles" Incident (October 2025):**

**What happened:**
1. User asked CEO Jay Graber about banning Jesse Singal (writer criticized for trans coverage)
2. Graber replied: "WAFFLES!" with waffle picture
3. CTO Paul Frazee defended: "if the guy doesn't break the rules we don't ban"
4. When users suggested apology, Graber said: "You could try a poster's strike. I hear that works"

**Impact:**
- Seen as minimizing marginalized users' concerns
- Perceived as mocking those wanting transphobia-free platform
- Damaged trust in leadership
- Led to broader discussion about platform values

**Earlier Crisis (July 2023):**
- Trolls created accounts with racial slurs as usernames
- Admin response seen as slow
- Graber silent for 10 days except community guidelines repost
- Led to user "posting strike"

#### F. Moderation Statistics (2024)

**From Bluesky's 2024 Moderation Report:**
- **1.75 million reports** of harassment/trolling/intolerance
- Largest category of user reports
- **17x increase** in moderation reports overall
- Platform growing faster than moderation capacity

**Platform Response:**
- Moderation team grew to ~100 people
- Developing tools to detect multi-account abuse
- Building toxicity detection in replies
- Focus on group harassment and "dog-piling"

---

## 8. Technical Challenges and Limitations

### Server-Side Filtering

**Status:** Not available (as of 2024-2025)
**Impact:** Forces inefficient client-side filtering
**Future:** Acknowledged as desired feature

### Label Behavior Bugs

**Issue #2367:**
- Labels `!hide` and `!warn` took effect even from labelers not advertising them
- Security/privacy concern
- Indicates potential for unintended label propagation

### Starter Pack Integration

**Issue #2614:**
- Cannot add labelers to starter packs
- Limits discoverability
- User experience friction

### Custom Self-Labels Limitations

**Discussion #2885:**
- Self-labels require global definition
- Can't create personal labels without mod service
- Less flexible than expected

---

## 9. Official Documentation and Resources

### Primary Documentation

1. **Labels Specification:**
   - https://atproto.com/specs/label
   - Definitive technical spec

2. **Firehose Documentation:**
   - https://docs.bsky.app/docs/advanced-guides/firehose
   - https://atproto.com/specs/sync

3. **Moderation and Labels Guide:**
   - https://docs.bsky.app/docs/advanced-guides/moderation
   - https://docs.bsky.app/blog/blueskys-moderation-architecture

4. **API Documentation:**
   - `com.atproto.label.subscribeLabels`: https://docs.bsky.app/docs/api/com-atproto-label-subscribe-labels
   - `com.atproto.label.queryLabels`: https://docs.bsky.app/docs/api/com-atproto-label-query-labels
   - `com.atproto.sync.subscribeRepos`: Firehose subscription

### Code Repositories

1. **Ozone (Official Labeler):**
   - https://github.com/bluesky-social/ozone
   - "web interface for labeling content in atproto / Bluesky"

2. **Labeler Starter Kit:**
   - https://github.com/aliceisjustplaying/labeler-starter-kit-bsky
   - Quick start for custom labelers

3. **Lightweight Alternative:**
   - https://github.com/skyware-js/labeler
   - "A lightweight alternative to Ozone"

4. **Example Implementations:**
   - https://github.com/snarfed/self-labeler - Custom self-labels
   - https://github.com/astrabun/sonasky - Fursona labeler example
   - https://github.com/BasixKOR/bluesky-labeler - Personal labeler

### SDKs and Tools

1. **Python SDK:**
   - https://atproto.blue/en/latest/atproto_firehose/index.html
   - Firehose consumer examples

2. **TypeScript/Node.js:**
   - `@atproto/api` package
   - `atproto-firehose` package

3. **Jetstream:**
   - https://docs.bsky.app/blog/jetstream
   - Efficient firehose consumption

### Discussions and Issues

1. **Protocol Updates:**
   - https://github.com/bluesky-social/atproto/discussions/2293
   - March 2024 updates on labelers

2. **Firehose Filtering:**
   - https://github.com/bluesky-social/atproto/discussions/2418
   - "Querying/Filtering on the Firehose stream"

3. **Label Abuse Prevention:**
   - https://github.com/bluesky-social/proposals/issues/19
   - "How to prevent labels being used to target abuse?"

4. **Recent Issues:**
   - https://github.com/bluesky-social/atproto/issues/3134 - Automated spam labeler
   - https://github.com/bluesky-social/atproto/issues/2803 - Large label sets
   - https://github.com/bluesky-social/atproto/issues/2367 - Label behavior bug

### Community Resources

1. **Bluesky Labeler Directory:**
   - https://blueskydirectory.com/labelers/all
   - https://www.bluesky-labelers.io/

2. **Labeler Repository Scraping:**
   - https://github.com/mary-ext/bluesky-labeler-scraping
   - Tracks labeler changes

---

## 10. Assessment for Keypair/Public Key Use Case

### Original Question
> Can a labeler efficiently find users who have public keys in their profiles?

### Answer: **No, not efficiently**

### Why Not

1. **No indexing mechanism**
   - Must process entire firehose
   - Can't query existing profiles
   - Only catches new/updated profiles

2. **Volume problems**
   - Thousands of events per second
   - 99%+ irrelevant data
   - High bandwidth costs (TB/month)

3. **Profile limitations**
   - No standard field for custom public keys
   - Would need to parse description text
   - Unreliable and error-prone

4. **Timing issues**
   - Can only detect when profiles are created/updated
   - Existing profiles invisible until they update
   - Could miss users entirely

### Alternative Approaches

#### A. Use DID Documents Directly
**Pros:**
- DIDs already contain public keys
- Standard `verificationMethod` field
- Can query PLC directory or did:web domains
- No firehose scanning needed

**Cons:**
- Keys are for signing, not custom use
- Adding custom keys not standard practice
- Would need PDS modifications

#### B. Custom Profile Service
**Instead of labeler:**
- Build separate service
- Users explicitly register public keys
- Maintain your own index
- Much more efficient

**Implementation:**
```
User → Register pubkey → Your service DB
Your service → Apply label → User profile
Other users → Query your service → See verification
```

#### C. Repository Record Approach
**Create custom record type:**
- Define new lexicon (e.g., `app.yourapp.crypto.pubkey`)
- Users create records with their public keys
- Subscribe to firehose for these specific records
- Much more efficient than scanning profiles

**Example filter:**
```typescript
client.on('commit', (evt) => {
  for (const op of evt.ops) {
    if (op.path.startsWith('app.yourapp.crypto.pubkey/')) {
      // Process public key record
      const pubkey = op.record.key
      // Validate and label
    }
  }
})
```

### Recommendation

**Do NOT use labeler to find public keys via firehose scanning**

**Instead:**
1. Use DID documents for signing keys (if appropriate)
2. Create custom record type for app-specific keys
3. Build separate registration service
4. Use labeler ONLY to apply verification badges, not to discover keys

**Separation of concerns:**
- **Discovery:** Your own indexed service
- **Verification:** Your validation logic
- **Labeling:** Apply badge to verified users

This approach is:
- Much more efficient
- More reliable
- Standard practice in ATProto ecosystem
- Better user experience

---

## 11. Key Takeaways

### For Developers

1. **Labelers are powerful but specific-purpose**
   - Great for: Moderating content in real-time
   - Bad for: Searching existing data, indexing content

2. **Firehose is "fire hose" not "search index"**
   - Real-time stream, not queryable database
   - No server-side filtering (yet)
   - High volume, high bandwidth

3. **Build separate indexes for search**
   - Consume firehose → Your database
   - Query your index, not the firehose
   - Use labeler to apply results

4. **Follow ATProto patterns**
   - Custom record types for app data
   - DID documents for identity keys
   - Labelers for annotations, not discovery

### For Privacy-Conscious Users

1. **Everything public is REALLY public**
   - Firehose exposes all public actions
   - Multiple services can track you
   - Labels can be used to categorize/target

2. **Labeler concerns are real**
   - Harassment via labeling documented
   - Follow-tracking raises privacy issues
   - Limited control over who labels you

3. **Platform still maturing**
   - Moderation scaling issues
   - Leadership controversies
   - Some abuse mechanisms not fully addressed

### For the Use Case

**Original goal:** Aztec validation with keypairs

**Findings:**
- Labeler-based discovery: ❌ Not efficient
- DID document keys: ✅ Better approach
- Custom record type: ✅ Best approach
- Separate service + labels: ✅ Recommended pattern

---

## 12. Conclusion

ATProto labelers are a powerful moderation and annotation system, but they are **not designed for efficient data discovery or search**. The firehose provides real-time access to all public network activity, but querying or filtering for specific patterns (like public keys) is a "needle in haystack" problem with significant efficiency challenges.

For use cases requiring finding specific data patterns, the recommended approach is to:
1. Build a separate indexed service
2. Consume the firehose to populate your index
3. Use labelers to apply annotations based on your index
4. Consider custom record types for structured data

The platform faces ongoing challenges around harassment, privacy, and moderation at scale, with active development and community discussion around these issues.

---

**Report compiled from:** Web searches, official ATProto documentation, GitHub discussions, Bluesky blog posts, and community reports (November 2025)
