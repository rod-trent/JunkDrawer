# Azure Zork: Porting the Great Underground Empire to Your Azure OpenAI Playground

### From xAI's Grok Wit to Azure's Enterprise Muscle – Same Classic Adventure, Now in Your Cloud

[Rod Trent](https://substack.com/@rodtrent)

Dec 5, 2025

If you've been following my retro-AI tinkering, you know I'm still knee-deep in the Great Underground Empire. Just minutes after Microsoft open-sourced the sacred Zork source code and I unveiled **[Grok Gork](https://github.com/rod-trent/JunkDrawer/tree/main/Grok%20Gork)** – that cheeky Grok-powered revival of Zork I – I've gone and ported it to Azure OpenAI/Foundry. Welcome to **Azure Zork**, a seamless adaptation that swaps xAI's freewheeling Grok for the robust, customizable brains of Azure's GPT deployments. It's the same pixel-less thrill of "OPEN MAILBOX" and grue-dodging, but now tuned for enterprise devs, Azure enthusiasts, or anyone with a deployment humming in the cloud.

Why the port? Grok Gork was a blast – quick to spin up, laced with that signature sarcasm – but Azure OpenAI offers deeper control: fine-tuned models, private endpoints, and integration with your org's guardrails. Plus, with Azure's scalability, you can host multiplayer sessions or embed it in a larger app without breaking a sweat. This isn't a rewrite; it's a lift-and-shift with Azure flair, proving how portable these AI adventures can be.

In this post, I'll cover the what, why, and how: from Azure setup to deployment, code tweaks, and why this 1980 classic still hooks us in 2025. Devs, grab your API keys – the white house awaits.

Rod’s Blog is a reader-supported publication. To receive new posts and support my work, consider becoming a free or paid subscriber.

## **What is Azure Zork?**

Azure Zork is a browser-based text adventure app that faithfully recreates Zork I: The Great Underground Empire, narrated by your Azure OpenAI deployment (think GPT-4o or a custom fine-tune). Type commands like "go north" or "take the sword," and get immersive, Infocom-style responses – rooms, puzzles, and objects straight from the original lore, with a dash of AI dynamism.

Powered by Streamlit for that clean chat interface, it starts you in the iconic open field west of the white house. No graphics, no mercy – just pure interactive fiction. But Azure's touch means precision: responses stay terse and true, referencing the actual ZIL source code for accuracy, while your model's personality (or lack thereof) shines through. Want a stoic narrator? Deploy a low-temp GPT. Craving quips? Crank the creativity.

It's the spiritual successor to Grok Gork, but Azure-native: same ~200 lines of Python, now wired to your endpoint. Fork it, deploy it, own it – all under MIT vibes, nodding to Microsoft's Zork open-source drop.

## **How It Works: Timeless Zork Logic + Azure Smarts**

Under the hood, Azure Zork mirrors the original game's parser-driven world: track inventory, navigate rooms, interact with objects, and unravel riddles like the thief in the treasure vault. But instead of static scripts, Azure OpenAI generates replies on the fly, grounded in the Zork source.

Key mechanics:
- **Source Fidelity**: The app caches truncated ZIL files (ZORK1.ZIL, ROOMS.ZIL, etc.) from the official GitHub repo, feeding them into the system prompt. Your Azure model gets: "Use only original rooms, objects, puzzles... Reference these excerpts."
- **Stateful Play**: Streamlit's session_state maintains chat history, so "inventory" remembers your rusty lamp across turns.
- **Azure Integration**: Calls hit your deployment via the AzureOpenAI client – secure, versioned (2024-10-21 API), and error-proof with diagnostics.
- **Adaptive Narration**: Temperature=0.8 keeps it balanced – creative enough for flavor, rigid enough for puzzle logic. No modern slips; the prompt bans "AI" or "Azure" chit-chat.

Result? A game that's 99% Zork, 1% magic. Stuck in the dark? "It is pitch black. You are likely to be eaten by a grue." Light the lamp, and Azure describes the damp tunnel ahead – every time feeling fresh, yet canon-compliant.

## **The Backstory: From Grok Gork to Azure Empire**

Remember November 20, 2025? Microsoft's bombshell: Zork I-III source code, MIT-licensed on GitHub, courtesy of OSPO, Team Xbox, and the Internet Archive. I reacted fast with Grok Gork, leveraging xAI's Grok-3 for a witty, accessible spin. It racked up forks and "XYZZY" cheers.

But Azure devs pinged me: "Make it cloud-ready!" Enter Azure Zork – a port born from that feedback. Swapped OpenAI client for AzureOpenAI, tweaked env vars for endpoints/deployments, and added sidebar diagnostics to catch "deployment not found" gremlins. It's not just compatible; it's optimized for Azure's ecosystem – think RBAC, monitoring via Application Insights, or chaining to Azure Functions for multi-game lobbies.

This port underscores Zork's enduring hackability: 45 years later, it's fueling AI experiments across clouds.

## **Requirements: Gear Up Your Azure Toolkit**

Lightweight as ever, but Azure-specific:
- **Python 3.8+**: Backend basics.
- **Libraries** (pip install): streamlit, python-dotenv, openai (for AzureOpenAI), requests (for ZIL fetches).
- **Azure OpenAI Setup**:
  - An active Azure subscription.
  - Deployed model in Azure OpenAI Studio (e.g., gpt-4o-mini for cost-efficiency, or gpt-4 for depth). Copy the exact deployment name.
  - API Key and Endpoint from Azure Portal > Azure OpenAI > Keys and Endpoint.
- **.env File**: For secrets – no hardcoding here.
- **GitHub Access**: Public Zork repo pulls are free and fast.

No GPUs, no fuss. Runs local for testing, scales to prod.

## **How to Implement: From Zero to Zork in 10 Minutes**

The code lives at its permanent home: [https://github.com/rod-trent/JunkDrawer/tree/main/Azure%20Zork](https://github.com/rod-trent/JunkDrawer/tree/main/Azure%20Zork). Single file: `Azure_Zork.py` – commented, concise, ready to fork.

### Step 1: Azure OpenAI Setup (If You're New)
1. Head to [Azure Portal](https://portal.azure.com) > Create Resource > Azure OpenAI.
2. Deploy a model: In Studio, pick GPT-4o or similar > Deploy > Name it (e.g., "zorkgpt").
3. Grab creds: Resource > Keys and Endpoint > Copy API Key, Endpoint URL, Deployment Name.
4. (Pro Tip: Enable content filters if you're paranoid about elf swords turning spicy.)

### Step 2: Clone and Configure
```
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/Azure Zork
pip install streamlit python-dotenv openai requests
```

Create `.env` in the folder:
```
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```
(Endpoint needs a trailing slash – the code handles it.)

### Step 3: Test and Run
```
streamlit run Azure_Zork.py
```
Browser pops to localhost:8501. Sidebar diagnostics confirm: "Deployment 'zorkgpt' is working!" If not, it'll pinpoint the issue (e.g., "Not found? Check Azure Portal").

**Code Highlights**:
- **Client Init**: AzureOpenAI with api_version="2024-10-21" for stability.
- **ZIL Fetch**: Cached via @st.cache_data, truncated to 12k chars/file to fit context.
- **Prompt Engineering**: System message embeds ZIL snippets, enforces "terse style" and "no modern mentions."
- **API Call**: max_tokens=500, temperature=0.8 – tweakable for your vibe.
- **UI Extras**: Bold assistant replies, quoted inputs, restart button. Sidebar cheats like "open mailbox; go north."

Tweak away: Add Azure AD auth, log to Cosmos DB, or prompt for Zork II. PRs welcome!

Costs? Pennies per session on gpt-4o-mini. Monitor via Azure Cost Management.

## **How to Play: Dive In, Don't Get Eaten**

Launch, read the opener: "West of House. You are standing in an open field..." Chat input: "What do you do?"

- **Starter Commands** (Sidebar Copy-Paste):
  ```
  open mailbox
  go north
  take lamp
  light lamp
  go down
  ```
- **Essentials**: "inventory," "examine [object]," "attack [foe] with [weapon]." Verbose wins: "swing sword at troll."
- **Gotchas**: Dark rooms = grue risk. Puzzles demand lateral thinking – no walkthroughs here.
- **Session Magic**: History persists; Azure builds on prior moves for coherent chaos.

In 5 minutes, you're mapping the empire. Pro move: Yell nonsensical commands for Azure's polite rebuffs.

## **Why Azure Zork is Ridiculously Fun (Even in 2025)**

Zork hooked millions because it *trusted you* – no tutorials, just discovery. Azure Zork amps that: AI makes every "examine" reveal fresh flavor, turning replays into therapy sessions. I've lost hours to the cyclops puzzle, cackling at Azure's deadpan "The cyclops, seeing you, instantly eats you." It's nostalgic crack for Gen X, educational gold for kids (teach parsing via code sidebar), and a dev flex – "Yeah, I Zork-ified my deployment."

Porting from Grok showed me AI's universality: Swap endpoints, and the empire endures. In a world of flashy VR, this text purity reminds us: Stories don't need polygons; they need spark. And Azure delivers it enterprise-grade.

Did the thief steal your treasures? Fork the repo and fight back. Hit reply or @rodtrent on X – what's your fave Zork moment?

*The Empire expands. Rod Trent, Speaker 25 (@rodtrent on X). Non-commercial fan project. © 1980 Infocom. Zork source MIT-licensed via Microsoft.*
