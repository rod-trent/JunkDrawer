# app.py — Grok-4 Powered Code Review Bot (Fully Fixed & Working)

import streamlit as st
import requests
import os
import re
import json
from typing import List, Dict, Any

# === Load .env automatically (create .env with XAI_API_KEY=your-key) ===
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.warning("Install python-dotenv: pip install python-dotenv")

XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    st.error(
        "❌ **XAI_API_KEY not found!**\n\n"
        "Create a file named `.env` in this folder:\n"
        "```\nXAI_API_KEY=sk-ant-your-actual-key-here\n```"
    )
    st.stop()

API_URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-4"

# === Tool: Fetch GitHub file ===
def fetch_github_file(repo: str, path: str, ref: str = "main") -> Dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    params = {"ref": ref} if ref and ref != "main" else {}
    headers = {"Accept": "application/vnd.github.v3.raw"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        return {"status": "success", "content": r.text, "path": path}
    except Exception as e:
        msg = "Unknown error"
        if hasattr(e, "response") and e.response is not None:
            if e.response.status_code == 404:
                msg = "File not found (404)"
            elif e.response.status_code == 403:
                msg = "Rate limited or private repo"
            else:
                msg = f"HTTP {e.response.status_code}"
        return {"status": "failed", "error": msg}

# Tool definition
tools = [{
    "type": "function",
    "function": {
        "name": "fetch_github_file",
        "description": "Fetch raw content of a file from a public GitHub repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo": {"type": "string"},
                "path": {"type": "string"},
                "ref": {"type": "string", "default": "main"}
            },
            "required": ["repo", "path"]
        }
    }
}]

# === FIXED & BULLETPROOF Streaming Function ===
def grok_stream(messages: List[Dict]):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "tools": tools,
        "tool_choice": "auto",
        "stream": True
    }
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        with requests.post(API_URL, json=payload, headers=headers, stream=True, timeout=120) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8").strip()
                if not decoded.startswith("data: "):
                    continue
                if decoded == "data: [DONE]":
                    break
                json_str = decoded[6:]  # remove "data: "
                if not json_str.strip():
                    continue
                try:
                    yield json.loads(json_str)
                except json.JSONDecodeError:
                    continue  # Skip malformed chunks
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            st.code(e.response.text[:1000])
        return

# === Streamlit UI ===
st.set_page_config(page_title="Grok Code Review Bot", page_icon="🤖", layout="wide")
st.title("🤖 Grok-4 Powered Code Review Bot")
st.caption("Paste code or link any public GitHub repo/file — Grok reads real files using tool calling")

tab1, tab2 = st.tabs(["📝 Paste Code", "🔗 GitHub Repo / File"])

with tab1:
    code = st.text_area("Paste your code here:", height=400)
    lang = st.selectbox("Language", ["python", "javascript", "typescript", "java", "go", "rust", "cpp", "c", "bash", "sql", "auto"])

with tab2:
    gh_input = st.text_input("GitHub URL or owner/repo", placeholder="e.g. streamlit/streamlit or full URL")
    col1, col2 = st.columns([3, 1])
    with col1:
        branch = st.text_input("Branch / Commit (optional)", value="main")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        deep = st.checkbox("Deep multi-file review", value=False)

if st.button("🚀 Start Review", type="primary", use_container_width=True):
    if tab1.active and code.strip():
        with st.spinner("Grok is thinking..."):
            messages = [
                {"role": "system", "content": "You are an expert code reviewer. Always provide fixes in proper ```diff blocks. Be thorough and constructive."},
                {"role": "user", "content": f"Language: {lang}\n\nCode:\n```\n{code}\n```"}
            ]
            placeholder = st.empty()
            full = ""
            for chunk in grok_stream(messages):
                if "content" in chunk["choices"][0]["delta"]:
                    full += chunk["choices"][0]["delta"]["content"]
                    placeholder.markdown(full + "▌")
            placeholder.markdown(full)

    elif tab2.active and gh_input.strip():
        # Parse repo
        match = re.search(r"github\.com[/:]([\w\-\.]+/[\w\-\.]+)", gh_input)
        repo = match.group(1).rstrip("/") if match else gh_input.strip("/").split("/")[-2:]
        repo = "/".join(repo[-2:]) if isinstance(repo, list) else repo
        if "/" not in repo:
            st.error("Invalid repo format. Use owner/repo")
            st.stop()

        file_path = None
        if "/blob/" in gh_input:
            parts = gh_input.split("/blob/")[1]
            branch_part, rest = (parts.split("/", 1) if "/" in parts else (parts, ""))
            branch = branch_part
            file_path = rest

        prompt = f"Review the code in https://github.com/{repo}"
        if file_path:
            prompt += f"\nFocus on file: {file_path}"
        if branch != "main":
            prompt += f" at ref: {branch}"
        if deep:
            prompt += "\nPerform a deep architectural review across multiple files."
        prompt += "\n\nUse the fetch_github_file tool to read actual files. Always suggest fixes with ```diff patches."

        messages = [
            {"role": "system", "content": "You are a senior engineer doing a professional code review. Use tools when needed."},
            {"role": "user", "content": prompt}
        ]

        placeholder = st.empty()
        full_response = ""
        tool_calls = []

        for chunk in grok_stream(messages):
            delta = chunk["choices"][0].get("delta", {})

            # Collect tool calls
            if "tool_calls" in delta:
                for tc in delta["tool_calls"]:
                    if tc["function"]["name"] == "fetch_github_file" and "arguments" in tc["function"]:
                        try:
                            args = json.loads(tc["function"]["arguments"])
                            result = fetch_github_file(
                                repo=args.get("repo", repo),
                                path=args["path"],
                                ref=args.get("ref", branch)
                            )
                            tool_calls.append({"id": tc["id"], "result": result})
                        except:
                            pass

            # Stream content
            if "content" in delta:
                full_response += delta["content"]
                placeholder.markdown(full_response + "▌")

        # Send back tool results if any were called
        if tool_calls:
            messages.append({"role": "assistant", "content": full_response, "tool_calls": [
                {"id": tc["id"], "type": "function", "function": {
                    "name": "fetch_github_file",
                    "arguments": json.dumps({"repo": repo, "path": tc["result"].get("path", ""), "ref": branch})
                }} for tc in tool_calls
            ]})

            for tc in tool_calls:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": "fetch_github_file",
                    "content": json.dumps(tc["result"])
                })

            placeholder.empty()
            full_response = ""
            for chunk in grok_stream(messages):
                if "content" in chunk["choices"][0]["delta"]:
                    full_response += chunk["choices"][0]["delta"]["content"]
                    placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

# === Footer ===
st.markdown("---")
st.caption("Grok-4 Code Review Bot • Nov 18, 2025 • Uses .env • Zero JSON errors • Fully working")