# Echo

AI proxy and experiments.

## AuroraShell

AuroraShell is a simple local daemon that allows a language model to
plan and execute commands on the host machine with user approval.
The server is implemented with Flask and uses a planner → validator →
executor pipeline. Memory lookups are delegated to AnythingLLM and more
complex workflows can be triggered via N8N.

To start the server:

```bash
python chat_interface.py
```

Open `http://localhost:5000/` in your browser to use the web chat UI
with a colorful Aurora motif.

Send a chat message with:

```bash
curl -X POST http://localhost:5000/chat -H 'Content-Type: application/json' \
    -d '{"message": "date"}'
```

The server will respond with the planned command. Send another request
with `{"approve": true}` to execute the plan.
