name: Deploy Frontend to AWS

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'
      - 'infrastructure/terraform/frontend/**'
      - '.github/workflows/deploy-frontend.yml'

env:
  AWS_REGION: us-east-1
  FRONTEND_BUCKET_NAME: ${{ secrets.FRONTEND_BUCKET_NAME }}
  CLOUDFRONT_DIST_ID: ${{ secrets.CLOUDFRONT_DIST_ID }}
  CUSTOM_DOMAIN_NAME: portal.lx-gateway.tech

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout source
        uses: actions/checkout@v3

      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v3
        with:
          role-to-assume: ${{ secrets.DEPLOYMENT_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies and build frontend
        working-directory: frontend
        run: |
          npm ci
          npm run build

      - name: Verify frontend build output
        run: ls -R frontend/build

      - name: Deploy to S3
        run: |
          aws s3 sync frontend/build s3://${{ env.FRONTEND_BUCKET_NAME }} --delete
        env:
          AWS_REGION: ${{ env.AWS_REGION }}

      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ env.CLOUDFRONT_DIST_ID }} \
            --paths "/*"
        env:
          AWS_REGION: ${{ env.AWS_REGION }}

      - name: Install Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.7

      - name: Deploy Frontend Infrastructure (Terraform)
        run: |
          cd infrastructure/terraform/frontend
          terraform init
          terraform apply -auto-approve \
            -var="bucket_name=${{ env.FRONTEND_BUCKET_NAME }}" \
            -var="domain_name=${{ env.CUSTOM_DOMAIN_NAME }}" \
            -var="acm_cert_arn=${{ secrets.ACM_CERT_ARN }}"
        env:
          AWS_REGION: ${{ env.AWS_REGION }}
