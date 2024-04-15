from __future__ import annotations

import re
from copy import copy
from fractions import Fraction
from hashlib import md5
from typing import Any, Dict, Optional

from ._number import Num, TNum, TPyNum

LATEX_TIMES = "\\times"  # "\\cdot"
LATEX_SYMBOL_NAMES = {"=": "equal",
                "+": "plus",
                LATEX_TIMES: "multiply",
                "/": "divide",
                "-": "minus"}

TProperties = Dict[str, Any]


class MathProblem(object):

    LABEL_MULTI = "t"  # multiplication, times
    LABEL_DIVIDE = "d"  # divide
    OPERATIONS = ["+", "-", "*", "/", LABEL_MULTI, LABEL_DIVIDE]

    def __init__(self,
                 operant1: TNum,
                 operation: str,
                 operant2: TNum,
                 result: Optional[TNum] = None,
                 properties: Optional[TProperties] = None) -> None:
        """properties: dict of properties.
                        Keys repesent the property name and must be text strings
        """

        self.operation = operation
        self.operant1 = operant1
        self.operant2 = operant2
        self.result = result
        self.properties = copy(properties)

    @property
    def operant1(self) -> Num:
        return self._op1

    @operant1.setter
    def operant1(self, val: TNum):
        self._op1 = Num(val)

    @property
    def operant2(self) -> Num:
        return self._op2

    @operant2.setter
    def operant2(self, val: TNum):
        self._op2 = Num(val)

    @property
    def result(self) -> Optional[Num]:
        return self._result

    @result.setter
    def result(self, val: Optional[TNum]):
        if val is None:
            self._result = None
        else:
            self._result = Num(val)

    @property
    def operation(self) -> str:
        return self._operation

    @operation.setter
    def operation(self, val: str):
        if val not in MathProblem.OPERATIONS:
            raise ValueError(f"Unknown operation: '{val}'")
        if val == MathProblem.LABEL_MULTI:
            self._operation = "*"
        elif val == MathProblem.LABEL_DIVIDE:
            self._operation = "/"
        else:
            self._operation = val

    def operation_label(self):
        if self._operation == "*":
            return self.LABEL_MULTI
        elif self._operation == "/":
            return self.LABEL_DIVIDE
        else:
            return self._operation

    def update_properties(self, props: Dict[str, Any]):
        if isinstance(self.properties, dict):
            self.properties.update(props.copy())
        else:
            self.properties = props.copy()

    def has_properites(self, props: TProperties) -> bool:
        """returns if problem is the properties defined in props"""
        if self.properties is None:
            return False
        for key, value in props.items():
            if key not in self.properties or self.properties[key] != value:
                return False
        return True

    def _as_dict(self) -> Dict[str, Any]:
        """minimal dict representation of the problem without properties"""
        rtn = {'op1': self._op1.label(),
               'operation': self.operation,
               'op2': self._op2.label()}

        if self._result is None:
            rtn['result'] = ""
        else:
            rtn['result'] = self._result.label()
        return rtn

    def problem_dict(self,
                     incl_hash=False,
                     problem_size=False,
                     n_carry=False) -> Dict[str, str | int | float]:

        rtn = self._as_dict()
        if self._result is not None:
            rtn['correct'] = int(self.is_correct())
            rtn['dev'] = self.deviation()

        if problem_size:
            rtn['prob_size'] = self.problem_size()
        if n_carry:
            nc = self.n_carry()
            if nc is not None:
                rtn['n_carry'] = nc

        rtn['label'] = self.label()
        if isinstance(self.properties, dict):
            rtn.update(self.properties)
        if incl_hash:
            rtn['hash'] = self.hash()
        return rtn

    def calc(self) -> TPyNum:
        # returns correct result
        o1 = self._op1.py_number
        o2 = self._op2.py_number

        if self.operation == "+":
            return o1 + o2
        elif self.operation == "-":
            return o1 - o2
        elif self.operation == "*":
            return o1 * o2
        elif self.operation == "/":
            if isinstance(o1, float) or isinstance(o2, float):
                return o1 / o2
            else:
                return Fraction(o1, o2)
        else:
            # should never happen
            raise RuntimeError(f"Unknown operation: '{self.operation}'")

    def deviation(self) -> Optional[float]:
        """deviation from correct"""
        if self._result is None:
            return None
        else:
            return float(self._result) - self.calc()

    def tex(self) -> str:
        o1 = self._op1.tex()
        o2 = self._op2.tex()
        if self.operation == "*":
            operation = LATEX_TIMES
        else:
            operation = self.operation
        rtn = f"{o1} {operation} {o2}"
        if self._result is not None:
            rtn += f" = {self._result.tex()}"
        return rtn

    def label(self) -> str:
        """labels not not have no spaces and not the characters \\*{}=
        They can thus be used for filenames and as ids in data tables
        """
        o1 = self._op1.label()
        o2 = self._op2.label()
        rtn = f"{o1}{self.operation_label()}{o2}"
        if self._result is not None:
            rtn += f"={self._result.label()}"
        return rtn

    def __str__(self) -> str:
        """text representation"""
        o1 = self._op1.label()
        o2 = self._op2.label()
        rtn = f"{o1} {self.operation} {o2}"
        if self._result is not None:
            rtn += f" = {self._result.label()}"
        return rtn

    def hash(self) -> str:
        md5_object = md5(self.label().encode())
        return md5_object.hexdigest()

    def is_correct(self):
        if self._result is None:
            return False
        return self.calc() == self._result.py_number

    def n_carry(self) -> Optional[int]:
        """number of carry operations for addition and subtraction
        else None"""

        if self.operant1.is_fraction() or self.operant2.is_fraction():
            return None
        if self.operation == "+":
            subtraction = False
        elif self.operation == "-":
            subtraction = True
        else:
            return None

        str_op1 = str(self.operant1)
        str_op2 = str(self.operant2)
        # Get the length of the longer number
        max_length = max(len(str_op1), len(str_op2))
        # Add leading zeros to make the numbers have the same length
        str_op1 = str_op1.zfill(max_length)
        str_op2 = str_op2.zfill(max_length)

        current_carry = 0
        ncarry = 0
        # Iterate over digits from right to left
        for i in range(max_length - 1, -1, -1):
            if subtraction:
                res = int(str_op1[i]) - int(str_op2[i])
                res -= current_carry
            else:
                res = int(str_op1[i]) + int(str_op2[i])
                res += current_carry

            if (subtraction and res < 0) or (not subtraction and res >= 10):
                ncarry += 1
                current_carry = 1
            else:
                current_carry = 0

        return ncarry

    def problem_size(self) -> float:
        return (_size(self.operant1) + _size(self.operant1)) / 2.0

    @staticmethod
    def parse(txt: str, properties: Optional[TProperties] = None) -> MathProblem:
        """fractions have to presented like in labels: frac5_6
        can also convert labels to problems
        """
        x = txt.split("=")
        if len(x) < 3:
            if len(x) == 1:
                result = None
            else:
                result = Num(x[1])

            op1, op2, operation = (None, None, None)
            for op in MathProblem.OPERATIONS:
                try:
                    op1, op2 = _split_after_digit(x[0], op)
                    operation = op
                    break
                except ValueError:
                    pass

            if None not in (op1, op2, operation):
                return MathProblem(
                    op1, operation, op2, result, properties)  # type: ignore

        raise ValueError(f"Can't convert '{txt}' to MathProblem.")

    def is_tie(self) -> bool:
        return self.operant1 == self.operant2

    def has_decade_solution(self) -> bool:
        return self.calc() % 10 == 0

    def has_same_parities(self) -> bool:
        return self.operant1.py_number % 2 == self.operant2.py_number % 2


def _split_after_digit(txt: str, letter: str):
    # splits txt at letter only if a digit proceeds the letter
    if letter in ["+", "*", "\\"]:
        letter = f"\\{letter}"
    a = re.search(f"\\d\\s*{letter}", txt)
    if a is not None:
        return txt[:a.span()[0]+1], txt[a.span()[1]:]
    else:
        return txt


def _size(num: Num) -> TPyNum:
    """helper for calculation problem size with fractions.
    In this case, return mean of numerator and denomintor"""
    if num.is_fraction():
        return (num.numerator + num.denominator) / 2.0
    else:
        return num.py_number
