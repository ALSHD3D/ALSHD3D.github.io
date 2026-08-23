#!/usr/bin/env python3
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / '_posts'

# well-formed token
well_re = re.compile(r'(!\[\]\()(?:/)?(assets/img/posts/([^\)\s]+)\))')
# malformed: token followed by backtick-wrapped original filename
malformed_re = re.compile(r'!\[\]\((?:/)?assets/img/posts/[^`\n]*`([^`]+)`')

modified = []
for md in sorted(POSTS.glob('*.md')):
    text = md.read_text(encoding='utf-8')
    orig = text
    lines = text.splitlines()
    changed = False
    for i,line in enumerate(lines):
        if 'assets/img/posts' not in line:
            continue
        # fix malformed occurrences first
        def malfix(m):
            name = m.group(1)
            return f'`{name}`'
        new_line = malformed_re.sub(malfix, line)
        if new_line != line:
            line = new_line
            changed = True
        # now fix well-formed tokens
        for m in list(well_re.finditer(line)):
            full = m.group(0)
            path = m.group(2)
            slug = m.group(3)
            token = f'![]({path})'
            # if line is exactly the token (maybe with spaces)
            if line.strip() == full:
                # normalize to no leading slash
                new_tok = f'![]({path})'
                if new_tok != full:
                    line = line.replace(full, new_tok)
                    changed = True
            else:
                # inline: replace with backticked original name
                # attempt to derive original name from slug
                s = slug
                if s.endswith('.png'):
                    origname = s[:-len('.png')] + '.png'
                elif s.endswith('-.png'):
                    origname = s[:-len('-.png')] + '.png'
                elif s.endswith('.svg'):
                    origname = s[:-len('.svg')] + '.png'
                else:
                    origname = s
                line = line.replace(full, f'`{origname}`')
                changed = True
        lines[i] = line
    if changed:
        bak = md.with_suffix(md.suffix + '.repairbak')
        if not bak.exists():
            bak.write_text(orig, encoding='utf-8')
        md.write_text('\n'.join(lines), encoding='utf-8')
        modified.append(str(md.relative_to(ROOT)))

print('Repaired inline/malformed tokens in', len(modified), 'files')
for m in modified:
    print(' -', m)
