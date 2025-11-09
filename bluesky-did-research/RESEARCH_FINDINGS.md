# Bluesky DID & PDS Migration Research

**Research Date:** 2025-11-08
**Topics:** did:plc vs did:web in ATProto, PDS Migration Strategies

---

## Part 1: Understanding did:plc vs did:web in Bluesky/ATProto

### What is did:plc?

**Full Name:** DID Placeholder (plc)

**Key Characteristics:**
- Created by Bluesky specifically for ATProto
- A new DID form consisting of a hash of a public key
- Can be used directly or sign new public keys to allow key rollover
- Requires querying Bluesky's PLC directory service to resolve DID documents
- **Most popular choice** - nearly all Bluesky users use this method

**Advantages:**
- **Portability**: Your DID remains constant even when changing PDS servers
- Can migrate between hosting providers without losing your identity
- Your social graph (followers, following) stays intact during migration
- Bluesky has indicated future plans to move PLC governance to a consensus model

**Disadvantages:**
- Relies on Bluesky's centralized PLC directory service
- Less decentralized than did:web
- Creates dependency on Bluesky infrastructure

### What is did:web?

**Full Name:** DID Web Method (W3C Standard)

**Key Characteristics:**
- Based on HTTPS and DNS
- The DID is derived from a domain name (e.g., `did:web:krasovs.ky`)
- DID document is resolved via HTTPS request to `https://domain/.well-known/did.json`
- Supported in ATProto as an independent alternative to did:plc

**Advantages:**
- **True decentralization**: No dependency on Bluesky infrastructure
- W3C standard, widely recognized outside ATProto
- Full control over your identity through domain ownership

**Disadvantages:**
- **Tied to domain**: You must maintain ownership of that domain forever
- **No migration path**: Changing domains means creating a completely new DID
- **Social graph loss**: If you switch to a new DID, you lose all followers
- **Less portable**: Identity is bound to domain name, not transferable
- **Rare in practice**: Very few Bluesky users actually use did:web

### Why Would You Use did:web for Bluesky?

**Use Cases:**
1. **Maximum decentralization**: You want zero dependency on Bluesky services
2. **Long-term domain ownership**: You own a domain you'll control forever
3. **Philosophical reasons**: Prefer W3C standards over Bluesky-specific solutions
4. **Corporate/organizational use**: Organizations with stable domain ownership
5. **Technical experimentation**: Testing ATProto's full decentralization capabilities

**When NOT to use did:web:**
- If you might change domains in the future
- If you value portability over decentralization
- If you want to preserve your social graph during migrations
- If you're a regular user (did:plc is the better choice)

### Real Examples of did:web Usage in ATProto

**Service Examples:**
- `did:web:api.bsky.chat` - Bluesky's official chat/DM service
- `did:web:blueskyweb.xyz` - Example from AT Protocol documentation

**User Examples:**
- **Savely Krasovsky** (`did:web:krasovs.ky`) - Handle: @krasovs.ky
  - Created utility tool: https://github.com/savely-krasovsky/bsky-did-web
  - Viewable on pdsls.dev at: https://pdsls.dev/at/did:web:krasovs.ky

**Other Tools:**
- Luke's did:web setup tool: https://atproto-did-web.lukeacl.com

### Looking Up did:web Accounts on pdsls.dev

**Format:** `https://pdsls.dev/at/did:web:DOMAIN`

**Examples:**
- `https://pdsls.dev/at/did:web:krasovs.ky`
- `https://pdsls.dev/at/did:web:api.bsky.chat`

**Note:** pdsls.dev requires JavaScript to be enabled to view account information.

### Migration Limitations: did:plc to did:web

**Critical Warning:** Migration between DID methods is effectively impossible without data loss.

If you migrate from did:plc to did:web:
- You can keep your handle and point it at your new DID
- **You WILL LOSE all followers** (they follow your DID, not your handle)
- All in-protocol references are based on DIDs, not handles
- You're essentially creating a new identity

**Conclusion on did:web:**
While technically supported, did:web is rarely used in practice for user accounts. The portability benefits of did:plc outweigh the decentralization benefits of did:web for most users.

---

## Part 2: Comprehensive PDS Migration Plan

### Current Status & Critical Warnings

