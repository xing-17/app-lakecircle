# LakeCircle Architecture

## Overview

**LakeCircle** is an S3 Lifecycle Management application designed to synchronize S3 bucket lifecycle configurations between manually defined rules (stored in S3 as TOML files) and actual AWS S3 bucket resources. The application follows a clean, layered architecture pattern with clear separation of concerns.

## System Design Principles

### 1. **Three-Layer Model Architecture**
The application uses a sophisticated three-layer model pattern to separate concerns:

```
┌─────────────────────────────────────────┐
│         Definition Layer                │  ← Manual configurations (TOML files in S3)
├─────────────────────────────────────────┤
│         Resource Layer                  │  ← Live AWS S3 resources (via boto3)
├─────────────────────────────────────────┤
│         Lifecycle Layer                 │  ← S3 lifecycle configuration models
└─────────────────────────────────────────┘
```

- **Definition Layer** (`app/model/definition/`): Represents the desired state loaded from TOML configuration files stored in S3
- **Resource Layer** (`app/model/resource/`): Represents the actual state from live AWS S3 buckets via boto3 API
- **Lifecycle Layer** (`app/model/lifecycle/`): Common data structures used by both definition and resource layers to model S3 lifecycle rules

### 2. **Component-Based Hierarchy**
All major classes inherit from `Component`, providing:
- Hierarchical logging infrastructure
- Automatic configuration inheritance (level, format, group)
- Consistent error handling patterns
- Parent-child relationships for context propagation

```
Component (base class)
├── Interface (orchestration)
├── Payload (configuration)
├── Setting (variable management)
├── SyncWork (workflow execution)
└── S3Component (AWS operations)
    ├── AccountDefinition
    ├── BucketDefinition
    ├── Account
    └── Bucket
```

## Directory Structure

```
app/
├── main.py                     # Entry point
├── base/
│   └── component.py            # Base Component class with logging
├── interface/
│   ├── constants.py            # Environment variable definitions
│   ├── interface.py            # Main orchestrator
│   └── payload.py              # Configuration transformer
├── variable/
│   ├── varkind.py              # Variable type enumeration
│   ├── variable.py             # Abstract variable base class
│   ├── environ.py              # Environment variable reader
│   ├── constant.py             # Constant value holder
│   └── setting.py              # Configuration aggregator
├── model/
│   ├── definition/             # Desired state (from TOML)
│   │   ├── account.py          # Account-level definitions
│   │   └── bucket.py           # Bucket-level definitions
│   ├── resource/               # Actual state (from AWS)
│   │   ├── common.py           # S3Component base class
│   │   ├── account.py          # AWS account with S3 access
│   │   └── bucket.py           # AWS S3 bucket resource
│   └── lifecycle/              # Shared lifecycle models
│       ├── common.py           # S3Configuration base
│       ├── lifecycleconfiguration.py
│       ├── lifecyclerule.py
│       ├── expiration.py
│       ├── transition.py
│       ├── filter.py
│       ├── storageclass.py
│       ├── noncurrentversionexpiration.py
│       ├── noncurrentversiontransition.py
│       └── abortincompletemultipartupload.py
└── work/
    └── sync.py                 # SYNC workflow implementation
```

## Core Components

### 1. Entry Point & Orchestration

#### main.py
- Simple entry point with exception handling
- Creates `Interface()` instance and calls `run()`
- Returns 0 on success, 1 on failure

#### Interface (interface/interface.py)
- **Purpose**: Main application orchestrator
- **Responsibilities**:
  - Load configuration via `Setting`
  - Configure logging (level, format, name)
  - Transform environment variables into structured `Payload`
  - Dispatch to appropriate workflow based on `LCC_ACTIONS`
- **Key Methods**:
  - `setup()`: Initialize configuration and logging
  - `run()`: Dispatch to workflows (currently only SYNC)

#### Payload (interface/payload.py)
- **Purpose**: Transform flat environment variables into hierarchical structure
- **Responsibilities**:
  - Validate required fields (endpoint, account, region)
  - Build nested dictionary structure
  - Provide key access methods (`get`, `has`, `require`)
  - Generate configuration fingerprint for tracking
