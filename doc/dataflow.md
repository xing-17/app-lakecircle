# Data Flow Documentation

## Overview

This document traces how data flows through the LakeCircle application, from environment variables through configuration processing, to workflow execution and AWS operations.

## High-Level Data Flow

```
┌─────────────────────┐
│ Environment Vars    │ (LCC_*)
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ Constants +         │ (constants.py)
│ Environ Definitions │
└──────────┬──────────┘
           │
           ↓ Setting.build()
┌─────────────────────┐
│ Flat Configuration  │ (dict[str, Any])
└──────────┬──────────┘
           │
           ↓ Payload.build()
┌─────────────────────┐
│ Nested Payload      │ (hierarchical dict)
└──────────┬──────────┘
           │
           ↓ Interface.run()
┌─────────────────────┐
│ Workflow Dispatch   │ (based on LCC_ACTIONS)
└──────────┬──────────┘
           │
           ↓ SyncWork.run()
┌─────────────────────┐
│ Dual Model Loading  │
│  - AccountDefinition│ (from S3 TOML)
│  - Account          │ (from AWS API)
└──────────┬──────────┘
           │
           ↓ difference()
┌─────────────────────┐
│ Change Calculation  │ (added/removed rules)
└──────────┬──────────┘
           │
           ↓ add_rule() / remove_rule()
┌─────────────────────┐
│ AWS API Calls       │ (put/delete lifecycle)
└─────────────────────┘
```

## Detailed Flow by Stage

### Stage 1: Environment Variable Collection

**Source**: Operating system environment variables

**Variables Collected** (all prefixed with `LCC_`):

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `LCC_ENDPOINT` | String | Yes | - | S3 URI base for definitions |
| `LCC_AWS_ACCOUNT` | String | Yes | - | AWS account ID |
| `LCC_AWS_REGION` | String | Yes | - | AWS region |
| `LCC_ACTIONS` | String | No | "SYNC" | Workflow to execute |
| `LCC_ACTION_PARAMS` | Dict | No | None | Workflow parameters |
| `LCC_APP_LEVEL` | String | No | "INFO" | Log level |
| `LCC_LOG_FORMAT` | String | No | "TREE" | Log format |
| `LCC_APP_NAME` | String | No | - | Override app name |

**Process**:
1. Constants defined in `interface/constants.py`
2. Each variable is an `Environ` object with:
   - Name (e.g., "LCC_ENDPOINT")
   - Kind (String, Integer, etc.)
   - Default value (optional)
   - Choices (valid values)
   - Description (documentation)

**Example**:
```python
Environ(
    name="LCC_ACTIONS",
    kind=VarKind.STRING,
    default="SYNC",
    choice=["SYNC", "DRYRUN"],
    description="Workflow action to execute"
)
```

### Stage 2: Configuration Building

**Module**: `variable/setting.py`

**Input**: List of `Environ` and `Constant` objects

**Process**:
1. `Setting.__init__()` resolves variables and constants
2. `Setting.build()` iterates through all variables
3. For each `Environ`:
   - Calls `get_value()` to read from environment
   - Parses value according to `kind` (string → int, bool, etc.)
   - Validates against `choice` if specified
   - Returns default if not set
4. For each `Constant`:
   - Returns pre-defined value
5. Returns flat dictionary: `{name: value, ...}`

**Example Output**:
```python
{
    "LCC_ENDPOINT": "s3://my-bucket/lifecycle/",
    "LCC_AWS_ACCOUNT": "123456789012",
    "LCC_AWS_REGION": "us-west-2",
    "LCC_ACTIONS": "SYNC",
    "LCC_APP_LEVEL": "DEBUG",
    "LCC_LOG_FORMAT": "TREE",
    "LCC_APP_NAME": "LakeCircle",
    # ... more
}
```

### Stage 3: Payload Transformation

**Module**: `interface/payload.py`

**Input**: Flat configuration dictionary from Setting

**Process**:
1. `Payload.__init__()` stores original data
2. `Payload.build()` transforms to nested structure:
   - Validates required fields (endpoint, account, region)
   - Creates hierarchical keys:
     - `app.*` → Application settings
     - `endpoint.*` → S3 URIs (base, current, definition, etc.)
     - `aws.*` → AWS credentials and region
     - `work.*` → Workflow configuration
3. Returns nested dictionary

