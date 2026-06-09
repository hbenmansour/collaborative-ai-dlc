"""Infrastructure setup script for Bedrock AgentCore orchestrator.

Provisions and configures the Leasing ERP orchestrator agent on AWS
using boto3. Creates the agent, registers tools, and sets up API Gateway
integration for frontend invocation.

Usage:
    python infra/agent-setup.py --region us-east-1 --env dev
"""

import argparse
import json
import sys
from pathlib import Path

import boto3

AGENT_CONFIG_PATH = Path(__file__).parent.parent / "agent" / "agent_config.json"


def load_agent_config() -> dict:
    with open(AGENT_CONFIG_PATH) as f:
        return json.load(f)


def create_agent(client, config: dict, env: str) -> str:
    """Create or update the Bedrock AgentCore agent."""
    agent_name = f"{config['agent_name']}-{env}"

    # Check if agent already exists
    existing = client.list_agents()
    for agent in existing.get("agentSummaries", []):
        if agent["agentName"] == agent_name:
            print(f"Agent '{agent_name}' already exists (id={agent['agentId']}). Updating...")
            client.update_agent(
                agentId=agent["agentId"],
                agentName=agent_name,
                instruction=config["instruction"],
                foundationModel=config["foundation_model"],
                idleSessionTTLInSeconds=config["idle_session_ttl_seconds"],
                description=config["description"],
            )
            return agent["agentId"]

    response = client.create_agent(
        agentName=agent_name,
        instruction=config["instruction"],
        foundationModel=config["foundation_model"],
        idleSessionTTLInSeconds=config["idle_session_ttl_seconds"],
        description=config["description"],
    )
    agent_id = response["agent"]["agentId"]
    print(f"Created agent '{agent_name}' with id={agent_id}")
    return agent_id


def create_agent_action_group(client, agent_id: str, config: dict) -> None:
    """Register tools as an action group on the agent."""
    # Domain API tool as action group
    domain_tool = next(t for t in config["tools"] if t["tool_name"] == "domain-api")

    # Load the tool spec from the Python file
    from agent.tools.domain_api_tool import TOOL_SPEC

    api_schema = {
        "functionSchema": {
            "functions": [
                {
                    "name": action["name"],
                    "description": action["description"],
                    "parameters": action["parameters"],
                }
                for action in TOOL_SPEC["actions"]
            ]
        }
    }

    client.create_agent_action_group(
        agentId=agent_id,
        agentVersion="DRAFT",
        actionGroupName="domain-api-actions",
        description=domain_tool["description"],
        actionGroupExecutor={"lambda": "arn:aws:lambda:{region}:{account}:function:leasing-erp-domain-api-proxy"},
        apiSchema=api_schema,
    )
    print("Registered domain-api action group")


def setup_api_gateway(region: str, env: str, agent_id: str) -> str:
    """Create API Gateway HTTP API for frontend agent invocation."""
    apigw = boto3.client("apigatewayv2", region_name=region)

    api_name = f"leasing-erp-agent-api-{env}"

    # Check existing
    apis = apigw.get_apis()
    for api in apis.get("Items", []):
        if api["Name"] == api_name:
            print(f"API Gateway '{api_name}' already exists: {api['ApiEndpoint']}")
            return api["ApiEndpoint"]

    response = apigw.create_api(
        Name=api_name,
        ProtocolType="HTTP",
        Description=f"Leasing ERP Agent invocation endpoint ({env})",
        CorsConfiguration={
            "AllowOrigins": ["*"],
            "AllowMethods": ["POST", "GET", "OPTIONS"],
            "AllowHeaders": ["Authorization", "Content-Type"],
            "MaxAge": 3600,
        },
    )
    api_id = response["ApiId"]
    endpoint = response["ApiEndpoint"]
    print(f"Created API Gateway: {endpoint}")

    # Create routes
    apigw.create_route(
        ApiId=api_id,
        RouteKey="POST /api/v1/agent/invoke",
    )
    apigw.create_route(
        ApiId=api_id,
        RouteKey="GET /api/v1/agent/sessions/{sessionId}",
    )

    # Create default stage with auto-deploy
    apigw.create_stage(
        ApiId=api_id,
        StageName="$default",
        AutoDeploy=True,
    )

    return endpoint


def main():
    parser = argparse.ArgumentParser(description="Set up Bedrock AgentCore orchestrator")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument("--env", default="dev", choices=["dev", "staging", "prod"], help="Environment")
    parser.add_argument("--dry-run", action="store_true", help="Print config without provisioning")
    args = parser.parse_args()

    config = load_agent_config()

    if args.dry_run:
        print("Agent Configuration:")
        print(json.dumps(config, indent=2))
        print(f"\nWould provision in region={args.region}, env={args.env}")
        return

    print(f"Provisioning Bedrock AgentCore agent in {args.region} ({args.env})...")

    bedrock_agent = boto3.client("bedrock-agent", region_name=args.region)

    # 1. Create/update agent
    agent_id = create_agent(bedrock_agent, config, args.env)

    # 2. Register action groups (tools)
    create_agent_action_group(bedrock_agent, agent_id, config)

    # 3. Set up API Gateway for frontend invocation
    endpoint = setup_api_gateway(args.region, args.env, agent_id)

    # 4. Prepare agent
    bedrock_agent.prepare_agent(agentId=agent_id)
    print(f"\nAgent prepared. Invoke endpoint: {endpoint}")

    print("\nSetup complete. Summary:")
    print(f"  Agent ID: {agent_id}")
    print(f"  Agent Name: {config['agent_name']}-{args.env}")
    print(f"  Model: {config['foundation_model']}")
    print(f"  Skills: {', '.join(s['skill_name'] for s in config['skills'])}")
    print(f"  API Endpoint: {endpoint}")


if __name__ == "__main__":
    main()
