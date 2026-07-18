"""
Converts an integer into a human readable string. Intended to be used for digital sizes
"""

SI_UNITS = ("", "K", "M", "G", "T", "P", "E", "Z", "Y")

def human_readable(value: int, metric: bool = False) -> str:
    """
    Converts an integer into a human readable string

    Args:
        value: Integer to convert
        metric: If true there are 1000 bytes in a KB, if false there are 1024.
    """

    if metric:
        base = 1000
    else:
        base = 1024

    end = len(SI_UNITS) - 1

    # Check all but last
    for i in range(end):
        # Check if value fits in next largest unit
        if base**(i + 1) < value:
            continue

        unit = SI_UNITS[i]
        exp = i
        break
    else:
        # Just use the biggest we have
        unit = SI_UNITS[end]
        exp = end

    # Format and return
    if unit and not metric:
        unit = f"{unit}i"
    return f"{round(value / (base**exp), 2):,g} {unit}B"
