# AWS Pricing Calculator — Browser Automation Guide

The AWS Pricing Calculator (https://calculator.aws/) has no API. Browser automation via Playwright MCP is the only way to generate shareable links.

## General Flow

1. Navigate to https://calculator.aws/
2. For each service:
   - Click "Add service"
   - Search for the service name
   - Configure the parameters
   - Click "Add to estimate"
3. Click "Save and share" → "Agree and continue"
4. Copy the generated URL

## Known Limitations

### Chatbot overlay
The AWS support chatbot notification can intercept pointer events. Close it first:
- Look for a chat/notification icon in the bottom-right
- Click to dismiss before interacting with the calculator

### OCU fields accept integers only
OpenSearch Serverless OCU fields reject decimal values (e.g., 0.5).
- Workaround: use `1` for both indexing and search OCU (total 2 OCU minimum in calculator)
- Note in the report that actual billing supports 0.5 OCU increments

### Service-specific tips

**OpenSearch Serverless**:
- Search for "OpenSearch Serverless"
- Set OCU for indexing and search separately
- Storage is charged separately per GB

**EC2**:
- Select region first
- Choose "On-Demand" pricing
- Specify instance type and OS

**VPC / Transit Gateway**:
- Search for "VPC"
- Add Transit Gateway attachments and data processing
- Add PrivateLink endpoints with AZ count

## Timing

Expect ~2-5 minutes for the full flow. Only offer this step when the user explicitly requests it.
