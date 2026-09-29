import re
import bs4

def extract_text(node: bs4.element.Tag):
    content = _extract_plain_text(node)
    cleaned = re.sub('  +', ' ', content) # remove double spaces
    return cleaned.strip()


def _extract_plain_text(node: bs4.element.Tag, parse_string=False):
    text = []
    for el in node.contents:
        if isinstance(el, bs4.element.NavigableString):
            if parse_string:
                text.append(_extract_string(el))
        elif isinstance(el, bs4.element.Tag):
            match el.name:
                case 'div' | 'titleBlock' | 'docTitle' | 'signed': # structural elements
                    text.append(_extract_plain_text(el))
                case 'lb': # line break
                    text.append('\n')
                case 'lg': # line group
                    contents = [_extract_plain_text(line, True).strip() for line in el.find_all('l')]
                    text.append('\n'.join(contents))
                    text.append('\n\n')
                case 'p' | 'cit' | 'titlePart': # paragraphs etc.
                    content = _extract_plain_text(el, True).strip()
                    if content:
                        text.append(content + '\n\n')
                case 'note': # footnotes (not part of original)
                    pass
                case 'orig': # corrections - use if available
                    text.append(el.attrs.get('reg', _extract_plain_text(el, True)))
                case 'sic': # idem
                    text.append(el.attrs.get('corr', _extract_plain_text(el, True)))
                case 'c': # punctuation
                    text.append(el.string)
                case 'hi' | 'seg' | 'num' | 'name' | 'title' | 'q' | 'quote' | 'foreign' | 'mentioned' | 'author': # inline text elements
                    text.append(_extract_plain_text(el, True))
                case 'figure' | 'pb' | 'ref' | 'xref': # figures / page breaks / references
                    pass
                case 'bibl': # bibliographical references
                    content = _extract_plain_text(el, True)
                    return f'[{content}]'
                case other:
                    print('Unexpected element type:', other)
                    text.append(_extract_plain_text(el, True))

    return ''.join(text)


def _extract_string(node: bs4.element.NavigableString):
    content = node.string

    # strip leading / final newlines
    if not node.previous_sibling or node.previous_sibling.name == 'lb':
        content = re.sub(r'^\s*(\n\s*)+', '', content)
    content = re.sub(r'\s*(\n\s*)+$', '', content)

    # strip linebreaks
    content = re.sub(r'\s*\n\s*', ' ', content)

    return content

