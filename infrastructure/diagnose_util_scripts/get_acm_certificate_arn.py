import boto3

def check_github_oidc_provider():
    iam = boto3.client('iam')

    try:
        response = iam.list_open_id_connect_providers()
        providers = response['OpenIDConnectProviderList']

        for provider in providers:
            provider_arn = provider['Arn']
            details = iam.get_open_id_connect_provider(OpenIDConnectProviderArn=provider_arn)
            url = details.get('Url', '')

            if url == 'token.actions.githubusercontent.com':
                print(f"✅ GitHub OIDC Provider found: {provider_arn}")
                print("Provider details:")
                print(f"- URL: {url}")
                print(f"- Client IDs: {details.get('ClientIDList', [])}")
                print(f"- Thumbprints: {details.get('ThumbprintList', [])}")
                return

        print("❌ GitHub OIDC Provider (token.actions.githubusercontent.com) NOT found.")

    except Exception as e:
        print(f"Error checking OIDC providers: {e}")

if __name__ == "__main__":
    check_github_oidc_provider()
