# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Read public ModularGrid pages. Print JSON; never write inventory or patch state."""

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rtd = None
        self.in_rtd = False
        self.json_parts = []
        self.detail_depth = 0
        self.description = []
        self.links = []
        self.count = False
        self.count_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("data-mg-json") == "rtd":
            self.in_rtd = True
        if tag == "span" and attrs.get("id") == "qtyModules":
            self.count = True
        if self.detail_depth:
            if tag not in {"br", "img", "hr", "input", "source", "wbr"}:
                self.detail_depth += 1
            if tag in {"p", "li", "br", "h2", "h3"}:
                self.description.append("\n")
            if tag == "a" and attrs.get("href", "").startswith(("https://", "http://")):
                self.links.append(attrs["href"])
        elif tag == "div" and attrs.get("id") == "module-details":
            self.detail_depth = 1

    def handle_endtag(self, tag):
        if tag == "script" and self.in_rtd:
            self.in_rtd = False
            self.rtd = json.loads("".join(self.json_parts))
        if tag == "span":
            self.count = False
        if self.detail_depth and tag not in {"br", "img", "hr", "input", "source", "wbr"}:
            self.detail_depth -= 1
            if tag in {"p", "li", "ul", "h2", "h3"}:
                self.description.append("\n")

    def handle_data(self, data):
        if self.in_rtd:
            self.json_parts.append(data)
        if self.detail_depth:
            self.description.append(data)
        if self.count:
            self.count_parts.append(data)


def validate_url(url, kind):
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.netloc not in {"modulargrid.net", "www.modulargrid.net"}
            or parsed.query or parsed.fragment):
        raise ValueError("Use a plain https://modulargrid.net URL without query or fragment")
    pattern = r"/[a-z]/racks/view/[0-9]+/?" if kind == "rack" else r"/[a-z]/[a-z0-9-]+/?"
    if not re.fullmatch(pattern, parsed.path):
        raise ValueError(f"Not a ModularGrid {kind} URL")
    return parsed.path.strip("/").split("/")


def parse_rack(html, url):
    parts = validate_url(url, "rack")
    page = Page()
    page.feed(html)
    if not isinstance(page.rtd, dict):
        raise ValueError("Rack data missing: login, blocking, or changed page layout; keep the old inventory")
    rack_data = page.rtd["rack"]
    rack = rack_data["Rack"]
    if str(rack["id"]) != parts[-1]:
        raise ValueError("Rack ID mismatch; refusing this response")
    models = rack_data["Module"]
    if not isinstance(models, list) or not models:
        raise ValueError("Empty/missing module list; confirm manually before clearing an inventory")
    count = "".join(page.count_parts).strip()
    if count and int(count) != len(models):
        raise ValueError("Module count mismatch; keep the old inventory")
    instances = []
    for model in models:
        placement = model["ModulesRack"]
        instances.append({
            "instance_id": str(placement["id"]),
            "module_id": str(model["id"]),
            "manufacturer": model["Vendor"]["name"],
            "name": model["name"],
            "summary": model.get("description", ""),
            "hp": int(model["te"]),
            "row": int(placement["row"]),
            "column": int(placement["col"]),
            "in_bounds": placement.get("is_inbounds"),
            "url": f"https://modulargrid.net/{parts[0]}/{model['slug']}",
        })
    if len({item["instance_id"] for item in instances}) != len(instances):
        raise ValueError("Duplicate instance IDs; keep the old inventory")
    return {
        "source_url": url,
        "rack_id": str(rack["id"]),
        "rack_name": rack["name"],
        "source_modified": rack.get("modified"),
        "rows": int(rack["rows"]),
        "hp_per_row": int(rack["te"]),
        "modules": sorted(instances, key=lambda item: (item["row"], item["column"], item["instance_id"])),
    }


def parse_module(html, url):
    validate_url(url, "module")
    page = Page()
    page.feed(html)
    lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(page.description).splitlines()]
    description = "\n".join(line for line in lines if line)
    if not description:
        raise ValueError("Module description missing: inspect the page manually; do not invent capabilities")
    return {"source_url": url, "description": description, "description_links": list(dict.fromkeys(page.links))}


def fetch(url):
    request = Request(url, headers={"User-Agent": "pi-modulargrid-reader/0.1 (public reference lookup)"})
    with urlopen(request, timeout=30) as response:
        # Do not follow a redirect to an unrelated site or mistake a login page for data.
        if urlsplit(response.url).hostname not in {"modulargrid.net", "www.modulargrid.net"}:
            raise ValueError("Unexpected redirect outside ModularGrid")
        body = response.read(10_000_001)
        if len(body) > 10_000_000:
            raise ValueError("Page too large")
        return body.decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["rack", "module"])
    parser.add_argument("url")
    parser.add_argument("--html", type=Path, help="Read previously downloaded HTML instead of making a request")
    args = parser.parse_args()
    try:
        validate_url(args.url, args.kind)
        html = args.html.read_text(encoding="utf-8") if args.html else fetch(args.url)
        result = (parse_rack if args.kind == "rack" else parse_module)(html, args.url)
        result["checked_at"] = datetime.now(timezone.utc).isoformat()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"ModularGrid read failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
