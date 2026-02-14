import requests
import sys
import time
import threading
import itertools
import json
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

# ==================================================
# ASCII BANNER
# ==================================================

BANNER = f"""{Fore.CYAN}
   _____ _   _  ____  _    _ _   _
  / ____| \\ | |/ __ \\| |  | | \\ | |
 | |  __|  \\| | |  | | |  | |  \\| |
 | | |_ | . ` | |  | | |  | | . ` |
 | |__| | |\\  | |__| | |__| | |\\  |
  \\_____|_| \\_|\\____/ \\____/|_| \\_|

{Fore.YELLOW}IP TRACKER - PRODUCTION EDITION
{Fore.GREEN}developed by @alzzdevmaret/bald
{Style.RESET_ALL}
"""

# ==================================================
# SPINNER
# ==================================================

class Spinner:
    def __init__(self, message="Processing"):
        self.spinner = itertools.cycle(
            ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        )
        self.running = False
        self.message = message
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def _spin(self):
        while self.running:
            sys.stdout.write(
                f"\r{Fore.CYAN}{self.message} {next(self.spinner)}"
            )
            sys.stdout.flush()
            time.sleep(0.1)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

# ==================================================
# TRACKER CORE
# ==================================================

class IPTracker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GNOWN-IP-Tracker/4.0 (Production Ready)"
        })

    def request_with_retry(self, url, retries=3):
        backoff = 1
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.RequestException:
                if attempt < retries - 1:
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    raise

    def track_ip_api(self, ip):
        url = f"http://ip-api.com/json/{ip}?fields=status,message,continent,country,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,hosting,query"
        data = self.request_with_retry(url)
        if data.get("status") == "success":
            return data
        raise Exception("Primary API failed")

    def track_ipwhois(self, ip):
        url = f"https://ipwho.is/{ip}"
        data = self.request_with_retry(url)

        if not data.get("success"):
            raise Exception("Fallback API failed")

        return {
            "query": data.get("ip"),
            "continent": data.get("continent"),
            "country": data.get("country"),
            "regionName": data.get("region"),
            "city": data.get("city"),
            "zip": data.get("postal"),
            "lat": data.get("latitude"),
            "lon": data.get("longitude"),
            "timezone": data.get("timezone", {}).get("id"),
            "isp": data.get("connection", {}).get("isp"),
            "org": data.get("connection", {}).get("org"),
            "as": data.get("connection", {}).get("asn"),
            "proxy": data.get("security", {}).get("proxy"),
            "hosting": data.get("security", {}).get("hosting"),
        }

    def get_my_ip(self):
        url = "https://api.ipify.org?format=json"
        data = self.request_with_retry(url)
        return data.get("ip")

    def track(self, ip):
        try:
            return self.track_ip_api(ip)
        except Exception:
            return self.track_ipwhois(ip)

# ==================================================
# OUTPUT
# ==================================================

def generate_maps_link(lat, lon):
    if lat and lon:
        return f"https://www.google.com/maps?q={lat},{lon}"
    return None

def display_pretty(data):
    print(Fore.GREEN + "\n=== TRACKING RESULT ===\n")

    for key, value in data.items():
        if value is not None:
            print(f"{Fore.YELLOW}{key:<15}{Fore.WHITE}: {value}")

    maps_link = generate_maps_link(data.get("lat"), data.get("lon"))
    if maps_link:
        print(f"\n{Fore.CYAN}Google Maps     : {Fore.WHITE}{maps_link}")

    print(Fore.GREEN + "\n=======================\n")

def display_json(data):
    maps_link = generate_maps_link(data.get("lat"), data.get("lon"))
    if maps_link:
        data["google_maps"] = maps_link
    print(json.dumps(data, indent=4))

# ==================================================
# CLI
# ==================================================

def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description=""
    )

    parser.add_argument(
        "--track",
        metavar="IP",
        help="Track target IP address or use 'myip'"
    )

    parser.add_argument(
        "-json",
        action="store_true",
        help="Output result in JSON format"
    )

    args = parser.parse_args()

    if not args.track:
        parser.print_help()
        sys.exit(0)

    tracker = IPTracker()
    spinner = Spinner("Tracking target")
    spinner.start()

    try:
        if args.track.lower() == "myip":
            target_ip = tracker.get_my_ip()
        else:
            target_ip = args.track

        result = tracker.track(target_ip)

    except Exception as e:
        spinner.stop()
        print(Fore.RED + f"[ERROR] {e}")
        sys.exit(1)

    spinner.stop()

    if args.json:
        display_json(result)
    else:
        display_pretty(result)

# ==================================================

if __name__ == "__main__":
    