**Example Output**:
```python
{
    "app": {
        "name": "LakeCircle",
        "level": "DEBUG",
        "format": "TREE"
    },
    "endpoint": {
        "base": "s3://my-bucket/lifecycle/",
        "current": "s3://my-bucket/lifecycle/current/",
        "previous": "s3://my-bucket/lifecycle/previous/",
        "history": "s3://my-bucket/lifecycle/history/",
        "definition": "s3://my-bucket/lifecycle/definition/",
        "data": "s3://my-bucket/lifecycle/data/",
        "log": "s3://my-bucket/lifecycle/log/"
    },
    "aws": {
        "account": "123456789012",
        "region": "us-west-2"
    },
    "work": {
        "actions": "SYNC",
        "params": None
    }
}
```

**Key Access**:
```python
payload.get("app.level")              # Returns "DEBUG"
payload.get("endpoint.definition")     # Returns "s3://..."
payload.require("aws.account")         # Returns account or raises KeyError
```

### Stage 4: Interface Orchestration

**Module**: `interface/interface.py`

**Process**:

#### 4.1 Setup Phase (`Interface.setup()`):
1. Create `Setting` with variables and constants
2. Build configuration dictionary
3. Configure logging:
   - Read `LCC_APP_LEVEL` → set logging level
   - Read `LCC_LOG_FORMAT` → choose format:
     - "TREE" → Tree format
     - "COLORTREE" → ColorTree format
     - "TEXT" → Text format
     - "COLORTEXT" → ColorText format
   - Read `LCC_APP_NAME` → override component name
4. Create `Payload` from configuration
5. Build nested payload structure
6. Log setup completion with fingerprint

**Data Transformations**:
```
Environment Variables
    ↓ Setting.build()
Flat Dict
    ↓ Payload.build()
Nested Dict
    ↓ Interface.setup()
Configured Interface with Payload
```

#### 4.2 Run Phase (`Interface.run()`):
1. Read `payload.get("work.actions")` → "SYNC"
2. Dispatch to workflow:
   - "SYNC" → Create `SyncWork(payload, parent=self)`
   - "DRYRUN" → Not implemented yet
3. Call `workflow.run()`
4. Log completion

**Data Flow**:
```
Payload → Interface.run() → SyncWork(payload) → workflow.run()
```

### Stage 5: SYNC Workflow Execution

**Module**: `work/sync.py`

**Input**: Payload object with nested configuration

**Process**:

#### 5.1 Extract Configuration:
```python
endpoint = payload.require("endpoint.definition")  # "s3://bucket/prefix/definition/"
account = payload.require("aws.account")           # "123456789012"
region = payload.require("aws.region")             # "us-west-2"
```

#### 5.2 Load Definition State (Desired):
```python
account_def = AccountDefinition(
    uri=endpoint,      # S3 location of TOML files
    account=account,
    region=region,
    parent=self
)
account_def.load()     # Loads all .toml files from S3
```

**AccountDefinition.load() Flow**:
1. Parse S3 URI to extract bucket and prefix
2. List all objects with prefix using `list_objects_v2` paginator
3. Filter `.toml` files
4. For each TOML file:
   - Download via `s3.get_object()`
   - Parse TOML with `tomllib.loads()`
   - Extract bucket definitions
   - Validate required keys ("BucketName", "LifecycleConfiguration")
   - Create/merge `BucketDefinition` objects
5. Store in `account_def.buckets` dict

**Example TOML Structure**:
```toml
BucketName = "my-data-bucket"

[LifecycleConfiguration]
[[LifecycleConfiguration.Rules]]
ID = "archive-old-data"
Status = "Enabled"
[LifecycleConfiguration.Rules.Expiration]
Days = 90
```

**Result**: Dictionary of bucket name → `BucketDefinition` with lifecycle configs

#### 5.3 Load Resource State (Actual):
```python
account_res = Account(
    account=account,
    region=region,
    parent=self
)
account_res.load()     # Loads all buckets from AWS
```

**Account.load() Flow**:
1. Create boto3 S3 client
2. Call `s3.list_buckets()`
3. For each bucket:
   - Create `Bucket` object
   - Call `bucket.load()` to fetch lifecycle configuration
4. Store in `account_res.buckets` dict

**Bucket.load() Flow**:
1. Call `get_lifecycle_configuration()`
2. If configuration exists:
   - Parse response into `LifecycleConfiguration` object
   - Store rules indexed by fingerprint
3. If no configuration:
   - Store empty configuration

**Result**: Dictionary of bucket name → `Bucket` with current lifecycle configs

