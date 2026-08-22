#!/usr/bin/env python3
import os, re, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / '_posts'
OUT = ROOT / 'assets' / 'img' / 'posts'
OUT.mkdir(parents=True, exist_ok=True)

img_ext_re = re.compile(r'(?i)\.(png|jpe?g|gif)')

def slugify(name):
    s = urllib.parse.unquote(name)
    s = s.replace('%20', ' ')
    s = re.sub(r'[^0-9a-zA-Z]+', '-', s)
    s = s.strip('-').lower()
    if not s:
        s = 'image'
    return s + '.svg'

created = set()
modified_files = []

for md in POSTS.glob('*.md'):
    text = md.read_text(encoding='utf-8')
    orig = text
    # find candidate image tokens (not starting with http or /)
    tokens = set(re.findall(r'([^\s\(\]\[]+\.(?:png|jpg|jpeg|gif))', text, flags=re.IGNORECASE))
    for tok in tokens:
        if tok.lower().startswith('http') or tok.startswith('/'):
            continue
        # create slug and svg file
        slug = slugify(tok)
        target_rel = f'/assets/img/posts/{slug}'
        target_path = OUT / slug
        if not target_path.exists():
            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400">
  <rect width="100%" height="100%" fill="#f3f4f6"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="20" fill="#6b7280">{tok}</text>
</svg>'''
            target_path.write_text(svg, encoding='utf-8')
            created.add(str(target_path.relative_to(ROOT)))
        # replace occurrences of the token (both percent-encoded and raw)
        text = text.replace(tok, target_rel)
        # also replace URL-decoded form if present
        decoded = urllib.parse.unquote(tok)
        if decoded != tok:
            text = text.replace(decoded, target_rel)
    if text != orig:
        # backup
        bak = md.with_suffix(md.suffix + '.bak')
        if not bak.exists():
            bak.write_text(orig, encoding='utf-8')
        md.write_text(text, encoding='utf-8')
        modified_files.append(str(md.relative_to(ROOT)))

print('Created files:')
for c in sorted(created):
    print(' -', c)
print('\nModified markdown files:')
for m in sorted(modified_files):
    print(' -', m)

if not created and not modified_files:
    print('No local image links found that needed changes.')
