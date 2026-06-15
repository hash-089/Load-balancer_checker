#!/usr/bin/env python3
"""
Real-World Load Balancer Analyzer
Professional tool for analyzing production load balancers and multi-backend systems
"""

import requests
import hashlib
import time
import sys
import os
import json
import csv
import random
import logging
from collections import Counter, defaultdict
from urllib.parse import urlparse, urljoin
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Any
import argparse
import signal

# For advanced features
try:
    from fake_useragent import UserAgent
    UA_AVAILABLE = True
except ImportError:
    UA_AVAILABLE = False
    print("[!] Install fake-useragent for better stealth: pip install fake-useragent")

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Define dummy color classes
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = RESET = ''
    class Style:
        BRIGHT = DIM = RESET_ALL = ''

class ProductionLoadBalancerAnalyzer:
    """Production-ready load balancer analyzer with real-world features"""
    
    def __init__(self, target_url: str, config: Dict = None):
        self.target_url = target_url.rstrip('/')
        self.config = self._load_default_config()
        if config:
            self.config.update(config)
            
        # Setup session with real browser headers
        self.session = self._create_session()
        
        # Data storage
        self.responses = []
        self.backends = {}
        self.statistics = {}
        
        # Setup logging
        self._setup_logging()
        
        # Initialize fake user agent
        self.ua = UserAgent() if UA_AVAILABLE else None
        
    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            'timeout': 10,
            'max_retries': 3,
            'retry_delay': 2,
            'rate_limit': 1.0,  # requests per second
            'max_workers': 5,
            'user_agent_rotation': True,
            'respect_robots': True,
            'verify_ssl': False,  # Set to True for production with valid SSL
            'allow_redirects': True,
            'max_redirects': 5,
            'follow_robots': False,
            'delay_min': 0.5,
            'delay_max': 2.0,
            'jitter': True,  # Add random delay to avoid detection
        }
    
    def _setup_logging(self):
        """Setup professional logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'lb_analyzer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_session(self) -> requests.Session:
        """Create a session with realistic browser headers"""
        session = requests.Session()
        
        # Base headers that mimic a real browser
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        return session
    
    def _get_headers(self) -> Dict:
        """Get randomized headers for each request"""
        headers = {}
        
        if self.config['user_agent_rotation'] and self.ua:
            headers['User-Agent'] = self.ua.random
        else:
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        # Add random referer
        referers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://duckduckgo.com/',
            None
        ]
        if random.choice([True, False]):
            headers['Referer'] = random.choice([r for r in referers if r])
        
        return headers
    
    def _respect_rate_limit(self):
        """Respect rate limiting with jitter"""
        if self.config['jitter']:
            delay = random.uniform(self.config['delay_min'], self.config['delay_max'])
        else:
            delay = self.config['rate_limit']
        
        if delay > 0:
            time.sleep(delay)
    
    def _make_request(self, url: str, payload: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make a single request with retries and error handling"""
        headers = self._get_headers()
        
        for attempt in range(self.config['max_retries']):
            try:
                self._respect_rate_limit()
                
                response = self.session.get(
                    url,
                    headers=headers,
                    params=payload,
                    timeout=self.config['timeout'],
                    verify=self.config['verify_ssl'],
                    allow_redirects=self.config['allow_redirects']
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', 60))
                    self.logger.warning(f"Rate limited! Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                return response
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1}/{self.config['max_retries']}")
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"Connection error: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
            
            if attempt < self.config['max_retries'] - 1:
                time.sleep(self.config['retry_delay'])
        
        return None
    
    def detect_load_balancer_type(self) -> Dict:
        """Detect the type of load balancer being used"""
        lb_signatures = {
            'AWS ALB': ['x-amzn-RequestId', 'x-amz-cf-id', 'x-amzn-trace-id'],
            'AWS ELB': ['x-amzn-RequestId', 'x-amz-id-2'],
            'CloudFlare': ['CF-RAY', 'CF-Cache-Status', 'CF-Request-ID'],
            'F5': ['X-F5-Request-ID', 'X-F5-Route-Id'],
            'NGINX': ['Server: nginx', 'X-Request-ID'],
            'HAProxy': ['Server: HAProxy', 'X-Request-ID'],
            'Apache': ['Server: Apache', 'mod_ssl'],
            'Google Cloud LB': ['X-Cloud-Trace-Context', 'alt-svc'],
            'Azure LB': ['x-ms-request-id', 'x-ms-client-request-id'],
            'Akamai': ['X-Akamai-Request-ID', 'X-Akamai-Transformed'],
            'Fastly': ['X-Served-By', 'X-Cache', 'X-Cache-Hits'],
            'Varnish': ['X-Varnish', 'X-Cache', 'X-Cache-Hits']
        }
        
        self.logger.info("Detecting load balancer type...")
        
        # Send test request
        response = self._make_request(self.target_url)
        if not response:
            return {'detected': False, 'type': 'Unknown', 'evidence': []}
        
        evidence = []
        detected_types = []
        
        for lb_type, headers in lb_signatures.items():
            matched = []
            for header in headers:
                if header in response.headers:
                    matched.append(header)
                elif ':' in header:
                    # Check for server header match
                    key, value = header.split(': ', 1)
                    if key in response.headers and value.lower() in response.headers[key].lower():
                        matched.append(header)
            
            if matched:
                detected_types.append(lb_type)
                evidence.extend(matched)
        
        return {
            'detected': len(detected_types) > 0,
            'type': ', '.join(detected_types) if detected_types else 'Unknown/L7 LB',
            'evidence': evidence,
            'headers': dict(response.headers)
        }
    
    def analyze_backend_health(self, num_requests: int = 50) -> Dict:
        """Analyze backend health and performance metrics"""
        self.logger.info(f"Analyzing backend health with {num_requests} requests...")
        
        metrics = {
            'backends': {},
            'overall': {
                'success_rate': 0,
                'avg_response_time': 0,
                'p95_response_time': 0,
                'p99_response_time': 0,
                'error_rate': 0
            }
        }
        
        response_times = []
        errors = 0
        
        for i in range(num_requests):
            start_time = time.time()
            response = self._make_request(self.target_url)
            elapsed = time.time() - start_time
            
            if response and response.status_code < 500:
                response_times.append(elapsed)
                
                # Identify backend by content hash
                content_hash = hashlib.md5(response.content[:500]).hexdigest()
                
                if content_hash not in metrics['backends']:
                    metrics['backends'][content_hash] = {
                        'requests': 0,
                        'response_times': [],
                        'status_codes': Counter(),
                        'hash': content_hash[:16]
                    }
                
                metrics['backends'][content_hash]['requests'] += 1
                metrics['backends'][content_hash]['response_times'].append(elapsed)
                metrics['backends'][content_hash]['status_codes'][response.status_code] += 1
            else:
                errors += 1
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                self.logger.info(f"  Progress: {i + 1}/{num_requests} requests")
        
        # Calculate metrics
        if response_times:
            sorted_times = sorted(response_times)
            metrics['overall']['avg_response_time'] = sum(response_times) / len(response_times)
            metrics['overall']['p95_response_time'] = sorted_times[int(len(sorted_times) * 0.95)]
            metrics['overall']['p99_response_time'] = sorted_times[int(len(sorted_times) * 0.99)]
            metrics['overall']['success_rate'] = (len(response_times) / num_requests) * 100
            metrics['overall']['error_rate'] = (errors / num_requests) * 100
        
        # Calculate per-backend metrics
        for backend in metrics['backends'].values():
            if backend['response_times']:
                backend['avg_response_time'] = sum(backend['response_times']) / len(backend['response_times'])
                backend['min_response_time'] = min(backend['response_times'])
                backend['max_response_time'] = max(backend['response_times'])
        
        self.statistics['health'] = metrics
        return metrics
    
    def find_backend_differences(self) -> List[Dict]:
        """Find functional differences between backends"""
        self.logger.info("Testing for backend differences...")
        
        test_payloads = [
            {'name': 'IDOR Test', 'payload': {'id': '1'}},
            {'name': 'SQL Injection', 'payload': {'id': "' OR '1'='1"}},
            {'name': 'Path Traversal', 'payload': {'file': '../../etc/passwd'}},
            {'name': 'XSS Test', 'payload': {'q': '<script>alert(1)</script>'}},
            {'name': 'Debug Param', 'payload': {'debug': 'true'}},
            {'name': 'Admin Access', 'payload': {'admin': 'true'}},
            {'name': 'API Version', 'payload': {'v': '2'}},
            {'name': 'Language Change', 'payload': {'lang': 'en'}},
            {'name': 'Format Change', 'payload': {'format': 'json'}},
            {'name': 'Deprecated Param', 'payload': {'legacy': 'true'}},
        ]
        
        differences = []
        
        # First, get baseline responses from each backend
        baseline_responses = {}
        for i in range(20):  # Send 20 requests to map backends
            response = self._make_request(self.target_url)
            if response:
                content_hash = hashlib.md5(response.content[:500]).hexdigest()
                if content_hash not in baseline_responses:
                    baseline_responses[content_hash] = response.text[:1000]
        
        # Test each payload on each backend
        for test in test_payloads:
            self.logger.info(f"  Testing: {test['name']}")
            
            backend_responses = defaultdict(list)
            
            # Send multiple requests to hit different backends
            for i in range(len(baseline_responses) * 3):
                response = self._make_request(self.target_url, test['payload'])
                if response:
                    content_hash = hashlib.md5(response.content[:500]).hexdigest()
                    backend_responses[content_hash].append(response)
            
            # Analyze responses per backend
            for hash_key, responses in backend_responses.items():
                if len(responses) > 0:
                    # Check for interesting patterns
                    for response in responses[:2]:  # Check first 2 responses
                        response_text = response.text.lower()
                        
                        if any(keyword in response_text for keyword in ['error', 'exception', 'warning', 'debug']):
                            differences.append({
                                'backend': hash_key[:16],
                                'test': test['name'],
                                'payload': test['payload'],
                                'finding': 'Error/Exception message',
                                'snippet': response.text[:200]
                            })
                        
                        if any(keyword in response_text for keyword in ['flag{', 'key{', 'ctf{', 'secret']):
                            differences.append({
                                'backend': hash_key[:16],
                                'test': test['name'],
                                'payload': test['payload'],
                                'finding': 'POTENTIAL FLAG FOUND!',
                                'snippet': response.text[:500]
                            })
                        
                        # Check for different response sizes
                        baseline_size = len(baseline_responses.get(hash_key, ''))
                        current_size = len(response.text)
                        if baseline_size and abs(current_size - baseline_size) > baseline_size * 0.2:  # 20% difference
                            differences.append({
                                'backend': hash_key[:16],
                                'test': test['name'],
                                'payload': test['payload'],
                                'finding': f'Significant size difference: {current_size} vs {baseline_size} bytes',
                                'snippet': response.text[:200]
                            })
        
        self.statistics['differences'] = differences
        return differences
    
    def session_persistence_test(self, num_requests: int = 30) -> Dict:
        """Test if load balancer uses sticky sessions"""
        self.logger.info("Testing session persistence...")
        
        results = {
            'sticky_sessions': False,
            'session_behavior': 'Unknown',
            'cookie_required': False,
            'analysis': {}
        }
        
        # Test 1: Same session (with cookies)
        session = requests.Session()
        session.headers.update(self._get_headers())
        
        same_session_responses = []
        for i in range(num_requests):
            response = session.get(self.target_url, timeout=10)
            if response:
                content_hash = hashlib.md5(response.content[:500]).hexdigest()
                same_session_responses.append(content_hash)
        
        same_session_unique = len(set(same_session_responses))
        
        # Test 2: Different sessions
        different_session_responses = []
        for i in range(num_requests):
            new_session = requests.Session()
            new_session.headers.update(self._get_headers())
            response = new_session.get(self.target_url, timeout=10)
            if response:
                content_hash = hashlib.md5(response.content[:500]).hexdigest()
                different_session_responses.append(content_hash)
        
        diff_session_unique = len(set(different_session_responses))
        
        # Analyze results
        results['analysis']['same_session_backends'] = same_session_unique
        results['analysis']['different_session_backends'] = diff_session_unique
        
        if same_session_unique == 1 and diff_session_unique > 1:
            results['sticky_sessions'] = True
            results['session_behavior'] = 'Cookie-based sticky sessions'
            results['cookie_required'] = True
        elif same_session_unique > 1 and diff_session_unique > 1:
            results['session_behavior'] = 'Round-robin or random (no stickiness)'
        elif same_session_unique == diff_session_unique == 1:
            results['session_behavior'] = 'Single backend detected'
        else:
            results['session_behavior'] = 'Complex load balancing strategy'
        
        self.statistics['session_test'] = results
        return results
    
    def extract_sensitive_info(self) -> List[Dict]:
        """Extract sensitive information from responses"""
        self.logger.info("Extracting sensitive information...")
        
        sensitive_patterns = {
            'API Keys': r'[a-zA-Z0-9_-]{32,}',
            'Email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'IP Address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'JWT Token': r'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
            'AWS Key': r'AKIA[0-9A-Z]{16}',
            'Private Key': r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
            'Password in URL': r'password=[^&\s]+',
            'Session Token': r'session=[a-f0-9]{32,}',
            'Database Creds': r'(mysql|postgres|mongodb)://[^:\s]+:[^@\s]+@',
            'Internal Paths': r'(?:/var|/home|/usr|/opt|/etc)/[\w/]+',
            'Debug Info': r'(debug|trace|dump)\s*:\s*\{[^}]+\}',
            'Stack Trace': r'(Traceback|Exception|Error|Warning):.*\n.*File "',
            'Flag Format': r'(flag|FLAG|key|KEY)\{[^}]+\}',
            'Hardcoded Secret': r'(secret|token|api_key)\s*=\s*["\'][^"\']+["\']',
        }
        
        findings = []
        
        for response in self.responses[:20]:  # Analyze first 20 responses
            for category, pattern in sensitive_patterns.items():
                import re
                matches = re.findall(pattern, response['full_body'], re.IGNORECASE)
                
                for match in matches[:3]:  # Limit matches per category
                    findings.append({
                        'category': category,
                        'match': match[:100],  # Truncate long matches
                        'request_num': response['request_num'],
                        'backend': response.get('backend_id', 'Unknown')
                    })
        
        # Remove duplicates
        unique_findings = []
        seen = set()
        for finding in findings:
            key = f"{finding['category']}:{finding['match']}"
            if key not in seen:
                seen.add(key)
                unique_findings.append(finding)
        
        self.statistics['sensitive_info'] = unique_findings
        return unique_findings
    
    def generate_report(self, format: str = 'json') -> str:
        """Generate professional report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"lb_analysis_report_{timestamp}.{format}"
        
        report_data = {
            'target': self.target_url,
            'timestamp': timestamp,
            'statistics': self.statistics,
            'total_backends': len(self.backends),
            'total_requests': len(self.responses),
            'config': self.config
        }
        
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
        
        elif format == 'csv':
            # Flatten the report for CSV
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Target', self.target_url])
                writer.writerow(['Timestamp', timestamp])
                writer.writerow(['Total Backends', len(self.backends)])
                writer.writerow(['Total Requests', len(self.responses)])
        
        self.logger.info(f"Report saved: {filename}")
        return filename
    
    def run_complete_analysis(self) -> Dict:
        """Run complete production analysis"""
        self.logger.info("="*60)
        self.logger.info("STARTING COMPLETE LOAD BALANCER ANALYSIS")
        self.logger.info("="*60)
        
        # 1. Detect load balancer type
        lb_info = self.detect_load_balancer_type()
        self.statistics['load_balancer'] = lb_info
        self.logger.info(f"Load Balancer: {lb_info['type']}")
        
        # 2. Send baseline requests
        self.logger.info("Sending baseline requests...")
        for i in range(30):
            response = self._make_request(self.target_url)
            if response:
                self.responses.append({
                    'request_num': i + 1,
                    'timestamp': datetime.now().isoformat(),
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'content_hash': hashlib.md5(response.content[:500]).hexdigest(),
                    'headers': dict(response.headers),
                    'full_body': response.text,
                    'response_time': response.elapsed.total_seconds()
                })
        
        # 3. Group by backend
        for response in self.responses:
            hash_key = response['content_hash']
            if hash_key not in self.backends:
                self.backends[hash_key] = []
            self.backends[hash_key].append(response)
            response['backend_id'] = hash_key[:16]
        
        # 4. Health analysis
        health = self.analyze_backend_health(50)
        
        # 5. Session persistence test
        session_test = self.session_persistence_test()
        
        # 6. Find backend differences
        differences = self.find_backend_differences()
        
        # 7. Extract sensitive info
        sensitive = self.extract_sensitive_info()
        
        # 8. Generate report
        report_file = self.generate_report('json')
        
        # 9. Summary
        self.logger.info("\n" + "="*60)
        self.logger.info("ANALYSIS COMPLETE - SUMMARY")
        self.logger.info("="*60)
        self.logger.info(f"Load Balancer Type: {lb_info['type']}")
        self.logger.info(f"Backends Detected: {len(self.backends)}")
        self.logger.info(f"Sticky Sessions: {session_test['sticky_sessions']}")
        self.logger.info(f"Sensitive Info Found: {len(sensitive)}")
        self.logger.info(f"Backend Differences: {len(differences)}")
        self.logger.info(f"Report Saved: {report_file}")
        
        # Highlight flags
        flags = [f for f in sensitive if 'Flag' in f['category']]
        if flags:
            self.logger.info(f"\n{Fore.GREEN}{Style.BRIGHT}[!!!] FLAGS FOUND:")
            for flag in flags:
                self.logger.info(f"  {flag['match']}")
        
        return self.statistics

def main():
    parser = argparse.ArgumentParser(
        description='Professional Load Balancer Analyzer for Real-World Applications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lb_analyzer.py -u http://balancer.hackycorp.com
  python3 lb_analyzer.py -u https://api.example.com -r 100 -t 5
  python3 lb_analyzer.py -u http://localhost:8080 --no-verify-ssl --output report.json
        """
    )
    
    parser.add_argument('-u', '--url', required=True, help='Target URL')
    parser.add_argument('-r', '--requests', type=int, default=50, help='Number of requests (default: 50)')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Number of threads (default: 5)')
    parser.add_argument('--delay-min', type=float, default=0.5, help='Minimum delay between requests (default: 0.5)')
    parser.add_argument('--delay-max', type=float, default=2.0, help='Maximum delay between requests (default: 2.0)')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('--no-verify-ssl', action='store_true', help='Disable SSL verification')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--stealth', action='store_true', help='Enable stealth mode (slower, randomized)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Configure based on arguments
    config = {
        'timeout': args.timeout,
        'max_workers': args.threads,
        'delay_min': args.delay_min,
        'delay_max': args.delay_max,
        'verify_ssl': not args.no_verify_ssl,
        'jitter': args.stealth,
        'user_agent_rotation': args.stealth or True,
    }
    
    if args.stealth:
        config['delay_min'] = max(1.0, config['delay_min'])
        config['delay_max'] = max(3.0, config['delay_max'])
        config['rate_limit'] = 0.5  # Slower rate
    
    # Initialize analyzer
    analyzer = ProductionLoadBalancerAnalyzer(args.url, config)
    
    if args.verbose:
        analyzer.logger.setLevel(logging.DEBUG)
    
    try:
        # Run analysis
        results = analyzer.run_complete_analysis()
        
        # Save output if specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n[✓] Results saved to {args.output}")
        
        # Return appropriate exit code
        if any('Flag' in str(f) for f in results.get('sensitive_info', [])):
            print(f"\n{Fore.GREEN}[✓] Flags successfully extracted!")
            sys.exit(0)
        else:
            print(f"\n{Fore.YELLOW}[!] Analysis complete but no flags found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
