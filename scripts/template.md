## document fro Template Group, Template, Item and Triggers

## **don't Edit this file**

## creating a template group for Simple check

```json
{
  "jsonrpc": "2.0",
  "method": "templategroup.create",
  "params": {
    "name": "MoniPro Simple check"
  },
  "id": 1
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "groupids": ["95"]
  },
  "id": 1
}
```

## creating a template for Simple check

```json
{
  "jsonrpc": "2.0",
  "method": "template.create",
  "params": {
    "host": "MoniPro ICMP PING",
    "groups": {
      "groupid": 95
    }
  },
  "id": 1
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "templateids": ["10739"]
  },
  "id": 1
}
```

## creating a global Macros for the items

```json
{
  "jsonrpc": "2.0",
  "method": "usermacro.createglobal",
  "params": {
    "macro": "{$MONIPRO_HISTORY_DAYS}",
    "value": "30d"
  },
  "id": 1
}
---
{
  "jsonrpc": "2.0",
  "method": "usermacro.createglobal",
  "params": {
    "macro": "{$MONIPRO_TRENDS_DAYS}",
    "value": "7d"
  },
  "id": 1
}

```

### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "globalmacroids": [
      "3"
    ]
  },
  "id": 1
}
---
{
  "jsonrpc": "2.0",
  "result": {
    "globalmacroids": [
      "4"
    ]
  },
  "id": 1
}
```

## creating a template group for active agents

```json
{
  "jsonrpc": "2.0",
  "method": "templategroup.create",
  "params": {
    "name": "MoniPro Active Agents"
  },
  "id": 1
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "groupids": ["96"]
  },
  "id": 1
}
```

## creating a template with general items

```json
{
  "jsonrpc": "2.0",
  "method": "template.create",
  "params": {
    "host": "MoniPro Active Agents General",
    "groups": {
      "groupid": 96
    }
  },
  "id": 1
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "templateids": ["10741"]
  },
  "id": 1
}
```
