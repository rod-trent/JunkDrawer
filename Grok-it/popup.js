document.addEventListener('DOMContentLoaded', async () => {
  const promptEl = document.getElementById('prompt');
  const responseEl = document.getElementById('response');
  const loadingEl = document.getElementById('loading');

  chrome.storage.session.get('grokPrompt', async data => {
    const prompt = data.grokPrompt || 'No text selected';
    promptEl.textContent = `Prompt: ${prompt}`;
    chrome.storage.session.remove('grokPrompt');

    try {
      const resp = await chrome.runtime.sendMessage({ action: "getGrokResponse", prompt });
      if (resp.error) {
        responseEl.textContent = `Error: ${resp.error}`;
        responseEl.classList.add('error');
      } else {
        responseEl.textContent = resp.answer || 'No answer.';
      }
    } catch (e) {
      responseEl.textContent = `Error: ${e.message}`;
      responseEl.classList.add('error');
    }

    loadingEl.style.display = 'none';
    responseEl.style.display = 'block';
  });
});