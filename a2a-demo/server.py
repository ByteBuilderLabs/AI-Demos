from dotenv import load_dotenv
load_dotenv()

from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication
from agent_executor import ResearchAgentExecutor
import uvicorn

skill = AgentSkill(
    id="research",
    name="Research Assistant",
    description="Researches a topic and returns a summary",
    tags=["research", "summary"],
    examples=["Research the latest trends in AI agents"],
)

agent_card = AgentCard(
    name="Research Agent",
    description="A LangGraph-powered research assistant",
    url="http://localhost:9999/",
    version="1.0.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
)

request_handler = DefaultRequestHandler(
    agent_executor=ResearchAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
)

if __name__ == "__main__":
    uvicorn.run(app.build(), host="0.0.0.0", port=9999)