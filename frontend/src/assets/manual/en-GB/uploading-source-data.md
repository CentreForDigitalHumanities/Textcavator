When you create a corpus, you will need to upload your source data as a CSV file.

CSV files are a lightweight format for data tables, supported by many data data applications. Below, we provide brief instructions on how to create a suitable CSV file using a spreadsheet editor (like Microsoft Excel), and using Python.

Finally, we also include a full specification of the requirements for the file, including an example file.

## Using a spreadsheet editor

For small datasets, you can use a spreedsheet editor like Microsoft Excel, Google Sheets or LibreOffice Calc to assemble or clean up your data. You can then export the sheet as a CSV file.

Your sheet should consist of a single table with all your data. Use the first row to write column headers. After that, each row contains a single document. For example, you could use the following spreadsheet to make a corpus with 2 fields and 3 documents:

<table class="spreadsheet">
    <thead>
        <tr>
            <th></th>
            <th>A</th>
            <th>B</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th>1</th>
            <td>title</td>
            <td>content</td>
        </tr>
        <tr>
            <th>2</th>
            <td>Frankenstein, or, the Modern Prometheus</td>
            <td>You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings.</td>
        </tr>
        <tr>
            <th>3</th>
            <td>Pride and Prejudice</td>
            <td>It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.</td>
        </tr>
        <tr>
            <th>4</th>
            <td>Alice's adventures in Wonderland / Through the Looking Glass</td>
            <td>Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do.</td>
        </tr>
    </tbody>
</table>

Do not include empty rows between documents, or write in cells outside of the named columns. Visual flair like the font, text colour, cell background, etc. will not show up in the exported file.

To export your file, use the "export" or "save as" option in your spreadsheet editor. In Microsoft Excel, use the "save as CSV UTF-8" option, rather than "save as CSV". The precise steps and options for exporting will depend on your editor.

After exporting, you can use a plain-text editor like Notepad to inspect your file.

If your data contains **formula cells**, make sure that the program exports the values, not the formulas themselves.

If your data contains **date fields**, make sure that they are formatted correctly. Dates must be stored as `year-month-day` in the exported file. If you entered them in a different way (e.g. `day/month/year`), you can adjust the formatting of the cells in the spreadsheet.

## Using Python

If your are processing your data in Python, you can use the [Python csv module](https://docs.python.org/3/library/csv.html#module-csv) to export your data.

Below is an example script to save a CSV file suitable for Textcavator. The script is using the default options when writing a CSV.

```python
import csv
from datetime import date

my_data = [
    {
        'title': 'Frankenstein, or, the Modern Prometheus',
        'content': 'You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings.',
        'date': date(year=1818, month=1, day=1),
    }, {
        'title': 'Pride and Prejudice',
        'content': 'It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.',
        'date': date(year=1813, month=1, day=28),
    }, {
        'title': 'Alice\'s adventures in Wonderland / Through the Looking Glass',
        'content': 'Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do.',
        'date': date(year=1865, month=11, day=9),
    }
]

fieldnames = ['title', 'date', 'content']

with open('data.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in my_data:
        writer.writerow(row)
```

Data libraries like pandas often have a built-in option to export data as CSV. In that case, the default options are usually fine. If you run into issues, consult the specification below to check your output format.

## Technical specification

The data file must be a CSV file. You should save the file with a `.csv` extension.

These are the requirements for the format of the data:

- You can use a comma (`,`), semicolon (`;`) or tab as a separator between columns. (Any is fine, but you cannot mix different separators in your data.)
- The first row of the file should be the header; it contains the column names.
- The file encoding should be `utf-8`.

The table below describes formatting requirements per data type.

| Data type | Notes |
|-----------|-------|
| text      | To avoid problems when the text contains the separator character (e.g. `,`), put the text between double quotes (`"`). (You can use quotes for other fields types, as well, but it is not necessary.) If the text field may contain line breaks and/or quote characters, put the text between three quotes (`"""`). |
| date      | Must be formatted as *year-month-day*. For example, "March 18th, 1927" can be written as `1927-3-18` or `1927-03-18`. |
| number (integer) | Plain numbers, without decimal points or units. |
| number (decimal) | Use a demical point (`.`), not a comma (`,`). The column can contain a mix of decimal and whole numbers. |
| boolean   | Write values as `true` or `false`. This is not case-sensitive, so `True`/`False` or `TRUE`/`FALSE` are also fine. |
| url       | Write the full URL including protocol (e.g. `http://` or `https://`) |

### Example

Below is an example of a valid CSV file.

```csv
date,genre,pages,rating,female_author,title,content
1818-01-01,"Science fiction",150,3.9,true,"Frankenstein, or, the Modern Prometheus","""You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings."""
1813-01-28,"Romance",334,4.1,true,"Pride and Prejudice","""It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife."""
1865-11-09,"Children",false,239,4.0,false,"Alice's adventures in Wonderland / Through the Looking Glass","""Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do."""
```

This file contains the following columns:  `date` (date), `genre` (text), `pages` (number, integer), `rating` (number, decimal), `female_author` (boolean), `title` (text), `content` (text).
