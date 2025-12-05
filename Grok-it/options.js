document.getElementById("save").onclick = () => {
  const key = document.getElementById("key").value.trim();
  const status = document.getElementById("status");
  
  if (!key) {
    status.textContent = "Please enter a valid API key";
    status.className = "error";
    return;
  }

  chrome.storage.sync.set({ grokApiKey: key }, () => {
    status.textContent = "Key saved! You can now use Grok-it.";
    status.className = "success";
    document.getElementById("key").value = "";
  });
};

chrome.storage.sync.get("grokApiKey", data => {
  const status = document.getElementById("status");
  if (data.grokApiKey) {
    status.textContent = "Key is already saved";
    status.className = "success";
  }
});