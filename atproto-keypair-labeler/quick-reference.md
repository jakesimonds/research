# ATProto Labeler Quick Reference

## Your Questions Answered

### 1. What are labelers in ATProto?
Self-authenticating annotation services that apply labels to content and accounts. Each labeler has a DID, signing key, and service endpoint. Users can subscribe to up to 20 labelers.

### 2. How do labeler services work?
```
Firehose → Labeler consumes stream → Applies logic → Signs labels → Distributes to App Views/PDS
```

### 3. How do they scan the firehose?
Subscribe to `com.atproto.sync.subscribeRepos` at `wss://bsky.network`. Receive all network events (posts, profiles, follows, etc.) in real-time. Must process client-side.

### 4. Can they query/search for specific data patterns?
**NO.** Major limitation:
- No server-side filtering
- No query interface
- Must consume entire firehose (1000+ events/sec)
- 99%+ wasted data for targeted searches
- One dev reported 6TB/month just to filter specific events

### 5. Is finding specific content efficient or "needle in haystack"?
**Needle in haystack.** Extremely inefficient for:
- Finding existing profiles with patterns
- Searching historical data
- Querying specific user data

Developer quote: *"Subscribing to a torrential full-network firehose (over a thousand events per second), just to pluck out a handful of individual events"*

### 6. What data can labelers access?
**From firehose:**
- All public posts, likes, follows, blocks
- User profiles (name, bio, avatar)
- Account metadata (DID, handle)
- Timestamps and relationships

**From DID resolution:**
- Public signing keys
- Service endpoints
- PDS location

**CANNOT access:**
- Private messages
- Encrypted data
- User credentials

---

## Key Concerns & Controversies

### Harassment & Tracking
- **Issue #19:** Labels used to target groups for harassment
- "Jesse Singal Watch" labeler tracked followers
- "Follow Tracker" shutdown due to misuse
- Community guidelines updated to prohibit label abuse

### Leadership Controversies
- **"Waffles" incident (Oct 2025):** CEO mocked users' moderation concerns
- **July 2023 crisis:** Slow response to racist usernames
- Trust & safety concerns during rapid growth

### Privacy Issues
- **Private School Labeler:** Tagged users without consent
- **1M post scraping (2024):** Firehose enables massive data collection
- No way to opt-out of public data access

### Scale Challenges
- **1.75M harassment reports in 2024** (17x increase)
- Moderation team: ~100 people
- Platform growing faster than moderation capacity

---

## Official Documentation

### Core Specs
- **Label Spec:** https://atproto.com/specs/label
- **Firehose:** https://docs.bsky.app/docs/advanced-guides/firehose
- **Sync Spec:** https://atproto.com/specs/sync
- **Moderation Guide:** https://docs.bsky.app/docs/advanced-guides/moderation

### Code Repositories
- **Ozone (Official):** https://github.com/bluesky-social/ozone
- **Starter Kit:** https://github.com/aliceisjustplaying/labeler-starter-kit-bsky
- **Lightweight:** https://github.com/skyware-js/labeler
- **Examples:** https://github.com/astrabun/sonasky

### Key Discussions
- **March 2024 Updates:** https://github.com/bluesky-social/atproto/discussions/2293
- **Firehose Filtering:** https://github.com/bluesky-social/atproto/discussions/2418
- **Label Abuse Prevention:** https://github.com/bluesky-social/proposals/issues/19

### GitHub Issues
- **#3134:** Need automated spam labeler
- **#2803:** Large label sets hit size limits
- **#2367:** Label behavior bug
- **#7076:** Block list abuse

### Reports & Blog Posts
- **2024 Moderation Report:** https://bsky.social/about/blog/01-17-2025-moderation-2024
- **Trust & Safety Update:** https://bsky.social/about/blog/09-18-2024-trust-safety-update
- **Jetstream (Efficiency):** https://docs.bsky.app/blog/jetstream
- **Labeler Grants:** https://docs.bsky.app/blog/label-grants

---

## For Your Keypair Use Case

### ❌ DON'T: Use labeler to find public keys in firehose
- Extremely inefficient
- Can't search existing profiles
- High bandwidth costs
- Unreliable

### ✅ DO: Use these approaches instead

**Option 1: DID Documents**
- DIDs already have public keys in `verificationMethod`
- Standard, efficient, queryable
- But: Intended for signing, not custom keys

**Option 2: Custom Record Type**
```typescript
// Define: app.yourapp.crypto.pubkey
// Subscribe to just this collection
// Much more efficient than scanning all profiles
```

**Option 3: Separate Service + Labels**
```
User → Register pubkey → Your indexed DB
Your service → Validate → Apply label
Others → See verification badge
```

### Recommended Pattern
1. **Discovery:** Your own service (indexed, queryable)
2. **Validation:** Your logic (Aztec proofs, etc.)
3. **Labeling:** Apply verification badge to validated users

**Separation of concerns = Better architecture**

---

## Code Examples

### Python Firehose Consumer
```python
from atproto import FirehoseSubscribeReposClient, parse_subscribe_repos_message

client = FirehoseSubscribeReposClient()

def on_message_handler(message) -> None:
    parsed = parse_subscribe_repos_message(message)
    for op in parsed.ops:
        if op.path.startswith('app.bsky.actor.profile'):
            # Process profile updates
            pass

client.start(on_message_handler)
```

### TypeScript Firehose Consumer
```typescript
import { subscribeRepos } from 'atproto-firehose'

const client = subscribeRepos(`wss://bsky.network`, {
  decodeRepoOps: true
})

client.on('commit', (evt) => {
  for (const op of evt.ops) {
    if (op.action === 'create' && op.path.startsWith('app.yourapp.crypto.pubkey/')) {
      // Process custom pubkey records
    }
  }
})
```

---

## Bottom Line

**Labelers are for annotation, not discovery.**

If you need to find specific data:
1. Build an index
2. Use custom record types
3. Query your own service
4. Apply labels to results

The firehose is a real-time stream, not a searchable database.
