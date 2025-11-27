import os

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from addcorpus.models import CorpusDataFile

here = os.path.dirname(os.path.abspath(__file__))


def test_csv_upload(admin_user, admin_client, json_mock_corpus):
    # clear corpus data file info
    CorpusDataFile.objects.all().delete()

    fp = os.path.join(here, 'files', 'example.csv')

    json_mock_corpus.owner = admin_user
    json_mock_corpus.save()

    # Test file upload
    with open(fp, 'rb') as f:
        data = {'corpus': json_mock_corpus.pk, 'is_sample': True, 'file': f}
        res = admin_client.post('/api/corpus/datafiles/', data)
    assert res.status_code == HTTP_201_CREATED
    file_pk = res.data.get('id')

    info_res = admin_client.get(f'/api/corpus/datafiles/{file_pk}/')

    # Check file info
    assert info_res.data.get('csv_info') == {
        'fields': [
            {'name': 'character', 'type': 'text_metadata'},
            {'name': 'line', 'type': 'text_metadata'},
            {'name': 'date-column', 'type': 'date'},
            {'name': 'FLOAT COLUMN', 'type': 'float'},
            {'name': 'int_column', 'type': 'integer'},
            {'name': 'bool column', 'type': 'boolean'}
        ],
        'n_rows': 10,
        'delimiter': ','
    }
