# Labeller Quickstart Guide

## TL;DR: Make Your Own Labeller in 30 Minutes

This is the fastest path to getting a working ATProto labeller for Aztec verification badges.

## What You'll Build

A labeller service that:
- Accepts verification requests from users
- Validates Aztec zero-knowledge proofs
- Applies verified badges to user profiles on Bluesky
- Allows users to subscribe and display badges

## Prerequisites

- [ ] Docker & Docker Compose installed
- [ ] Bluesky account (for the labeller service identity)
- [ ] Basic command line knowledge
- [ ] Domain name (or ngrok for testing)

## Quick Setup (5 minutes)

### 1. Clone the Labeller Repository

```bash
git clone https://github.com/bsky-watch/labeler.git
cd labeler
```

### 2. Configure Environment

```bash
# Copy example files
cp example.env .env
cp example_config.yaml config.yaml
```

### 3. Edit config.yaml

Create your verification badges:

```yaml
did: "did:plc:YOUR_DID_HERE"  # Your Bluesky DID
password: "YOUR_APP_PASSWORD"  # Generate at Bluesky settings

labels:
  - name: "aztec-verified"
    description: "Verified via Aztec zero-knowledge proof"

  - name: "age-verified"
    description: "Age verified using ZK proof (18+)"

  - name: "credential-verified"
    description: "Professional credentials verified via Aztec"

  - name: "member-verified"
    description: "Membership verified without revealing identity"
```

### 4. Generate Signing Key

```bash
# Generate a private key for signing labels
openssl ecparam -genkey -name secp256k1 -noout -out private-key.pem
openssl ec -in private-key.pem -text -noout

# Copy the private key hex to config.yaml under signing_key
```

### 5. Launch the Service

```bash
# Start the labeller
docker compose up --build -d

# Enable the API for label creation
cp docker-compose.override.example.yaml docker-compose.override.yaml
docker compose up -d
```

### 6. Register Your Labeller

```bash
# Register with PLC directory
docker compose exec labeler ./update-plc --config=/config.yaml
```

## Testing Locally (2 minutes)

### Create a Label via API

```bash
# Apply "aztec-verified" badge to a user
curl -X POST --json '{
  "uri": "did:plc:USER_DID_HERE",
  "val": "aztec-verified"
}' http://127.0.0.1:8081/label
```

### Check It Worked

```bash
# View logs
docker compose logs -f
```

You should see the label being created and published.

## Make It Public (10 minutes)

### Option A: Using ngrok (for testing)

```bash
# Install ngrok
npm install -g ngrok

# Create tunnel
ngrok http 8080

# Use the HTTPS URL as your service endpoint
```

### Option B: Production Deployment

1. **Get a domain**: yourservice.com
2. **Deploy to VPS**: Use Digital Ocean, AWS, etc.
3. **Set up HTTPS**: Use Let's Encrypt/Certbot
4. **Update DNS**: Point domain to your server
5. **Update config.yaml**: Set public endpoint URL

### Update Your DID Document

```bash
# Update with your public URL
docker compose exec labeler ./update-plc --config=/config.yaml --endpoint=https://yourservice.com
```

## Integrate Aztec Verification (15 minutes)

### Basic Verification Endpoint

Create `verify-service.js`:

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

