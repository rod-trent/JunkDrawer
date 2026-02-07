# Privacy Statement for JunkDrawer Repository

Last updated: February 7, 2026

## Introduction

Thank you for your interest in the JunkDrawer repository (https://github.com/rod-trent/JunkDrawer). This repository is a personal collection of miscellaneous tools, scripts, and utilities, many of which incorporate AI capabilities (e.g., via Grok from xAI), cybersecurity features, productivity aids, and creative applications. These tools are provided as open-source code for educational, experimental, and personal use.

As the repository owner (@rodtrent), I do not collect, store, process, or have access to any personal data from users who download, fork, or run these tools. All code execution happens on your local machine or environment, and any data handling is under your control. This privacy statement outlines how data may be handled by the tools themselves, particularly when they interact with external services.

This statement does not apply to third-party services or APIs integrated into the tools—please review their respective privacy policies for details.

## Data Collection and Processing

The majority of tools in this repository do not collect or process personal data. They are designed to run locally and process inputs provided by you without persistent storage. However:

- **User Inputs in Interactive Tools**: Tools like Grok Persona Chat, Resume Critic, Roast My Fitness, JobAgent, or Phishing Triage may require you to provide personal information (e.g., resumes, fitness details, emails, or chat prompts) for processing. This data is handled locally on your device unless the tool explicitly integrates with an external API. No data is transmitted to the repository owner.

- **AI Integrations (e.g., Grok/xAI API)**: Many tools (e.g., Grok Disinformation Checker, Patch Agent, SciFi Cowriter, Travel Agent) use the xAI API for AI-powered features. When you run these tools, your inputs (e.g., prompts, queries, or uploaded content) are sent to xAI's servers for processing. xAI may collect and use this data according to their privacy policy (available at xAI's website). I recommend reviewing it before use, as it may involve data like IP addresses, usage patterns, or content for model improvement.

- **External API Integrations**:
  - **BreachWise**: Uses the Have I Been Pwned (HIBP) API to check for data breaches. It requires an email address, which is sent directly to HIBP. No data is stored locally or by me—refer to HIBP's privacy notice for details.
  - **Fitness Sync Tools (e.g., Peloton2Garmin, Peloton2Strava2Garmin)**: These may sync data between services like Peloton, Strava, and Garmin. Data is handled by those platforms' APIs; review their privacy policies.
  - **Other Services**: Tools like GrokCyberNews or Project Oracle may pull public data from sources like GitHub or news feeds, but do not collect personal user data unless you input it.

- **No Tracking or Analytics**: There are no built-in tracking mechanisms, cookies, or analytics in the repository's code that send data back to me or any third party beyond the explicit API calls mentioned above.

If a tool requires API keys (e.g., for xAI, HIBP, or fitness services), you provide them directly in your local configuration. I do not have access to these keys.

## Data Usage

Any data processed by the tools is used solely for the tool's intended functionality (e.g., generating responses, analyzing inputs, or syncing data). There is no secondary use, such as marketing or profiling, by me.

## Data Sharing and Disclosure

I do not share, sell, or disclose any data, as I do not collect it. Data sharing only occurs if a tool sends information to an external API as part of its operation (e.g., to xAI or HIBP), which is done on your behalf and under your initiation.

In the event of legal requirements (e.g., subpoenas), I would comply, but since no data is stored, this is unlikely to involve user information.

## Data Security

The tools are provided "as-is" under the MIT License, without warranties. You are responsible for:
- Securing your local environment and any API keys used.
- Ensuring safe handling of sensitive inputs (e.g., avoid committing personal data to public forks).
- Reviewing code before running it, as with any open-source software.

For security vulnerabilities in the code, please report them via the repository's SECURITY.md guidelines.

## Your Rights and Choices

Since no personal data is collected by me:
- You control all data inputs and can delete or modify them on your device.
- For data sent to third-party services (e.g., xAI), exercise your rights directly with those providers (e.g., data access, deletion requests).
- If you have concerns about a specific tool, feel free to open a GitHub issue for clarification.

## Children's Privacy

These tools are not intended for children under 13 (or equivalent age in your jurisdiction). If you are a parent or guardian and believe a child has provided data via a tool, contact the relevant third-party service.

## Changes to This Statement

I may update this privacy statement periodically to reflect changes in the repository or legal requirements. Changes will be posted here with an updated "Last updated" date. Continued use of the tools after changes implies acceptance.

## Contact Information

If you have questions about this privacy statement or the tools, please:
- Open an issue on the GitHub repository: https://github.com/rod-trent/JunkDrawer/issues
- Contact me via X (Twitter): @rodtrent

This statement is provided for transparency and does not create any legal obligations beyond those in the repository's LICENSE.
