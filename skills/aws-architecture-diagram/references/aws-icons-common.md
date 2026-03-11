# Common Icons: General Resources, Groups, Arrows

## General Resources (`#232F3E`)

### Dedicated shapes

Use pattern: `shape=mxgraph.aws4.<shape>`
Required: `fillColor=#232F3E;strokeColor=none`

| Display Name | shape |
|---|---|
| User | `user` |
| Users | `users` |
| Client | `client` |
| Mobile Client | `mobile_client` |
| Traditional Server | `traditional_server` |
| Servers | `servers` |
| Internet | `internet` |
| Internet (alt 1) | `internet_alt1` |
| Internet (alt 2) | `internet_alt2` |
| Corporate Data Center | `corporate_data_center` |
| Office Building | `office_building` |
| Globe | `globe` |
| Generic Application | `generic_application` |
| Generic Database | `generic_database` |
| Generic Firewall | `generic_firewall` |
| Git Repository | `git_repository` |
| Document | `document` |
| Documents | `documents` |
| Email | `email_2` |
| Folder | `folder` |
| Folders | `folders` |
| Gear | `gear` |
| Logs | `logs` |
| Metrics | `metrics` |
| SSL Padlock | `ssl_padlock` |
| Magnifying Glass | `magnifying_glass_2` |
| Shield | `shield2` |
| Source Code | `source_code` |
| SDK | `external_sdk` |
| Toolkit | `external_toolkit` |
| Camera | `camera2` |
| Chat | `chat` |
| Multimedia | `multimedia` |
| Question | `question` |
| Recover | `recover` |
| SAML Token | `saml_token` |
| Tape Storage | `tape_storage` |
| Cold Storage | `cold_storage` |
| Disk | `disk` |
| Data Stream | `data_stream` |
| Data Table | `data_table` |
| JSON Script | `json_script` |
| Programming Language | `programming_language` |
| Management Console | `management_console2` |
| Authenticated User | `authenticated_user` |
| Alert | `alert` |
| Credentials | `credentials` |
| Forums | `forums` |
| Marketplace | `marketplace` |

---

## Groups (container shapes)

Groups wrap other elements. Use `container=1;collapsible=0;recursiveResize=0;` in style.

### AWS Cloud

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;
```

### AWS Cloud (alt)

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;
```

### Region

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=1;
```

### Availability Zone

```
fillColor=none;strokeColor=#147EBA;dashed=1;verticalAlign=top;fontStyle=0;fontColor=#147EBA;
```

### Security Group

```
fillColor=none;strokeColor=#DD3522;verticalAlign=top;fontStyle=0;fontColor=#DD3522;
```

### Auto Scaling Group

```
shape=mxgraph.aws4.groupCenter;grIcon=mxgraph.aws4.group_auto_scaling_group;grStroke=1;strokeColor=#D86613;fillColor=none;verticalAlign=top;fontColor=#D86613;
```

### VPC

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;
```

### Private Subnet

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#00A4A6;fillColor=#E6F6F7;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=0;
```

### Public Subnet

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#7AA116;fillColor=#E9F3E6;verticalAlign=top;align=left;spacingLeft=30;fontColor=#248814;dashed=0;
```

### Account

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_account;strokeColor=#CD2264;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#CD2264;dashed=0;
```

### Corporate Data Center

```
shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_corporate_data_center;strokeColor=#147EBA;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=0;
```

### Generic Group (dashed)

```
fillColor=none;strokeColor=#5A6C86;dashed=1;verticalAlign=top;fontStyle=0;fontColor=#5A6C86;
```

---

## Arrows (edge styles)

Default AWS arrow color: `strokeColor=#545B64`

### Default (right arrow)

```
edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;elbow=vertical;startArrow=none;endFill=1;strokeColor=#545B64;rounded=0;
```

### Bidirectional

```
edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;elbow=vertical;startArrow=block;startFill=1;endFill=1;strokeColor=#545B64;rounded=0;
```

### Dashed

```
edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;elbow=vertical;startArrow=none;endFill=1;strokeColor=#545B64;rounded=0;dashed=1;
```

### No arrow (line only)

```
edgeStyle=orthogonalEdgeStyle;html=1;endArrow=none;elbow=vertical;startArrow=none;strokeColor=#545B64;rounded=0;
```
