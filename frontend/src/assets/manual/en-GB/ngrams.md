The "neighbouring words" graph provides an overview of the words that most commonly surround the search term. This can be useful to narrow down a search, or to understand the context in which the search term is used.

The graph offers two modes: collocates and n-grams. _Collocates_ are individual words that are used within the specified distance of the search term. For example, if you search for _democrat_, you might find the collocates _party_ and _social_: these terms often appear around _democrat_ in the corpus.

_N-grams_ are sequences of words. In this mode, you search for phrases that contain the search term. If you search for two-word phrases (bigrams) containing _democrat_, you may find _democrat party_ and _social democrat_.

## Options

There are several options to control how frequencies are calculated:

- **Mode:** Search for _ngrams_ or _collocates_ (see above).
- **Length of n-gram:** Only available in ngram mode. Search for _bigrams_ (two words), _trigrams_ (three words), or _fourgrams_ (four words).
- **Maximum distance:** Only available in collocates mode. Maximum distance from the search term. A distance of 1 searches for directly adjacent words.
- **Position of search term:** Only available in ngram mode. Specify the position that the search term should have within the n-gram. Choose "any" to include all positions, or choose a specific position. For instance, "first" will only include n-grams where the search term is the first word.
- **Compensate for frequency**: This option determines how results are scored: you can choose whether to compensate for the overall frequency of terms in the corpus. See "scoring" below for details.
- **Language processing**: This option is not available for all corpora. If available, it selects what kind of processing should be done on the text before counting. Options are:
    - _None:_ Use the original text, without any processing. (This is selected if the dropdown does not appear.)
    - _Remove stopwords:_ Remove [stopwords](/manual/glossary#stopword).
    - _Stem and remove stopwords_: Remove stopwords and apply [stemming](https://en.wikipedia.org/wiki/Stemming) to all words.
- **Document limit:** How many results are analysed per time interval. A small limit will provide faster results, but a high limit provides more reliable data.
- **Number of n-grams:** The number of ngrams to display in the results.

## Scoring

If *compensate for frequency* is turned off, the visualisation shows the absolute number of times the ngram or collocate was observed in the search results.

This often reflects terms that are common across the entire corpus. Alternatively, you can turn on *compensate for frequency* to get terms that are unusually common in the neighbourhood of the search term, compared to their overall frequency.

If you select "Yes", the frequency of the ngram is divided by the average frequency (across the entire corpus) of the individual terms. This score is calculated as:

<math display="block" class="block">
    <mi>score</mi>
    <mo>(</mo>
    <mi>a</mi>
    <mi>b</mi>
    <mo>)</mo>
    <mo>=</mo>
    <mfrac>
        <mrow>
            <mi>freq</mi>
            <mo>(</mo>
            <mi>a</mi>
            <mi>b</mi>
            <mo>)</mo>
        </mrow>
        <mrow>
            <mi>avg</mi>
            <mo>(</mo>
            <mi>freq</mi>
            <mo>(</mo>
            <mi>a</mi>
            <mo>)</mo>
            <mo>,</mo>
            <mi>freq</mi>
            <mo>(</mo>
            <mi>b</mi>
            <mo>)</mo>
            <mo>)</mo>
        </mrow>
    </mfrac>
</math>

The frequency of the pair is counted per interval, but the background frequency of the individual terms is always based on the entire corpus.

This option can surface interesting combinations, but can also cause extreme results where collocations with rare terms are extremely high, even when the collocation is only observed a few times, so not very significant.

The "Yes (experimental)" provides a different calculation that we are currently testing. This calculates scores based on point-wise mutual information, based on the definition in [Manning & Schütze (1999)](https://nlp.stanford.edu/fsnlp/promo/colloc.pdf).

In this mode, if you visualise the ngrams or collocations of <math><mi>a</mi></math>, the score of the pair <math><mi>ab</mi></math> is calculated as

<math display="block" class="block">
    <mi>score</mi>
    <mo>(</mo>
    <mi>a</mi>
    <mi>b</mi>
    <mo>)</mo>
    <mo>=</mo>
    <msub>
        <mi>log</mi>
        <mn>2</mn>
    </msub>
    <mfrac>
        <mfrac>
            <mrow>
                <mi>freq</mi>
                <mo>(</mo>
                <mi>a</mi>
                <mi>b</mi>
                <mo>)</mo>
            </mrow>
            <mi>T</mi>
        </mfrac>
        <mrow>
            <mfrac>
                <mrow>
                    <mi>freq</mi>
                    <mo>(</mo>
                    <mi>a</mi>
                    <mo>)</mo>
                </mrow>
                <mi>T</mi>
            </mfrac>
            <mo>*</mo>
            <mfrac>
                <mrow>
                    <mi>freq</mi>
                    <mo>(</mo>
                    <mi>b</mi>
                    <mo>)</mo>
                </mrow>
                <mi>T</mi>
            </mfrac>
        </mrow>
    </mfrac>
</math>

where <math><mi>T</mi></math> is the total number of words in the corpus. As with the original formula, the frequency of the individual terms is based on the entire corpus, not the time interval.


## Visualisation

Each row of the graph shows the frequency of a single collocate or n-gram.

The line graph for each row shows how the frequency of that co-occurence varies over time. You can hover over a point to see the frequency at that point in time. (Depending on your choice in "compensate for frequency", this either an absolute or relative number.)

By default, all the line graphs use the same scale. This can mean that for the lower (less frequent) items, the development over time can be difficult to make out. You can select "fixed height for line graphs" at the bottom of the graph. If this is selected, each line graph is scaled separately to fit the row.

The bar chart on the right shows the total frequency of the n-gram. This is calculated as the sum of each of the frequencies per time period.

## Complex queries

The most straightforward way to use the neighbouring words graph is to search for a single term. The visualisation supports most complex queries, but some options are not supported.

### Multiple search terms

You can search for multiple terms, e.g. _democratic autocratic_ or _democratic + autocratic_. Documents are only counted if they match the full query - meaning they would also appear in your search results.

Within the document, we look for matches to any of the search terms. In collocates mode, this means you find words surrounding "democratic" or "autocratic". If we see 50 occurrences of "democratic state" and 50 occurrences of "autocratic state", then "state" is counted 100 times as a collocate.

In n-grams mode, you find n-grams containing either word. Here, "democratic state" and "autocratic state" would be counted as *separate* ngrams.

If you use the "compensate for frequency" option, the formula will use the background frequency of the collocate (e.g. "state") and the background frequency of the *query* (e.g. "autocratic democratic"), i.e. the number of matches for the query across the entire corpus.

### Phrase search

You can search for phrases, e.g. _"social democrat"_. In this case, distances are always counted from the phrase as a whole, as if it's a single term. So selecting bigrams (in ngrams mode) or a distance of 1 (in collocates mode) would find a phrase like "social democrat party".

### Negative search terms

Negative search terms (e.g. _"-republic"_) can be used to exclude documents containing search terms. Depending on how you build your query, your results might still include these terms, for example with _"democratic -republic"_. This will find documents that contain "democratic" and/or do *not* contain "republic". (Use _"democratic + -republic"_ if you want a hard exclude.)

Negative terms like this will affect what documents are returned and how they are ranked, but they are not considered query terms for the purpose of identifying neighbouring words. So in the example query, the results would include ngrams/collocates for "democratic" but not for "republic".

### Wildcard and fuzzy search

You can use wildcard of fuzzy search terms, like _democrat*_ or _democracy~2_. This is handled like searching for multiple search terms. (As if you listed all matching words in a query like "democrat democratic democrats democratical democratically".)

### Proximity search

Proximity search is not supported in this visualisation.
