"""Optional LLM bridges — Ollama/Llama local, Grok API — for research/startup tier."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LLMBridgeConfig:
    provider: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    model: str = "llama3.2"
    grok_api_key: str = ""
    grok_model: str = "grok-2"
    timeout_s: float = 60.0

    @classmethod
    def from_env(cls) -> "LLMBridgeConfig":
        return cls(
            provider=os.environ.get("MESIE_LLM_PROVIDER", "ollama"),
            base_url=os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"),
            model=os.environ.get("MESIE_LLM_MODEL", "llama3.2"),
            grok_api_key=os.environ.get("XAI_API_KEY", os.environ.get("GROK_API_KEY", "")),
            grok_model=os.environ.get("MESIE_GROK_MODEL", "grok-2"),
        )


@dataclass
class LLMBridge:
    """Research/startup tier — chat with Llama (Ollama) or Grok alongside MESIE tools."""

    config: LLMBridgeConfig = field(default_factory=LLMBridgeConfig.from_env)
    system_tools_context: str = ""

    def available(self) -> Dict[str, bool]:
        return {
            "ollama": self._probe_ollama(),
            "grok": bool(self.config.grok_api_key),
            "configured_provider": self.config.provider,
        }

    def _probe_ollama(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.config.base_url.rstrip('/')}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3.0):
                return True
        except (urllib.error.URLError, OSError):
            return False

    def chat(self, messages: List[Dict[str, str]], *, tools_hint: bool = True) -> Dict[str, Any]:
        if tools_hint and self.system_tools_context:
            sys_msg = {
                "role": "system",
                "content": self.system_tools_context,
            }
            messages = [sys_msg] + list(messages)

        if self.config.provider == "grok" and self.config.grok_api_key:
            return self._chat_grok(messages)
        if self.config.provider in ("ollama", "llama"):
            return self._chat_ollama(messages)
        return {"ok": False, "error": f"unknown provider: {self.config.provider}"}

    def _chat_ollama(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        body = json.dumps({
            "model": self.config.model,
            "messages": messages,
            "stream": False,
        }).encode("utf-8")
        url = f"{self.config.base_url.rstrip('/')}/api/chat"
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "ok": True,
                    "provider": "ollama",
                    "model": self.config.model,
                    "content": data.get("message", {}).get("content", ""),
                    "raw": data,
                }
        except urllib.error.URLError as exc:
            return {"ok": False, "provider": "ollama", "error": str(exc)}

    def _chat_grok(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        body = json.dumps({
            "model": self.config.grok_model,
            "messages": messages,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.x.ai/v1/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.grok_api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {
                    "ok": True,
                    "provider": "grok",
                    "model": self.config.grok_model,
                    "content": content,
                    "raw": data,
                }
        except urllib.error.URLError as exc:
            return {"ok": False, "provider": "grok", "error": str(exc)}