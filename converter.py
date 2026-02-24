"""
Metric <-> Imperial Unit Converter
Supports: length, weight/mass, volume, temperature, area, speed
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class Conversion:
    from_unit: str
    to_unit: str
    factor: float | None  # None means use a custom function
    fn: Callable[[float], float] | None = None
    inverse_fn: Callable[[float], float] | None = None


# ---------------------------------------------------------------------------
# Conversion definitions (metric → imperial; reversed automatically below)
# ---------------------------------------------------------------------------

CONVERSIONS: dict[str, dict[str, dict[str, float | Callable]]] = {
    # category -> from_unit -> to_unit -> factor
    "length": {
        "mm":  {"in": 0.0393701, "ft": 0.00328084, "yd": 0.00109361, "mi": 6.2137e-7},
        "cm":  {"in": 0.393701,  "ft": 0.0328084,  "yd": 0.0109361,  "mi": 6.2137e-6},
        "m":   {"in": 39.3701,   "ft": 3.28084,    "yd": 1.09361,    "mi": 0.000621371},
        "km":  {"in": 39370.1,   "ft": 3280.84,    "yd": 1093.61,    "mi": 0.621371},
    },
    "weight": {
        "mg":  {"oz": 3.5274e-5, "lb": 2.2046e-6, "st": 1.5747e-7, "ton_us": 1.1023e-9},
        "g":   {"oz": 0.035274,  "lb": 0.0022046,  "st": 0.000157473, "ton_us": 1.1023e-6},
        "kg":  {"oz": 35.274,    "lb": 2.20462,    "st": 0.157473,  "ton_us": 0.00110231},
        "t":   {"oz": 35274.0,   "lb": 2204.62,    "st": 157.473,   "ton_us": 1.10231},
    },
    "volume": {
        "ml":  {"fl_oz": 0.033814,  "pt": 0.00211338, "qt": 0.00105669, "gal": 0.000264172, "cup": 0.00422675},
        "l":   {"fl_oz": 33.814,    "pt": 2.11338,    "qt": 1.05669,    "gal": 0.264172,    "cup": 4.22675},
        "m3":  {"fl_oz": 33814.0,   "pt": 2113.38,    "qt": 1056.69,    "gal": 264.172,     "cup": 4226.75},
    },
    "area": {
        "mm2": {"in2": 0.00155,     "ft2": 1.076e-5,  "yd2": 1.196e-6,  "ac": 2.471e-10, "mi2": 3.861e-13},
        "cm2": {"in2": 0.155,       "ft2": 0.00107639, "yd2": 0.000119599, "ac": 2.471e-8, "mi2": 3.861e-11},
        "m2":  {"in2": 1550.0,      "ft2": 10.7639,   "yd2": 1.19599,   "ac": 0.000247105, "mi2": 3.861e-7},
        "km2": {"in2": 1.55e9,      "ft2": 1.076e7,   "yd2": 1.196e6,   "ac": 247.105,   "mi2": 0.386102},
        "ha":  {"in2": 1.55e7,      "ft2": 107639.0,  "yd2": 11959.9,   "ac": 2.47105,   "mi2": 0.00386102},
    },
    "speed": {
        "m/s":  {"ft/s": 3.28084, "mph": 2.23694, "kn": 1.94384},
        "km/h": {"ft/s": 0.911344, "mph": 0.621371, "kn": 0.539957},
    },
}

# Temperature uses custom functions
TEMPERATURE_CONVERSIONS = {
    ("C", "F"):  (lambda c: c * 9 / 5 + 32,        "°C → °F"),
    ("F", "C"):  (lambda f: (f - 32) * 5 / 9,       "°F → °C"),
    ("C", "K"):  (lambda c: c + 273.15,              "°C → K"),
    ("K", "C"):  (lambda k: k - 273.15,              "K → °C"),
    ("F", "K"):  (lambda f: (f - 32) * 5 / 9 + 273.15, "°F → K"),
    ("K", "F"):  (lambda k: (k - 273.15) * 9 / 5 + 32, "K → °F"),
}

# Unit aliases (lowercase user input → canonical key)
ALIASES: dict[str, str] = {
    # length
    "millimeter": "mm", "millimeters": "mm", "millimetre": "mm", "millimetres": "mm",
    "centimeter": "cm", "centimeters": "cm", "centimetre": "cm", "centimetres": "cm",
    "meter": "m", "meters": "m", "metre": "m", "metres": "m",
    "kilometer": "km", "kilometers": "km", "kilometre": "km", "kilometres": "km",
    "inch": "in", "inches": "in", '"': "in",
    "foot": "ft", "feet": "ft", "'": "ft",
    "yard": "yd", "yards": "yd",
    "mile": "mi", "miles": "mi",
    # weight
    "milligram": "mg", "milligrams": "mg",
    "gram": "g", "grams": "g",
    "kilogram": "kg", "kilograms": "kg",
    "tonne": "t", "tonnes": "t", "metric ton": "t", "metric tons": "t",
    "ounce": "oz", "ounces": "oz",
    "pound": "lb", "pounds": "lb", "lbs": "lb",
    "stone": "st",
    "short ton": "ton_us", "us ton": "ton_us",
    # volume
    "milliliter": "ml", "milliliters": "ml", "millilitre": "ml", "millilitres": "ml",
    "liter": "l", "liters": "l", "litre": "l", "litres": "l",
    "cubic meter": "m3", "cubic meters": "m3", "cubic metre": "m3",
    "fluid ounce": "fl_oz", "fluid ounces": "fl_oz",
    "pint": "pt", "pints": "pt",
    "quart": "qt", "quarts": "qt",
    "gallon": "gal", "gallons": "gal",
    "cup": "cup", "cups": "cup",
    # area
    "square millimeter": "mm2", "square millimeters": "mm2",
    "square centimeter": "cm2", "square centimeters": "cm2",
    "square meter": "m2", "square meters": "m2",
    "square kilometer": "km2", "square kilometers": "km2",
    "hectare": "ha", "hectares": "ha",
    "square inch": "in2", "square inches": "in2",
    "square foot": "ft2", "square feet": "ft2",
    "square yard": "yd2", "square yards": "yd2",
    "acre": "ac", "acres": "ac",
    "square mile": "mi2", "square miles": "mi2",
    # speed
    "meters per second": "m/s", "metres per second": "m/s",
    "kilometers per hour": "km/h", "kilometres per hour": "km/h", "kph": "km/h",
    "feet per second": "ft/s",
    "miles per hour": "mph",
    "knot": "kn", "knots": "kn",
    # temperature
    "celsius": "C", "centigrade": "C",
    "fahrenheit": "F",
    "kelvin": "K",
}

# ---------------------------------------------------------------------------
# Build a flat lookup: (from_unit, to_unit) -> factor
#
# Strategy: for each category, express every unit as a magnitude relative to
# the first metric unit in that category (the "base").  For metric units this
# is done via a shared imperial pivot; for imperial units it is the reciprocal
# of the base's own factor to that imperial unit.
# Once every unit has a _to_base value, any pair (A → B) is simply
# _to_base[A] / _to_base[B], giving full transitive coverage:
#   mm → cm, in → ft, oz → lb, mph → kn, etc.
# ---------------------------------------------------------------------------

_LOOKUP: dict[tuple[str, str], float] = {}

for _category, _units in CONVERSIONS.items():
    _base: str = next(iter(_units))                    # e.g. "mm" for length
    _pivot: str = next(iter(_units[_base]))            # first imperial target of base
    _base_to_pivot: float = float(_units[_base][_pivot])

    # _to_base[u] = "how many base units equal 1 of u"
    _to_base: dict[str, float] = {}

    for _m_unit, _targets in _units.items():
        if _pivot in _targets:
            # factor(m_unit → base) = factor(m_unit → pivot) / factor(base → pivot)
            _to_base[_m_unit] = float(_targets[_pivot]) / _base_to_pivot
        else:
            # fallback: use any imperial unit that is also defined for the base
            for _imp, _f in _targets.items():
                if _imp in _units[_base]:
                    _to_base[_m_unit] = float(_f) / float(_units[_base][_imp])
                    break

    # Imperial units: 1 imp = 1 / (base → imp) base units
    _all_imperial: set[str] = {imp for t in _units.values() for imp in t}
    for _imp in _all_imperial:
        _to_base[_imp] = 1.0 / float(_units[_base][_imp])

    # Populate every pair in this category (including same-unit identity)
    for _a, _va in _to_base.items():
        for _b, _vb in _to_base.items():
            _LOOKUP[(_a, _b)] = _va / _vb


# ---------------------------------------------------------------------------
# Core conversion function
# ---------------------------------------------------------------------------

def _canonicalize(unit: str) -> str:
    """Resolve alias or return as-is (lowercased for matching)."""
    stripped = unit.strip()
    return ALIASES.get(stripped.lower(), stripped)


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert *value* from *from_unit* to *to_unit*.
    Raises ValueError if the conversion pair is unknown.
    """
    f = _canonicalize(from_unit)
    t = _canonicalize(to_unit)

    if f == t:
        return value

    # Temperature
    key = (f.upper(), t.upper())
    if key in TEMPERATURE_CONVERSIONS:
        fn, _ = TEMPERATURE_CONVERSIONS[key]
        return fn(value)

    if (f, t) in _LOOKUP:
        return value * _LOOKUP[(f, t)]

    raise ValueError(
        f"Unknown conversion: '{from_unit}' → '{to_unit}'. "
        "Run with --list to see supported units."
    )


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

