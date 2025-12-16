# Corpus database models

As discussed in [corpus definitions](/documentation/Corpus-definitions.md), corpora can be defined in a Python class that is partially represented in the database, or be database-only. This document provides more detail about the structure of the database and how Python corpora are imported.

## Database models

A full corpus definition is represented in four models:

- `Corpus` - the main reference point for the corpus
- `CorpusConfiguration` - has a one-to-one relationship with `Corpus` and represents all configured metadata
- `Field` - has a many-to-one relationship with `CorpusConfiguration` and represents a field in the corpus.
- `CorpusDocumentationPage` - has a many-to-many relationship with `CorpusConfiguration` and represents documentation for users.
- `CorpusDataFile` - manages CSV source data for database-only corpora.

These are defined in [/backend/addcorpus/models.py](/backend/addcorpus/models.py).

### Corpus vs. CorpusConfiguration

The distinction between a `Corpus` and its `CorpusConfiguration` is that the configuration is less stable. The `CorpusConfiguration` (and its related `Field` instances) is completely overwritten when you import a corpus defintion.

On the other hand, the `Corpus` contains information about corpus access that is not covered by the definition. It also serves as the reference point for relationships with other models, such as search history, downloads, and document tags.

 ## Importing Python corpora

Python definitions can be loaded into the database with the `loadcorpora` Django command in the backend. Normally, this is run when you start the server, so you do not need to run it manually.

This command will parse any configured python corpora and save a database representation for them. If the python corpus cannot be loaded, the `Corpus` object will still exist in the database, but it will be inactive.

If a corpus by the same name already exists in the database, the command will completely overwrite its `CorpusConfiguration` and `Field` instances. This means that changing the database representation of a corpus with a Python definition is always temporary (except for adjusting permissions). If you want to make permanent changes to the corpus, adjust the Python definition and run `loadcorpora` again.

## Corpus visibility

Corpora have an `active` status that determines whether they are available for searching. In addition, you can configure the `groups` connected to a corpus, which determines who has access to it. A user will see a corpus if it is active and they are in a group that is given access. (A superuser implicitly has access to all active corpora.)

Textcavator always includes a group named `'basic'`, which everyone is a member of by default, including anonymous users. If you want a corpus to be public, add this group to it.

While a corpus is inactive, its validation is less strict. This allows you to build a database-only corpus in steps, and save an incomplete definition as a work in progress. See [Corpus validation](/documentation/Corpus-validation.md) for more details.

### Disabling and deleting Python corpora

If you want to remove a Python corpus from your environment, or transition it to a database-only corpus, remove it from the Django settings.

Removing a corpus from the settings will not delete the `Corpus` object. It has the following effect:

- The python definition will no longer be imported during startup.
- The next time you run `loadcorpora`, the properties `corpus.active` and `corpus.has_python_definition` are set to `False`. As the corpus is now inactive, it will be hidden from the search interface.

Since the underlying `Corpus` is not actually deleted, related search history, downloads, tags, and permissions will be preserved. If you reinstate the corpus in settings, all of these will function as before.

At this point, you can activate the corpus again and use it as a database-only corpus, or you can remove the `Corpus` object completely, which will remove all related data.
