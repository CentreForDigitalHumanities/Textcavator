from corpora.emblems.emblems import EmblemsIndexReader, DATA_DIR, EmblemsDataReader

def test_emblems_index_reader():
    reader = EmblemsIndexReader(DATA_DIR)
    docs = list(reader.documents())
    assert len(docs)


def test_emblems_data_reader():
    reader = EmblemsDataReader()
    docs = list(reader.documents())
    assert len(docs)
