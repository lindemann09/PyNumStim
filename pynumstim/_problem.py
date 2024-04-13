from __future__ import annotations

import re
from copy import copy
from fractions import Fraction
from hashlib import md5
from typing import Any, Dict, Optional

from ._number import Num, NumType, PyNum

SYMBOL_NAMES = {"=": "equal",
                "+": "plus",
                "*": "multiply",
                "/": "divide",
                "-": "minus"}

class MathProblem(object):

    LABEL_MULTI = "t"  # multiplication, times
    LABEL_DIVIDE = "d"  # divide
    OPERATIONS = ["+", "-", "*", "/", LABEL_MULTI, LABEL_DIVIDE]

    def __init__(self,
                 operant1: NumType,
                 operation: str,
                 operant2: NumType,
                 result: Optional[NumType] = None,
                 properties: Optional[Dict[str, Any]] = None) -> None:
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
    def operant1(self, val:NumType):
        self._op1 = Num(val)

    @property
    def operant2(self) -> Num:
        return self._op2

    @operant2.setter
    def operant2(self, val:NumType):
        self._op2 = Num(val)

    @property
    def result(self) -> Optional[Num]:
        return self._result

    @result.setter
    def result(self, val:Optional[NumType]):
        if val is None:
            self._result = None
        else:
            self._result = Num(val)

    @property
    def operation(self) -> str:
        return self._operation

    @operation.setter
    def operation(self, val:str):
        if val not in MathProblem.OPERATIONS:
            raise ValueError(f"Unknown operation: '{val}'")
        if val == MathProblem.LABEL_MULTI:
            self._operation= "*"
        elif val == MathProblem.LABEL_DIVIDE:
            self._operation= "/"
        else:
            self._operation= val

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

    def as_dict(self, incl_hash=False) -> dict:

        rtn = {'op1': self._op1.label(),
               'operation': self.operation,
               'op2': self._op2.label()}
        if self._result is None:
            rtn['result'] = ""
        else:
            rtn['result'] = self._result.label()
            rtn['correct'] = str(int(self.is_correct()))
            rtn['dev'] = str(self.deviation())
        rtn['label'] = self.label()
        if isinstance(self.properties, dict):
            rtn.update(self.properties)
        if incl_hash:
            rtn['hash'] = self.hash()
        return rtn

    def calc(self) -> PyNum:
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
            raise RuntimeError(f"Unknown operation: '{self.operation}'") # should never happen

    def deviation(self) -> Num:
        """deviation from correct"""
        if self._result is None:
            return Num(0)
        else:
            return self._result - self.calc()

    def tex(self) -> str:
        o1 = self._op1.tex()
        o2 = self._op2.tex()
        rtn = f"{o1} {self.operation} {o2}"
        if self._result is not None:
            rtn += f" = {self._result.tex()}"
        return rtn

    def label(self) -> str:
        """labels not not have no spaces and not the characters \\*{}=
        They can thus be used for filenames and as ids in data tables
        """
        o1 = self._op1.label()
        o2 = self._op2.label()
        rtn = f"{o1} {self.operation_label()} {o2}"
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

    @staticmethod
    def parse(txt: str, properties: Optional[Dict[str, Any]] = None) -> MathProblem:
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


def _split_after_digit(txt: str, letter: str):
    # splits txt at letter only if a digit proceeds the letter
    if letter in ["+", "*", "\\"]:
        letter = f"\\{letter}"
    a = re.search(f"\\d\\s*{letter}", txt)
    if a is not None:
        return txt[:a.span()[0]+1], txt[a.span()[1]:]
    else:
        return txt
