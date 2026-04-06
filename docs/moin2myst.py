#!/usr/bin/env python3
"""Convert MoinMoin wiki markup to plain MyST Markdown.

Usage:
    python3 moin2myst.py <input.md> [output.md]

If no output file is given, the input file is overwritten.

Assumptions:
- The input file already has a MyST anchor and H1 heading at the top
  (i.e. the page title is NOT taken from the MoinMoin #title directive).
- MoinMoin section headings (= H =) map to ## in MyST (one level below H1).
- Local relative wiki links use https://help.ubuntu.com/community/ as the base URL.
- Images ({{attachment:...}}) are replaced with HTML comments.
- <<BR>> inside list items is converted to a continuation line indented by 2 spaces
  (assumes top-level list items; adjust indent for deeper nesting if needed).

MoinMoin-specific constructs handled:
- ## comment lines (invisible in rendered wiki) are stripped.
- /* ... */ block comments (invisible in rendered wiki) are stripped.
- !WikiWord NoLink markers (e.g. !OpenStack) are stripped to plain text.
- Word``Word CamelCase-suppression backtick pairs are collapsed (e.g. Ge``Force
  becomes GeForce).
- <<TableOfContents>> and <<FullSearch>> standalone macro lines are removed.
- ''italic'' is converted to _italic_ (underscore form preferred in MyST).
"""

import re
import sys


def strip_block_comments(text: str) -> str:
    """Remove MoinMoin /* ... */ block comment sections.

    Block comments are invisible in rendered wiki output.  They may span
    multiple lines: the section starts with a line whose first non-whitespace
    characters are /* and ends with a line whose last non-whitespace
    characters are */.  Single-line /* comment */ forms are also removed.
    Content inside fenced code blocks (``` ... ```) is left untouched.
    """
    lines = text.split('\n')
    result = []
    in_comment = False
    in_fence = False
    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
        if in_fence:
            result.append(line)
            continue
        stripped = line.strip()
        if not in_comment:
            if stripped.startswith('/*'):
                if stripped.endswith('*/') and len(stripped) > 2:
                    continue  # single-line /* comment */ — drop it
                else:
                    in_comment = True
                    continue  # drop the /* opener line
            else:
                result.append(line)
        else:
            if stripped.endswith('*/'):
                in_comment = False  # drop the */ closer line
            # else: drop comment body line
    return '\n'.join(result)


def strip_moinmoin_comments(text: str) -> str:
    """Remove MoinMoin ## comment lines.

    In MoinMoin any line that begins with ## (with or without a following
    space) is a processing comment and is never rendered in the output.
    This includes both ordinary comments (## some note) and macro-style
    markers such as ##StartSectionBugs or ##FIXME.

    Content inside fenced code blocks (``` ... ```) is left untouched so
    that shell-style ## comments inside code examples are preserved.

    Call this *after* the {{{ }}} → ``` conversion so that fence detection
    works correctly, and *before* the = heading = → ## heading conversion
    so that comment lines are not mistaken for Markdown headings.
    """
    lines = text.split('\n')
    result = []
    in_fence = False
    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
        if not in_fence and re.match(r'^##', line):
            continue
        result.append(line)
    return '\n'.join(result)


def wrap_naked_urls(text: str) -> str:
    """Wrap bare URLs in [URL](URL) Markdown link markup.

    A URL is considered 'naked' if it is not already preceded by '(' (link
    href) or '[' (link text), and is not inside a fenced code block or an
    inline backtick code span.

    Trailing sentence punctuation (.,;:!?)'") that is not part of the URL is
    stripped from the matched URL and re-appended after the closing ')'.
    """
    url_re = re.compile(r'(?<!\()(?<!\[)(https?://\S+)')

    def _wrap(m):
        url = m.group(1)
        # Strip trailing punctuation that belongs to the sentence, not the URL.
        trail = ''
        while url and url[-1] in '.,;:!?)\'"\\]>':
            trail = url[-1] + trail
            url = url[:-1]
        if not url:
            return m.group(0)
        return f'[{url}]({url}){trail}'

    lines = text.split('\n')
    result = []
    in_fence = False

    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
            result.append(line)
            continue

        if in_fence:
            result.append(line)
            continue

        # Split line into inline-code spans and plain-text segments so that
        # URLs inside backtick code are not touched.
        parts = re.split(r'(`[^`\n]+`)', line)
        result.append(''.join(
            part if (part.startswith('`') and part.endswith('`')) else url_re.sub(_wrap, part)
            for part in parts
        ))

    return '\n'.join(result)


