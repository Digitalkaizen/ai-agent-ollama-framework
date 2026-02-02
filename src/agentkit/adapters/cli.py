from dotenv import load_dotenv
load_dotenv()

import typer

from agentkit.core.agent import Agent
from agentkit.core.models import AgentInput

app = typer.Typer(add_completion=False)


@app.command()
def chat(message: str):
    """Send one message to the agent and print response."""
    agent = Agent()
    out = agent.run(AgentInput(message=message, session_id="cli"))
    typer.echo(out.answer)
    typer.echo(f"\ntrace_id: {out.trace_id}")


if __name__ == "__main__":
    app()
