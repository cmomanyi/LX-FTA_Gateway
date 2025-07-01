import requests
import threading
import time
import json
from datetime import datetime
import random

API_BASE = "https://api.lx-gateway.tech/simulate"
NUM_THREADS = 30
TOTAL_REQUESTS = 1200
REQUEST_INTERVAL = 0.01  # delay between requests per thread

# Attack payload samples
attack_samples = {
    "spoofing": {
        "sensor_id": "sensor-x",
        "payload": "abc123",
        "ecc_signature": "invalid_hash"
    },
    "replay": {
        "sensor_id": "sensor-x",
        "timestamp": "",
        "nonce": ""
    },
    "firmware": {
        "sensor_id": "sensor-x",
        "firmware_version": "1.0.3",
        "firmware_signature": "invalid_signature"
    },
    "ml_evasion": {
        "sensor_id": "sensor-x",
        "values": [1.2, 2.3, 3.4]
    },
    "ddos": {
        "sensor_id": "sensor-x",
        "threshold": 10
    },
    "sensor_hijack": {
        "sensor_id": "sensor-x",
        "unauthorized_access": True
    },
    "api_abuse": {
        "sensor_id": "sensor-x",
        "excessive_calls": 200
    },
    "tamper_breach": {
        "sensor_id": "sensor-x",
        "casing_opened": True
    },
    "side_channel": {
        "sensor_id": "sensor-x",
        "timing_leak": "detected"
    }
}

attack_types = list(attack_samples.keys())


def dynamic_payload(attack_type, template):
    payload = dict(template)  # shallow copy
    if attack_type == "replay":
        payload["timestamp"] = datetime.utcnow().isoformat()
        payload["nonce"] = f"nonce-{random.randint(100000, 999999)}"
    elif attack_type == "ddos":
        payload["threshold"] = 10
    return payload


def simulate_attack(attack_type, payload, thread_id):
    url = f"{API_BASE}/{attack_type}"
    try:
        res = requests.post(url, json=payload, timeout=3)
        res.raise_for_status()
        data = res.json()
        status = "🚫 Blocked" if data.get("blocked") else "✅ Allowed"
        print(f"[T{thread_id:02}] [{attack_type.upper()}] {status} - {data.get('message')}")
    except Exception as e:
        print(f"[T{thread_id:02}] [{attack_type.upper()}] ❌ Error: {str(e)[:80]}")


def attack_worker(thread_id, attack_type):
    template = attack_samples[attack_type]
    num_requests = TOTAL_REQUESTS // NUM_THREADS
    for _ in range(num_requests):
        payload = dynamic_payload(attack_type, template)
        simulate_attack(attack_type, payload, thread_id)
        time.sleep(REQUEST_INTERVAL)


def main():
    print(
        f"🚀 Starting randomized attack simulation with {NUM_THREADS} threads and {TOTAL_REQUESTS} total requests...\n")
    threads = []

    for i in range(NUM_THREADS):
        attack_type = random.choice(attack_types)
        thread = threading.Thread(target=attack_worker, args=(i + 1, attack_type))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("\n✅ Simulation completed.")


if __name__ == "__main__":
    main()
