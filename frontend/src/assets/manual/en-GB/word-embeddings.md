[Word embeddings](https://en.wikipedia.org/wiki/Word_embedding) are an abstract way of representing words as a sequence of numbers. You can think of this like drafting a map and giving each word in a corpus a set of coordinates, so that similar words are placed close to one another, and very dissimilar words are spaced far apart.

This page provides a general explanation of what word embeddings are and how they can be used in research. The pages [related words](/manual/relatedwords), [compare similarity](/manual/comparesimilarity), and [network of nearest neighbours](/manual/neighbour-network) describe how these models are used in Textcavator.

## What is similarity?

To see which words a similar, a machine learning model scans a corpus: words are similar if they are used in similar contexts. For example, *cow* and *calf* may be similar because they are both used around the same words like *barn*, *grass*, and *milk*, whereas *cow* and *cat* are less similar, because the contexts in which cows and cats are mentioned have less overlap.

Words that are very similar (i.e. that occur in the same contexts) often have related meanings. You can think of synonyms (like *big* and *large*), but also antonyms (like *light* and *dark*). Similarity can also reflect other relations (like *cow* and *calf*; a calf is a type of cow), or simply words that are associated with the same topic (like *cow* and *barn*).

## How are word embeddings created?

A machine learning model will determine the representation of each word in the model, based on the text of the corpus. Together, these representations form a model of the words in the corpus, and of how those words are used in the text.

This model counts which words tend to occur together in the corpus. (For example, you can count pairs of words that occur at most 4 words apart.) From these counts, the model creates a "map" that tries to capture similarities between words.

You can think of this process like trying to draw up a seating arrangement for a large family at a wedding. You want to make sure that everyone sits next to people they get along with. In this way, your seating arrangement becomes a model of the family relationships. An observant guest could then use the seating arrangement to learn something about those relationships: people who sit next to each other, apparently get along.

There are different algorithms to train word embeddings. What algorithm works, and how exactly this should be configured, can depend on the corpus. (For example, this can depend on the amount of text, or the lexical variety in the text.) If a corpus on Textcavator has word embeddings available, the information page will describe what algorithm was used.

The result of this algorithm is a set of coordinates for each word. This is different from a geographical map, which is two-dimensional and thus represents each point with two numbers. With word embeddings, words are represented by much longer sequences of numbers, for example 100. This allows them to capture much more complex information than if you tried to arrange all words on a 2D map.

It also means that we cannot easily visualise this map containing all the words. The exact coordinates of a word are to abstract for us to interpret directly. But like with the seating arrangement, if we want to learn something about a word, we can look at what other words are next to it.

## How can you use word embeddings?

While word embeddings are very abstract representations, they can be a very useful tool. You can evaluate and expand your search terms by exploring similar terms in the model. We discuss a few ways in which you can employ word embeddings in your research process.

### Finding related search terms

When you start your research on a corpus, you often have a few keywords that you are interested in. For example, say that you want to search for *democracy*. A possible pitfall is that an author or speaker may talk about issues of democracy and representation, but not use this specific word. Since those documents will not match your search, you may never realise what you are missing.

To help you out, you can use the word embeddings of a corpus to find terms related to your initial search term, *democracy*. When you explore the most similar words, you may find other terms such as *representation*, *democratic* or *parliament*. Perhaps you also find words that you would not have thought of, such as *liberalism*, which was very closely associated with the concept of democracy in the 19th century, but has a more distinct meaning today.

You may also find terms that are not synonymous with democracy, but are closely related because they are often contrasted with democracy, such as *dictatorship*. So if you are researching how Dutch authors or orators discuss democracy and representation, it may be useful to extend your search to "dictatorship".

So by looking at the related words, you can identify other search terms that may be interesting for your research.

### Discovering other senses of a word

When you have selected a search term for your research, it is possible that this term also has other meanings that you did not think of. For example, there might be a historic use of the term that you were not aware of.

By exploring the most similar words, you can identify words that are related to other uses of your search term. For example, when we search for *democracy*, we may find terms that are very closely related to "social democracy", such as *socialism*, *labour*, and *marxism*. If an author mentions *social democracy*, they are discussing a political movement, but not necessarily talking about democracy as a concept.

It's good to be aware of phrases or other meanings that might interfere with your results. If these other meanings are very common (perhaps more common than what you were interested in), you can try to exclude them when you search through the corpus.

### Showing changes over time

Word embeddings on Textcavator are always *diachronic*: rather than creating a single model of the whole corpus, we train separate models for different time intervals. So when you look at the similarity scores between words, you can compare how that similarity changes over time.

Changes in similarity can reflect changes in how words are used over time. Words can be used in new contexts and take on new meanings. (Or conversely, some usage may fall out of use.) Because such changes tend to cover long time periods, it can be difficult to reliably detect such changes if you are only relying on close reading. After all, you can only read a limited amount of text.

Therefore, it can be useful to note trends that are captured in the model and compare them with your own observations. For example, as mentioned above, your corpus may show that the the terms *democracy* and *liberalism* show a very high similarity in the 19th century and a lower similarity in the late 20th century.

This may be an interesting observation in itself, if you are investigating how concepts like democracy and liberalism evolve over time. It can confirm or challenge what you observed in reading documents from these periods. Or you could start by exploring these trends, and use them as a jumping-off point for closer inspection.

Observing these changes can also help you to avoid blind spots in your research. When dealing with historic texts, it is important to be aware of how the meaning of a word can change over time. When you search for a term that takes on a completely different meaning, you will get very different results from different time periods.
