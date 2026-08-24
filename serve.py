#!/usr/bin/env python3
"""Live-preview server for experimenting with content and style.

    python3 serve.py [port]      (default port 8000)

Opens the site in your browser. Whenever you save content.md, style.md,
base.css, pages/*.md, template.html, or build.py, the site is rebuilt and
the browser reloads itself. Build errors appear as a red overlay at the bottom of the
page instead of a silently stale site. Ctrl-C to stop.

The auto-reload script is injected only by this dev server — the generated
.html files on disk stay clean.
"""

import importlib
import json
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import build as builder

ROOT = Path(__file__).parent
LOCK = threading.Lock()
STATE = {"version": 0, "error": None, "mtimes": None}

RELOAD_SNIPPET = """
<script>
/* live-reload — injected by serve.py, not present in the committed files */
(function () {
  var seen = null;
  function overlay(text) {
    var el = document.getElementById('__live_err');
    if (!text) { if (el) el.remove(); return; }
    if (!el) {
      el = document.createElement('pre');
      el.id = '__live_err';
      el.style.cssText = 'position:fixed;left:0;right:0;bottom:0;margin:0;' +
        'padding:1rem;background:#7f1d1d;color:#fff;font:14px/1.4 monospace;' +
        'white-space:pre-wrap;z-index:9999';
      document.body.appendChild(el);
    }
    el.textContent = 'build error:\\n' + text;
  }
  function tick() {
    fetch('/__status').then(function (r) { return r.json(); }).then(function (s) {
      overlay(s.error);
      if (seen !== null && s.version !== seen && !s.error) location.reload();
      seen = s.version;
    }).catch(function () {}).finally(function () { setTimeout(tick, 300); });
  }
  tick();
})();
</script>
""".encode()


def sources():
    files = [builder.CONTENT, builder.STYLE, builder.BASE_CSS,
             builder.TEMPLATE, ROOT / "build.py"]
    if builder.PAGES_DIR.is_dir():
        files += sorted(builder.PAGES_DIR.glob("*.md"))
    return files


def rebuild_if_changed():
    global builder
    with LOCK:
        snap = {str(p): p.stat().st_mtime for p in sources() if p.exists()}
        if snap == STATE["mtimes"]:
            return
        STATE["mtimes"] = snap
        try:
            builder = importlib.reload(builder)  # pick up build.py edits too
            builder.build()
            STATE["error"] = None
        except (Exception, SystemExit) as exc:
            STATE["error"] = f"{type(exc).__name__}: {exc}"
            print(f"build error: {STATE['error']}", file=sys.stderr)
        STATE["version"] += 1


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path == "/__status":
            rebuild_if_changed()
            body = json.dumps(
                {"version": STATE["version"], "error": STATE["error"]}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        fspath = Path(self.translate_path(self.path))
        if fspath.is_dir():
            fspath = fspath / "index.html"
        if fspath.suffix == ".html" and fspath.exists():
            body = fspath.read_bytes().replace(
                b"</body>", RELOAD_SNIPPET + b"</body>"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        if not (args and "/__status" in str(args[0])):
            super().log_message(fmt, *args)


def main():
    argv = [a for a in sys.argv[1:] if a != "--no-open"]
    port = int(argv[0]) if argv else 8000
    rebuild_if_changed()
    server = ThreadingHTTPServer(
        ("127.0.0.1", port), partial(Handler, directory=str(ROOT))
    )
    url = f"http://localhost:{port}/"
    print(f"live preview at {url} — save a source file to reload; Ctrl-C to stop")
    if "--no-open" not in sys.argv:
        threading.Timer(0.3, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