- **Output Structure**:
```python
{
    "app": {
        "name": "LakeCircle",
        "level": "INFO",
        "format": "TREE"
    },
    "endpoint": {
        "base": "s3://bucket/prefix/",
        "current": "s3://bucket/prefix/current/",
        "definition": "s3://bucket/prefix/definition/",
        # ... more endpoints
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

### 2. Configuration System

#### Variable System (variable/)
A sophisticated type-safe configuration system:

- **VarKind**: Enum defining supported types (String, Integer, Float, Boolean, List, Dict)
- **Variable**: Abstract base class with type parsing and validation
- **Environ**: Reads from `os.environ` and parses by kind
- **Constant**: Holds static configuration values
- **Setting**: Aggregates variables and constants, builds final configuration

**Features**:
- Type coercion (string → int, bool, list, dict, etc.)
- Choice validation (value must be in allowed list)
- Strict mode (require non-empty values)
- Default value support
- from_dict() serialization/deserialization

### 3. Model Layers

#### Definition Layer (model/definition/)
Loads desired state from TOML files in S3:

**AccountDefinition**:
- Reads all `.toml` files from S3 URI prefix
- Parses TOML into bucket lifecycle configurations
- Aggregates rules across multiple files (merges rules for same bucket)
- Creates `BucketDefinition` objects for each bucket

**BucketDefinition**:
- Holds bucket name and lifecycle configuration
- Stores desired state (does not interact with AWS)

#### Resource Layer (model/resource/)
Interacts with live AWS S3 resources:

**S3Component** (common.py):
- Base class for AWS S3 operations
- Provides boto3 client resolution
- Parent-child inheritance for account/region/client
- Utility methods (`resolve_date`)

**Account**:
- Lists all S3 buckets in AWS account
- Creates `Bucket` objects for each bucket
- Provides bucket name listing

**Bucket**:
- Interacts with single S3 bucket
- Methods:
  - `get_lifecycle_configuration()`: Fetch current config from AWS
  - `put_lifecycle_configuration()`: Update config in AWS (or delete if empty)
  - `add_rule()`: Add a single lifecycle rule
  - `remove_rule()`: Remove a single lifecycle rule
  - `load()`: Load current lifecycle configuration

#### Lifecycle Layer (model/lifecycle/)
Shared data structures modeling S3 lifecycle configurations:

**LifecycleConfiguration**:
- Top-level container for lifecycle rules
- Indexed by rule fingerprint (SHA256 hash)
- Methods:
  - `add_rule()`: Add rule to configuration
  - `delete_rule()`: Remove rule by fingerprint or object
  - `difference()`: Calculate added/removed rules vs another config
  - `to_payload()`: Convert to AWS API request format

**LifecycleRule**:
- Represents single lifecycle rule
- Supports:
  - Expiration (delete after N days)
  - Transitions (move to GLACIER, etc.)
  - Filters (prefix, tags, size)
  - Noncurrent version handling
  - Multipart upload cleanup
- Auto-generates fingerprint for deduplication

**Supporting Classes**:
- `Expiration`: Object deletion settings
- `Transition`: Storage class change settings
- `Filter`: Rule application criteria
- `NoncurrentVersionExpiration`: Delete old versions
- `NoncurrentVersionTransition`: Archive old versions
- `AbortIncompleteMultipartUpload`: Cleanup incomplete uploads
- `StorageClass`: Enum of AWS storage classes

### 4. Workflow System

#### SyncWork (work/sync.py)
Currently the only implemented workflow:

**Purpose**: Synchronize lifecycle definitions with AWS reality

**Algorithm**:
1. Load `AccountDefinition` from S3 (manual definitions)
2. Load `Account` from AWS (actual resources)
3. Find intersection of bucket names (only sync shared buckets)
4. For each bucket:
   - Load lifecycle configuration from both sides
   - Calculate difference (added rules, removed rules)
   - Apply additions via `bucket.add_rule()`
   - Apply removals via `bucket.remove_rule()`
5. Log results (counts of adds/removes per bucket)

**Error Handling**:
- Continues on individual rule failures
- Logs warnings for failures
- Does not halt entire sync for single bucket failure

## Design Patterns

### 1. **Parent-Child Inheritance**
Components inherit configuration from parents:
```python
parent = Component(name="Parent", level="DEBUG")
child = Component(parent=parent)
# child automatically inherits DEBUG level
```

### 2. **Type-Safe Configuration**
Environment variables are parsed with type safety:
```python
Environ("LCC_ACTIONS", kind=VarKind.STRING, choice=["SYNC", "DRYRUN"])
# Validates type and allowed values
```

### 3. **Fingerprint-Based Deduplication**
Lifecycle rules use SHA256 fingerprints to prevent duplicates and enable fast comparison.

### 4. **Dual Format Support**
All lifecycle model classes support:
- `from_dict()`: Create from AWS API response or dict
- `to_payload()`: Convert to AWS API request format
- `to_dict()`: Serialize to plain dict
- `describe()`: Human-readable representation

### 5. **Fail-Safe Operations**
- Empty lifecycle configurations are deleted rather than put (AWS validation)
- Bucket operations continue even if individual rules fail
- Comprehensive error logging without halting execution

## AWS Integration

### boto3 Client Management
- Single S3 client per account/region combination
- Client inherited through parent-child relationships
- Lazy client creation in S3Component base class

### API Operations Used
- `list_buckets`: List all buckets in account
- `list_objects_v2`: List TOML definition files
- `get_object`: Read TOML file content
- `get_bucket_lifecycle_configuration`: Fetch current rules
- `put_bucket_lifecycle_configuration`: Update rules
- `delete_bucket_lifecycle`: Remove all rules

## Configuration Flow

```
Environment Variables (LCC_*)
    ↓