**Official Bluesky Stance (as of November 2024):**
- Federation to self-hosted PDSs is in "experimental phases"
- Intended primarily for developers and test accounts
- **NOT recommended for production/primary accounts**
- Account migration is "potentially destructive"
- If something goes wrong, you could be **permanently locked out**
- Bluesky cannot help recover your account if migration fails

### Why Are You Scared? (Valid Reasons)

**Legitimate Risks:**

1. **Permanent Account Loss**
   - Migration involves signing away your old PDS's ability to update your DID
   - No recovery mechanism if migration fails mid-process
   - Must understand PLC operations thoroughly

2. **Data Loss Scenarios**
   - Failed blob (images/videos) transfers
   - Corrupted repository during transfer
   - Incomplete preference migration
   - Database corruption

3. **Operational Complexity**
   - Must maintain server uptime (unlike Bluesky's managed service)
   - Need technical expertise for troubleshooting
   - Responsible for backups and disaster recovery
   - Must monitor and update software

4. **Federation Instability**
   - Still experimental (as of 2024)
   - May encounter bugs or unexpected behavior
   - Limited community support compared to managed hosting

5. **Cost & Maintenance**
   - Ongoing AWS/hosting costs ($12-72/month depending on setup)
   - Time investment for monitoring and maintenance
   - Potential for unexpected expenses

### Architecture Options Comparison

#### Option 1: AWS CDK Serverless (Official AWS Sample)

**Repository:** https://github.com/aws-samples/deploy-bluesky-pds-with-aws-cdk

**Architecture:**
- Single AWS Fargate task behind Application Load Balancer
- Spans two availability zones for redundancy
- AWS Secrets Manager for credentials (admin password, JWT secret)
- AWS KMS for PLC rotation key
- Litestream sidecar for continuous SQLite replication to S3
- File backup sidecar for individual user databases
- CloudWatch for logs and monitoring
- Private ECR repository for container images

**Cost:** ~$72/month

**Pros:**
- Highest resiliency and fault tolerance
- Built-in backup and replication
- Multi-AZ redundancy
- Comprehensive monitoring
- Security-focused (KMS, Secrets Manager, VPC isolation)
- Serverless (no server management)
- Automatic recovery from failures

**Cons:**
- Most expensive option
- More complex architecture
- Overkill for single-user PDS
- AWS expertise required for troubleshooting

**Best For:**
- Organizations or users requiring maximum uptime
- Those with AWS expertise
- Multi-user PDS hosting
- Users willing to pay premium for reliability

---

#### Option 2: AWS Lightsail (Budget Option)

**Service:** Amazon Lightsail Containers

**Architecture:**
- Single container instance
- "Medium" plan minimum (2 vCPU + 2 GB memory)
- Managed load balancing and TLS certificates
- Built-in DNS management
- 500 GB data transfer quota included

**Cost:** $40/month for Lightsail + ~$2.40 for storage = **$42.40/month**

**Pros:**
- Much cheaper than CDK approach
- Simpler setup and management
- Includes TLS certificates automatically
- Managed DNS
- Good for single-user or small multi-user setups
- AWS ecosystem benefits

**Cons:**
- Single-zone deployment (less redundant)
- Less sophisticated monitoring
- Manual backup configuration required
- Limited scalability
- Still requires AWS knowledge

**Best For:**
- Budget-conscious users
- Single-user PDS
- Those wanting AWS benefits at lower cost
- Users comfortable with basic AWS services

---

#### Option 3: EC2 Instance (Most Flexible)

**Service:** AWS EC2 + Docker Compose

**Architecture:**
- Single EC2 instance (t3.small or t3.medium recommended)
- Docker Compose setup
- Manual configuration of backups
- Elastic IP for static address
- Route53 for DNS
- ACM for TLS certificates

**Cost:**
- EC2 t3.small: ~$15-17/month
- EBS storage: ~$3-5/month
- Data transfer: ~$5-10/month
- **Total: ~$25-35/month**

**Pros:**
- Most cost-effective AWS option
- Full control over configuration
- Familiar VPS-like experience
- Can be stopped when not in use (cost savings)
- Easy to understand and troubleshoot

**Cons:**
- Manual setup and configuration
- Single point of failure
- No automatic recovery
- Must manage OS updates and security
- More hands-on maintenance required
- No built-in redundancy

**Best For:**
- Technical users comfortable with Linux administration
- Those wanting maximum cost savings on AWS
- Users who need full control
- Experimentation and learning

---

#### Option 4: Alternative Providers (Non-AWS)

**Digital Ocean Droplet:** $12-18/month
**Linode/Akamai:** $12-24/month
**Hetzner Cloud:** €4-8/month (~$4-9/month)
**Oracle Cloud Free Tier:** FREE (but risky - accounts can be closed)

**Pros:**
- Potentially cheaper than AWS
- Simpler pricing models
- Often easier to use than AWS
- Some offer better price/performance

**Cons:**
- Outside AWS ecosystem (if you prefer keeping everything in AWS)
- May have less sophisticated backup options
- Smaller provider ecosystems
- Oracle specifically has reputation issues

---

### Recommended Architecture: AWS EC2 with Proper Backups

**For most users wanting to stay in AWS, I recommend:**

1. **EC2 t3.small instance** (~$17/month)
2. **30 GB EBS volume** with daily snapshots (~$3/month)
3. **S3 bucket** for database backups with lifecycle policies (~$1-2/month)
4. **Route53** for DNS management (~$1/month)
5. **AWS Certificate Manager** for free TLS certificates
6. **CloudWatch** for basic monitoring (free tier)

**Total Cost:** ~$25-30/month

**Why This Approach:**
- Balances cost, reliability, and simplicity
- Stays within AWS ecosystem
- Automated backups via EBS snapshots
- Additional S3 backups for redundancy
- Manageable complexity
- Can upgrade to more sophisticated setup later

---

### Migration Strategy: Step-by-Step Plan

#### Phase 0: Preparation & Risk Mitigation (1-2 weeks)

**DO NOT SKIP THIS PHASE**

1. **Create Test Account**
   - Create a new test account on Bluesky
   - Practice the entire migration process with this account
   - Document any issues you encounter

2. **Understand Your Current Account**
   ```bash
   # Document your current state:
   # - Number of posts
   # - Number of followers/following
   # - Number of images/videos (blobs)
   # - Total data size
   ```

3. **Set Up Monitoring for Current Account**
   - Use https://pdsls.dev to view your current account
   - Screenshot your profile, follower count, post count
   - Document your DID and handle

4. **Learn PLC Operations**
   - Read: https://github.com/bluesky-social/pds/blob/main/ACCOUNT_MIGRATION.md
   - Understand DID rotation
   - Understand the 72-hour rotation window
   - Learn how to verify DID documents

5. **Choose Migration Tool**
   - **Option A:** Manual migration (maximum control, highest complexity)
   - **Option B:** PDS MOOver (https://pdsmoover.com) - recommended for most users

6. **Set Up Your Infrastructure**
   - Deploy PDS on your chosen platform
   - Verify it's accessible from the internet
   - Configure DNS properly
   - Obtain and configure TLS certificate
   - Test with a new account creation (not your main account)

#### Phase 1: Infrastructure Setup (1 week)

**1.1 Domain Setup**
- Purchase or use existing domain
- Configure DNS A record pointing to your server
- Set up `_atproto` TXT record for service endpoint
- Verify DNS propagation (use `dig` or `nslookup`)

**1.2 EC2 Instance Setup (Recommended Approach)**

```bash
# Launch EC2 instance
# - AMI: Ubuntu 22.04 LTS
# - Instance type: t3.small
# - Storage: 30 GB gp3
# - Security groups: Allow 80, 443, and SSH

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# Clone official PDS repository
git clone https://github.com/bluesky-social/pds.git
cd pds

# Configure environment
cp .env.example .env
# Edit .env with your settings:
# - PDS_HOSTNAME=pds.yourdomain.com
# - PDS_ADMIN_EMAIL=your@email.com
# - etc.

# Start PDS
sudo docker-compose up -d
```

**1.3 Configure Backups**

```bash
# Set up S3 backup bucket
aws s3 mb s3://your-pds-backups

# Create backup script
cat > /usr/local/bin/pds-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="/tmp/pds-backup-${BACKUP_DATE}.tar.gz"

# Stop PDS temporarily
cd /path/to/pds
docker-compose stop

# Create backup
tar -czf ${BACKUP_FILE} /pds

# Restart PDS
docker-compose start

# Upload to S3
aws s3 cp ${BACKUP_FILE} s3://your-pds-backups/
rm ${BACKUP_FILE}
EOF

chmod +x /usr/local/bin/pds-backup.sh

# Schedule daily backups
echo "0 2 * * * /usr/local/bin/pds-backup.sh" | crontab -
```

**1.4 Testing**
- Create a test account on your new PDS
- Verify federation works
- Test posting, following, uploading images
- Verify your test account appears in Bluesky app
- Let it run for 1 week to ensure stability

#### Phase 2: Pre-Migration Checklist (3 days before migration)

**Critical Checks:**

- [ ] PDS has been running stable for at least 1 week
- [ ] Backups are working and tested (restore from backup successfully)
- [ ] DNS is correctly configured and propagated
- [ ] TLS certificate is valid
- [ ] You have successfully migrated a test account
- [ ] You understand the 4-stage migration process
- [ ] You have access to your recovery codes
- [ ] You have your PLC rotation key secured
- [ ] You have notified followers about potential downtime
- [ ] You have screenshots/exports of all important data
- [ ] You have a rollback plan

**Data Export:**
```bash
# Export current account data using official tools
# Save all posts, media, preferences locally
# This is your safety net
```

#### Phase 3: Migration Execution (Using PDS MOOver - Recommended)

**Why PDS MOOver:**
- Handles all 4 migration stages automatically
- Client-side operation (data stays in your browser)
- Includes backup functionality
- Has recovery tools if something goes wrong
- Free for individual accounts

**Migration Process:**

1. **Go to https://pdsmoover.com**

2. **Backup Phase**
   - Click "Backup" option
   - Enter your current Bluesky credentials
   - Wait for backup to complete (stores repo + blobs)
   - Verify backup completed successfully
   - Download backup locally as additional safety

3. **Migration Phase**
   - Enter source PDS: `https://bsky.social`
   - Enter destination PDS: `https://pds.yourdomain.com`
   - Enter credentials for both
   - Start migration

4. **Wait for Completion**
   - Repository transfer
   - Blob uploads (can take hours for many images/videos)
   - Preferences migration
   - DID update
   - Account activation

**Important Notes:**
- Migration is NOT parallel - blobs upload one at a time
- Large accounts can take many hours
- Do NOT close browser during migration
- Keep a window open to monitor progress

5. **Verification**
   - Log into Bluesky app using your new PDS endpoint
   - Verify all posts are visible
   - Check follower/following counts
   - Verify images and videos load
   - Test posting new content

6. **Missing Media Recovery**
   - If any images/videos are missing, use PDS MOOver's "Missing" tool
   - This recovers blobs from your old PDS
   - Run this within 30 days of migration

#### Phase 4: Post-Migration (1-2 weeks after)

**Immediate (Day 1):**
- [ ] Verify account fully functional
- [ ] Post announcement of successful migration
- [ ] Monitor for any federation issues
- [ ] Keep old PDS account accessible for 30 days (DO NOT delete yet)

**Week 1:**
- [ ] Daily checks of PDS health
- [ ] Monitor disk usage
- [ ] Verify backups are running
- [ ] Check for missing blobs
- [ ] Respond to any follower questions

**Week 2:**
- [ ] Create post explaining your migration experience
- [ ] Document any lessons learned
- [ ] Fine-tune backup schedule
- [ ] Optimize server performance if needed

**30 Days After:**
- If everything is stable, consider deactivating old account
- Do NOT delete immediately - keep for another 30 days
- After 60 days total, can delete old account

---

### Alternative: Manual Migration (For Advanced Users)

If you prefer maximum control or want to understand the process deeply:

**Stage 1: Create Account on New PDS**
```bash
# Get service auth JWT from old PDS
curl -X POST https://bsky.social/xrpc/com.atproto.server.getServiceAuth \
  -H "Authorization: Bearer $OLD_PDS_TOKEN" \
  -d '{"aud": "did:web:pds.yourdomain.com"}'

# Create account on new PDS
curl -X POST https://pds.yourdomain.com/xrpc/com.atproto.server.createAccount \
  -H "Authorization: Bearer $SERVICE_JWT" \
  -d '{"handle": "yourhandle.yourdomain.com", ...}'
```

**Stage 2: Migrate Data**
```bash
# Download repository
curl https://bsky.social/xrpc/com.atproto.sync.getRepo?did=$YOUR_DID \
  -o repo.car

# Upload to new PDS
curl -X POST https://pds.yourdomain.com/xrpc/com.atproto.repo.importRepo \
  -H "Authorization: Bearer $NEW_PDS_TOKEN" \
  -H "Content-Type: application/vnd.ipld.car" \
  --data-binary @repo.car

# Migrate blobs (images/videos) - repeat for each blob
# ... (see official docs for full blob migration)
```

**Stage 3: Update DID**
```bash
# Get recommended credentials
curl https://pds.yourdomain.com/xrpc/com.atproto.identity.getRecommendedDidCredentials

# Submit PLC operation (requires email verification)
curl -X POST https://pds.yourdomain.com/xrpc/com.atproto.identity.submitPlcOperation \
  -d '{"operation": {...}}'
```

**Stage 4: Activate Account**
```bash
curl -X POST https://pds.yourdomain.com/xrpc/com.atproto.server.activateAccount \
  -H "Authorization: Bearer $NEW_PDS_TOKEN"
```

**NOTE:** This is highly simplified. See full docs at:
https://github.com/bluesky-social/pds/blob/main/ACCOUNT_MIGRATION.md

---

### Backup Strategies

**Critical: Multiple Backup Layers**

**Layer 1: EBS Snapshots (AWS)**
- Daily automated snapshots
- 7-day retention
- Point-in-time recovery
- Cost: ~$0.05/GB/month

```bash
# Create snapshot policy in AWS Console or CLI
aws ec2 create-snapshot --volume-id vol-xxxxx --description "PDS Daily Backup"
```

**Layer 2: S3 Database Backups**
- SQLite database backups to S3
- Use Litestream for continuous replication
- Or simple tar archives daily

```dockerfile
# Add to docker-compose.yml
litestream:
  image: litestream/litestream:latest
  volumes:
    - ./pds:/pds
  command: replicate /pds/pds.sqlite s3://your-bucket/pds.sqlite
```

**Layer 3: Full System Backups**
- Weekly full PDS directory backup
- Store off-server (S3, another region)
- Test restoration quarterly

**Layer 4: PDS MOOver Backups**
- Use PDS MOOver's backup feature monthly
- Stores on their cloud infrastructure
- Provides account recovery option

**Testing Backups:**
```bash
# Quarterly: Spin up a new instance and restore from backup
# Verify all data is intact
# Document restoration time
# Update runbooks if needed
```

---

### Disaster Recovery Plan

**Scenario 1: Server Goes Down**
- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 24 hours

**Steps:**
1. Spin up new EC2 instance
2. Restore from most recent EBS snapshot
3. Verify data integrity
4. Update DNS if IP changed (or use Elastic IP)
5. Restart PDS container

**Scenario 2: Data Corruption**
- Restore from S3 database backup
- If corruption is recent, restore from EBS snapshot
- Use PDS MOOver recovery if needed

**Scenario 3: Complete Account Loss**
- This is why we NEVER delete old PDS for 60 days
- Can potentially re-migrate from old PDS
- Or restore from PDS MOOver backup

**Scenario 4: AWS Account Issues**
- Keep backups in different AWS account or region
- Or use PDS MOOver backups (stored separately)
- Have documented manual recovery process

---

### Monitoring & Maintenance

**Daily:**
- Check PDS is responding: `curl https://pds.yourdomain.com/xrpc/_health`
- Monitor disk usage: `df -h`
- Check Docker containers: `docker ps`

**Weekly:**
- Review CloudWatch logs for errors
- Check backup completion
- Monitor bandwidth usage
- Test posting and federation

**Monthly:**
- Update PDS software: `docker-compose pull && docker-compose up -d`
- Review and adjust backup retention
- Check TLS certificate expiry
- Review costs
- Test backup restoration

**Quarterly:**
- Full disaster recovery test
- Review security settings
- Update documentation
- Evaluate if self-hosting still makes sense

---

### Cost Breakdown (EC2 Approach)

**Monthly Costs:**
- EC2 t3.small instance: $15-17
- EBS 30GB storage: $3
- EBS snapshots (210GB total): $10.50
- S3 database backups (10GB): $0.23
- Data transfer (50GB): $4.50
- Route53 hosted zone: $0.50

**Total: ~$33-35/month**

**Compared to:**
- Bluesky hosted: FREE
- AWS CDK approach: $72/month
- AWS Lightsail: $42/month

---

### Should You Actually Do This?

**Consider Self-Hosting If:**
- You want to learn about ATProto/PDS internals
- You value data ownership highly
- You have technical expertise (Linux, Docker, AWS)
- You're willing to spend $30-70/month
- You can handle 2-4 hours/month maintenance
- You want to contribute to decentralization
- You're comfortable with some risk

**Stay on Bluesky Hosted If:**
- This is your primary/only account
- You can't afford to lose your account
- You don't have time for maintenance
- You're not technical or willing to learn
- You just want to use the social network
- You don't want to spend money
- **You're risk-averse** (THIS IS YOU RIGHT NOW - and that's okay!)

---

### My Honest Recommendation

**For your current situation:**

Given that you said "so far i've been scared off i dont want to lose my everything," my recommendation is:

**DO NOT MIGRATE YOUR PRIMARY ACCOUNT YET**

Instead:

1. **Create a test account on Bluesky**
2. **Set up a self-hosted PDS (EC2 or Lightsail)**
3. **Use your test account on your PDS for 3-6 months**
4. **Participate in the ATProto community** (Discord, GitHub discussions)
5. **Wait for migration tools to mature** (currently experimental)
6. **Monitor for success stories** from others who have migrated
7. **Re-evaluate in 6-12 months** when:
   - Migration is more stable
   - Better tools exist
   - Community best practices are established
   - You have hands-on PDS experience

**In the meantime:**
- Keep using your primary account on Bluesky's hosting
- Experiment with self-hosting using test accounts
- Build your knowledge and confidence
- Watch for improvements in the migration process

**The technology will mature.** Federation is still experimental. The risks you're sensing are real and valid. There's no shame in waiting until the process is more stable and battle-tested.

---

### Resources & Further Reading

**Official Documentation:**
- AT Protocol: https://atproto.com
- PDS Documentation: https://github.com/bluesky-social/pds
- Migration Guide: https://github.com/bluesky-social/pds/blob/main/ACCOUNT_MIGRATION.md
- Self-Hosting Guide: https://atproto.com/guides/self-hosting

**Tools:**
- PDS MOOver: https://pdsmoover.com
- pdsls.dev (account viewer): https://pdsls.dev
- Luke's did:web tool: https://atproto-did-web.lukeacl.com

**AWS Resources:**
- AWS CDK PDS: https://github.com/aws-samples/deploy-bluesky-pds-with-aws-cdk
- AWS PDS Cost Guide: https://github.com/aws-samples/deploy-bluesky-pds-with-aws-cdk/blob/main/guides/COST.md

**Community:**
- ATProto Discord: https://discord.gg/atproto
- ATProto GitHub Discussions: https://github.com/bluesky-social/atproto/discussions
- Bluesky Directory (PDS list): https://blueskydirectory.com

**Blog Posts & Tutorials:**
- Matt Dyson's Self-Hosting Guide: https://mattdyson.org/blog/2024/11/self-hosting-bluesky-pds/
- Casey Primozic's Notes: https://cprimozic.net/notes/posts/notes-on-self-hosting-bluesky-pds-alongside-other-services/

---

### Conclusion

**On did:web:**
While technically supported and philosophically appealing for maximum decentralization, did:web is rarely used in practice due to domain portability concerns. Unless you have specific requirements, did:plc is the better choice for ATProto identities.

**On PDS Migration:**
The technology is real and works, but it's still experimental. Your fear is healthy and appropriate. Wait for the tooling to mature unless you're comfortable with significant risk and have the technical skills to recover from problems.

The future of self-hosted PDS is promising, but the present is still early days. Patience will reward you with better tools, clearer documentation, and proven migration paths.

**Remember:** Decentralization is a means to an end (user autonomy), not an end in itself. If centralized hosting serves your needs better right now, that's a perfectly valid choice.

---

**Created:** 2025-11-08
**Last Updated:** 2025-11-08
**Next Review:** 2025-05-08 (6 months)
