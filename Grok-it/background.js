let API_KEY = "";
let WORKING_MODEL = "grok-3-mini";

chrome.storage.sync.get(["grokApiKey", "workingModel"], data => {
  if (data.grokApiKey) API_KEY = data.grokApiKey.trim();
  if (data.workingModel) WORKING_MODEL = data.workingModel;
});

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "grokIt",
    title: "Grok-it",
    contexts: ["selection"]
  });
  discoverModels();
});

async function discoverModels() {
  if (!API_KEY) return;
  try {
    const res = await fetch("https://api.x.ai/v1/models", {
      headers: { "Authorization": `Bearer ${API_KEY}` }
    });
    if (res.ok) {
      const json = await res.json();
      const models = json.data.map(m => m.id);
      if (models.length > 0) {
        WORKING_MODEL = models[0];
        chrome.storage.sync.set({ workingModel: WORKING_MODEL });
      }
    }
  } catch (_) {}
}

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId !== "grokIt" || !info.selectionText) return;
  chrome.storage.session.set({ grokPrompt: info.selectionText.trim() });
  chrome.action.openPopup();
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action !== "getGrokResponse") return;

  if (!API_KEY) {
    sendResponse({ error: "API key missing – open Options and paste it" });
    return true;
  }

  fetch("https://api.x.ai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: WORKING_MODEL,
      messages: [
        { role: "system", content: "You are Grok. Always respond in clear, natural English. Never use any other language." },
        { role: "user", content: msg.prompt }
      ],
      temperature: 0.7,
      max_tokens: 1500
    })
  })
  .then(r => r.json().then(d => ({ ok: r.ok, status: r.status, data: d })))
  .then(res => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const answer = res.data.choices?.[0]?.message?.content?.trim() || "No answer.";
    sendResponse({ answer });
  })
  .catch(err => sendResponse({ error: err.message }));

  return true;
});