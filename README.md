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
with a colorful Aurora motif. The input box includes a **mode selector**
so you can choose between simple chat and command execution.

Send a chat message with:

```bash
curl -X POST http://localhost:5000/chat -H 'Content-Type: application/json' \
    -d '{"message": "date", "mode": "execute"}'
```

The server will respond with the planned command. Set `mode` to `execute`
in the JSON body (or select **Execute** in the web UI) to trigger the
approval workflow. Send another request with `{"approve": true}` to run
the command.

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

   Edit `config.yaml` and replace the default server addresses, ports, and
   any API tokens required by your local services. You can also open the
   **Settings** menu in the web UI to change these values while AuroraShell
   is running. Example configuration values:

   ```yaml
  port: 5000
  n8n_url: "http://127.0.0.1:5678"       # Update with your N8N URL
  n8n_token: ""
  anythingllm_url: "http://127.0.0.1:3001"  # Update with your AnythingLLM URL
  anythingllm_token: ""
  lmstudio_url: "http://127.0.0.1:1234"   # Update with your LM Studio URL
  lmstudio_token: ""
  ```

   If your services require authentication tokens, fill in the appropriate
   fields in `config.yaml` or via the Settings menu.

5. **Run the server**

   ```bash
   python chat_interface.py
   ```

6. **Access the UI**

   Open `http://<your-ip>:<port>/` in your browser (replace the default
   values with those you configured) to begin chatting with the agent.

   Visit `/system` to view the status dashboard. Use the **Settings** link
   in the top bar to adjust endpoints while the server is running.
   Services that are unavailable will show a red light and the server will
   automatically retry the connection every 10 seconds.

   There is also a separate **LM Studio Chat** page at `/lmchat` for simple
   conversations directly with your local model. Messages there are sent to
   the LM Studio API and the full chat log is displayed on screen.

## Monitoring and Resilience

AuroraShell keeps running even if its supporting services are down. The
server polls LM Studio, AnythingLLM and N8N every 10 seconds. Connection
loss or restoration events appear as toast notifications in the UI. Use
the System Status page to check current connectivity states at any time.
