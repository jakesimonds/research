# 🎯 Quick Usage Guide

## Deployment (One Command!)

```bash
./deploy.sh
```

That's it! The script will install Docker if needed and start the honeypot.

## Monitoring

### Watch logs in real-time
```bash
# All logs (stdout + access log)
docker-compose logs -f

# Just the access log
tail -f logs/access.log

# Pretty-print JSON logs
tail -f logs/access.log | jq .
```

### Quick stats while running
```bash
# Total requests so far
wc -l logs/access.log

# Unique IPs
cat logs/access.log | jq -r .ip | sort -u | wc -l

# Most requested paths
cat logs/access.log | jq -r .path | sort | uniq -c | sort -rn | head

# Requests per IP
cat logs/access.log | jq -r .ip | sort | uniq -c | sort -rn

# See what bots are trying to POST
cat logs/access.log | jq 'select(.post_data != null) | {ip, path, post_data}'

# Find SQL injection attempts
cat logs/access.log | jq 'select(.path | test("union|select|1=1"; "i")) | {ip, path}'
```

### Live dashboard (updates every 2 seconds)
```bash
watch -n 2 'echo "Total: $(wc -l < logs/access.log) | IPs: $(cat logs/access.log | jq -r .ip | sort -u | wc -l)"'
```

## Analysis

### Generate full report
```bash
python3 analyze_logs.py
```

### Custom analysis with jq
```bash
# Top 10 user agents
cat logs/access.log | jq -r .user_agent | sort | uniq -c | sort -rn | head -10

# Requests by hour
cat logs/access.log | jq -r '.timestamp[:13]' | sort | uniq -c

# Countries (if you add GeoIP)
cat logs/access.log | jq -r .country | sort | uniq -c | sort -rn

# See all POST data
cat logs/access.log | jq 'select(.method == "POST") | {ip, path, post_data}'

# Find config file requests
cat logs/access.log | jq 'select(.path | test("\\.env|config|backup|\\.git"; "i")) | {ip, path}'

# WordPress-specific requests
cat logs/access.log | jq 'select(.path | test("wp-|wordpress"; "i")) | {ip, path}'
```

## Useful Commands

### Check if honeypot is running
```bash
docker ps
curl http://localhost/
```

### Restart honeypot
```bash
docker-compose restart
```

### Stop honeypot
```bash
docker-compose down
```

### View internal stats endpoint
```bash
curl http://localhost/honeypot/stats | jq .
```

### Export logs for later analysis
```bash
# Copy logs before terminating EC2
scp -i your-key.pem ec2-user@your-ip:~/honeypot-demo/logs/access.log ./

# Or create a tarball
tar -czf honeypot-logs-$(date +%Y%m%d-%H%M).tar.gz logs/
```

## Testing Locally

### Simulate bot traffic
```bash
# WordPress login attempt
curl -X POST http://localhost/wp-login.php -d "log=admin&pwd=password123"

# PHPMyAdmin access
curl http://localhost/phpmyadmin

# Config file probe
curl http://localhost/.env

# SQL injection attempt
curl "http://localhost/admin?id=1' OR '1'='1"

# Shell command attempt
curl "http://localhost/shell?cmd=ls -la"
```

### Generate fake traffic for testing
```bash
# Quick script to generate test traffic
for i in {1..10}; do
  curl -s http://localhost/wp-admin > /dev/null &
  curl -s http://localhost/phpmyadmin > /dev/null &
  curl -s http://localhost/.env > /dev/null &
done

# Then analyze
python3 analyze_logs.py
```

## Troubleshooting

### Logs not appearing?
```bash
# Check if container is running
docker ps

# Check container logs
docker-compose logs

# Verify log directory permissions
ls -la logs/

# Manually check inside container
docker exec -it honeypot-demo ls -la /var/log/honeypot/
```

### Port 80 already in use?
```bash
# Find what's using port 80
sudo lsof -i :80
# OR
sudo netstat -tlnp | grep :80

# Stop conflicting service (e.g., Apache)
sudo systemctl stop httpd
# OR
sudo systemctl stop apache2
```

### Can't access from outside?
```bash
# Verify security group allows port 80
# AWS Console -> EC2 -> Security Groups

# Check if server is listening
sudo netstat -tlnp | grep :80

# Test locally first
curl http://localhost/

# Check firewall (if using)
sudo iptables -L -n
```

## After Your Experiment

### Save results
```bash
# Generate report
python3 analyze_logs.py > results.txt

# Save everything
tar -czf honeypot-experiment-$(date +%Y%m%d).tar.gz logs/ results.txt

# Download to local machine
scp -i your-key.pem ec2-user@your-ip:~/honeypot-experiment-*.tar.gz ./
```

### Clean up
```bash
# Stop container
docker-compose down

# Remove images (optional)
docker rmi honeypot-demo_honeypot

# On AWS: TERMINATE THE EC2 INSTANCE
# Don't forget this! Otherwise you'll keep getting charged.
```

## Pro Tips

1. **Run during different times**: Daytime vs nighttime, weekday vs weekend
2. **Different regions**: Deploy in different AWS regions to see regional patterns
3. **Longer duration**: Try 6-24 hours for more comprehensive data
4. **Multiple ports**: Expose other common ports (3306 for MySQL, 5432 for Postgres)
5. **Compare**: Run multiple experiments and compare results

## Creating Content

### Screenshot checklist
- [ ] Terminal showing live logs scrolling
- [ ] Analysis report output
- [ ] Top attacked paths
- [ ] Interesting POST data attempts
- [ ] Timeline of first request to last
- [ ] Geographic distribution (if added)

### Data points for video/blog
- When did first bot find you?
- Total requests in X minutes
- Most persistent attacker IP
- Most common attack vector
- Strangest/most creative attempt
- Credential pairs tried
- Config files requested

Enjoy your honeypot! 🍯
