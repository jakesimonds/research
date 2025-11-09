# Real did:web Examples in ATProto/Bluesky

## Confirmed Real-World Examples

### 1. Bluesky Chat Service
```
did:web:api.bsky.chat
```
- **Purpose**: Bluesky's official chat/DM service
- **Usage**: Used in service proxying headers for chat requests

### 2. Feed Generators
Feed generators can use did:web when hosted on custom domains:
```
did:web:feeds.example.com
did:web:your-domain.com
```

### 3. Labeling Services
```
did:web:labeler.example.com#atproto_labeler
```
- **Purpose**: Content moderation/labeling services

## did:web Format in ATProto

**Supported:**
```
did:web:example.com
did:web:subdomain.example.com
```

**NOT Supported:**
- Path-based DIDs like `did:web:example.com:user:alice` are NOT supported in ATProto
- Only hostname-level did:web DIDs work

## How to Find More Examples

1. **Query a PDS for did:web repos:**
   ```bash
   curl "https://bsky.social/xrpc/com.atproto.sync.listRepos" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     | jq '.repos[] | select(.did | startswith("did:web:"))'
   ```

2. **Check pdsls.dev:**
   - Browse repositories and filter by DID type

3. **Look for self-hosted PDS instances:**
   - Self-hosted PDS operators often use did:web for their domain-based identity

## Why did:web is Less Common

- **did:plc is default**: Most users have `did:plc:...` identifiers
- **Migration issues**: did:web ties identity to domain ownership (lose domain = lose identity)
- **Services preferred**: did:web is more common for services than personal accounts

## did:web vs did:plc

| Feature | did:web | did:plc |
|---------|---------|---------|
| Format | `did:web:domain.com` | `did:plc:random123abc` |
| Control | Domain owner | Cryptographic keys |
| Migration | Cannot migrate domain | Can migrate hosts |
| Common for | Services, feed generators | User accounts |

## Resources

- **Setup tool**: https://atproto-did-web.lukeacl.com/
- **GitHub repo**: https://github.com/lukeacl/atproto-did-web
- **Docs**: https://atproto.com/specs/did

## Example Use Cases

1. **Feed Generator on your domain:**
   - Host at `feeds.yourdomain.com`
   - DID: `did:web:feeds.yourdomain.com`

2. **Self-hosted PDS:**
   - Host at `pds.yourdomain.com`
   - DID: `did:web:pds.yourdomain.com`

3. **Service endpoints:**
   - Chat: `did:web:api.bsky.chat`
   - Labeler: `did:web:labeler.yourdomain.com`

---

**Created:** 2025-11-09
**Note:** did:web accounts are relatively rare in the Bluesky ecosystem. Most accounts use did:plc.
