# Corpus definitions

Corpus definitions are the way that we configure each corpus in Textcavator.

This documents gives a basic explanation of how corpus definitions work in the backend. It introduces the core concepts and mechanics.

## Corpus definitions

Each corpus is defined by a collection of metadata. This describes things like:

- basic information to display in the interface
- what fields the corpus contains, and how they should be configured
- support for optional functionality like word models or media attachments
- where and how to extract data from source files

Note that a corpus definition does not include the actual data (i.e. documents), it just tells you where to find it. Reading the source data and loading it into the database is a separate action called *indexing*.

Corpora can be created in two ways:

- a **Python corpus** is defined in a Python module. Most data from this module is loaded into the database, but the module also implements custom functions for complex functionality, such as data extraction.
- a **database-only corpus** is only represented in the database and does not use any custom Python functions. It offers less customisation, but is easier to create.

> [!NOTE]
> Database-only corpora are a new feature that is still in development. This option is not yet recommended for production.

The sections below give a a more detailed overview of the differences between these options. Per option, there is also a more detailed description of how it works.

## Python vs. database-only corpora

These are the key differences between Python and database-only corpora.

### Data extraction

A Python corpus can theoretically extract data from any format. In practice, we rely on the [ianalyzer_readers](https://ianalyzer-readers.readthedocs.io/en/latest/) package which provides extraction utilities for common file types like CSV and XML, but the methods for extraction can be as complex as you want. The design philosophy is that you can use the original format of a dataset as the source data for Textcavator, without any pre-processing.

A database-only corpus only supports CSV extraction with very little room for customisation. Here, the idea is that you pre-process your data *before* you pass it on to Textcavator. If it is convenient, you can use the `ianalyzer_readers` package to do so.

### Customisation of the interface

Generally speaking, Python corpora support more customisation of the interface, while the process for entering database-only corpora is designed to infer a lot of these options.

For example, if you want the search interface to show a filter for a field in the corpus, a Python corpus requires that you enter a custom description for the filter, but if you use the API for database-only corpora, the description will be auto-generated.

This means that some customisation is only available for Python corpora. However, it also means that database-only corpora can offer a more streamlined and accessible process for creating a corpus definition.

### Advanced functionality

Database-only corpora do not support some advanced functionality. Notably:
- word models (i.e. word embeddings)
- media attachments to documents
- updating the data of a corpus instead of re-indexing it from scratch
- named entity annotations

### Python class

Python-based corpora are written as Python classes. Each definition should be a subclass of `CorpusDefinition`.

The [corpora](/backend/corpora/) directory contains definitions for all corpora we create. (On top of that, [corpora_test](/backend/corpora_test/) defines corpora for for unit tests. Corpora *can* be saved anywhere.) This directory is not a Django app, but just a collection of scripts and metadata.

To be imported into the application, a definition needs to be added in the Django project settings. The `CORPORA` setting defines a mapping of names and python files, which declares what definitions should be loaded.

When you start up a server, all configured corpus definitions will be imported into the database. During much of the runtime, the backend will refer to the database model rather than the Python class. However, this class can be loaded for more advanced features where custom functions may be used. The most common situation where this happens is when you index the source data.

While Python corpora are *represented* in the database, the source code is still seen as the ultimate source of truth. Each time you start up the server, the corpus is imported again, and this overwrites any changes that that were made to the database in the meantime.

## Database-only corpora

Database-only corpora are just database objects, so unlike Python corpora, they have no single method to be created.

However, database-only corpora have a JSON API that is the recommended way of entering corpora. You can write a corpus definition as a JSON and import it  through the API. In the future, we also plan to have a form that connects to this API.
