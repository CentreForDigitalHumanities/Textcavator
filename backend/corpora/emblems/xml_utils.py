import re
import html
from typing import List, Dict
import bs4
from langcodes import Language, standardize_tag

def extract_text(nodes: List[bs4.element.Tag]):
    content = [_extract_plain_text(node) for node in nodes]
    return _clean_extracted_text(''.join(content))


def _clean_extracted_text(content: str):
    cleaned = re.sub('  +', ' ', content) # remove double spaces
    return cleaned.strip()


def _extract_plain_text(node: bs4.element.Tag):
    '''
    Extract text contents. This is a custom, recursive function with some awareness of
    node semantics. Output may contain double spaces and leading/trailing whitespace.
    '''
    text = []
    for el in node.contents:
        if isinstance(el, bs4.element.NavigableString):
            text.append(_extract_string(el))
        elif isinstance(el, bs4.element.Tag):
            match el.name:
                case 'div' | 'titleBlock' | 'docTitle' | 'signed': # structural elements
                    text.append(_extract_plain_text(el))
                case 'lb': # line break
                    text.append('\n')
                case 'lg': # line group
                    text.append(_extract_plain_text(el) + '\n')
                case 'l':
                    text.append(_extract_plain_text(el).strip() + '\n')
                case 'p' | 'cit' | 'titlePart': # paragraphs etc.
                    content = _extract_plain_text(el).strip()
                    if content:
                        text.append(content + '\n\n')
                case 'note': # footnotes (not part of original)
                    pass
                case 'orig': # corrections - use if available
                    text.append(el.attrs.get('reg', _extract_plain_text(el)))
                case 'sic': # idem
                    text.append(el.attrs.get('corr', _extract_plain_text(el)))
                case 'c': # punctuation
                    text.append(el.string or '')
                case 'hi' | 'seg' | 'num' | 'name' | 'title' | 'q' | 'quote' | 'foreign' | 'mentioned' | 'author': # inline text elements
                    text.append(_extract_plain_text(el))
                case 'figure' | 'pb' | 'ref' | 'xref': # figures / page breaks / references
                    pass
                case 'bibl': # bibliographical references
                    content = _extract_plain_text(el)
                    text.append(f'[{content}]\n')
                case other:
                    # print('Unexpected element type:', other)
                    text.append(_extract_plain_text(el))

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

# noop function to override the normal value extraction in the XML extractor
def noop(value): return value


def extract_translation(
    sections: List[bs4.element.Tag],
    translations: List[bs4.element.Tag],
    links: List[str],
):
    '''Assemble translation for a page.

    Merges translation notes in the order of the original text and adds [...] for
    untranslated sections
    '''
    text = []
    translations_present = []

    tr_mapping = _map_translations(links)

    for section in sections:
        section_id = section.attrs.get('id')
        tr_ids = tr_mapping.get(section_id, [])
        has_translation = False

        for tr in translations:
            if tr.attrs.get('id') in tr_ids:
                content = _extract_plain_text(tr)
                text.append(content + '\n\n')
                has_translation = True
                break

        translations_present.append(has_translation)
        if has_translation:
            continue

        # check if the original element had text content
        content = _extract_plain_text(section).strip()
        if len(content):
            text.append('[...]\n\n')

    if any(translations_present):
        return ''.join(text).strip()


def _map_translations(links: List[str]) -> Dict[str, List[str]]:
    'Create dict mapping from translation target strings'
    mapping = dict()
    for link in links:
        orig_id, tr_id = link.split()
        existing = mapping.get(orig_id, [])
        mapping[orig_id] = existing + [tr_id]
    return mapping


def remove_doctype(content: str):
    'Remove the initial doctype section which causes issues for beautifulsoup'
    return re.sub(r'<!DOCTYPE .*\[.*\]>', '', content, 1, flags=re.DOTALL)


def replace_ampersands(content: str):
    'Replace ampersand escape characters (before parsing)'
    content = html.unescape(content)

    # additional nonstandard codes
    for code, character in _additional_ampersands.items():
        content = content.replace(f'&{code};', character)

    return content


# additional ampersand codes used in the source data that are not HTML standard
_additional_ampersands = {
    'apost': '\'',
    'lsquot': '“',
    'aelig': 'æ',
    'oelig': 'œ',
    'eacute': 'é',
    'ograve': 'ò',
    'amacron': 'ā',
    'emacron': 'ē',
    'nmacron': 'n',
    'omacron': 'ō',
    'umacron': 'ū',
}


def parse_language(value: str) -> str:
    'Parse a language tag into a display name'
    language = Language.make(standardize_tag(value))
    return language.display_name()


def format_language_list(values: List[str]) -> List[str]:
    'Assemble non-overlapping list of language names from tags'
    unique = set(values)
    return list(sorted(map(parse_language, unique)))
