# Layout Guidelines for AWS Architecture Diagrams

## General Principles

1. **Max 15-20 icons per diagram** - Keep diagrams focused and readable
2. **Primary data flow on horizontal axis** (left-to-right)
3. **Auxiliary services above/below main flow**
4. **Japanese text by default** for labels
5. **Plain text only** - No HTML in labels

## Typography

- **Icon labels**: 12px, fontColor=#232F3E
- **Edge labels**: 10px
- **Group labels**: 12px, bold (fontStyle=1)
- **Label position**: Below icon (`verticalLabelPosition=bottom;verticalAlign=top;`)

## Icon Sizing

- **Service icons (resourceIcon)**: 48×48 (`w2` in source)
- **Resource icons (dedicated shapes)**: 48×48
- **Group minimum size**: 130×130

## Nesting Order (outermost → innermost)

1. AWS Cloud group
2. Region group
3. VPC group
4. Subnet group (Public/Private)
5. Individual resources

## Spacing

- **Between icons**: 80-120px horizontal, 60-80px vertical
- **Group padding**: 30px from group border to contained icons
- **Between groups**: 40-60px

## Edge/Arrow Rules

- Color: `strokeColor=#545B64`
- Style: `edgeStyle=orthogonalEdgeStyle`
- Use `rounded=0` for clean corners
- Label edges with data flow description when helpful
- Edge label style: `fontSize=10;fontColor=#545B64;`

## Common Layout Patterns

### Three-tier Architecture
```
[Users] → [CloudFront/ALB] → [EC2/Lambda] → [RDS/DynamoDB]
```

### Event-driven
```
[Source] → [EventBridge/SNS/SQS] → [Lambda] → [Target]
```

### Data Pipeline
```
[Source] → [Kinesis/S3] → [Lambda/Glue] → [S3/Redshift] → [QuickSight]
```

### RAG Architecture (closed network + Transit Gateway)
```
Ingest: [EC2] → [Transit GW] → [Data Source] → [S3] → [Bedrock KB] → [OpenSearch]
Search: [Users] → [VPN] → [EC2] ↔ [Bedrock KB] ↔ [OpenSearch], [EC2] ↔ [Bedrock Claude]
```

## PNG Export Considerations

- **Always add a full-coverage background**: A light `#F5F5F5` rounded rectangle behind all content (title, diagram, legend). Without this, PNG export shows black background behind any content outside groups.
- Background style: `rounded=1;whiteSpace=wrap;fillColor=#F5F5F5;strokeColor=#E0E0E0;arcSize=2;`
- Legend and title should be inside the background rect, not floating outside

## Multi-Flow Diagrams (Swim Lanes)

When a diagram has multiple distinct flows:

1. **Single AWS Cloud group** spanning all flows (not one per flow)
2. **Lane headers** with step-by-step summaries: `"① チケット取得 → ② データ保存 → ③ AI変換 → ④ 索引化"`
3. **Dashed vertical divider** between lanes instead of separate colored blocks
4. **Step-numbered edges** — use circled numbers (① ② ③ or ❶ ❷ ❸) on edges instead of technical labels
5. Different number styles per flow for visual distinction (white circled vs black circled)

### Lane header style
```
rounded=1;whiteSpace=wrap;fillColor=#DBEAFE;strokeColor=none;fontColor=#1E40AF;fontSize=13;fontStyle=1;verticalAlign=top;spacingTop=8;
```

### Dashed divider style
```
strokeColor=#94A3B8;strokeWidth=1;dashed=1;dashPattern=8 4;
```

## Managed Services and VPC Endpoints Layout

When a diagram has VPC resources accessing AWS managed services via VPC Endpoints:

### Two-box structure
```
┌─── AWS Cloud ───────────────────────────────────────────────────┐
│                                                                  │
│  ┌─── VPC ──────────────┐  🔌  ┌─── Managed Services ────────┐ │
│  │ EC2, etc.             │ VPC  │ S3, Bedrock KB, OpenSearch  │ │
│  │ (user-deployed)       │ EP   │ (AWS-managed)               │ │
│  └───────────────────────┘      └─────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

- **VPC box**: Standard VPC group with subnets and user-deployed resources
- **Managed Services box**: Dashed-border group for AWS managed services that live outside the VPC
- **VPC Endpoints icon**: Placed between the two boxes on the boundary
- Arrows go directly from source to target — do NOT route through VPC Endpoints icon
- The visual layout communicates "these cross the VPC boundary" without cluttering arrows

### Managed Services group style
```
rounded=1;whiteSpace=wrap;fillColor=none;strokeColor=#879196;strokeWidth=1;dashed=1;dashPattern=4 4;fontColor=#232F3E;fontSize=12;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10;spacingTop=8;container=1;collapsible=0;
```

### Managed Services group ID convention
- Group: `grp-managed`
- Icons inside: `svc-s3`, `svc-bedrock-kb`, `svc-opensearch`, etc.

## Cell ID Convention

Use descriptive IDs for maintainability:
- Groups: `grp-cloud`, `grp-region`, `grp-vpc`, `grp-subnet-pub`, `grp-subnet-priv`
- Icons: `svc-lambda`, `svc-s3`, `svc-bedrock`, etc.
- Edges: `edge-1`, `edge-2`, etc.

## XML Structure Template

```xml
<mxCell id="svc-lambda" value="Lambda" style="...shape style..."
        vertex="1" parent="grp-subnet-priv">
  <mxGeometry x="100" y="50" width="48" height="48" as="geometry" />
</mxCell>
```

## Style Template Quick Reference

### Service icon (resourceIcon pattern)
```
sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=<CATEGORY_COLOR>;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.<SERVICE_ICON>;
```

### Dedicated shape (resource-level)
```
sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=<CATEGORY_COLOR>;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.<SHAPE_NAME>;
```

### Group container
```
sketch=0;outlineConnect=0;fontColor=#232F3E;fontStyle=0;container=1;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.<GROUP_ICON>;...
```

### Edge
```
edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;elbow=vertical;startArrow=none;endFill=1;strokeColor=#545B64;rounded=0;fontSize=10;fontColor=#545B64;
```
