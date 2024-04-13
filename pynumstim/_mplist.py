
from __future__ import annotations

from pathlib import Path
from random import randint, shuffle
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import toml

from ._number import NumType
from ._problem import MathProblem


class MathProblemList(object):

    def __init__(self):
        self.list: List[MathProblem] = []

    def __str__(self):
        return str(self.data_frame())

    def append(self, problem: Union[MathProblem, MathProblemList]):
        if isinstance(problem, MathProblem):
            self.list.append(problem)
        if isinstance(problem, MathProblemList):
            for x in problem.list:
                self.list.append(x)

    def add(self, first_operant: NumType | str,
            operation: str,
            second_operant: NumType | str,
            result: Optional[NumType | str] = None,
            properties: Optional[Dict[str, Any]] = None):

        self.append(MathProblem(operant1=first_operant, operation=operation,
                                operant2=second_operant, result=result,
                                properties=properties))

    def pop_random(self, n_problems: int = 1) -> MathProblemList:
        # get a random problem
        rtn = MathProblemList()
        for _ in range(n_problems):
            index = randint(0, len(self.list)-1)
            rtn.append(self.list.pop(index))
        return rtn

    def find(self, first_operant: Optional[NumType] = None,
             operation: Optional[str] = None,
             second_operant: Optional[NumType] = None,
             correct: Optional[bool] = None,
             result: Optional[NumType] = None,
             deviation: Optional[NumType] = None) -> MathProblemList:

        lst = self.list
        if first_operant is not None:
            lst = [x for x in lst if x.operant1 == first_operant]
        if operation is not None:
            lst = [x for x in lst if x.operation == operation]
        if second_operant is not None:
            lst = [x for x in lst if x.operant2 == second_operant]
        if correct is not None:
            lst = [x for x in lst if x.is_correct() == correct]
        if result is not None:
            lst = [x for x in lst if x.result == result]
        if deviation is not None:
            lst = [x for x in lst if x.deviation() == deviation]
        rtn = MathProblemList()
        for x in lst:
            rtn.append(x)
        return rtn

    def shuffel(self):
        shuffle(self.list)

    def data_frame(self, first_id: Optional[int] = None) -> pd.DataFrame:
        """pandas data frame, includes problem ids, if first_id is defined"""
        rtn = pd.DataFrame([a.as_dict() for a in self.list])
        if first_id is not None:
            rtn['problem_id'] = range(first_id, first_id+len(rtn))
        return rtn

    def to_csv(self, filename: Union[Path, str], first_id: Optional[int] = None) -> pd.DataFrame:
        """pandas data frame, includes problem ids, if first_id is defined"""
        df = self.data_frame(first_id=first_id)
        df.to_csv(filename, sep="\t", index=False, lineterminator="\n")
        return df

    def import_toml(self, filename: Union[Path, str]):
        return self.import_dict(toml.load(filename))

    def import_dict(self, problem_dict: dict,
                    sections: Union[None, str, Tuple[str], List[str]] = None):
        """imports dicts

        the following methods exist (illustrated by toml representation):
        method a:

            [category]
            op1 = [12, 13, 14]
            op2 = [6, 7, 8, 9]
            operation = "*"

        method b:

            [category]
            problems = [[1, "*", 4, 45]
                        ["1/6723", "-", 4, 45]]

        Args:
            problem_dict: _description_
            sections: _description_. Defaults to None.
        """
        if sections is None:
            sections = list(problem_dict.keys())
        elif isinstance(sections, (tuple, list)):
            sections = list(sections)

        for s in sections:
            prop = {"category": s}
            d = problem_dict[s]
            if "problems" in d:
                for x in d["problems"]:
                    p = MathProblem(x[0], x[1], x[2], properties=prop)
                    self.append(p)
            if 'op1' in d and 'op2' in d and 'operation' in d:
                for op1 in d['op1']:
                    for op2 in d['op2']:
                        p = MathProblem(op1, d['operation'], op2,
                                        properties=prop)
                        self.append(p)
