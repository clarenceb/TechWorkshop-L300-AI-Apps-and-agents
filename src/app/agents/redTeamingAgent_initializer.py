# Azure imports
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation.red_team import RedTeam, RiskCategory, AttackStrategy
from pyrit.prompt_target import AzureMLChatTarget
import os
import asyncio
import logging
from dotenv import load_dotenv

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file from the src directory (3 levels up from src/app/agents)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
load_dotenv(os.path.join(src_dir, '.env'))

# Azure AI Project Information
azure_ai_project = os.getenv("AZURE_AI_AGENT_ENDPOINT")

# Validate required environment variables
required_vars = {
    "AZURE_AI_AGENT_ENDPOINT": azure_ai_project,
    "gpt_deployment": os.getenv("gpt_deployment"),
    "gpt_endpoint": os.getenv("gpt_endpoint"),
    "gpt_api_key": os.getenv("gpt_api_key"),
    "gpt_api_version": os.getenv("gpt_api_version"),
}

missing_vars = [k for k, v in required_vars.items() if not v]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

print(f"✅ Configuration loaded:")
print(f"   - Endpoint: {required_vars['gpt_endpoint']}")
print(f"   - Deployment: {required_vars['gpt_deployment']}")
print(f"   - API Version: {required_vars['gpt_api_version']}")

# Instantiate your AI Red Teaming Agent
red_team_agent = RedTeam(
    azure_ai_project=azure_ai_project,
    credential=DefaultAzureCredential(),
    risk_categories=[
        RiskCategory.Violence,
        RiskCategory.HateUnfairness,
        RiskCategory.Sexual,
        RiskCategory.SelfHarm
    ],
    num_objectives=5,
)

chat_target = AzureMLChatTarget(
    deployment_name=required_vars["gpt_deployment"],
    endpoint=required_vars["gpt_endpoint"],
    api_key=required_vars["gpt_api_key"],
    api_version=required_vars["gpt_api_version"],
) 


async def main():
    try:
        logger.info("🚀 Starting red team scan...")
        red_team_result = await red_team_agent.scan(target=chat_target)
        logger.info("✅ Scan completed successfully")
        return red_team_result
    except Exception as e:
        logger.error(f"❌ Scan failed with error: {type(e).__name__}: {str(e)}")
        logger.exception("Full traceback:")
        raise

if __name__ == "__main__":
    asyncio.run(main())
