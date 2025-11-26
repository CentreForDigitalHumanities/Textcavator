# Word models

This module contains code pertaining to word models.

Textcavator does not train models; the code used for training is found in the [WordModels repository](https://github.com/UUDigitalHumanitieslab/WordModels) (private).

The code here is used to retrieve word models belonging to a corpus and perform analysis for visualisations.

## Documentation

To display documentation about word models, save "documentation.md" file into a "wm" directory within the corpus path.

## Testing

The module comes with a mock corpus that includes trained word models.

The models are trained on the 5 most frequently downloaded books from the [gutenberg project](https://www.gutenberg.org/). At the time of writing, these are Pride and Prejudice, Alice's Adventures in Wonderland, The Adventures of Sherlock Holmes, and Moby Dick. Some common sense knowledge about the material may be used for test cases.

The following time frames are used:

- 1810-1839: Pride and Prejudice, Frankenstein
- 1840:1869: Alice in Wonderland, Moby Dick
- 1870-1899: Sherlock Holmes

The models for each time frame, as well as the complete model, are trained with a maximum vocabulary size of 200 words and 20 dimensions. The models were saved as gensim KeyedVectors.

### Training data

The training data is not included in this repository, since we do not need to test training here. If you need to reproduce the dataset, you can download the books as txt files. Remove gutenberg's information about copyright from each file and split each file into paragraphs (split by `\n\n`), filtering out paragraphs under 50 characters. Make sure each file is saved as `{year}-{filename}.txt`, e.g. `1813-austen-1.txt` so it is recognised by the wordmodels script.
