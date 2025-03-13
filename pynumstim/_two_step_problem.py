from __future__ import annotations

from hashlib import md5
from typing import Optional

from ._number import Num, TNum, TPyNum
from ._problem import MathProblem, SimpleArithmetic, TProperties


class TwoStepArithmetic(MathProblem):
    def __init__(
        self,
        operand1: TNum,
        operand2: TNum,
        operand3: TNum,
        operation1: str,
        operation2: str,
        result: Optional[TNum] = None,
        properties: Optional[TProperties] = None,
    ) -> None:
        """properties: dict of properties.
        Keys represent the property name and must be text strings
        """

        self.step1 = SimpleArithmetic(
            operand1=operand1, operation=operation1, operand2=operand2
        )
        self.step2 = SimpleArithmetic(
            operand1=self.step1.calc(),
            operation=operation2,
            operand2=operand3,
            result=result,
            properties=properties,
        )

    @property
    def operand1(self) -> Num:
        return self.step1.operand1

    @property
    def operand2(self) -> Num:
        return self.step1.operand2

    @property
    def operand3(self) -> Num:
        return self.step2.operand2

    @property
    def operation1(self) -> str:
        return self.step1.operation

    @property
    def operation2(self) -> str:
        return self.step2.operation

    @property
    def result(self) -> Num | None:
        return self.step2.result

    def operation1_label(self) -> str:
        return self.step1.operation_label()

    def operation2_label(self) -> str:
        return self.step2.operation_label()

    def calc(self) -> TPyNum:
        return self.step2.calc()

    def tex(self, brackets: bool = True) -> str:
        part1 = self.step1.tex()
        part2 = self.step2.tex().split(maxsplit=1)[1]
        if brackets:
            part1 = f"({part1})"
        return f"{part1} {part2}"

    def label(self) -> str:
        """labels not not have no spaces and not the characters \\*{}=
        They can thus be used for filenames and as ids in data tables
        """
        o1 = self.operand1.label()
        o2 = self.operand2.label()
        o3 = self.operand3.label()
        rtn = f"{o1}{self.operation1_label()}{o2}{self.operation2_label()}{o3}"
        if self.result is not None:
            rtn += f"={self.result.label()}"
        return rtn

    def __str__(self) -> str:
        """text representation"""
        o1 = self.operand1.label()
        o2 = self.operand2.label()
        o3 = self.operand3.label()
        rtn = f"({o1} {self.operation1} {o2}) {self.operation2} {o3}"
        if self.result is not None:
            rtn += f" = {self.result.label()}"
        return rtn

    def hash(self) -> str:
        md5_object = md5(self.label().encode())
        return md5_object.hexdigest()
