units = {
    'km/h': ['kph','kilometers per hour'],
    'm/s': ['mps','meters per second'],
    'km': ['kilometers', 'kilometer'],
    'm': ['meters', 'meter'],
    'dm': ['decimeters', 'decimeter'],
    'cm': ['centimeters', 'centimeter', 'centimetre'],
    'mm': ['millimeters', 'millimeter'],
    'g': ['grams', 'gram'],
    'kg': ['kilograms', 'kilogram', 'kilos'],
    #'ms': ['milliseconds', 'millisecond'],
    #'N': ['newtons', 'newton'],
    #'kN': ['kilonewton'],
    #'A': ['amperes', 'ampere'],
    #'K': ['kelvins', 'kelvin'],
}

lenght_units = {
        'si': (
            ['m', 'mm', 'cm', 'dm', 'km'],
            [1, 0.001, 0.01, 0.1, 1000]
        ),
        'imperial': (
            ['in','ft','yd','miles'],
            [1, 12, 36, 63360]
        ),
        'si-imp': 39.37007874,
        'imp-si': 0.0254
    }

unitsString = '|'.join(units.keys())

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
        number, rest = convert_to_specific(number, rest, lenght_units['si'], lenght_units['si-imp'],lenght_units['imperial'])
    elif rest in lenght_units['imperial'][0]:
        number, rest = convert_to_specific(number, rest, lenght_units['imperial'], lenght_units['imp-si'],lenght_units['si'])
    
    return number, rest