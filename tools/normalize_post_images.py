#!/usr/bin/env python3
import re, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / '_posts'
OUT = ROOT / 'assets' / 'img' / 'posts'
OUT.mkdir(parents=True, exist_ok=True)

def slugify(name):
    s = urllib.parse.unquote(name)
    s = s.replace('%20', ' ')
    s = s.strip()
    # take basename if path
    s = s.split('/')[-1]
    s = re.sub(r'[^0-9a-zA-Z]+', '-', s)
    s = s.strip('-').lower()
    if not s:
        s = 'image'
    return s + '.svg'

pattern_md = re.compile(r'!\[.*?\]\((.*?)\)')
pattern_obs = re.compile(r'!\[\[([^\]]+)\]\]')

modified = []
created = set()
for md in sorted(POSTS.glob('*.md')):
    text = md.read_text(encoding='utf-8')
    orig = text
    # collect matches
    matches = []
    for m in pattern_md.finditer(text):
        inner = m.group(1).strip()
        if inner.lower().startswith('http'):
            continue
        # local file reference (not http)
        if re.search(r'\.(png|jpe?g|gif|svg)$', inner, flags=re.IGNORECASE) or 'pasted' in inner.lower() or 'screenshot' in inner.lower():
            matches.append((m.span(), inner))
    for m in pattern_obs.finditer(text):
        inner = m.group(1).strip()
        if re.search(r'\.(png|jpe?g|gif|svg)$', inner, flags=re.IGNORECASE) or 'pasted' in inner.lower() or 'screenshot' in inner.lower() or inner.startswith('/assets'):
            matches.append((m.span(), inner))
    # process matches in reverse order to keep spans valid
    for span, inner in reversed(matches):
        # derive basename
        # if inner contains pipe like 'name|918' remove pipe part
        inner_clean = inner.split('|')[0].strip()
        # if inner is like /assets/img/posts/slug.svg or already svg, keep basename
        basename = inner_clean.split('/')[-1]
        slug = slugify(basename)
        target = f'assets/img/posts/{slug}'
        target_path = OUT / slug
        if not target_path.exists():
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400">\n  <rect width="100%" height="100%" fill="#f3f4f6"/>\n  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="20" fill="#6b7280">{basename}</text>\n</svg>'
            target_path.write_text(svg, encoding='utf-8')
            created.add(str(target_path.relative_to(ROOT)))
        # replace the whole match with standard markdown image link (no leading slash)
        new_token = f'![]({target})'
        a,b = span
        text = text[:a] + new_token + text[b:]
    if text != orig:
        bak = md.with_suffix(md.suffix + '.normbak')
        if not bak.exists():
            bak.write_text(orig, encoding='utf-8')
        md.write_text(text, encoding='utf-8')
        modified.append(str(md.relative_to(ROOT)))

print('Created:', len(created))
for c in sorted(created):
    print(' -', c)
print('Modified files:', len(modified))
for m in modified:
    print(' -', m)
