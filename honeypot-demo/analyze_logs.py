#!/usr/bin/env python3
"""
Analyze honeypot logs and generate a summary report
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

def analyze_logs(log_file='logs/access.log'):
    """Parse and analyze honeypot access logs"""

    if not Path(log_file).exists():
        print(f"❌ Log file not found: {log_file}")
        return

    requests = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                requests.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    if not requests:
        print("No requests logged yet. Wait a bit longer!")
        return

    # Analysis
    total = len(requests)
    unique_ips = set(r['ip'] for r in requests)
    paths = Counter(r['path'] for r in requests)
    methods = Counter(r['method'] for r in requests)
    user_agents = Counter(r['user_agent'] for r in requests)
    ips_by_count = Counter(r['ip'] for r in requests)

    # Detect attack patterns
    sql_injection = [r for r in requests if any(
        keyword in (r['path'] + r.get('query_string', '')).lower()
        for keyword in ['union', 'select', '1=1', 'drop', 'or 1', '--', 'insert']
    )]

    credential_attempts = [r for r in requests if r.get('post_data') and any(
        key in str(r['post_data']).lower()
        for key in ['password', 'passwd', 'pwd', 'pass']
    )]

    config_file_requests = [r for r in requests if any(
        target in r['path'].lower()
        for target in ['.env', 'config', '.git', 'backup', '.sql']
    )]

    # Time series
    first_request = datetime.fromisoformat(requests[0]['timestamp'])
    last_request = datetime.fromisoformat(requests[-1]['timestamp'])
    duration = (last_request - first_request).total_seconds() / 60  # minutes

    # Generate report
    print("\n" + "="*80)
    print("🍯 HONEYPOT ANALYSIS REPORT")
    print("="*80)

    print(f"\n📊 OVERVIEW")
    print(f"  Total Requests: {total}")
    print(f"  Unique IP Addresses: {len(unique_ips)}")
    print(f"  Duration: {duration:.1f} minutes")
    print(f"  Requests/min: {total/max(duration, 1):.1f}")

    print(f"\n🎯 TOP TARGETED PATHS")
    for path, count in paths.most_common(15):
        print(f"  {count:4d}x  {path}")

    print(f"\n🌐 TOP SOURCE IPS")
    for ip, count in ips_by_count.most_common(10):
        print(f"  {count:4d}x  {ip}")

    print(f"\n🤖 TOP USER AGENTS")
    for ua, count in user_agents.most_common(10):
        ua_short = ua[:70] + "..." if len(ua) > 70 else ua
        print(f"  {count:4d}x  {ua_short}")

    print(f"\n📝 HTTP METHODS")
    for method, count in methods.most_common():
        print(f"  {method}: {count}")

    print(f"\n⚠️  ATTACK PATTERNS DETECTED")
    print(f"  SQL Injection Attempts: {len(sql_injection)}")
    print(f"  Credential Stuffing Attempts: {len(credential_attempts)}")
    print(f"  Config File Requests: {len(config_file_requests)}")

    if sql_injection:
        print(f"\n💉 SQL INJECTION EXAMPLES:")
        for req in sql_injection[:5]:
            print(f"  {req['ip']} -> {req['path']}?{req.get('query_string', '')}")

    if credential_attempts:
        print(f"\n🔑 CREDENTIAL ATTEMPTS (sample):")
        for req in credential_attempts[:5]:
            print(f"  {req['ip']} -> {req['path']}")
            if req.get('post_data'):
                data_str = str(req['post_data'])[:200]
                print(f"     Data: {data_str}")

    if config_file_requests:
        print(f"\n📄 CONFIG FILE REQUESTS:")
        config_paths = Counter(r['path'] for r in config_file_requests)
        for path, count in config_paths.most_common(10):
            print(f"  {count:4d}x  {path}")

    # Interesting requests
    print(f"\n🎪 INTERESTING/UNUSUAL REQUESTS:")
    interesting = [r for r in requests if (
        len(r['path']) > 50 or
        'script' in r['path'].lower() or
        '../' in r['path'] or
        '%' in r['path']
    )]
    for req in interesting[:10]:
        print(f"  {req['ip']} -> {req['method']} {req['path'][:100]}")

    print("\n" + "="*80)
    print(f"💡 TIP: Full JSON logs available in {log_file}")
    print("="*80 + "\n")

    # Optional: save summary to file
    summary = {
        'total_requests': total,
        'unique_ips': len(unique_ips),
        'duration_minutes': duration,
        'top_paths': dict(paths.most_common(20)),
        'top_ips': dict(ips_by_count.most_common(20)),
        'attack_summary': {
            'sql_injection_attempts': len(sql_injection),
            'credential_attempts': len(credential_attempts),
            'config_file_requests': len(config_file_requests)
        }
    }

    with open('logs/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"📁 Summary saved to logs/summary.json\n")

if __name__ == '__main__':
    log_file = sys.argv[1] if len(sys.argv) > 1 else 'logs/access.log'
    analyze_logs(log_file)
