from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agentkit.core.agent import Agent
from agentkit.core.models import AgentInput

app = FastAPI(title="ai-agent-starter-kit")
agent = Agent()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = "web"


class ChatResponse(BaseModel):
    answer: str
    trace_id: str


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>AI Agent Starter Kit</title>
    <style>
      body { font-family: Arial; max-width: 800px; margin: 40px auto; }
      #log { border: 1px solid #ddd; padding: 12px; height: 360px; overflow: auto; }
      .row { margin: 8px 0; }
      .me { color: #333; }
      .bot { color: #0b5; }
      input { width: 80%; padding: 8px; }
      button { padding: 8px 12px; }
    </style>
  </head>
  <body>
    <h2>AI Agent Starter Kit</h2>
    <div id="log"></div>
    <div class="row">
      <input id="msg" placeholder="Type message (try: what time is it?)" />
      <button onclick="send()">Send</button>
    </div>

    <script>
      const log = document.getElementById('log');
      const msg = document.getElementById('msg');

      function addLine(cls, text) {
        const div = document.createElement('div');
        div.className = 'row ' + cls;
        div.textContent = text;
        log.appendChild(div);
        log.scrollTop = log.scrollHeight;
      }

      async function send() {
        const text = msg.value.trim();
        if (!text) return;
        addLine('me', 'You: ' + text);
        msg.value = '';

        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({message: text, session_id: 'web'})
        });
        const data = await res.json();
        addLine('bot', 'Agent: ' + data.answer + ' (trace_id: ' + data.trace_id + ')');
      }

      msg.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') send();
      });
    </script>
  </body>
</html>
"""


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    out = agent.run(AgentInput(message=req.message, session_id=req.session_id))
    return ChatResponse(answer=out.answer, trace_id=out.trace_id)
