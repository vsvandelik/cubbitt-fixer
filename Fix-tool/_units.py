units = {
    'km/h': {
        'cs': ['km/h', 'kph', 'kilometr za hodinu', 'kilometry za hodinu', 'kilometrů za hodinu', 'kilometrů v hodině',
               'kilometr v hodině', 'kilometry v hodině'],
        'en': ['km/h', 'kph', 'kilometers per hour', 'kilometer per hour', 'kilometres per hour', 'kilometres an hour',
               'kilometers an hour', 'kilometer-an-hour']},
    'm/s': {
        'cs': ['m/s', 'mps', 'metr za sekundu', 'metry za sekundu', 'metrů za sekundu', 'metru za sekundu'],
        'en': ['m/s', 'mps', 'meters per second', 'meter per second']},
    'm2': {
        'cs': ['metr čtvereční', 'metru čtverečního', 'metry čtvereční', 'metrů čtverečních'],
        'en': ['square meter', 'square meters', 'square metre', 'square metres', 'square-metre', 'square-meter']},
    'km2': {
        'cs': ['kilometr čtvereční', 'kilometru čtverečního', 'kilometry čtvereční', 'kilometrů čtverečních'],
        'en': ['square kilometer', 'square kilometers', 'square kilometre', 'square kilometres', 'square-kilometre', 'square-kilometer']},
    'm3': {
        'cs': ['metr krychlový', 'metru krychlového', 'metry krychlové', 'metrů krychlových'],
        'en': ['cubic meter', 'cubic meters', 'cubic metre', 'cubic metres']},
    'km': {
        'cs': ['km', 'kilometr', 'kilometry', 'kilometrů', 'kilometru'],
        'en': ['km', 'kilometers', 'kilometer', 'kilometre', 'kilometres']},
    'm': {
        'cs': ['m', 'metr', 'metry', 'metrů', 'metru'],
        'en': ['m', 'meters', 'meter', 'metre', 'metres']},
    'dm': {
        'cs': ['dm', 'decimetr', 'decimetry', 'decimetrů'],
        'en': ['dm', 'decimeters', 'decimeter', 'metre', 'metres']},
    'cm': {
        'cs': ['cm', 'centimetr', 'centimetry', 'centimetrů'],
        'en': ['cm', 'centimeters', 'centimeter', 'centimetre', 'centimetre', 'centimetres']},
    'mm': {
        'cs': ['mm', 'milimetr', 'milimetry', 'milimetrů'],
        'en': ['mm', 'millimeters', 'millimeter', 'milimetre', 'millimetre', 'milimetres', 'millimetres']},
    'g': {
        'cs': ['g', 'gram', 'gramy', 'gramů'],
        'en': ['g', 'grams', 'gram']},
    'kg': {
        'cs': ['kg', 'kilogram', 'kilogramy', 'kilogramů', 'kila', 'kilo', 'kil'],
        'en': ['kg', 'kilograms', 'kilogram', 'kilos']},
}

units_by_language = {}
for _, val in units.items():
    for lang, u in val.items():
        if lang not in units_by_language.keys():
            units_by_language[lang] = []

        units_by_language[lang] += u

units_strings = {lang: '|'.join(units_list) for lang, units_list in units_by_language.items()}

units_categories = {}
for category, val in units.items():
    for lang, lang_list in val.items():
        if lang not in units_categories.keys():
            units_categories[lang] = {}

        for unit in lang_list:
            units_categories[lang][unit] = category
"""
lenght_units = {
    'si': (
        ['m', 'mm', 'cm', 'dm', 'km'],
        [1, 0.001, 0.01, 0.1, 1000]
    ),
    'imperial': (
        ['in', 'ft', 'yd', 'miles'],
        [1, 12, 36, 63360]
    ),
    'si-imp': 39.37007874,
    'imp-si': 0.0254
}


def convert_to_specific(number, rest, source, rate, target):
    idx = source[0].index(rest)
    number_in_base = number * source[1][idx]

    base_in_second = number_in_base * rate
    for i in range(len(target[0]) - 1, -1, -1):
        calc = base_in_second / target[1][i]
        if calc >= 1:
            return calc, target[0][i]

    return base_in_second, target[0][0]


def convert_unit(number: int, rest: str):
    if rest in lenght_units['si'][0]:
        number, rest = convert_to_specific(number, rest, lenght_units['si'], lenght_units['si-imp'],
                                           lenght_units['imperial'])
    elif rest in lenght_units['imperial'][0]:
        number, rest = convert_to_specific(number, rest, lenght_units['imperial'], lenght_units['imp-si'],
                                           lenght_units['si'])

    return number, rest
"""
