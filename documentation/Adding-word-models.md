# Adding word models

Corpora have the option to include word vectors. (This option is only supported for Python corpora.)

Textcavator visualisations are built for _diachronic_ word models, showing how word meaning changes over time. As such, Textcavator expects that you trained models for different time intervals.

## Expected file format
Word embeddings are expected to come with the following files:
- `_full.wv` (contains gensim KeyedVectors for a model trained on the whole time period)
For each time bin, it expects files of the format
- `_{startYear}_{endYear}.wv` (contains gensim KeyedVectors for a model trained on the time bin)

## Documentation
Please include documentation on the method and settings used to train a model. See the separate documentation on [how to include documentation pages](./Writing-a-corpus-definition-in-Python.md#documentation-files-and-corpus-image) and [how to write documenation pages](./Corpus-documentation.md).

## Including word models

If your are adding newly trained word models, you will also need to specify in the corpus definition that they may be included. Set the `word_models_path` property in the corpus to the directory in which the word models are stored. See [troonredes.py](../backend/corpora/troonredes/troonredes.py) or [uk.py](../backend/corpora/parliament/uk.py) for examples.

