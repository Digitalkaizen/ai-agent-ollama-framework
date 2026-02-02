from agentkit.core.agent import Agent
from agentkit.core.models import AgentInput


def test_agent_responds():
    agent = Agent()
    out = agent.run(AgentInput(message="hello"))
    assert isinstance(out.answer, str)
    assert out.trace_id


def test_agent_time_tool():
    agent = Agent()
    out = agent.run(AgentInput(message="what time is it?"))
    assert "UTC" in out.answer
