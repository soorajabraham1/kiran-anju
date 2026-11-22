"""Build the invitation from content.yml.

    python build.py

Reads content.yml, fills src/index.template.html and src/event.template.ics,
and writes index.html plus one <event id>.ics per event. Commit the outputs;
GitHub Pages serves them as plain static files.
"""
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).parent


def ics_escape(text):
    """Escape TEXT values per RFC 5545."""
    return (str(text).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def main():
    data = yaml.safe_load((ROOT / "content.yml").read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(ROOT / "src"),
        undefined=StrictUndefined,          # typo in content.yml -> clear error, not blank text
        keep_trailing_newline=True,
        autoescape=select_autoescape(["html"]),  # HTML escaped, .ics not
    )
    env.filters["ics"] = ics_escape

    html = env.get_template("index.template.html")
    (ROOT / "index.html").write_text(html.render(**data), encoding="utf-8", newline="\n")
    print("wrote index.html")

    ics = env.get_template("event.template.ics")
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for event in data["events"]:
        out = ROOT / f"{event['id']}.ics"
        out.write_text(ics.render(e=event, now=now, **data), encoding="utf-8", newline="\r\n")
        print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
