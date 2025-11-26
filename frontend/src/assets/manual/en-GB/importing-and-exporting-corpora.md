You can download and upload a file that describes the configuration for your corpus. This can be useful to make a back-up, or to make a copy of your corpus.

This file contains everything you have entered in the corpus form, such as the title, documentation, and fields. However, it does not contain the corpus image (if you have uploaded one), or your data. So if you want to make a full back-up of your corpus, make sure that you also store a copy of the image and the data.

The corpus definition is a JSON file. JSON is a file format that can hold any kind of data, but Textcavator will only accept files that describe corpora.

## Downloading a backup

From the corpus overview, use the "import/export" link for your corpus. On this page, click the "download JSON" button to download a copy of your configuration.

## Creating a corpus from a file

When you create a corpus, you can choose whether to begin in the interactive editor or upload a JSON file.

After you have uploaded a file, you can open the interactive editor; fields will be filled in based on your file. If your corpus was already complete, you will need to do two more things:

- In the first step (corpus information), upload your corpus image, if you have one.
- In the second step (upload source data), upload your data file.

## Restoring a corpus to previous settings

If you download a backup file for your corpus, you can use it to return the corpus to earlier settings. To do this, go to the "import/export" page (where you also download a backup file). Use the "upload JSON" button to upload your file. The corpus will be updated based on your file.

Depending on your changes, you may also need to upload a new (or old) CSV file in the interactive editor.

## Advanced usage

We generally recommend that you create corpora using the interactive editor because this option provides more guidance, and only use JSON files to create copies or backups. However, it is possible to write and edit JSON files directly.

We do not provide a manual for writing corpus files, but you can inspect the [specification](/api/corpus/definition-schema), which is encoded as a [JSON schema](https://json-schema.org/). However, be aware that this specification only describes the *format*, not what makes a valid corpus. For example, you can specify a `sort` property for fields, but not all field types support sorting.
