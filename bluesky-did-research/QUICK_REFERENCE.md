# Quick Reference Guide

## did:web Examples to Look Up on pdsls.dev

### User Accounts
- `https://pdsls.dev/at/did:web:krasovs.ky` - Savely Krasovsky (@krasovs.ky)

### Services
- `https://pdsls.dev/at/did:web:api.bsky.chat` - Bluesky Chat Service
- `https://pdsls.dev/at/did:web:blueskyweb.xyz` - Example from docs

### Tools to Create did:web Accounts
- https://atproto-did-web.lukeacl.com - Luke's did:web setup tool
- https://github.com/savely-krasovsky/bsky-did-web - Savely's utility

## did:plc vs did:web Summary

| Feature | did:plc | did:web |
|---------|---------|---------|
| **Popularity** | 99%+ of users | <1% of users |
| **Portability** | High - can migrate servers | Low - tied to domain |
| **Decentralization** | Depends on Bluesky service | Fully decentralized |
| **Social graph migration** | Preserved | Lost on migration |
| **Best for** | Most users | Organizations with stable domains |

## PDS Migration - Should You Do It?

### DO IT IF:
- Test/secondary account
- Technical expertise
- Want to learn
- Can afford $30-70/month
- Comfortable with risk

### DON'T DO IT IF:
- Primary account
- Risk-averse
- Not technical
- Can't afford data loss
- Just want to use social network

## Migration Cost Comparison

| Option | Monthly Cost | Complexity | Reliability |
|--------|-------------|------------|-------------|
| Bluesky Hosted | FREE | None | Excellent |
| EC2 (Recommended) | $25-35 | Medium | Good |
| Lightsail | $42 | Low | Good |
| AWS CDK | $72 | High | Excellent |

## Essential Migration Steps

1. **DO NOT migrate primary account yet**
2. Create test account
3. Set up PDS infrastructure
4. Test for 1+ week
5. Use PDS MOOver for migration
6. Keep old account for 60 days
7. Monitor closely

## Critical Resources

- **Migration Tool:** https://pdsmoover.com
- **Account Viewer:** https://pdsls.dev
- **Official Migration Guide:** https://github.com/bluesky-social/pds/blob/main/ACCOUNT_MIGRATION.md
- **AWS CDK Template:** https://github.com/aws-samples/deploy-bluesky-pds-with-aws-cdk

## Daily Health Check Commands

```bash
# Check PDS is running
curl https://pds.yourdomain.com/xrpc/_health

# Check disk usage
df -h

# Check Docker containers
docker ps

# View logs
docker-compose logs -f --tail=100
```

## Backup Verification

```bash
# List EBS snapshots
aws ec2 describe-snapshots --owner-id self

# List S3 backups
aws s3 ls s3://your-pds-backups/

# Test restore (on separate instance)
docker-compose down
# Restore from backup
docker-compose up -d
```

## Emergency Contacts

- **ATProto Discord:** https://discord.gg/atproto
- **GitHub Issues:** https://github.com/bluesky-social/pds/issues
- **PDS MOOver Support:** Via their website

## Current Status (November 2025)

- Federation: **Experimental**
- Migration Safety: **Risky for primary accounts**
- Recommended Action: **Wait 6-12 months for production use**
- Best Use Case: **Test accounts and learning**

---

**Remember:** Your fear of losing everything is valid and rational. The technology will mature. There's no rush.
