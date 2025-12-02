from fractions import Fraction
from typing import ClassVar


class Beat:
    _value: Fraction
    MIN: ClassVar[Fraction] = Fraction(1, 32)
    MAX: ClassVar[Fraction] = Fraction(8, 1)
    ACCEPTED_VALUES: ClassVar[tuple[Fraction, ...]] = tuple(
        [Fraction(1, x) for x in (32, 16, 8, 4, 2, 1)] + [Fraction(x, 1) for x in (2, 4, 8)]
    )

    def __init__(self, numerator, denominator=None):
        self._value = self._valiparse_fraction(numerator, denominator)

    def _valiparse_fraction(self, *args):
        """Validate and parse arguments as a fractions.Fraction"""
        if len(args) == 1:
            numerator = args[0]
            denominator = None
        elif len(args) == 2:
            numerator, denominator = args
        else:
            raise ValueError("Cannot extract args for Fraction")
        try:
            v = Fraction(numerator, denominator)
        except TypeError:
            raise TypeError(f"Cannot interpret {(numerator, denominator)!r} as a Fraction")

        if (self.MIN <= v <= self.MAX) and (v in self.ACCEPTED_VALUES):
            return v
        raise ValueError(f"Fraction {v} not in accepted range")

    @property
    def value(self) -> Fraction:
        return self._value

    @property
    def string(self) -> str:
        """Get plain string without repr"""
        return str(self._value)

    def __repr__(self) -> str:
        return f"<Beat: {self.value}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Beat):
            return False
        return self.value == other.value
