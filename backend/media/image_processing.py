from pypdf import PdfReader, PdfWriter
from io import BytesIO

from os.path import getsize, split


def pdf_pages(page_index: int, total_pages: int, window_size: int = 2):
    '''
    Selects indices of pages surrounding the target pages.

    Parameters:
        page_index: zero-based index of the target page
        total_pages: total number of pages in the document
        window_size: number of pages to "pad" the target document. 2 pages (default)
            means 2 pages on either side, if available.
    '''
    start = max(0, page_index - window_size)
    end = min(total_pages - 1, page_index + window_size)
    return list(range(start, end + 1))


def build_partial_pdf(pages, input_pdf):
    '''
    Build a partial pdf consisting of the requires pages.
    Returns a temporary file stream.
    '''
    tmp = BytesIO()
    pdf_writer = PdfWriter()
    for p in pages:
        pdf_writer.add_page(input_pdf.pages[p])
    pdf_writer.write(tmp)
    tmp.seek(0)  # reset stream

    return tmp


def retrieve_pdf(path):
    '''
    Retrieve the pdf as a file object.
    '''
    pdf = PdfReader(path)

    return pdf


def get_pdf_info(path):
    '''
    Gather pdf information.
    '''
    pdf = PdfReader(path, 'rb')
    title = pdf.metadata.title
    _dir, filename = split(path)
    num_pages = len(pdf.pages)
    info = {
        'filename': title if title else filename,
        'filesize': sizeof_fmt(getsize(path)),
        'all_pages': list(range(0, num_pages)),
        'num_pages': num_pages,
    }
    return info


def sizeof_fmt(num, suffix='B'):
    '''
    Converts numerical filesize to human-readable string.
    Maximum of three numbers before the decimal, and one behind.
    E.g. 124857000 -> "119.1 MB"
    '''
    for unit in ['', 'K', 'M', 'G']:
        if abs(num) < 1024.0:
            return "{:3.1f} {}{}".format(num, unit, suffix)
        num /= 1024.0
