from __future__ import annotations

import re
from fractions import Fraction
from typing import Optional, Tuple

TPyNum = int | float | Fraction


class Num(object):
    # Rational number, that will not be normalized as Fractions

    def __init__(self,
                 numerator: TPyNum | Num | str,  # fixme str to parse
                 denominator: Optional[int | float] = None) -> None:

        if isinstance(numerator, (Fraction, Num, str)):
            if denominator is not None:
                raise ValueError("Denominator not allowed, if creating Num from " +
                                 "Fraction, String or other Num)")
            if isinstance(numerator, str):
                self.numerator, self.denominator = _parse(numerator)
            else:
                self.numerator = numerator.numerator
                self.denominator = numerator.denominator
        else:
            self.numerator = numerator
            if denominator is None:
                self.denominator = 1
            else:
                self.denominator = denominator

    def __str__(self) -> str:
        return self.text()

    def __float__(self) -> float:
        return self.numerator / self.denominator

    def __add__(self, val2):
        return Num(self.py_number + Num(val2).py_number)

    def __sub__(self, val2):
        return Num(self.py_number - Num(val2).py_number)

    def __mul__(self, val2):
        return Num(self.py_number * Num(val2).py_number)

    def __truediv__(self, val2):
        return Num(self.py_number / Num(val2).py_number)

    __rmul__ = __mul__

    @property
    def py_number(self) -> TPyNum:
        """returns Python Rational (int, Fraction) or float  for calculations"""
        if isinstance(self.numerator, Num):
            n = self.numerator.py_number
        else:
            n = self.numerator
        if isinstance(self.denominator, Num):
            d = self.denominator.py_number
        else:
            d = self.denominator

        if d == 1:
            return n
        if isinstance(n, float) or isinstance(d, float):
            return n / d
        else:
            return Fraction(n, d)

    def is_fraction(self):
        return self.denominator != 1

    def tex(self) -> str:
        if self.is_fraction():
            return f"\\frac{{{self.numerator}}}{{{self.denominator}}}"
        else:
            return f"{self.numerator}"

    def label(self) -> str:
        if self.is_fraction():
            return f"{self.numerator}_{self.denominator}"
        else:
            return f"{self.numerator}"

    def text(self) -> str:
        if self.is_fraction():
            return f"{self.numerator}/{self.denominator}"
        else:
            return f"{self.numerator}"


def _parse(txt: str) -> Tuple[int | float, int | float]:
    """return numerator, denominator
    converts 1_2 to Num(1, 2) or '3' to Num(3,1)
    """
    x = re.split("[_/]", txt)
    if len(x) == 1:
        try:
            return int(x[0]), 1
        except ValueError:
            pass

        try:
            return float(x[0]), 1
        except ValueError:
            pass

    elif len(x) == 2:
        n, _ = _parse(x[0])
        d, _ = _parse(x[1])
        return n, d

    raise ValueError(f"Can't convert '{txt}' to Num.")


TNum = TPyNum | Num | str