#### 5.4 Find Intersection:
```python
def_names = set(account_def.buckets.keys())
res_names = set(account_res.buckets.keys())
shared_names = def_names & res_names
```

**Purpose**: Only sync buckets that exist in both definitions and AWS

#### 5.5 Calculate Differences:
For each bucket in intersection:
```python
bucket_def = account_def.buckets[name]
bucket_res = account_res.buckets[name]

# Get lifecycle configurations
def_lc = bucket_def.lifecycle_configuration
res_lc = bucket_res.lifecycle_configuration

# Calculate difference
diff = def_lc.difference(res_lc)
# Returns: {"added": [...], "removed": [...]}
```

**LifecycleConfiguration.difference() Algorithm**:
1. Get fingerprints of all rules in both configs
2. Added rules = rules in definition but not in resource
3. Removed rules = rules in resource but not in definition
4. Return dict with added and removed rule objects

**Example Difference**:
```python
{
    "added": [
        LifecycleRule(id="new-archive", ...),
        LifecycleRule(id="new-glacier", ...)
    ],
    "removed": [
        LifecycleRule(id="old-rule", ...)
    ]
}
```

#### 5.6 Apply Changes:
```python
# Apply additions
for rule in diff["added"]:
    bucket_res.add_rule(rule)
    
# Apply removals
for rule in diff["removed"]:
    bucket_res.remove_rule(rule)
```

**Bucket.add_rule() Flow**:
1. Load current lifecycle configuration
2. Create configuration if doesn't exist
3. Call `lifecycle_config.add_rule(rule)`
4. Call `put_lifecycle_configuration(lifecycle_config)`

**Bucket.remove_rule() Flow**:
1. Load current lifecycle configuration
2. If no configuration, return (nothing to remove)
3. Call `lifecycle_config.delete_rule(rule)`
4. If configuration now empty:
   - Call `delete_bucket_lifecycle()` (AWS requires deletion, not empty put)
5. Else:
   - Call `put_lifecycle_configuration(lifecycle_config)`

**Bucket.put_lifecycle_configuration() Logic**:
```python
if not config.rules:
    # Empty configuration → delete lifecycle
    s3.delete_bucket_lifecycle(Bucket=name)
else:
    # Has rules → update lifecycle
    payload = config.to_payload()
    s3.put_bucket_lifecycle_configuration(
        Bucket=name,
        LifecycleConfiguration=payload
    )
```

#### 5.7 Logging Results:
```python
self.info(
    "Sync completed",
    bucket=name,
    added_count=len(diff["added"]),
    removed_count=len(diff["removed"])
)
```

### Stage 6: AWS API Interactions

**Operations Used**:

#### List Buckets:
```python
response = s3.list_buckets()
# Returns: {"Buckets": [{"Name": "...", "CreationDate": ...}, ...]}
```

#### Get Lifecycle Configuration:
```python
response = s3.get_bucket_lifecycle_configuration(Bucket=name)
# Returns: {"Rules": [{...}, {...}, ...]}
# Raises: ClientError if no configuration exists
```

#### Put Lifecycle Configuration:
```python
s3.put_bucket_lifecycle_configuration(
    Bucket=name,
    LifecycleConfiguration={
        "Rules": [
            {
                "ID": "rule1",
                "Status": "Enabled",
                "Expiration": {"Days": 90},
                # ...
            }
        ]
    }
)
```

#### Delete Lifecycle:
```python
s3.delete_bucket_lifecycle(Bucket=name)
# Removes all lifecycle rules from bucket
```

#### List Objects (for TOML):
```python
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
    for obj in page.get("Contents", []):
        key = obj["Key"]
        # ...
```

#### Get Object (for TOML):
```python
response = s3.get_object(Bucket=bucket, Key=key)
body = response["Body"].read()
content = body.decode("utf-8")
data = tomllib.loads(content)
```

## Data Structures

### Lifecycle Rule Structure

**Internal Representation** (LifecycleRule):
```python
{
    "id": "archive-rule",
    "status": "Enabled",
    "prefix": "logs/",
    "filter": Filter(prefix="logs/", tags=[...]),
    "expiration": Expiration(days=90),
    "transitions": [
        Transition(days=30, storageclass="STANDARD_IA"),
        Transition(days=60, storageclass="GLACIER")
    ],
    "noncurrent_expiration": NoncurrentVersionExpiration(days=30),
    "abort_incomplete_multipart_upload": AbortIncompleteMultipartUpload(days=7),
    "fingerprint": "a1b2c3d4"  # SHA256 hash
}
```

