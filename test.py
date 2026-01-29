import boto3

bedrock = boto3.client("bedrock", region_name="ap-southeast-2")
models = bedrock.list_foundation_models()
for m in models["modelSummaries"]:
    if "anthropic" in m["modelId"]:
        print(f"Available: {m['modelId']}")
