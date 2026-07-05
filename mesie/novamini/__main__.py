"""CLI: python -m mesie.novamini"""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

from mesie.novamini.runtime import NovaMiniRuntime, VERSION


def _repl(runtime: NovaMiniRuntime) -> int:
    print(f"NOVAMINI (MESIE-LM) v{VERSION} — sovereign native speech")
    print(f"Session: {runtime.session_id} | Ctrl+C or 'exit' to quit\n")
    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[novamini] shutdown.")
            return 0
        if not line:
            continue
        if line.lower() in ("exit", "quit", ":q"):
            return 0
        if line == "/status":
            print(json.dumps(runtime.status(), indent=2))
            continue
        if line.startswith("/learn "):
            target = line[len("/learn "):].strip()
            result = runtime.learn(target)
            if result.get("ok"):
                print(f"[novamini] learned '{result['name']}' — {result['chunks_indexed']} chunks indexed\n")
            else:
                print(f"[novamini] learn failed: {result.get('reason')}\n")
            continue
        resp = runtime.chat(line)
        print(f"\n{resp.role}> {resp.spoken}")
        print(f"  [{resp.latency_ms}ms | memory_hits={len(resp.memory_hits)}]\n")


def _serve(runtime: NovaMiniRuntime, port: int) -> int:
    class Handler(BaseHTTPRequestHandler):
        runtime = runtime

        def log_message(self, *_: Any) -> None:
            return

        def _json(self, code: int, payload: Dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-NOVAMINI", VERSION)
            self.send_header("X-MESIE-LM", "AuroNativeLM-v1")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path in ("/", "/status", "/health"):
                self._json(200, self.runtime.status())
            elif self.path == "/artifacts":
                self._json(200, {"artifacts": self.runtime.memory.artifacts()})
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self) -> None:
            if self.path not in ("/", "/chat", "/learn"):
                self._json(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            try:
                data = json.loads(raw or "{}")
            except json.JSONDecodeError:
                self._json(400, {"error": "invalid json"})
                return
            if self.path == "/learn":
                source = data.get("path") or data.get("text") or ""
                if not source:
                    self._json(400, {"error": "path or text required"})
                    return
                result = self.runtime.learn(source, name=data.get("name"))
                self._json(200 if result.get("ok") else 422, result)
                return
            text = data.get("text") or data.get("message") or ""
            if not text:
                self._json(400, {"error": "text required"})
                return
            resp = self.runtime.chat(text)
            self._json(200, resp.to_dict())

    print(f"[novamini] HTTP hub http://127.0.0.1:{port}  POST /chat {{\"text\":\"...\"}}")
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[novamini] server stopped.")
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NOVAMINI (MESIE-LM) — sovereign mini Nova runtime")
    parser.add_argument("message", nargs="?", help="One-shot message (omit for REPL)")
    parser.add_argument("--serve", type=int, metavar="PORT", help="Local HTTP hub (e.g. 6180)")
    parser.add_argument("--status", action="store_true", help="Print status JSON and exit")
    parser.add_argument("--json", action="store_true", help="JSON output for one-shot")
    parser.add_argument("--learn", metavar="PATH", help="Ingest a file into spectral memory and exit")
    args = parser.parse_args(argv)

    runtime = NovaMiniRuntime()

    if args.learn:
        result = runtime.learn(args.learn)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1
    if args.status:
        print(json.dumps(runtime.status(), indent=2))
        return 0
    if args.serve:
        return _serve(runtime, args.serve)
    if args.message:
        resp = runtime.chat(args.message)
        if args.json:
            print(json.dumps(resp.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(resp.spoken)
        return 0
    return _repl(runtime)


if __name__ == "__main__":
    raise SystemExit(main())