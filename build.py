"""Build the invitation from content.yml.

    python build.py

Reads content.yml, fills src/index.template.html and src/event.template.ics,
and writes index.html (all events), <slug>/index.html for every entry under
"invites" (only that invite's events), plus one <event id>.ics per event. Commit the outputs;
GitHub Pages serves them as plain static files.
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).parent


def ics_escape(text):
    """Escape TEXT values per RFC 5545."""
    return (str(text).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def asset_version(name):
    """Short content hash, appended as ?v=... so phones never mix a new page with an old cached file."""
    return hashlib.sha1((ROOT / name).read_bytes()).hexdigest()[:8]


def merge(base, extra):
    """Return base with extra laid over it; nested dicts are merged, not replaced."""
    out = dict(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], value)
        else:
            out[key] = value
    return out


def invite_context(data, invite):
    """Settings for one invite page: only its events, its overrides, its own countdown."""
    by_id = {e["id"]: e for e in data["events"]}
    unknown = [i for i in invite["events"] if i not in by_id]
    if unknown:
        raise SystemExit(f"invite '{invite['slug']}': unknown event id(s) {unknown}")
    ctx = merge(data, invite.get("overrides", {}))
    ctx["events"] = [by_id[i] for i in invite["events"]]
    main = ctx["events"][-1]
    ctx["countdown"] = merge(ctx["countdown"],
                             {"to": f"{main['date'].isoformat()}T{main['start']}:00+05:30"})
    ctx["base"] = "../"
    ctx["page_url"] = f"{data['site_url']}{invite['slug']}/"
    return ctx


def main():
    data = yaml.safe_load((ROOT / "content.yml").read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(ROOT / "src"),
        undefined=StrictUndefined,          # typo in content.yml -> clear error, not blank text
        keep_trailing_newline=True,
        autoescape=select_autoescape(["html"]),  # HTML escaped, .ics not
    )
    env.filters["ics"] = ics_escape
    env.globals["v"] = {name: asset_version(name) for name in ("style.css", "script.js")}

    html = env.get_template("index.template.html")
    (ROOT / "index.html").write_text(
        html.render(**data, base="", page_url=data["site_url"]), encoding="utf-8", newline="\n")
    print("wrote index.html")

    for invite in data.get("invites", []):
        out = ROOT / invite["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(html.render(**invite_context(data, invite)), encoding="utf-8", newline="\n")
        print(f"wrote {invite['slug']}/index.html")

    ics = env.get_template("event.template.ics")
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for event in data["events"]:
        out = ROOT / f"{event['id']}.ics"
        out.write_text(ics.render(e=event, now=now, **data), encoding="utf-8", newline="\r\n")
        print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
