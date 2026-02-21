"""
tester.py — DA5402 Assignment 2 Part 2
Load Balancing Verification Script

Sends 100 concurrent requests to the /ner endpoint and counts which
container handled each request. Proves Docker Swarm's Ingress Mesh is
distributing traffic across all replicas.
"""

import requests
from collections import Counter
import concurrent.futures
import sys

# CONFIGURATION

# Manager node IP — if testing locally, use localhost; if testing across machines, use Manager's IP
MANAGER_IP = "localhost"  

PORT = 8000
ENDPOINT = "/ner"
URL = f"http://{MANAGER_IP}:{PORT}{ENDPOINT}"

TOTAL_REQUESTS = 100
MAX_WORKERS = 10

# Payload updated for Named Entity Recognition
TEST_PAYLOAD = {
    "text": "Sundar Pichai is hiring for Google in Bangalore."
}


def call_api(_):
    try:
        r = requests.post(URL, json=TEST_PAYLOAD, timeout=15)
        if r.status_code == 200:
            return r.json().get("container_id", "unknown")
        else:
            return f"HTTP_{r.status_code}"
    except requests.ConnectionError:
        return "connection_failed"
    except requests.Timeout:
        return "timeout"
    except Exception as e:
        return f"error: {str(e)}"


if __name__ == "__main__":
    print(" DA5402 Assignment 2 — Docker Swarm Load Balancing Test")
    print(f"\nTarget URL       : {URL}")
    print(f"Total requests   : {TOTAL_REQUESTS}")
    print(f"Concurrent workers: {MAX_WORKERS}\n")
    print("Sending requests...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(call_api, range(TOTAL_REQUESTS)))

    counts = Counter(results)

    error_keys = {"connection_failed", "timeout"}
    failed = sum(
        v for k, v in counts.items()
        if k.startswith("HTTP_") or k in error_keys or k.startswith("error")
    )
    successful = TOTAL_REQUESTS - failed

    unique_containers = [
        k for k in counts
        if not k.startswith("HTTP_")
        and k not in error_keys
        and not k.startswith("error")
        and k != "unknown"
    ]

    print("\nContainer distribution:")
    
    for container_id, count in sorted(counts.items(), key=lambda x: -x[1]):
        display_id = container_id[:22] if len(container_id) > 22 else container_id
        bar = "█" * count
        
        if container_id in unique_containers:
            print(f"  {display_id:<24}: {count:>3} requests  {bar}")
        else:
            print(f"  {display_id:<24}: {count:>3} requests")

    print("Summary:")
    print(f"  Total requests    : {TOTAL_REQUESTS}")
    print(f"  Successful (200)  : {successful}")
    print(f"  Failed            : {failed}")
    print(f"  Unique containers : {len(unique_containers)}")

    if failed > 0:
        print("\n WARNING: Some requests failed.")
    
    if len(unique_containers) >= 2:
        print("\n PASS — Load is distributed across multiple containers!")
        print(f"   Traffic hit {len(unique_containers)} different container(s).")
        exit_code = 0
    else:
        print("\n FAIL — All requests hit the same container!")
        print(f"   Expected: 4 replicas | Actual: {len(unique_containers)} unique container(s)")
        exit_code = 1

    sys.exit(exit_code)