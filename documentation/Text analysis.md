# Text analysis

Searchable text fields rely on text analyzers in Elasticsearch, which handle processing like conversion to lowercase and tokenisation, and optionally stopword filtering and stemming. See the [Elasticsearch documentation on text analysis](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/analysis.html); the core concepts will not be explained in this document.

Textcavator provides custom analyzers for a variety of languages. In content fields, we use [multifields](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/multi-fields.html) to allow multiple analysis options on the same text.

## Field analyzers

A language configuration will typically implement three analyzers:

- A "standard" analyzer that only uses light transformation on the text. This allows users to find more-or-less exact matched in the text.
- A "clean" analyzer that removes stopwords and numbers. This is mostly useful in visualisations such as the wordcloud.
- A "stemmed" analyzer that removes stopwords and numbers, and performs stemming. This can help with finding relevant matches, and is also used in visualisations. Users can also choose whether to use stemming when making search queries.

Depending on the language, the clean and stemmed analyzers may not be available (see "Language support" below).

Based on these analyzers, text content fields use the following multifields:

- The base field uses the standard analyzer.
- A "length" multifield contains an integer of the token count, using the standard analyzer.
- A "clean" multifield uses the "clean" analyzer.
- A "stemmed" multifield uses the "stemmed" analyzer.

The clean and stemmed multifields are only included if those analyzers are present.

Text metadata fields may also use the standard analyzer for the language.

## Language support

[language_analysis.py](../backend/addcorpus/language_analysis.py) defines text analysis settings per language. Each language configuration is a class that inherits `LanguageAnalyzer`. This means you can override properties/methods as needed to get detailed customisation.

Notes:
- If a language is not included in this module, Textcavator will use the [standard analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/analysis-standard-analyzer.html), without stopword or stemming support.
- Use the `get_analyzer` function to get the right `LanguageAnalyzer`. This function includes the logic to select equivalent tags, and select highly similar languages if applicable.

You can add languages in this module as needed. Be sure to look at [Elasticsearch's language analyzer reference](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/analysis-lang-analyzer.html#_reimplementing_language_analyzers) - this may include useful filters or normalization.

For stopword lists, use the NLTK stopwords corpus if possible. We prefer this over the stopword lists from Elasticsearch because [the NLTK lists are more extensive which fits our use case](https://github.com/CentreForDigitalHumanities/Textcavator/issues/767). We also use the NLTK lists when training word models, and it's nice if those applications are consistent. If neither NLTK not Elasticsearch have a stopwords list for the language, you can get it from elsewhere.

## Customising text analysis per corpus

In most cases, the configuration for text analysis should be determined by the languages used; a corpus only specifies the language(s).

That said, it is possible to customise text analysis per corpus. This may be useful when the corpus has particularly bad OCR or uses a historical variant of the language.

To customise text analysis, specify the `es_settings` for the corpus, and the `es_mapping` for your fields as needed.
