"""Inject data.json into the template -> index.html (no deps)."""
import pathlib
tpl = pathlib.Path("index.template.html").read_text(encoding="utf-8")
data = pathlib.Path("data.json").read_text(encoding="utf-8")
pathlib.Path("index.html").write_text(tpl.replace("__DATA__", data), encoding="utf-8")
print(f"built index.html from {len(data)} bytes of data")
