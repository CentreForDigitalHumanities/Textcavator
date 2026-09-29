import bs4

def extract_text(node: bs4.element.Tag):
    children = node.find_all(['p', 'titlePart', 'lg'])

    paragraphs = [
        _extract_lg_text(child) if child.name == 'lg' else _extract_plain_text(child)
        for child in children
    ]

    result = '\n\n'.join(filter(len, paragraphs))
    return result


def _extract_plain_text(node: bs4.element.Tag):
    text = []
    for el in node.contents:
        if isinstance(el, bs4.element.NavigableString):
            if len(text) and not text[-1].endswith('\n'):
                text.append(' ')
            text.append(el.string.strip())
        elif isinstance(el, bs4.element.Tag):
            if el.name == 'lb':
                text.append('\n')
            elif el.name == 'note':
                continue
            elif el.name == 'orig':
                if el.has_attr('reg'):
                    text.append(el.attrs['reg'])
                else:
                    text.append(_extract_plain_text(el))
            else:
                content = _extract_plain_text(el)
                text.append(content)
    return ''.join(text).strip()


def _extract_lg_text(node: bs4.element.Tag):
    lines = node.find_all('l')
    line_contents = map(_extract_plain_text, lines)
    return '\n'.join(line_contents)
