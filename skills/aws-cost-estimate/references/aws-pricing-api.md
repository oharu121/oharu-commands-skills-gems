# AWS Price List API Reference

The Price List API returns exact, region-specific pricing as structured JSON. The API endpoint is only available in `us-east-1` and `ap-south-1`, but can query any region's prices.

## Prerequisites

```bash
# Check CLI + credentials (run silently — don't ask the user)
which aws && aws sts get-caller-identity --query Account --output text 2>/dev/null
```

If either fails → fall back to web search.

## Common Service Codes

| Service | Service Code |
|---|---|
| EC2 | `AmazonEC2` |
| S3 | `AmazonS3` |
| OpenSearch | `AmazonES` |
| Bedrock | `AmazonBedrock` |
| Transit Gateway | `AWSTransitGateway` |
| VPC Endpoints | `AmazonVPCEndpoints` |

## Example Queries

### EC2 On-Demand pricing

```bash
aws pricing get-products \
  --service-code AmazonEC2 \
  --region us-east-1 \
  --filters \
    "Type=TERM_MATCH,Field=instanceType,Value=t3.medium" \
    "Type=TERM_MATCH,Field=location,Value=Asia Pacific (Tokyo)" \
    "Type=TERM_MATCH,Field=operatingSystem,Value=Linux" \
    "Type=TERM_MATCH,Field=tenancy,Value=Shared" \
    "Type=TERM_MATCH,Field=preInstalledSw,Value=NA" \
    "Type=TERM_MATCH,Field=capacitystatus,Value=Used" \
  --output json
```

### OpenSearch Serverless

```bash
aws pricing get-products \
  --service-code AmazonES \
  --region us-east-1 \
  --filters \
    "Type=TERM_MATCH,Field=location,Value=Asia Pacific (Tokyo)" \
  --output json
```

### S3 Standard Storage

```bash
aws pricing get-products \
  --service-code AmazonS3 \
  --region us-east-1 \
  --filters \
    "Type=TERM_MATCH,Field=location,Value=Asia Pacific (Tokyo)" \
    "Type=TERM_MATCH,Field=storageClass,Value=General Purpose" \
    "Type=TERM_MATCH,Field=volumeType,Value=Standard" \
  --output json
```

### Transit Gateway

```bash
aws pricing get-products \
  --service-code AWSTransitGateway \
  --region us-east-1 \
  --filters \
    "Type=TERM_MATCH,Field=location,Value=Asia Pacific (Tokyo)" \
  --output json
```

### VPC Endpoints (PrivateLink)

```bash
aws pricing get-products \
  --service-code AmazonVPCEndpoints \
  --region us-east-1 \
  --filters \
    "Type=TERM_MATCH,Field=location,Value=Asia Pacific (Tokyo)" \
  --output json
```

## Parsing the Response

Each product has a nested JSON structure:

```
terms.OnDemand.<offerTermCode>.priceDimensions.<rateCode>.pricePerUnit.USD
```

Use `jq` to extract prices:

```bash
# Extract all price dimensions for a product
aws pricing get-products ... --output json | jq -r '
  .PriceList[] | fromjson |
  .terms.OnDemand | to_entries[] |
  .value.priceDimensions | to_entries[] |
  "\(.value.description): $\(.value.pricePerUnit.USD)/\(.value.unit)"
'
```

## Tips

- Always use `--filters` to narrow results — unfiltered queries return massive JSON
- The `location` field uses display names (`"Asia Pacific (Tokyo)"`), not region codes (`ap-northeast-1`)
- For Bedrock models, filter by model ID (e.g., `anthropic.claude-sonnet-4-6-20250514-v1:0`)
- Run queries in parallel when possible — each service is independent
