import dns.resolver
import time

# Replace this with your domain
DOMAIN = "lx-gateway.tech"

# Expected AWS Route 53 nameservers
EXPECTED_NS = {
    "ns-799.awsdns-35.net.",
    "ns-98.awsdns-12.com.",
    "ns-1826.awsdns-36.co.uk.",
    "ns-1482.awsdns-57.org."
}

# Public DNS resolvers to check against
RESOLVERS = {
    "Google": "8.8.8.8",
    "Cloudflare": "1.1.1.1",
    "OpenDNS": "208.67.222.222",
    "Quad9": "9.9.9.9",
}

def check_ns(resolver_ip, label):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [resolver_ip]
    try:
        answer = resolver.resolve(DOMAIN, 'NS')
        returned_ns = {str(r).lower() for r in answer}
        success = EXPECTED_NS.issubset(returned_ns)
        return (label, success, returned_ns)
    except Exception as e:
        return (label, False, str(e))

def main():
    print(f"Checking NS propagation for {DOMAIN}...\nExpected: {EXPECTED_NS}\n")
    for label, ip in RESOLVERS.items():
        result = check_ns(ip, label)
        if result[1]:
            print(f"[✔] {label} ({ip}) sees all expected NS records.")
        else:
            print(f"[✖] {label} ({ip}) missing NS records.")
            print(f"    Returned: {result[2]}")
    print("\nCheck again later if not all resolvers are updated.")

if __name__ == "__main__":
    main()
