FROM ghcr.io/centrefordigitalhumanities/ianalyzer-backend:latest as ianalyzer

RUN pip install --upgrade pip
# make a directory in the container
WORKDIR /backend
# copy requirements from the host system to the directory in the container
COPY requirements.txt /backend/
# run pip install on container
RUN pip install -r requirements.txt

FROM ianalyzer AS indexing
WORKDIR /backend
COPY manage.py .
COPY api/ api/
COPY ianalyzer/ ianalyzer/
COPY addcorpus/ addcorpus/
COPY corpora/ corpora/
COPY download/ download/
COPY es/ es/
COPY indexing/ indexing/
COPY media/ media/
COPY tag/ tag/
COPY users/ users/
COPY visualization/ visualization/
COPY wordmodels/ wordmodels/
COPY about/ about/
RUN mkdir .log