UNIT_LABELS: dict[str, str] = {
    "mm": "mm", "cm": "cm", "m": "m", "km": "km",
    "in": "in", "ft": "ft", "yd": "yd", "mi": "mi",
    "mg": "mg", "g": "g", "kg": "kg", "t": "t",
    "oz": "oz", "lb": "lb", "st": "st", "ton_us": "short ton",
    "ml": "mL", "l": "L", "m3": "m³",
    "fl_oz": "fl oz", "pt": "pt", "qt": "qt", "gal": "gal", "cup": "cup",
    "mm2": "mm²", "cm2": "cm²", "m2": "m²", "km2": "km²", "ha": "ha",
    "in2": "in²", "ft2": "ft²", "yd2": "yd²", "ac": "ac", "mi2": "mi²",
    "m/s": "m/s", "km/h": "km/h", "ft/s": "ft/s", "mph": "mph", "kn": "kn",
    "C": "°C", "F": "°F", "K": "K",
}


def _label(unit: str) -> str:
    canon = _canonicalize(unit)
    return UNIT_LABELS.get(canon, canon)


def _fmt(value: float) -> str:
    if abs(value) >= 1_000_000 or (abs(value) < 0.0001 and value != 0):
        return f"{value:.6e}"
    return f"{value:,.6f}".rstrip("0").rstrip(".")


