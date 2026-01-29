from __future__ import annotations
import json 
import boto3
import ollama
import os
from app.base.component import Component
from app.interface.payload import Payload
from app.model.definition.account import AccountDefinition
from app.model.definition.bucket import BucketDefinition
from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
from app.model.resource.account import Account
from app.model.resource.bucket import Bucket


class SummariseWork(Component):
    SYSTEM_PROMPT = (
        "You are an AWS senior engineer. "
        "Summarize the following S3 Lifecycle configuration "
        "into a short, friendly sentence. Explain what happens to the files and when."
    )
    
    def __init__(
        self,
        parent: Component,
        payload: Payload,
    ) -> None:
        super().__init__(
            parent=parent,
        )
        self.parent = parent
        self.payload = payload
        
    def run(self) -> None:
        account: str = self.payload.get("aws.account")
        region: str = self.payload.get("aws.region")

        # Load account resources
        account: Account = Account(
            account=account,
            region=region,
            parent=self,
        )
        account.load()

        self.info(
            f"Loaded {len(account.buckets)} bucket resources", 
            context={"buckets": list(account.buckets.keys())},
        )
        
        # Initialize the Bedrock Runtime client
        client = boto3.client(
            'bedrock-runtime', 
            region_name=region
        )
        model_id = 'amazon.nova-lite-v1:0'
        prompt = (
            "You are an AWS S3 lifecycle expert. "
            "Summarize lifecycle rules concisely and clearly. "
            "As simple as possble. "
            "Output format: \n"
            " - Where: ...\n"
            " - Actions: ...\n"
            "For where: the prefix if observed. \n"
            "For actions: one action per bulletpoint, focus on what, when, and storage class change. \n"
            "Keep it readable."
            "The data is here as follows:\n"
        )
        
        # # Format the request for Claude 3
        # native_request = {
        #     "anthropic_version": "bedrock-2023-05-31",
        #     "max_tokens": 200,
        #     "messages": [
        #         {
        #             "role": "user",
        #             "content": [{"type": "text", "text": prompt}]
        #         }
        #     ]
        # }
        for bucketname, bucket in account.buckets.items():
            bucket.load()
            lcc: LifecycleConfiguration = bucket.lifecycle_configuration
            rules = lcc.rules.values()
            if not rules:
                self.info(f"Bucket '{bucketname}' has no lifecycle rules configured.")
                continue
            try:
                self.info(
                    f"Summarising lifecycle rules in '{bucketname}'",
                    context=lcc.describe(),
                )
                native_request = {
                    "schemaVersion": "messages-v1",  # <--- MUST be present
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt + json.dumps(lcc.to_dict())}]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 300,      # <--- camelCase (No underscore)
                        "temperature": 0.1,
                        "topP": 0.9
                    }
                }
                response = client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(native_request)
                )
                
                # Parse the response
                response_body = json.loads(response.get('body').read())
                result = response_body["output"]["message"]["content"][0]["text"]
                #result = response_body['content'][0]['text']
                self.info(
                    f"Summary for bucket '{bucketname}':",
                    context={"bucket": bucketname, "summary": result.splitlines()}
                )
            except Exception as e:
                msg = f"Failed to summarise bucket '{bucketname}': "
                self.error(msg, context={"error": str(e)})
                continue

            
            