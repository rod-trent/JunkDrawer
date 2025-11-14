document.getElementById('check').addEventListener('click', async () => {
  document.getElementById('result').innerText = 'Loading API key...';

  let apiKey;
  try {
    // Fetch the .env file from the extension's directory
    const envUrl = chrome.runtime.getURL('.env');
    const response = await fetch(envUrl);
    if (!response.ok) {
      throw new Error('Failed to load .env file.');
    }
    const envText = await response.text();

    // Parse the .env file (simple key-value parser)
    const envLines = envText.split('\n');
    for (const line of envLines) {
      const trimmedLine = line.trim();
      if (trimmedLine.startsWith('GROK_API_KEY=')) {
        apiKey = trimmedLine.split('=')[1].trim();
        break;
      }
    }

    if (!apiKey) {
      throw new Error('GROK_API_KEY not found in .env file.');
    }
  } catch (error) {
    document.getElementById('result').innerText = `Error loading API key: ${error.message}. Ensure .env exists in the extension directory with GROK_API_KEY=yourkey.`;
    return;
  }

  document.getElementById('result').innerText = 'Analyzing...';

  try {
    // Get the active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Extract page text using scripting (gets visible text from body)
    const [{ result: pageText }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => document.body.innerText
    });

    // Truncate to avoid exceeding context limits (increased slightly for larger model context; adjust as needed)
    const truncatedText = pageText.substring(0, 20000);

    // Prepare prompt for disinformation analysis
    const prompt = `Analyze the following page content for disinformation, misinformation, or false claims. Use live search to reference current data, news, or events if needed to verify claims. Provide a summary of any issues found, with explanations and sources if possible. If none, say so. Content: ${truncatedText}`;

    // API request body (updated model and added search_parameters for real-time access)
    const requestBody = {
      messages: [
        { role: 'system', content: 'You are a neutral, fact-checking AI assistant specialized in detecting disinformation.' },
        { role: 'user', content: prompt }
      ],
      model: 'grok-4-fast-reasoning',  // Updated to a more current, advanced model with larger context and reasoning capabilities (higher cost)
      search_parameters: { mode: 'auto' },  // Enables Live Search for real-time web/X data access (use 'on' to force search, 'auto' for model-decided)
      stream: false,
      temperature: 0.5,     // Lower for more factual responses
      max_tokens: 1000      // Limit output length
    };

    // Make the API call
    const response = await fetch('https://api.x.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} - ${await response.text()}`);
    }

    const data = await response.json();
    const analysis = data.choices[0].message.content;

    document.getElementById('result').innerText = analysis;
  } catch (error) {
    document.getElementById('result').innerText = `Error: ${error.message}. Check your API key, credits, or network.`;
  }
});