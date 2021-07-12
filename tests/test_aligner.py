from fixer._aligner import FastAlignAligner, OrderAligner
from fixer._languages import Languages


def test_get_external_alignment():
    src_text = "In 2016, 665 km of regional roads were in a state of emergency, with a further 313 kilometres identified as unsatisfactory."
    trg_text = "V roce 2016 bylo 665 km krajských silnic v havarijním stavu, dalších 313 kilometrů bylo označeno jako nevyhovující."

    alignment = FastAlignAligner.get_alignment(src_text, trg_text, Languages.EN, Languages.CS)

    expected_result = [('In', 'V'), ('2016', '2016'), ('665', '665'), ('km', 'km'), ('regional', 'krajských'), ('roads', 'silnic'), ('were', 'bylo'), ('in', 'v'), ('a', 'havarijním'), ('state', 'stavu'), ('of', 'stavu'), ('emergency', 'havarijním'), (',', ','), ('further', 'dalších'), ('313', '313'), ('kilometres', 'kilometrů'), ('identified', 'označeno'), ('as', 'jako'),
                       ('unsatisfactory', 'nevyhovující'), ('.', '.')]

    assert alignment == expected_result


def test_get_external_alignment_empty_sentences():
    alignment = FastAlignAligner.get_alignment("", "", Languages.EN, Languages.CS)

    assert alignment == []


def test_get_order_alignment():
    src_text = "In 2016, 665 km of regional roads were in a state of emergency, with a further 313 kilometres identified as unsatisfactory."
    trg_text = "V roce 2016 bylo 665 km krajských silnic v havarijním stavu, dalších 313 kilometrů bylo označeno jako nevyhovující."

    alignment = OrderAligner.get_alignment(src_text, trg_text, Languages.EN, Languages.CS)

    expected_result = [('2016', '2016'), ('665', '665'), ('km', 'km'), ('313', '313'), ('kilometres', 'kilometrů')]

    assert alignment == expected_result


def test_get_order_alignment_names():
    src_text = "Koupil Petrovi, Ivanovi a Davidovi dům."
    trg_text = "He bought Peter, Ivan and David a house."

    alignment = OrderAligner.get_alignment(src_text, trg_text, Languages.EN, Languages.CS)

    expected_result = [('Petrovi', 'Peter'), ('Ivanovi', 'Ivan'), ('Davidovi', 'David')]

    assert alignment == expected_result


def test_get_order_alignment_empty_sentences():
    alignment = OrderAligner.get_alignment("", "", Languages.EN, Languages.CS)

    assert alignment == []
