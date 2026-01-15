# Textcavator

> [!NOTE]
> We are currently in the process of renaming this application from I-analyzer to Textcavator.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8064133.svg)](https://doi.org/10.5281/zenodo.8064133)
[![Backend unit tests](https://github.com/CentreForDigitalHumanities/Textcavator/actions/workflows/backend-test.yml/badge.svg)](https://github.com/CentreForDigitalHumanities/Textcavator/actions/workflows/backend-test.yml)
[![Frontend unit tests](https://github.com/CentreForDigitalHumanities/Textcavator/actions/workflows/frontend-test.yml/badge.svg)](https://github.com/CentreForDigitalHumanities/Textcavator/actions/workflows/frontend-test.yml)

> "The great text mining tool that obviates all others."
> — Julian Gonggrijp

Textcavator is a web application for exploring corpora (large collections of texts). You can use Textcavator to find relevant documents, or to make visualisations to understand broader trends in the corpus. The interface is designed to be accessible for users of all skill levels.

Textcavator is primarily intended for academic research and higher education. We focus on data that is relevant for the humanities, but we are open to datasets that are relevant for other fields.

## Contents

This repository contains the source code for the Textcavator web application, which consists of a Django backend and Angular frontend.

For corpora included in Textcavator, the backend includes a definition file that specifies how to read the source files, and how this data should be structured and presented in Textcavator. This repository does _not_ include the source data itself, beyond a few sample files for testing.

## Usage

If you are interested in using Textcavator, the most straightforward way to get started is to visit [textcavator.hum.uu.nl](https://textcavator.hum.uu.nl/). This server is maintained by the Research Software Lab and contains corpora focused on a variety of fields. We also maintain more specialised collections at [PEACE portal](https://peace.sites.uu.nl/epigraphy/search/) and [People & Parliament](https://people-and-parliament.hum.uu.nl/).

Textcavator does not have an "upload data" option (yet!). If you are interested in using Textcavator as a way to publish your dataset, or to make it easier to search and analyse, you can go about this two ways:

- Contact us (see below for details) about hosting your dataset on one of our existing servers, or hosting a new server for your project.
- Self-host Textcavator. This would allow you to maintain full control over the data and who can access it. Textcavator is open source software, so you are free to host it yourself, either as-is or with your own modifications. However, feel free to contact us with any questions or issues.

## Development

The [documentation directory](./documentation/) contains documentation for developers. This includes [installation instructions](./documentation/First-time-setup.md) to set up an Textcavator server.

## Licence

The source code of Textcavator is shared under an MIT licence. See [LICENSE](./LICENSE) for the full licence statement.

### Images

This licence does *not* cover the images used for corpora, which are licensed individually. These images are located in the [corpora directory](/backend/corpora/), in the "images" folder for each corpus.

Each image is accompanied by a `*.license` file that provides information on licensing for that image. If you wish to reuse or distribute this repository including these images, you will have to ensure that you comply with the license terms of the image as well.

Some images currently lack a licence file. We are working on providing clear copyright information for all images; until then, assume that these images are protected under copyright.

## Citation

If you wish to cite this repository, please use the metadata provided in our [CITATION.cff file](./CITATION.cff).

If you wish to cite material that you accessed through Textcavator, or you are not sure if you should also be citing this repository, please refer to the [citation instructions in the user manual](./frontend/src/assets/manual/en-GB/citation.md).

## Contact

For questions, small feature suggestions, and bug reports, feel free to [create an issue](https://github.com/CentreForDigitalHumanities/Textcavator/issues/new/choose). If you don't have a Github account, you can also [contact the Centre for Digital Humanities](https://cdh.uu.nl/contact/).

If you want to add a new corpus to Textcavator, or have an idea for a project, please [contact the Centre for Digital Humanities](https://cdh.uu.nl/contact/) rather than making an issue, so we can discuss the possibilities with you.