def normalize_text_indent(text: str) -> str:
    """Strip leading whitespace from regular text lines.

    Preserves indentation inside fenced code blocks and for list continuation
    lines (indented lines immediately following a list item or another
    indented continuation, with no blank line in between).
    """
    list_item_re = re.compile(r'^\s*(?:[*-]|\d+\.)\s')
    lines = text.split('\n')
    result = []
    in_fence = False
    in_list = False

    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
            in_list = False
            result.append(line)
            continue

        if in_fence:
            result.append(line)
            continue

        if not line.strip():
            # Blank line resets list context; next list item will re-set it.
            in_list = False
            result.append(line)
            continue

        if list_item_re.match(line):
            in_list = True
            result.append(line)
            continue

        if in_list and line[0] == ' ':
            # Indented continuation of a list item — preserve indent.
            result.append(line)
            continue

        # Regular text: strip accidental leading whitespace.
        result.append(line.lstrip())

    return '\n'.join(result)


def ensure_blank_before_lists(text: str) -> str:
    """Ensure there is always a blank line immediately before the first item of a list.

    Operates line-by-line and respects code fences (does not modify content
    inside fenced blocks).
    """
    list_item_re = re.compile(r'^\s*(?:[*-]|\d+\.)\s')
    lines = text.split('\n')
    result = []
    in_fence = False

    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
        if (
            not in_fence
            and list_item_re.match(line)
            and result
            and result[-1] != ''
            and not list_item_re.match(result[-1])
        ):
            result.append('')
        result.append(line)

    return '\n'.join(result)


def loosen_long_lists(text: str) -> str:
    """Add blank lines between list items when any item line exceeds 78 chars.

    Processes each contiguous list block. If any line in the block (item
    starters and continuation lines) exceeds 78 characters, blank lines are
    inserted before every item except the first.
    """
    list_item_re = re.compile(r'^\s*(?:[*-]|\d+\.)\s')
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        if list_item_re.match(lines[i]):
            # Collect the full contiguous list block (items + continuation lines).
            block = []  # list of (is_item_start, line)
            while i < len(lines):
                if list_item_re.match(lines[i]):
                    block.append((True, lines[i]))
                    i += 1
                elif lines[i] and block:
                    # Non-empty, non-marker line: continuation of the previous item.
                    block.append((False, lines[i]))
                    i += 1
                else:
                    break

            has_long = any(len(line) > 78 for _, line in block)

            if has_long:
                first_item = True
                for is_item_start, line in block:
                    if is_item_start and not first_item:
                        result.append('')
                    result.append(line)
                    if is_item_start:
                        first_item = False
            else:
                for _, line in block:
                    result.append(line)
        else:
            result.append(lines[i])
            i += 1

    return '\n'.join(result)


