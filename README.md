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

## Installation

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd echo
   ```

2. **Create a virtual environment (optional but recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AuroraShell**

   Edit `config.yaml` and replace the default server addresses, ports,
   and any API tokens required by your local services. Example:

   ```yaml
   port: 5000
   n8n_url: "http://127.0.0.1:5678"       # Update with your N8N URL
   anythingllm_url: "http://127.0.0.1:3001"  # Update with your AnythingLLM URL
   ```

   If your N8N or AnythingLLM instances require authentication tokens,
   make sure to set those in the configuration as well.

5. **Run the server**

   ```bash
   python chat_interface.py
   ```

6. **Access the UI**

   Open `http://<your-ip>:<port>/` in your browser (replace the default
   values with those you configured) to begin chatting with the agent.
