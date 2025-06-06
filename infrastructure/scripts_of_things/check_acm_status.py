import boto3
import sys

# Replace with your actual certificate ARN
CERTIFICATE_ARN = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"
REGION = "us-east-1"


def main():
    acm = boto3.client("acm", region_name=REGION)

    try:
        response = acm.describe_certificate(CertificateArn=CERTIFICATE_ARN)
        cert = response["Certificate"]
        status = cert["Status"]
        domain = cert["DomainName"]

        print(f"🔍 Certificate for {domain}")
        print(f"📄 Status: {status}")

        if status == "ISSUED":
            print("✅ Certificate has been issued.")
        elif status == "PENDING_VALIDATION":
            print("⚠️ Certificate is pending validation.")
            print("📌 DNS records required for validation:")

            for option in cert["DomainValidationOptions"]:
                if "ResourceRecord" in option:
                    rr = option["ResourceRecord"]
                    print(f"\n➡️ Name:  {rr['Name']}")
                    print(f"   Type:  {rr['Type']}")
                    print(f"   Value: {rr['Value']}")
                else:
                    print("❗ ResourceRecord not yet available. Please wait a moment and try again.")
        else:
            print(f"ℹ️ Certificate is in state: {status}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