def convert(text: str) -> str:
    # ── Step 1: Remove known MoinMoin metadata directives
    text = re.sub(
        r'(?m)^#(title|acl|language|format|pragma|redirect|refresh|deprecated|superscript|subscript)\b[^\n]*\n?',
        '',
        text,
    )

    # ── Step 1b: Remove standalone macro lines with no Markdown equivalent
    text = re.sub(r'(?m)^<<(?:TableOfContents|FullSearch)(?:\([^)]*\))?>>[^\n]*\n?', '', text)

    # ── Step 2: <<BR>> linebreak macro → newline + 2-space indent for list continuation
    # The 2-space indent keeps continuation text inside the list item in MyST/CommonMark.
    text = text.replace('<<BR>>', '\n  ')

    # ── Step 3: <<Anchor(name)>> → (name)= anchor label
    def replace_anchor(m):
        name = m.group(1).strip()
        return f'({name})='

    text = re.sub(r'<<Anchor\(([^)]+)\)>>', replace_anchor, text)

    # ── Step 4: Inline code (no newlines inside): {{{word}}} → `word`
    text = re.sub(r'\{\{\{([^{}\n]+)\}\}\}', r'`\1`', text)

    # ── Step 5: Block code (newlines inside): {{{ ... }}} → fenced none block
    def replace_code_block(m):
        code = m.group(1).strip('\n')
        return f'\n```none\n{code}\n```\n'

    text = re.sub(r'\{\{\{(.*?)\}\}\}', replace_code_block, flags=re.DOTALL, string=text)

    # ── Step 6: Remove MoinMoin block comments, comment lines, and NoLink markers.
    # These steps run after code conversion (Steps 4–5) so that fence detection
    # (```) works correctly, and before heading conversion (Step 8) so that ##
    # comment lines are not mistaken for Markdown headings.

    # Remove /* ... */ block comments (invisible in rendered wiki)
    text = strip_block_comments(text)

    # Remove ## comment lines (invisible in rendered wiki)
    text = strip_moinmoin_comments(text)

    # Remove !WikiWord NoLink markers: !OpenStack → OpenStack.
    # The leading ! suppresses MoinMoin CamelCase auto-linking; in Markdown
    # there is no auto-linking so the marker is simply noise.
    # Pattern is safe: Markdown image syntax uses ![ (bracket, not uppercase),
    # and != operators use = not an uppercase letter.
    text = re.sub(r'!([A-Z][A-Za-z]+)', r'\1', text)

    # Remove CamelCase-suppression backtick pairs: Ge``Force → GeForce.
    # MoinMoin inserts an invisible `` pair inside a CamelCase word to prevent
    # auto-linking; the pair is invisible in rendered wiki output.
    # The lookbehind/lookahead ensure only pairs between word characters are
    # removed; triple-backtick code fences and inline code spans are unaffected.
    text = re.sub(r'(?<=[A-Za-z0-9])``(?=[A-Za-z0-9])', '', text)

    # ── Step 7: Remove MoinMoin table wrapper  ||<style="...">CONTENT||
    text = re.sub(r'\|\|(?:<[^>]*>)?(.*?)\|\|', lambda m: m.group(1).strip(), text)

    # ── Step 8: Images {{attachment:file.png|desc}} → HTML comment
    def replace_image(m):
        filename = m.group(1).strip()
        desc = m.group(2).strip() if m.group(2) else ''
        if desc:
            return f'<!-- Image: {filename} | {desc} -->'
        else:
            return f'<!-- Image: {filename} -->'

    text = re.sub(r'\{\{attachment:([^|}]+?)(?:\|([^}]*))?}}', replace_image, text)

    # ── Step 9: Section headings  = H2 =  == H3 ==  === H4 ===
    def convert_heading(m):
        level = len(m.group(1))
        title = m.group(2).strip()
        hashes = '#' * (level + 1)  # = → ##, == → ###, etc.
        slug = title.lower()
        slug = re.sub(r"'", '', slug)
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return f'\n\n({slug})=\n{hashes} {title}'

    text = re.sub(r'(?m)^(=+)\s+(.+?)\s+\1\s*$', convert_heading, text)

    # ── Step 10: Horizontal rules  -----  →  ---
    # Use [^\S\n]* (not \s*) so trailing whitespace on the rule line is stripped
    # without consuming the newlines that follow it.
    text = re.sub(r'(?m)^-{4,}[^\S\n]*$', '---', text)

    # ── Step 11: Links — mailto first
    def replace_mailto(m):
        addr = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else addr
        email_match = re.search(r'<([^>]+)>', addr)
        email = email_match.group(1) if email_match else addr
        return f'[{label}](mailto:{email})'

    text = re.sub(r'\[\[mailto:([^|\]]+?)(?:\|([^\]]*))?\]\]', replace_mailto, text)

    # [[URL|label]]  →  [label](URL)
    text = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'[\2](\1)', text)

    # [[URL]] or [[WikiPage]]  (bare links)
    def replace_bare_link(m):
        target = m.group(1).strip()
        if re.match(r'[a-z]+://', target):
            return f'[{target}]({target})'
        else:
            page = target.replace(' ', '_')
            return f'[{target}](https://help.ubuntu.com/community/{page})'

    text = re.sub(r'\[\[([^\]]+)\]\]', replace_bare_link, text)

    # ── Step 12: Emphasis — bold+italic, bold, italic
    # MoinMoin bold+italic ('''''text''''') → **_text_** (nested bold+italic).
    # *** is not valid MyST inline markup; use ** wrapping _.._ instead.
    # ''italic'' → _italic_ (underscore form is conventional in MyST and
    # avoids ambiguity with bullet-list * markers).
    text = re.sub(r"'{5}(.+?)'{5}", r'**_\1_**', text)
    text = re.sub(r"'{3}(.+?)'{3}", r'**\1**', text)
    text = re.sub(r"'{2}(.+?)'{2}", r'_\1_', text)

    # ── Step 13: Strip internal leading/trailing horizontal whitespace from ** ... **
    # spans.  Using full paired-span matching avoids the ambiguity between opening
    # and closing markers that one-sided patterns suffer from (e.g. "content:** next"
    # would be incorrectly treated as an opening marker by a naive left-side-only
    # pattern, stripping the space before "next").
    def _strip_bold(m):
        return f'**{m.group(1).strip(" \t")}**'

    text = re.sub(r'(?<!\*)\*{2}(?!\*)([^\n]*?)(?<!\*)\*{2}(?!\*)', _strip_bold, text)

    # ── Step 14: /!\ warning icon (line-level)  →  {note} admonition
    def replace_warning(m):
        content = m.group(1).strip()
        return f'```{{note}}\n{content}\n```'

    text = re.sub(r'(?m)^/!\\\s+(.+)$', replace_warning, text)

    # ── Step 15: Bullet lists — normalize MoinMoin indented " * " to Markdown
    def fix_bullet(m):
        spaces = len(m.group(1))
        indent_level = max(0, (spaces - 1) // 2)
        return '  ' * indent_level + '* ' + m.group(2)

    text = re.sub(r'(?m)^( +)\* (.+)', fix_bullet, text)

    # ── Step 16: Numbered lists — normalize MoinMoin indented " 1. "
    def fix_numbered(m):
        spaces = len(m.group(1))
        indent_level = max(0, (spaces - 1) // 2)
        return '  ' * indent_level + '1. ' + m.group(2)

    text = re.sub(r'(?m)^( +)1\. (.+)', fix_numbered, text)

    # ── Step 17: Clean up malformed link brackets with spaces: [ text ]( url )
    text = re.sub(r'\[\s+([^\]]+?)\s*\]\(\s*([^)]+?)\s*\)', r'[\1](\2)', text)
    text = re.sub(r'\[\s+([^\]]+?)\s*\](?!\()', r'[\1]', text)

    # ── Step 18: Wrap naked URLs (not already inside link markup or code spans)
    text = wrap_naked_urls(text)

    # ── Step 19: Strip end-of-line trailing whitespace
    text = re.sub(r'(?m) +$', '', text)

    # ── Step 20: Blank line before opening code/admonition fence
    # Matches any non-blank line immediately followed by a fence opener (```lang or ```{role}).
    text = re.sub(r'([^\n])\n(```[a-z{])', r'\1\n\n\2', text)

    # ── Step 21: Blank line after closing code fence (line containing only ```)
    # Mark closing fences, add blank line, then remove marker.
    text = re.sub(r'(?m)^```$', '```\x00', text)
    text = re.sub(r'```\x00\n([^\n\x00])', '```\x00\n\n\\1', text)
    text = text.replace('\x00', '')

    # ── Step 22: Collapse 3+ blank lines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    # ── Step 23: Merge consecutive anchor labels (no blank line between them)
    # e.g. (translation)=\n\n(filing-a-translation-bug)= → consecutive labels on a heading
    text = re.sub(
        r'(\([a-z][a-z0-9-]*\)=)\n\n(\([a-z][a-z0-9-]*\)=)',
        r'\1\n\2',
        text,
    )

    # ── Step 24: Ensure exactly 2 blank lines before heading anchor blocks
    # A heading anchor block is one or more (label)= lines followed by a # heading.
    # Match any number of preceding newlines (1+) so that under-spaced cases
    # (e.g. a single \n after ---) are also caught.
    # Only applies when preceded by at least one \n (not at start of file).
    text = re.sub(
        r'\n+(\([a-z][a-z0-9-]*\)=\n(?:(?:\([a-z][a-z0-9-]*\)=\n)*)#{1,6} )',
        r'\n\n\n\1',
        text,
    )

    # ── Step 25: Strip leading whitespace from regular text lines.
    # List continuation lines (indented, immediately following a list item) are preserved.
    # Content inside fenced blocks is preserved.
    text = normalize_text_indent(text)

    # ── Step 26: Add blank line before every list (regardless of item length)
    text = ensure_blank_before_lists(text)

    # ── Step 27: Add blank lines between long list items
    text = loosen_long_lists(text)

    # ── Step 28: Collapse 4+ blank lines to 3 (preserves the 2-blank-line heading spacing
    # that may have been exceeded by list loosening immediately before a heading)
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    # ── Step 29: Ensure blank line after heading line
    text = re.sub(r'(?m)^(#{1,6} .+)\n([^\n])', r'\1\n\n\2', text)

    return text


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path

    with open(input_path, encoding='utf-8') as f:
        text = f.read()

    result = convert(text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Converted: {input_path} → {output_path}")


if __name__ == '__main__':
    main()
