# Salary Transparency Enforcer: The App That Fights Back When Companies Hide Pay

In the ever-evolving world of work, salary transparency remains a hot-button issue. Despite laws in states like California, New York, and Colorado mandating pay ranges in job postings, many companies—especially in tech and startups—still play coy, omitting compensation details to lowball candidates. This tactic exploits the information gap between employers and job seekers, potentially costing you thousands (or tens of thousands) in lost earnings.

Enter **Salary Transparency Enforcer**: a no-nonsense web app I built to level the playing field. It parses job descriptions, uncovers hidden market salary data, and generates a polished counter-offer email—all in under a minute, powered entirely by Grok-4 from xAI. No more endless Googling or awkward negotiation scripts. Just facts, confidence, and a ready-to-send email that cites real 2025 comp benchmarks.

I've open-sourced the full code on GitHub for anyone to fork, tweak, or deploy their own instance. Check it out here: [https://github.com/rod-trent/JunkDrawer/tree/main/Salary%20Transparency%20Enforcer](https://github.com/rod-trent/JunkDrawer/tree/main/Salary%20Transparency%20Enforcer). It's part of my "JunkDrawer" repo—a catch-all for experimental side projects like this one.

### A Quick Demo: From Job Post to Counter-Offer in 3 Steps

1. **Input the Job**: Paste the full job description or drop in a URL (e.g., from LinkedIn or a company careers page). The app uses Grok-4 to extract essentials:
   - Company
   - Job title
   - Location
   - Whether they're hiding the salary (a cheeky yes/no flag)

   Example output for a "Senior Product Manager" role at a fictional fintech:  
   - Company: FinTech Innovators Inc.  
   - Title: Senior Product Manager  
   - Location: New York, NY (Hybrid)  
   - Hides Salary? **Yes** ⚠️

2. **Fetch Market Data**: Hit "Get Real Salary Data," and Grok-4 pulls the latest 2025 figures from sources like Levels.fyi, Glassdoor, Blind threads, and SEC filings. You'll get:
   - Average base salary
   - Total compensation (base + bonus + equity)
   - Low/high range
   - Credible source

   For that PM role:  
   - Avg Base: $185,000  
   - Total Comp: $285,000  
   - Range: $160k–$220k base  
   - Source: Levels.fyi + recent H1B data

3. **Craft Your Counter**: Enter their initial offer (say, $150k base), and boom—Grok-4 drafts a professional email countering at 20-25% higher ($187.5k–$193.75k). It's grateful yet firm, data-driven, and ends with a call to action. Download as .txt and send.

   Sample snippet:  
   **Subject:** Counter-Offer for Senior Product Manager at FinTech Innovators Inc.  

   Dear [Hiring Manager],  

   Thank you for the offer—I'm excited about the impact I can make on your team. Based on 2025 market data from Levels.fyi, the median base for this role in NYC is $185k, with total comp averaging $285k. To align with that benchmark, I'm proposing $190k base plus equity to reach $300k total.  

   Best regards,  
   [Your Name]

### Why Build This? (And Why Now)

Hiring is brutal right now. Layoffs in Big Tech linger, remote roles are scarcer, and AI is automating entry-level gigs. Yet, executive pay soars—why should you settle for less when armed with data?

This app embodies my frustration with opaque hiring practices. As a developer (@rodtrent on X), I've negotiated my own offers and seen friends undervalue themselves. With Grok-4's zero-shot capabilities, building this was a weekend hack: parse text, query real-time data, generate prose. No fine-tuning, no datasets—just a prompt and an API key.

Pro tip: Laws are catching up (e.g., Washington's new transparency rules effective Jan 1, 2026), but enforcement is spotty. Tools like this bridge the gap until then.

### Under the Hood: Tech Breakdown

The repo contains a single Python file (`SalaryTransparent.py`) deployable via Streamlit. Key ingredients:

- **Streamlit**: For the slick, interactive UI—tabs for text/URL input, metrics for salary viz, and a styled email preview.
- **Grok-4 API**: Handles everything AI:
  - Job parsing (JSON extraction from messy text).
  - Salary research (prompted for 2025-specific data).
  - Email drafting (tone: confident, structure: 3-4 paras).
- **BeautifulSoup**: Scrapes URLs if you paste a link, stripping junk like nav bars.
- **dotenv**: Securely loads your xAI API key (get one at [x.ai/api](https://x.ai/api)).

To run locally:
1. Clone the repo: `git clone https://github.com/rod-trent/JunkDrawer.git`
2. `cd JunkDrawer/Salary Transparency Enforcer`
3. Set up `.env` with `GROK_API_KEY=your_key_here`
4. `pip install streamlit requests beautifulsoup4 python-dotenv`
5. `streamlit run SalaryTransparent.py`

It's lightweight (~200 lines), with custom CSS for that green-accented, email-like polish. Fork it to add features like multi-job batching or equity simulators.

### Real-World Wins (And a Call to Action)

A beta tester (anon tech lead) used it for a DevOps role at a Series B: Offer jumped from $140k to $170k after sending the generated email. "It felt less like begging, more like business," they said.

If you're job hunting, a recruiter, or just mad at the system—try it. Star the repo, share on X, or contribute (PRs welcome for better prompts or EU law integrations).

P.S. To recruiters: Post the range upfront. It's 2025. Transparency isn't a perk; it's table stakes.
