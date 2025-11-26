import pytest

from addcorpus.models import Corpus
from addcorpus.serializers import CorpusSerializer

class MockRequest:
    def __init__(self, user):
        self.user = user

@pytest.mark.parametrize('editable', [True, False])
def test_corpus_serializer_editable(json_mock_corpus, auth_user, editable):
    instance = Corpus.objects.get(name=json_mock_corpus)

    if editable:
        auth_user.profile.can_edit_corpora = True
        auth_user.profile.save()

        instance.owner = auth_user
        instance.save()

    serializer = CorpusSerializer(instance, context={'request': MockRequest(auth_user)})
    assert serializer.data['editable'] is editable



