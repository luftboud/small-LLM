"""Local site for the Zero Cycles demo.

Run ``python app/server.py`` and open http://127.0.0.1:8000.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from model_origin.demo import client_boot, run_pair  # noqa: E402

TEMPLATES = Path(__file__).resolve().parent / "templates"
STATIC = Path(__file__).resolve().parent / "static"
PAGES = {
    "distillation": ("Knowledge Distillation", "cat-distill.png"),
    "pruning": ("Pruning", "cat-pruning.png"),
    "quantization": ("Quantization", "cat-quant.png"),
}
MIME = {
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
}
_BODY_LIMIT = 100_000


class Handler(BaseHTTPRequestHandler):
    """Serves the three screens and the inference endpoint."""

    def do_GET(self) -> None:  # noqa: N802 — stdlib handler name
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, "text/html; charset=utf-8", (TEMPLATES / "index.html").read_bytes())
            return
        if path == "/methods":
            self._send(200, "text/html; charset=utf-8", (TEMPLATES / "methods.html").read_bytes())
            return
        if path.startswith("/method/"):
            name = path[len("/method/") :]
            if name in PAGES:
                self._send(200, "text/html; charset=utf-8", _method_page(name))
                return
        if path.startswith("/static/"):
            self._static(path[len("/static/") :])
            return
        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802 — stdlib handler name
        if urlparse(self.path).path != "/api/infer":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, _failure("The request was not valid JSON."))
            return
        if length > _BODY_LIMIT:
            self._json(400, _failure("The prompt is too long."))
            return
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, _failure("The request was not valid JSON."))
            return
        pair = payload.get("pair")
        if pair not in ("bert", "qwen"):
            self._json(400, _failure("Choose BERT or Qwen."))
            return
        text = payload.get("text") or ""
        title = payload.get("title") or ""
        if not isinstance(text, str) or not isinstance(title, str):
            self._json(400, _failure("The request was not valid JSON."))
            return
        self._json(200, run_pair(pair, text, title))

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _static(self, relative: str) -> None:
        candidate = (STATIC / relative).resolve()
        try:
            candidate.relative_to(STATIC.resolve())
        except ValueError:
            self.send_error(404)
            return
        if not candidate.is_file():
            self.send_error(404)
            return
        self._send(
            200, MIME.get(candidate.suffix, "application/octet-stream"), candidate.read_bytes()
        )

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._send(status, "application/json; charset=utf-8", body)

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)


def _method_page(name: str) -> bytes:
    title, cat = PAGES[name]
    boot = json.dumps(client_boot(name), ensure_ascii=False).replace("<", "\\u003c")
    html = (TEMPLATES / "method.html").read_text(encoding="utf-8")
    html = (
        html.replace("__TITLE__", _escape(title)).replace("__CAT__", cat).replace("__BOOT__", boot)
    )
    return html.encode("utf-8")


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _failure(message: str) -> dict:
    return {"base": None, "compressed": None, "error": message}


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Zero Cycles demo at http://127.0.0.1:8000", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
