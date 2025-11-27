### Download search results

When you search a corpus, you can use the "download" tab to download a table of your search results. On this page, you choose which fields should be downloaded and how the results should be sorted.

Large downloads may take longer to create; you will be able to request the download and receive an email when the file is ready. This option is only available if you are signed in.

You can select which fields should be included in the CSV download. In addition, you can include your tags, and a link to the original document in Textcavator. Your search query will also be included as an extra column.

You can also choose the file encoding. We recommend the "utf-16" encoding if you are using Microsoft Excel, and "utf-8" for all other applications. If an application is not displaying special characters correctly (while they appear normal on Textcavator itself), it may help to use a different file encoding.

### Download visualization data

All visualisations on Textcavator also have a "table view" to see the data used in the visualisation. You can download this data using the "download table data" button.

#### Full data

When visualisations are based on a sample of the search results, you may have the option to request the full data. This applies to the [frequency of the search term](/manual/termfrequency) and [neighbouring words](/manual/ngrams) visualisations. (See the documentation of each visualisation for more information on how data is sampled.)

This option allows you to download a CSV table of the result based on all documents in your search results, instead of a sample. Since the analysis for these tables may take some time, you will receive an email with a download link when the result is ready.

### Download history

If you are signed in, you can visit your [downloads history](/download-history). This page shows an overview of your past CSV downloads. You can use this page to view the process of large downloads, re-download older files, or check what query you used in previous downloads.

### Using CSV files

You can import csv files in a spreadsheet program like Microsoft Excel, Google Sheets or LibreOffice Calc.

The csv files for search results are delimited by `;`. If the columns are not imported correctly, you may need to set the delimiter. (The csv files for visualisations are delimited by `,` and should be imported correctly by default.)

If you process the csv further in R or Python, you can specify the delimiter which should be used.
For example, in R:
```
data <- read.csv('your-search-results.csv', sep=';')
data <- read.csv('your-visualisation.csv')
```

In Python [Pandas](https://pandas.pydata.org/) (note that this requires that you have pandas installed).
```
import pandas as pd
data = pd.read_csv('your-search-results.csv', sep=';')
data = pd.read_csv('your-visualisation.csv')
```
