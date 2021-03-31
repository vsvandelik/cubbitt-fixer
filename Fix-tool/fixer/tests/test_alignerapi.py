from fixer._aligner import *


def test_get_external_alignment():
    src_text = "In 2016, 665 km of regional roads were in a state of emergency, with a further 313 kilometres identified as unsatisfactory."
    trg_text = "V roce 2016 bylo 665 km krajských silnic v havarijním stavu, dalších 313 kilometrů bylo označeno jako nevyhovující."

    alignment = ExternalAligner.get_alignment(src_text, trg_text)

    expected_result = [('In', 'V'), ('2016', '2016'), ('665', '665'), ('km', 'km'), ('regional', 'krajských'), ('roads', 'silnic'), ('were', 'bylo'), ('in', 'v'), ('a', 'havarijním'), ('state', 'stavu'), ('of', 'stavu'), ('emergency', 'havarijním'), (',', ','), ('further', 'dalších'), ('313', '313'), ('kilometres', 'kilometrů'), ('identified', 'označeno'), ('as', 'jako'),
                       ('unsatisfactory', 'nevyhovující'), ('.', '.')]

    assert alignment == expected_result


def test_get_external_alignment_empty_sentences():
    alignment = ExternalAligner.get_alignment("", "")

    assert alignment == []


def test_get_order_alignment():
    src_text = "In 2016, 665 km of regional roads were in a state of emergency, with a further 313 kilometres identified as unsatisfactory."
    trg_text = "V roce 2016 bylo 665 km krajských silnic v havarijním stavu, dalších 313 kilometrů bylo označeno jako nevyhovující."

    alignment = OrderAligner.get_alignment(src_text, trg_text)

    expected_result = [('2016', '2016'), ('665', '665'), ('km', 'km'), ('313', '313'), ('kilometres', 'kilometrů')]

    assert alignment == expected_result


def test_get_order_alignment_empty_sentences():
    alignment = ExternalAligner.get_alignment("", "")

    assert alignment == []
