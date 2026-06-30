## Mapping

Stemmed/cleaned field now get the analysed text AND use the analyser, that makes no sense.

For English, it's a safe assumption that you can use the main field for tokenisation, and then analyse the same token with all analysers. So the assumption is that the token spans are the same (except the clean/stemmed analyser will omit some tokens). So maybe just use a single token field with multifield analysers?

Removed the keyword field option, but in hindsight, that would be necessary for some analysis. If you want to find which words in the corpus match a fuzzy query, or have the same stemmed match, you need to do a terms aggregation.

So maybe this structure:
- keyword field with the token
- up to 3 multifields for standard/clean/stemmed analysis.

Term vectors in the token field do not need to store positions/offsets, but they are probably copying that setting from the original corpus.

## Threshold

Index size is large, currently around 2-3x the original corpus. Perhaps we could add a minimum frequency threshold. That would save a lot of space.

For most analysis, it would be fine to leave out all singletons from consideration, so that would be an option.

But if a word has fewer than, say, 20 occurrences, counting it in the original corpus is very fast anyway, so you could also use that as a threshold. Then you only use this to optimise high-frequency terms, and low-frequency terms are analysed on the original index.

## Document IDs

The ID of the original document should be included, e.g. as `:doc_id` field. Tag filters use the id, so filters on `_id` should be converted to use `:doc_id`.

