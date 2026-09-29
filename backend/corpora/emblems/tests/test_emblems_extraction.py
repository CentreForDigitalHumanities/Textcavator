import os
from corpora.emblems.emblems import EmblemsIndexReader, Emblems

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

def test_emblems_index_reader():
    reader = EmblemsIndexReader(DATA_DIR)
    docs = list(reader.documents())
    assert len(docs) == 1


def test_emblems_data_reader(monkeypatch):
    monkeypatch.setattr(Emblems, 'data_directory', DATA_DIR)
    reader = Emblems()
    docs = list(reader.documents())
    assert len(docs) == 4

    first = docs[0]
    assert first['title'] == 'Quaeris quid sit Amor'
    assert first['author'] == 'Heinsius, Daniël'
    assert first['editor'] == 'De Gheyn, Jacques'
    assert first['id'] == 'he1601front1'
    assert first['pub_year'] == 1601
    assert first['pub_place'] == 'Amsterdam'
    assert first['content'] == '''Quris quid sit Amor, quid amare, cupidinis et quid
Castra sequi? chartam hanc inspice, doctus eris.
Hc tibi delicias hortumque ostendit Amorum:
Inspice; sculptori est ingeniosa manus.'''
    assert first['body_langs'] == ['lat']
    assert first['translation_nl'] == ['''Wat liefde is vraag je, en wat het is te beminnen en het kamp der Begeerte te volgen? Kijk goed naar deze kaart, je zult dan een expert zijn. Deze toont je de genoegens en de tuin der Eroten. Ja, kijk eens goed. De graveur heeft een getalenteerde hand.''']
    assert first['translation_en'] == ['''What love is do you ask, what it is to love and what it is to Follow desires camp? Have a look at this map, you will become an expert. This shows you the delights and the garden of the Cupids. Have a look. The engraver has a talented hand.''']

    e23 = docs[-2]
    assert e23['content'] == '''23. Ser detrectat onus qui subijt.

Hier voortijdts als ick placht Van minnen thooren spreken,
En van dat bitter soet end Van die loose treken,
My docht het was zoo moy, men coster uyt end in,
Dat heeft my eerst ghebroght het minnen in de sin.
Ick sach het jock wel aen, maer tdocht my licht te wesen,
Ghevlochten end ghebreyt, Van rooskens tsaem ghelesen
Uit VENUS gouden tuyn, my docht ick was een man,
Maer als ick weet wat tis, en can ick daer niet van.

[H. Grotius]
Frustr tento oneri me jam subducere: frustra
Jam juga detrectant, qu subiere boves'''
