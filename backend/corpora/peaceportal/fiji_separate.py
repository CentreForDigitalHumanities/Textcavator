from corpora.peaceportal.peaceportal import PeacePortal


class FIJISEPARATE(PeacePortal):

    es_index = 'peace-fiji'

    # all fields listed here will be ignored if they are
    # in the PeacePortal base class definition. Ideal for excluding
    # filters that are irrelevant
    redundant_fields = ('source_database', 'region')

    def __init__(self):
        super().__init__()
        self.fields = [
            f for f in self.fields if f.name not in self.redundant_fields
        ]
