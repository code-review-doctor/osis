from decimal import Decimal


def get_chiffres_significatifs(nombre_decimal: Decimal) -> str:
    if nombre_decimal:
        str_volume = str(nombre_decimal)
        return str_volume.rstrip('0').rstrip('.') if '.' in str_volume else str_volume
    return ''
