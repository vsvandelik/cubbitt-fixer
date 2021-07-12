from fixer.sentences_splitter import SentencesSplitter, FixerConfigurator


def test_split_text_to_sentences():
    input_sentences = "Koupil si dům. Velmi drahý dům. Žil v něm celý život.\nAž do smrti.\n\nOna měla také dům. Žila v něm také velmi dlouho.\nAle než až do smrti."
    correct_output = [
        ["Koupil si dům.", "Velmi drahý dům.", "Žil v něm celý život.", "Až do smrti."],
        ["Ona měla také dům.", "Žila v něm také velmi dlouho.", "Ale než až do smrti."]
    ]

    configuration = FixerConfigurator()
    configuration.load_from_dict(get_default_configuration())

    assert SentencesSplitter.split_text_to_sentences(input_sentences, configuration.source_lang, configuration) == correct_output


def get_default_configuration():
    return {
        'source_lang': 'cs',
        'target_lang': 'en',
        'aligner': 'fast_align',
        'lemmatizator': 'udpipe_online',
        'names_tagger': 'nametag',
        'mode': 'fixing',
        'base_tolerance': 0.1,
        'approximately_tolerance': 0,
        'target_units': ['imperial', 'USD', 'F'],
        'exchange_rates': 'cnb',
        'tools': ['separators', 'units']
    }
