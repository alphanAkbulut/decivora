#!/usr/bin/env python3
"""Local Markdown heading/explicit-ID checks; external URLs are not requested."""
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]


def anchors(text):
    result=set(re.findall(r'(?:id|name)=[\"\']([^\"\']+)[\"\']',text))
    seen={};fence=None
    for line in text.splitlines():
        marker=re.match(r'^\s*(`{3,}|~{3,})',line)
        if marker:
            if fence is None:fence=marker.group(1)[0]
            elif marker.group(1)[0]==fence:fence=None
            continue
        if fence:continue
        heading=re.match(r'^#{1,6}\s+(.+?)\s*#*$',line)
        if not heading:continue
        title=heading.group(1)
        title=re.sub(r'\[([^]]+)\]\([^)]*\)',r'\1',title)
        title=re.sub(r'<[^>]+>','',title).lower()
        slug=''.join(c for c in title if c in '-_ ' or unicodedata.category(c)[0] in 'LNM').replace(' ','-')
        n=seen.get(slug,0);seen[slug]=n+1
        result.add(slug+('-'+str(n) if n else ''))
    return result


def check(root=ROOT):
    errors=[];checked=0
    for path in sorted(root.rglob('*.md')):
        text=path.read_text()
        # Ignore fenced code examples, whose links are not navigable Markdown.
        text=re.sub(r'(?m)^```[^\n]*\n[\s\S]*?^```\s*$', '', text)
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '#' not in target or '://' in target or target.startswith('mailto:'):continue
            filename,fragment=target.split('#',1)
            if not fragment:continue
            other=path.parent/unquote(filename) if filename else path
            if other.suffix!='.md':continue
            checked+=1
            if not other.exists() or unquote(fragment) not in anchors(other.read_text()):
                errors.append(str(path.relative_to(root))+': '+target)
    return checked,errors


if __name__=='__main__':
    n,errors=check()
    for error in errors:print(error)
    print(('FAIL' if errors else 'PASS')+': %d local Markdown anchors checked'%n)
    sys.exit(bool(errors))