Constants + Environ (variables/)
    ↓
Setting.build() → dict
    ↓
Payload.build() → nested dict
    ↓
Interface.run() → dispatch
    ↓
SyncWork.run() → execute workflow
    ↓
AccountDefinition + Account → load states
    ↓
Bucket operations → apply changes
```

## Logging Architecture

### Hierarchical Logging
- All components inherit from `Component`
- Parent-child relationships propagate logging config
- Supports multiple formats: Text, ColorText, Tree, ColorTree

### Log Methods
- `info()`: Informational messages (default level)
- `debug()`: Detailed debugging (only visible in DEBUG level)
- `warning()`: Non-fatal issues
- `error()`: Fatal errors
- `log()`: Alias for info()

### Log Context
All log methods accept `**kwargs` for additional context:
```python
self.info("Rule added", rule_id="archive-rule", days=90)
```

## Extension Points

### Adding New Workflows
1. Create new class in `app/work/` inheriting from `Component`
2. Implement workflow logic in `run()` method
3. Add workflow name to `LCC_ACTIONS` choices in constants.py
4. Add dispatch case in `Interface.run()`

### Adding New Variable Types
1. Add new enum value to `VarKind`
2. Add parsing method `_parse_<type>()` in `Variable` class
3. Add case in `_parse_by_kind()` method

### Adding Lifecycle Features
1. Create new class in `app/model/lifecycle/` inheriting from `S3Configuration`
2. Implement `from_dict()`, `to_payload()`, `to_dict()`, `describe()`
3. Add to `LifecycleRule` as attribute and resolver method

## Testing Strategy

### Test Coverage
- **280+ tests** across all modules
- **100% pass rate**
- Focus areas:
  - Variable parsing and validation
  - Model serialization/deserialization
  - AWS operations (via moto mocking)
  - Lifecycle rule management
  - Error handling edge cases

### Test Organization
- Tests colocated with source in `tests/` subdirectories
- Naming convention: `test_class_<classname>_all.py`
- Uses pytest fixtures and moto for AWS mocking

## Security Considerations

### Credentials
- Uses AWS SDK standard credential chain (environment, ~/.aws/credentials, IAM roles)
- No credentials stored in code or logs

### Permissions Required
- `s3:ListBucket`: List buckets in account
- `s3:GetBucketLifecycleConfiguration`: Read lifecycle rules
- `s3:PutBucketLifecycleConfiguration`: Update lifecycle rules
- `s3:DeleteBucketLifecycle`: Remove lifecycle rules
- `s3:GetObject`: Read TOML definition files
- `s3:ListBucket`: List TOML files in definition prefix

## Performance Characteristics

### Scalability
- Sequential processing of buckets (no parallelization)
- Network-bound (AWS API calls dominate execution time)
- Memory usage scales with number of buckets and rules

### Optimization Opportunities
1. Parallel bucket processing with concurrent.futures
2. Caching of lifecycle configurations
3. Batch operations where AWS API supports it
4. Rate limiting to respect AWS API throttles

## Dependencies

### Core
- **boto3**: AWS SDK for S3 operations
- **xlog**: Structured logging with multiple formats
- **Python 3.11+**: Type hints, match/case statements

### Development
- **pytest**: Testing framework
- **moto**: AWS service mocking
- **tomllib**: TOML parsing (standard library in Python 3.11+)

## Future Enhancements

### Planned Features
1. **DRYRUN workflow**: Preview changes without applying
2. **Parallel bucket processing**: Speed up large account syncs
3. **Change history tracking**: Store applied changes in S3
4. **Rollback capability**: Revert to previous configurations
5. **Diff reporting**: Generate detailed change reports
6. **Email notifications**: Alert on sync completion/failures
7. **Metrics export**: CloudWatch metrics for monitoring

### Architecture Improvements
1. Add middleware layer for cross-cutting concerns (auth, rate limiting)
2. Implement retry logic with exponential backoff
3. Add caching layer for frequently accessed configurations
4. Support multiple definition sources (not just S3)