def print_result(value: float, from_unit: str, to_unit: str, result: float) -> None:
    print(f"  {_fmt(value)} {_label(from_unit)}  =  {_fmt(result)} {_label(to_unit)}")


# ---------------------------------------------------------------------------
# List supported units
# ---------------------------------------------------------------------------

def list_units() -> None:
    print("\nSupported units by category:\n")
    categories = {
        "Length":      ["mm", "cm", "m", "km", "in", "ft", "yd", "mi"],
        "Weight/Mass": ["mg", "g", "kg", "t", "oz", "lb", "st", "ton_us"],
        "Volume":      ["ml", "l", "m3", "fl_oz", "pt", "qt", "gal", "cup"],
        "Area":        ["mm2", "cm2", "m2", "km2", "ha", "in2", "ft2", "yd2", "ac", "mi2"],
        "Speed":       ["m/s", "km/h", "ft/s", "mph", "kn"],
        "Temperature": ["C (°C)", "F (°F)", "K (Kelvin)"],
    }
    for cat, units in categories.items():
        print(f"  {cat}:")
        print(f"    {', '.join(units)}")
    print()


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def interactive_mode() -> None:
    print("=" * 50)
    print("   Metric ↔ Imperial Unit Converter")
    print("=" * 50)
    print("Type 'list' to see all units, 'quit' to exit.\n")

    while True:
        try:
            raw = input("Enter conversion (e.g.  100 km to mi): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not raw:
            continue
        if raw.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if raw.lower() == "list":
            list_units()
            continue

        # Parse: <value> <from_unit> [to|in|as] <to_unit>
        tokens = raw.split()
        try:
            value = float(tokens[0])
            if len(tokens) >= 4 and tokens[2].lower() in ("to", "in", "as", "->", "→"):
                from_unit = tokens[1]
                to_unit = tokens[3]
            elif len(tokens) == 3:
                from_unit = tokens[1]
                to_unit = tokens[2]
            else:
                raise ValueError
        except (ValueError, IndexError):
            print("  Format: <value> <from_unit> to <to_unit>  (e.g. 5 kg to lb)\n")
            continue

        try:
            result = convert(value, from_unit, to_unit)
            print_result(value, from_unit, to_unit, result)
        except ValueError as e:
            print(f"  Error: {e}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="converter",
        description="Convert between metric and imperial units.",
        epilog="Examples:\n"
               "  python converter.py 100 km to mi\n"
               "  python converter.py 98.6 F to C\n"
               "  python converter.py 5 kg to lb\n"
               "  python converter.py --list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("value", nargs="?", type=float, help="Numeric value to convert")
    parser.add_argument("from_unit", nargs="?", help="Source unit (e.g. km, lb, C)")
    parser.add_argument("to_keyword", nargs="?", help="'to' keyword (optional)")
    parser.add_argument("to_unit", nargs="?", help="Target unit (e.g. mi, kg, F)")
    parser.add_argument("--list", "-l", action="store_true", help="List all supported units")

    args = parser.parse_args()

    if args.list:
        list_units()
        return

    # Resolve flexible arg order: value from [to] to_unit
    if args.value is not None and args.from_unit is not None:
        if args.to_keyword and args.to_keyword.lower() in ("to", "in", "as", "->", "→"):
            to_unit = args.to_unit
        elif args.to_keyword and args.to_unit is None:
            to_unit = args.to_keyword  # user skipped "to" keyword
        else:
            to_unit = args.to_unit

        if to_unit is None:
            parser.print_help()
            return

        try:
            result = convert(args.value, args.from_unit, to_unit)
            print_result(args.value, args.from_unit, to_unit, result)
        except ValueError as e:
            print(f"Error: {e}")
        return

    # No arguments → interactive mode
    interactive_mode()


if __name__ == "__main__":
    main()
