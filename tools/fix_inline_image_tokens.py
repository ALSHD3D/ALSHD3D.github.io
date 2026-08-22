#!/usr/bin/env python3
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / '_posts'

img_token_re = re.compile(r'!\[]\((assets/img/posts/([^\)\s]+)\))')

def original_name(slug):
    s = slug
    for suffix in ['-png', '-png.svg', '-svg.svg', '.svg']:
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    # normalize
    return s + '.png'

modified = []
for md in sorted(POSTS.glob('*.md')):
    lines = md.read_text(encoding='utf-8').splitlines()
    changed = False
    for i,line in enumerate(lines):
        if 'assets/img/posts' in line and '![](' in line:
            # find tokens
            tokens = list(img_token_re.finditer(line))
            if not tokens:
                continue
            # if the line is just the token (maybe with spaces), keep it
            if line.strip() in [m.group(0) for m in tokens]:
                continue
            # otherwise replace each token with inline code filename
            new_line = line
            for m in reversed(tokens):
                slug = m.group(2)
                orig = original_name(slug)
                replacement = f'`{orig}`'
                a,b = m.span(0)
                new_line = new_line[:a] + replacement + new_line[b:]
            if new_line != line:
                lines[i] = new_line
                changed = True
    if changed:
        bak = md.with_suffix(md.suffix + '.inlinebak')
        if not bak.exists():
            bak.write_text(md.read_text(encoding='utf-8'), encoding='utf-8')
        md.write_text('\n'.join(lines), encoding='utf-8')
        modified.append(str(md.relative_to(ROOT)))

print('Fixed inline tokens in', len(modified), 'files')
for m in modified:
    print(' -', m)
