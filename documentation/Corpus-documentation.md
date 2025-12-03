# Corpus documentation pages

Corpora can include markdown templates containing documentation. Textcavator supports several types of documentation pages.

- general information
- citation guidelines
- documentation on word models
- a licence for re-using the data
- terms of service (usually from a third party that provides the dataset)

All are optional.

### Writing documentation

Documentation files are written in markdown. For information about supported flavours, see [marked.js documentation](https://marked.js.org/) - the frontend uses that package with default options.

It is not necessary to include a top-level header in a documentation file.

Documentation pages can use the [Django template language](https://docs.djangoproject.com/en/5.0/topics/templates/). See [documentation.py](/backend/addcorpus/documentation.py) for the provided context.

Examples of documentation:
- [general information (DBNL)](/backend/corpora/dbnl/description/dbnl.md)
- [citation guidelines (DBNL)](/backend/corpora/dbnl/citation/citation.md)
- [word models documentation (People & Parliament corpora)](/backend/corpora/parliament/wm/documentation.md)
