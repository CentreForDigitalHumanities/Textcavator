The word models for these parliamentary speeches were trained with Word2Vec, as implemented in the Python library [Gensim](https://radimrehurek.com/gensim/models/word2vec.html).

Models were trained for 10-year time windows with a shift of 5 years.

Training parameters:
- training algorithm: CBOW
- window size: 5
- minimum word count for inclusion in model: 80
- vector dimensionality: 100

The original training script is available on [Word2VecElastic](https://github.com/CentreForDigitalHumanities/Word2VecElastic)
