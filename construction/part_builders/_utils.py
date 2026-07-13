import re
from math import gcd


def inches_to_feet_inches_str(inches, denom=64):
    total_units = round(inches * denom)

    total_inches, frac_num = divmod(total_units, denom)
    feet, whole_inches = divmod(total_inches, 12)

    if frac_num:
        g = gcd(frac_num, denom)
        frac = f'{frac_num // g}/{denom // g}'
    else:
        frac = ''

    if whole_inches and frac:
        inch_part = f'{whole_inches} {frac}in'
    elif whole_inches:
        inch_part = f'{whole_inches}in'
    elif frac:
        inch_part = f'{frac}in'
    else:
        inch_part = ''

    if feet and inch_part:
        return f'{feet}ft {inch_part}'
    if feet:
        return f'{feet}ft'
    return inch_part or '0in'


def safe_name(name: str):
    return '_' + re.sub(r'[^A-Za-z0-9_]+', '_', name)

def find_obj(doc, name, label=None):
    obj = doc.getObject(name)
    if obj:
        return obj
    for o in doc.Objects:
        if o.Name == name or (label and o.Label == label):
            return o
    return None
