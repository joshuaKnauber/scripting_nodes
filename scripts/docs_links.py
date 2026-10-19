"""Check the docs' internal links and images.

    python scripts/docs_links.py

Every `/docs/...` link in website/content/docs must point at a page (a folder
in parentheses doesn't add to the URL, a folder's index.mdx is the folder's
URL) and every `/screenshots/...` image must exist in website/public.
Anchors (#...) aren't checked.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "website", "content", "docs")
PUBLIC = os.path.join(ROOT, "website", "public")

LINK = re.compile(r"""(?:\]\(|href=["'{]+)(/docs[^)\s"'#}]*)""")
IMAGE = re.compile(r"""(?:\]\(|src=["'{]+)(/screenshots/[^)\s"'}]+)""")


def url_of(path):
    rel = os.path.relpath(path, DOCS)[: -len(".mdx")]
    parts = [
        p for p in rel.split(os.sep) if not (p.startswith("(") and p.endswith(")"))
    ]
    if parts and parts[-1] == "index":
        parts.pop()
    return "/".join(["/docs", *parts]).rstrip("/") or "/docs"


def main():
    pages = {}
    for folder, _, files in os.walk(DOCS):
        for name in files:
            if name.endswith(".mdx"):
                path = os.path.join(folder, name)
                pages[url_of(path)] = path

    broken = []
    for url, path in sorted(pages.items()):
        with open(path) as f:
            text = f.read()
        rel = os.path.relpath(path, ROOT)
        for link in LINK.findall(text):
            if link.rstrip("/") not in pages:
                broken.append(f"{rel}: link {link}")
        for image in IMAGE.findall(text):
            if not os.path.exists(os.path.join(PUBLIC, image.lstrip("/"))):
                broken.append(f"{rel}: image {image}")

    print(f"{len(pages)} pages")
    if broken:
        print("\n".join(broken))
        sys.exit(f"{len(broken)} broken")


if __name__ == "__main__":
    main()
