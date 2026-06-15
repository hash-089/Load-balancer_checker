# Load Balancer Analyzer - Complete Usage Guide

## Installation

```bash
git clone https://github.com/hash-089/load-balancer-analyzer.git
cd load-balancer-analyzer
 1.Make it executable
chmod +x install.sh
 2. Run it
./install.sh
4.chmod +x lb_analyzer.py
Command Reference
Basic Command Structure
bash
python lb_analyzer.py -u <TARGET_URL> [OPTIONS]
All Available Options
Option	Description	Default	Example
-u, --url	Target URL (required)	None	-u http://balancer.com
-r, --requests	Number of requests to send	50	-r 200
-t, --threads	Concurrent threads	5	-t 20
--delay-min	Minimum delay in seconds	0.5	--delay-min 1
--delay-max	Maximum delay in seconds	2.0	--delay-max 5
--timeout	Request timeout in seconds	10	--timeout 30
--stealth	Enable stealth mode	False	--stealth
--no-verify-ssl	Disable SSL verification	False	--no-verify-ssl
-v, --verbose	Verbose output	False	-v
--output	Save results to file	None	--output results.json
Usage Examples
Example 1: Basic Scan
bash
python lb_analyzer.py -u http://balancer.taget.com
Output:

text
[+] Sending 50 requests to http://balancer.target.com
  Request   1: Status=200, Size=12453, Time=0.234s, Hash=a3f5c8e1
  Request   2: Status=200, Size=12453, Time=0.198s, Hash=b4e6d9f2
  
ANALYSIS RESULTS
[✓] DETECTED MULTIPLE BACKENDS!
    - Backend #1: 25 requests
    - Backend #2: 25 requests
[!!!] FLAGS FOUND: flag{example_123}
Example 2: Stealth Mode
bash
python lb_analyzer.py -u https://api.example.com --stealth -r 30
Example 3: High Speed Scan
bash
python lb_analyzer.py -u http://target.com -r 200 -t 20
Example 4: Save Results to File
bash
python lb_analyzer.py -u http://balancer.target.com --output results.json -v
Example 5: Disable SSL Verification
bash
python lb_analyzer.py -u https://self-signed.com --no-verify-ssl
Example 6: Complete Security Audit
bash
python lb_analyzer.py -u https://secure-app.com -r 100 -t 10 --output audit.json -v
Example 7: Slow and Careful Scan
bash
python lb_analyzer.py -u https://production.com --delay-min 2 --delay-max 5 -r 20
Example 8: API Testing
bash
python lb_analyzer.py -u https://api.example.com/v1 --stealth -r 50 --output api_scan.json
Example 9: Debug Mode (Verbose)
bash
python lb_analyzer.py -u http://test.com -v -r 20
Example 10: Multiple Backends Detection Only
bash
python lb_analyzer.py -u http://balancer.com -r 100 --delay-min 0.1
Common Scenarios
Scenario 1: CTF Challenge
bash
python lb_analyzer.py -u http://balancer.hackycorp.com --stealth -v
Scenario 2: Production Environment
bash
python lb_analyzer.py -u https://yourcompany.com --stealth --delay-min 2 --delay-max 5 -r 50 --output prod_scan.json
Scenario 3: Internal Network
bash
python lb_analyzer.py -u http://10.0.0.100 -r 200 -t 20 --no-verify-ssl
Scenario 4: Development Server
bash
python lb_analyzer.py -u http://dev-server.local -r 100 -v --output dev_results.json
Understanding Output
What the Output Means
text
[+] Sending 50 requests          # Tool is working
Request 1: Status=200            # HTTP 200 = OK
Size=12453                       # Response size in bytes
Time=0.234s                      # Response time
Hash=a3f5c8e1                    # Unique content identifier

[✓] DETECTED MULTIPLE BACKENDS   # Different hashes found
Backend #1: 25 requests           # First server handled 25 requests
Backend #2: 25 requests           # Second server handled 25 requests

[!!!] FLAGS FOUND                 # Potential flags discovered
flag{example_123}                 # The actual flag
Status Codes Explained
Code	Meaning	Action
200	OK - Normal response	Good
301/302	Redirect	Followed automatically
403	Forbidden	May indicate hidden backend
404	Not Found	Probably wrong path
429	Too Many Requests	Rate limited - increase delays
500	Server Error	Backend issue - investigate
Troubleshooting
Problem: SSL Certificate Error
Solution:

bash
python lb_analyzer.py -u https://target.com --no-verify-ssl
Problem: Rate Limited (429 errors)
Solution:

bash
python lb_analyzer.py -u http://target.com --delay-min 3 --delay-max 8 -r 20
Problem: Connection Timeout
Solution:

bash
python lb_analyzer.py -u http://target.com --timeout 30
Problem: No Backends Found
Solution:

bash
python lb_analyzer.py -u http://target.com -r 200
Problem: Too Slow
Solution:

bash
python lb_analyzer.py -u http://target.com -t 20 --delay-min 0.1
Problem: Blocked by WAF
Solution:

bash
python lb_analyzer.py -u http://target.com --stealth --delay-min 3 --delay-max 8
Advanced Usage
Custom Configuration File
Create config.json:

json
{
  "timeout": 15,
  "max_retries": 5,
  "delay_min": 1,
  "delay_max": 3,
  "threads": 10,
  "stealth": true
}
Pipe Results to Other Tools
bash
python lb_analyzer.py -u http://target.com --output results.json
cat results.json | jq '.flags'
Run in Background
bash
nohup python lb_analyzer.py -u http://target.com -r 500 --output scan.json &
Schedule Regular Scans
bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/tool && python lb_analyzer.py -u http://target.com --output daily_$(date +\%Y\%m\%d).json
Quick Reference Card
bash
# Most common commands

# Quick test
python lb_analyzer.py -u http://target.com

# Stealth mode
python lb_analyzer.py -u https://target.com --stealth

# Save results
python lb_analyzer.py -u http://target.com --output results.json

# Verbose + save
python lb_analyzer.py -u http://target.com -v --output debug.json

# High speed
python lb_analyzer.py -u http://target.com -r 200 -t 20

# Bypass SSL
python lb_analyzer.py -u https://target.com --no-verify-ssl

# Avoid rate limits
python lb_analyzer.py -u http://target.com --delay-min 2 --delay-max 5

# Complete audit
python lb_analyzer.py -u https://target.com -r 100 -t 10 --stealth --output full_audit.json -v
Tips and Best Practices
Start with default settings - Use basic command first

Increase requests if needed - Use -r 100 for better detection

Use stealth for production - Always use --stealth on live sites

Save results always - Use --output to keep findings

Be respectful - Use delays when scanning production

Check logs - Verbose mode -v helps debug issues

Verify findings - Manually check discovered flags

Stay legal - Only scan authorized targets

Exit Codes
Code	Meaning
0	Success - Flags found
1	Completed - No flags found
130	Interrupted by user
255	Error occurred
Help Command
bash
python lb_analyzer.py --help
Uninstall
bash
# Remove the tool
rm -rf load-balancer-analyzer

# Or if installed via pip
pip uninstall load-balancer-analyzer
License
MIT License - Free for educational and authorized testing use.

Disclaimer
Use only on systems you own or have permission to test. Unauthorized scanning may violate laws.

