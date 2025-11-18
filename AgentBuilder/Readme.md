# Build Custom Copilot Agents in Seconds: Meet CreateAgentYAML.py – A Hidden Gem for Microsoft 365 Copilot Fans

If you're deep in the Microsoft 365 Copilot ecosystem (or the new "Agent" wave with Copilot Studio), you know one of the biggest pain points: creating the **agent manifest YAML** file by hand.

That YAML file defines everything about your custom agent:

- Name, description, icons  
- Instructions (the system prompt)  
- Capabilities (web search, file access, etc.)  
- Actions (API calls, plugins)  
- Authentication settings  
- And a dozen other fields that are easy to get wrong  

One tiny indentation error and your agent fails to deploy. 😩

Enter a tiny but insanely useful Python script from Microsoft Sentinel legend **Rod Trent**:  
[**CreateAgentYAML.py**](https://github.com/rod-trent/JunkDrawer/blob/main/AgentBuilder/CreateAgentYAML.py)

### What does it do?

It asks you a series of friendly questions in the terminal (or you can pass arguments), then spits out a **perfectly formatted, ready-to-use `agent.yaml`** manifest for Microsoft Copilot Studio / Microsoft 365 Agents.

No more copying from half-broken samples.  
No more guessing which fields are required vs optional in 2025.  
No more YAML syntax nightmares.

Just run the script → answer ~20 simple questions → get a deploy-ready file.

### Why this is awesome right now (November 2025)

Microsoft has been rapidly evolving the agent platform:

- Declarative agents in Copilot Studio  
- The new “Bring Your Own Agent” model in Microsoft 365  
- Built-in support for custom instructions + tools + auth  

The official templates exist, but they’re scattered across docs and they get outdated fast. Rod’s script appears to be kept current with the latest schema (as of late 2025 it includes the newest fields like `icon_url`, `categories`, `model_override`, multi-language support, etc.).

### How to use it (30-second guide)

```bash
# Clone Rod's junk drawer (yes, that's literally the repo name 😂)
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/AgentBuilder

# Run the script
python CreateAgentYAML.py
```

You’ll be prompted for:

- Agent name & description  
- System instructions (your core prompt)  
- Whether it can create/analyze files, use the web, etc.  
- Custom actions (OpenAPI specs)  
- Authentication type (None, OAuth, API key)  
- Icons, categories, languages, and a bunch more  

When you’re done, it creates `agent.yaml` in the current folder.

Drop that file into Copilot Studio → New Agent → Import manifest → boom, your custom agent is live.

### Bonus: It’s in the “JunkDrawer” repo

Rod Trent (aka @rodtrent on X/Mastodon) is famous for dropping ridiculously useful Sentinel KQL, SOAR playbooks, and random automation gold into his [JunkDrawer](https://github.com/rod-trent/JunkDrawer) repo. This AgentBuilder folder is just the latest treasure.

If you live in Microsoft 365, Defender, or Sentinel, star that repo. You’ll thank yourself later.

### Final thoughts

In a world where everyone is racing to build the next killer agent, the winners will be the ones who can prototype fastest. Tools like `CreateAgentYAML.py` shave hours off that loop.

Huge thanks to Rod for open-sourcing yet another time-saver.

Go grab it here:  
https://github.com/rod-trent/JunkDrawer/blob/main/AgentBuilder/CreateAgentYAML.py

Now stop hand-crafting YAML and start shipping agents 🤖

P.S. If you build something cool with it, tag Rod (or me)! I’d love to see what people are creating in late 2025.