**AWS API Format** (via to_payload()):
```python
{
    "ID": "archive-rule",
    "Status": "Enabled",
    "Prefix": "logs/",
    "Filter": {
        "Prefix": "logs/",
        "Tags": [...]
    },
    "Expiration": {
        "Days": 90
    },
    "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 60, "StorageClass": "GLACIER"}
    ],
    "NoncurrentVersionExpiration": {"NoncurrentDays": 30},
    "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}
}
```

### Configuration Fingerprint

**Purpose**: Unique identifier for configurations to track changes

**Generation** (in Payload):
```python
def fingerprint(self) -> str:
    content_str = json.dumps(self.origin, sort_keys=True)
    hash_obj = hashlib.sha256(content_str.encode())
    return hash_obj.hexdigest()[:8]  # First 8 chars
```

**Usage**:
- Log configuration state
- Compare configurations across runs
- Track when configuration changes

## Error Handling & Data Validation

### Validation Points

#### 1. Environment Variable Parsing:
```python
# In Environ.get_value()
raw = os.environ.get(self.name)
if raw is None:
    return self.default
value = self._parse_by_kind(raw)  # Raises ValueError if invalid
if self.choice and value not in self.choice:
    raise ValueError(f"Value {value!r} not in choice {self.choice!r}")
return value
```

#### 2. Required Field Validation:
```python
# In Payload.build()
endpoint = data.get("LCC_ENDPOINT")
account = data.get("LCC_AWS_ACCOUNT")
region = data.get("LCC_AWS_REGION")

if not endpoint:
    msg = "LCC_ENDPOINT is required."
    self.error(msg)
    raise ValueError(msg)
# Similar for account and region
```

#### 3. TOML Validation:
```python
# In AccountDefinition.load()
account_def.require(data, "BucketName", strict=True)
account_def.require(data, "LifecycleConfiguration", strict=True)
# Raises KeyError if missing
```

#### 4. AWS API Error Handling:
```python
# In Bucket.get_lifecycle_configuration()
try:
    response = s3.get_bucket_lifecycle_configuration(Bucket=name)
except ClientError as e:
    if e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
        return None  # Normal case: no configuration
    else:
        raise  # Unexpected error
```

### Error Propagation

**Strategy**: Fail fast at validation, continue on operational errors

**Examples**:

**Configuration Errors** (fatal):
```python
# Missing required environment variable
ValueError: LCC_ENDPOINT is required.
```

**Operational Errors** (continue with warning):
```python
# Single rule fails to add
self.warning(
    "Failed to add rule",
    bucket=name,
    rule_id=rule.id,
    error=str(e)
)
# Continue processing other rules
```

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Load definitions | O(n) | n = number of TOML files |
| Load resources | O(m) | m = number of buckets |
| Calculate difference | O(r) | r = number of rules |
| Apply changes | O(c) | c = number of changes |
| Full SYNC | O(n + m + b×r + c) | b = shared buckets |

### Network Operations

**Per Execution**:
- 1× `list_buckets` (all buckets in account)
- n× `list_objects_v2` (paginated, for TOML files)
- n× `get_object` (one per TOML file)
- b× `get_bucket_lifecycle_configuration` (one per shared bucket)
- c× `put_bucket_lifecycle_configuration` OR `delete_bucket_lifecycle` (one per change)

**Example** (100 buckets, 10 definitions, 5 shared, 10 changes):
- Total API calls: 1 + 1 + 10 + 5 + 10 = 27 calls
- Estimated time: ~5-10 seconds (network latency dependent)

### Memory Usage

**Peak Memory**:
- All TOML definitions in memory
- All bucket lifecycle configurations in memory
- Typically < 100MB for thousands of buckets

## Data Persistence

### Ephemeral Data:
- All runtime data (configurations, payloads, etc.)
- Lost after execution completes

### Persistent Data:
- **TOML definition files** in S3 (manually maintained)
- **Lifecycle configurations** in AWS S3 buckets (managed by application)

### Future Persistence:
- Change history logs (planned: `endpoint.history`)
- Current state snapshots (planned: `endpoint.current`)
- Previous state backups (planned: `endpoint.previous`)

## Data Security

### Sensitive Data Handling:
- AWS credentials never logged
- Account IDs logged for tracking (not sensitive)
- Bucket names logged (not sensitive)
- No PII or secrets in logs

### Access Control:
- Application requires AWS credentials with S3 permissions
- Follows AWS SDK credential chain (environment → config file → IAM role)
- No custom authentication mechanism
