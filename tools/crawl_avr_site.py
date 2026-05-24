import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urldefrag, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://avr.ifsp.edu.br/"
OUT_JSON = ROOT / "data" / "site_pages.json"
OUT_DOC = ROOT / "docs" / "mapa_site_coletado.md"
MAX_PAGES = 220


SKIP_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".zip",
    ".rar",
    ".7z",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".mp4",
    ".mp3",
)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.links = []
        self.text_parts = []
        self.heading_parts = []
        self._tag_stack = []
        self._current_href = None
        self._current_link_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self._tag_stack.append(tag)
        if tag == "a" and attrs.get("href"):
            self._current_href = attrs["href"]
            self._current_link_text = []

    def handle_endtag(self, tag):
        if tag == "a" and self._current_href:
            self.links.append(
                {
                    "text": clean_text(" ".join(self._current_link_text)),
                    "href": self._current_href,
                }
            )
            self._current_href = None
            self._current_link_text = []
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data):
        text = clean_text(data)
        if not text:
            return

        if self._tag_stack and self._tag_stack[-1] == "title":
            self.title += text

        if self._current_href:
            self._current_link_text.append(text)

        if self._tag_stack and self._tag_stack[-1] in {"h1", "h2", "h3"}:
            self.heading_parts.append(text)

        if not any(tag in {"script", "style", "noscript"} for tag in self._tag_stack):
            self.text_parts.append(text)


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def is_internal(url):
    parsed = urlparse(url)
    return parsed.netloc in {"", "avr.ifsp.edu.br"}


def normalize_url(base, href):
    url, _fragment = urldefrag(urljoin(base, href))
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc != "avr.ifsp.edu.br":
        return None
    if parsed.path.lower().endswith(SKIP_EXTENSIONS):
        return None
    if "/administrator" in parsed.path:
        return None
    if "format=feed" in parsed.query:
        return None

    safe_path = quote(parsed.path, safe="/%")
    safe_query = quote(parsed.query, safe="=&?/%")
    return urlunparse((parsed.scheme, parsed.netloc, safe_path, parsed.params, safe_query, ""))


def fetch(url):
    request = Request(
        url,
        headers={
            "User-Agent": "RoboAssistenteIFSPAvare/0.1 (+projeto academico)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=20) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return None
        return response.read().decode("utf-8", errors="replace")


def parse_page(url, html):
    parser = PageParser()
    parser.feed(html)
    text = clean_text(" ".join(parser.text_parts))
    headings = []
    for heading in parser.heading_parts:
        heading = clean_text(heading)
        if heading and heading not in headings:
            headings.append(heading)

    links = []
    for link in parser.links:
        normalized = normalize_url(url, link["href"])
        if normalized:
            links.append({"text": link["text"], "url": normalized})

    emails = sorted(set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)))
    phones = sorted(set(re.findall(r"\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}|\b\d{4}[-\s]?\d{4}\b", text)))

    return {
        "url": url,
        "title": clean_text(parser.title) or headings[0] if headings else url,
        "headings": headings[:12],
        "text": text[:12000],
        "summary": text[:700],
        "emails": emails,
        "phones": phones,
        "links": links,
    }


def crawl():
    queue = [BASE_URL]
    seen = set()
    pages = []
    errors = []

    while queue and len(pages) < MAX_PAGES:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)

        try:
            html = fetch(url)
            if not html:
                continue
            page = parse_page(url, html)
            pages.append(page)
            for link in page["links"]:
                if link["url"] not in seen and link["url"] not in queue:
                    queue.append(link["url"])
            print(f"[{len(pages):03}] {page['title']} - {url}")
            time.sleep(0.15)
        except Exception as exc:
            errors.append({"url": url, "error": str(exc)})
            print(f"[erro] {url}: {exc}")

    return pages, errors


def write_outputs(pages, errors):
    payload = {
        "fonte_inicial": BASE_URL,
        "total_paginas": len(pages),
        "gerado_em": time.strftime("%Y-%m-%d"),
        "pages": [
            {
                "url": page["url"],
                "title": page["title"],
                "headings": page["headings"],
                "summary": page["summary"],
                "emails": page["emails"],
                "phones": page["phones"],
            }
            for page in pages
        ],
        "errors": errors,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Mapa Coletado do Site IFSP Avaré",
        "",
        f"- Fonte inicial: {BASE_URL}",
        f"- Total de páginas HTML coletadas: {len(pages)}",
        f"- Data da coleta: {payload['gerado_em']}",
        "",
        "## Páginas",
        "",
    ]
    for page in pages:
        lines.append(f"- [{page['title']}]({page['url']})")
        if page["headings"]:
            lines.append(f"  - Tópicos: {', '.join(page['headings'][:5])}")
        if page["emails"]:
            lines.append(f"  - E-mails: {', '.join(page['emails'])}")
        if page["phones"]:
            lines.append(f"  - Telefones: {', '.join(page['phones'])}")

    if errors:
        lines.extend(["", "## Erros", ""])
        for error in errors:
            lines.append(f"- {error['url']}: {error['error']}")

    OUT_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    pages, errors = crawl()
    write_outputs(pages, errors)
    print(f"Coleta finalizada: {len(pages)} páginas, {len(errors)} erros.")
    print(f"JSON: {OUT_JSON}")
    print(f"Mapa: {OUT_DOC}")


if __name__ == "__main__":
    main()