// Verification endpoint
app.post('/verify', async (req, res) => {
  const { proof, publicInputs, userDid, verificationType } = req.body;

  try {
    // TODO: Actually verify the Aztec proof here
    // For now, we'll simulate verification
    const isValid = await verifyAztecProof(proof, publicInputs);

    if (isValid) {
      // Apply label via labeller API
      await applyLabel(userDid, verificationType);
      res.json({ success: true, message: 'Verification successful' });
    } else {
      res.status(400).json({ success: false, message: 'Invalid proof' });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

async function verifyAztecProof(proof, publicInputs) {
  // Placeholder: Replace with actual Aztec/Noir verification
  // Options:
  // 1. Call Noir verifier library
  // 2. Check on-chain verification contract
  // 3. Use Aztec SDK to validate proof

  console.log('Verifying proof...', { proof, publicInputs });

  // For testing, return true
  // In production, implement real verification
  return true;
}

async function applyLabel(userDid, labelType) {
  // Map verification type to label
  const labelMap = {
    'age': 'age-verified',
    'credential': 'credential-verified',
    'member': 'member-verified'
  };

  const label = labelMap[labelType] || 'aztec-verified';

  // Call labeller API
  await axios.post('http://localhost:8081/label', {
    uri: userDid,
    val: label
  });

  console.log(`Applied label ${label} to ${userDid}`);
}

app.listen(3000, () => {
  console.log('Verification service running on port 3000');
});
```

### Run Verification Service

```bash
npm install express axios
node verify-service.js
```

### Test End-to-End

```bash
# Submit verification request
curl -X POST http://localhost:3000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "proof": "mock_proof_data",
    "publicInputs": ["0x123..."],
    "userDid": "did:plc:test-user",
    "verificationType": "age"
  }'
```

## User Flow

### For Users Getting Verified

1. **Visit verification portal** (you'll build this)
2. **Connect wallet or generate proof**
3. **Submit proof + Bluesky DID**
4. **Receive confirmation**
5. **Subscribe to your labeller** in Bluesky settings
6. **Badge appears on profile**

### Subscribing to Your Labeller

Users subscribe via:
- Bluesky app: Settings → Moderation → Labelers → Add labeler
- Direct link: `https://bsky.app/profile/YOUR_DID_HERE`
- Or programmatically via ATProto API

## Architecture Diagram

```
User                 Verification           Labeller            Bluesky
 │                      Service              Service            Network
 │                         │                    │                  │
 │  1. Generate Proof      │                    │                  │
 │────────────────────────>│                    │                  │
 │                         │                    │                  │
 │                         │  2. Validate       │                  │
 │                         │                    │                  │
 │  3. Success             │                    │                  │
 │<────────────────────────│                    │                  │
 │                         │                    │                  │
 │                         │  4. Apply Label    │                  │
 │                         │───────────────────>│                  │
 │                         │                    │                  │
 │                         │                    │  5. Publish      │
 │                         │                    │─────────────────>│
 │                         │                    │                  │
 │  6. Badge visible on profile (if subscribed) │                  │
 │<─────────────────────────────────────────────────────────────────│
```

## Common Issues & Solutions

### "Permission denied" when running Docker

```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### "Label not appearing on profile"

- Ensure user is subscribed to your labeller
- Check labeller service logs
- Verify DID is correct (did:plc:... format)
- Wait a few minutes for propagation

### "PLC registration failed"

- Check your DID and password are correct
- Ensure you're using an app password, not your main password
- Generate app password at: Settings → Advanced → App Passwords

### "Proof verification failing"

- Verify proof format matches expected structure
- Check public inputs are in correct format
- Ensure Noir circuit matches verifier

## Next Steps

### Make It Production-Ready

- [ ] Implement real Aztec proof verification
- [ ] Add rate limiting to prevent abuse
- [ ] Set up monitoring and logging
- [ ] Implement proof replay prevention
- [ ] Add database for audit trail
- [ ] Create terms of service
- [ ] Build user-friendly web interface

### Advanced Features

- [ ] Multiple verification types
- [ ] Proof expiry and renewal
- [ ] Revocation mechanism
- [ ] On-chain verification option
- [ ] Batch verification processing
- [ ] Analytics dashboard

### Expand Your Service

- [ ] Register on labeler directories
- [ ] Create documentation for users
- [ ] Build community around verified badges
- [ ] Integrate with other ATProto services
- [ ] Explore Blue Badge integration for richer visuals

## Resources

- **bsky-watch/labeler**: https://github.com/bsky-watch/labeler
- **ATProto Label Spec**: https://atproto.com/specs/label
- **Bluesky API Docs**: https://docs.bsky.app/
- **Noir Documentation**: https://noir-lang.org/
- **ATProto Discord**: Join for community support

## Example Aztec Use Cases

### Age Verification
- Prove you're over 18/21 without revealing birthday
- Use case: Adult content, alcohol, gambling

### Professional Credentials
- Verify medical license, bar admission, engineering certification
- Use case: Professional networking, expert verification

### Education
- Prove degree from university without exposing transcripts
- Use case: Alumni networks, job applications

### Membership
- Verify membership in organization/DAO/club
- Use case: Exclusive communities, event access

### Financial
- Prove accredited investor status
- Prove token holdings above threshold
- Use case: Investment opportunities, gated content

### Identity
- Prove government ID ownership
- Prove residency in country/region
- Use case: Regional services, compliance

## Support

If you get stuck:
1. Check the labeler repository issues
2. Review ATProto documentation
3. Join Bluesky developer Discord
4. Ask in Aztec developer community

## Success Checklist

- [ ] Labeller service running
- [ ] Labels defined in config
- [ ] PLC registration complete
- [ ] API endpoint working
- [ ] Test label created successfully
- [ ] Public endpoint configured
- [ ] Verification service integrated
- [ ] End-to-end test completed
- [ ] Users can subscribe to labeller
- [ ] Badges appearing on profiles

---

**You're ready to build a privacy-preserving verification system on Bluesky!** 🎉
