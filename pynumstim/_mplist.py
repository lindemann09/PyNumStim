from __future__ import annotations

from pathlib import Path
from random import randint, shuffle
from typing import List, Optional, Tuple, Union

import pandas as pd
import toml

from ._number import TNum
from ._problem import MathProblem, TProperties


class MathProblemList(object):

    def __init__(self):
        self.list: List[MathProblem] = []

    def __str__(self):
        rtn = ""
        for x in self.list:
            rtn += str(x) + "\n"
        return rtn

    def append(self, problem: Union[MathProblem, MathProblemList]):
        if isinstance(problem, MathProblem):
            self.list.append(problem)
        if isinstance(problem, MathProblemList):
            for x in problem.list:
                self.list.append(x)

    def add(self, first_operant: TNum | str,
            operation: str,
            second_operant: TNum | str,
            result: Optional[TNum | str] = None,
            properties: Optional[Optional[TProperties]] = None):

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

    def find(self, first_operant: Optional[TNum] = None,
             operation: Optional[str] = None,
             second_operant: Optional[TNum] = None,
             correct: Optional[bool] = None,
             result: Optional[TNum] = None,
             deviation: Optional[TNum] = None,
             n_carry: Optional[int] = None,
             is_tie: Optional[bool] = None,
             has_same_parities: Optional[bool] = None,
             has_decade_solution: Optional[bool] = None,
             problem_size: Optional[float] = None,
             properties: Optional[TProperties] = None) -> MathProblemList:

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
        if n_carry is not None:
            lst = [x for x in lst if x.n_carry() == n_carry]
        if is_tie is not None:
            lst = [x for x in lst if x.is_tie() == is_tie]
        if problem_size is not None:
            lst = [x for x in lst if x.problem_size() == problem_size]
        if has_same_parities is not None:
            lst = [x for x in lst if x.has_same_parities() == has_same_parities]
        if has_decade_solution is not None:
            lst = [x for x in lst if x.has_decade_solution() == deviation]

        if properties is not None:
            lst = [x for x in lst if x.has_properites(properties)]

        rtn = MathProblemList()
        for x in lst:
            rtn.append(x)
        return rtn

    def shuffel(self):
        shuffle(self.list)

    def update_properties(self, properties:TProperties):
        """updates the properties of all problems"""
        for x in self.list:
            x.update_properties(properties)

    def data_frame(self,
                   first_id: Optional[int] = None,
                   problem_size=False,
                   n_carry=False) -> pd.DataFrame:
        """pandas data frame, includes problem ids, if first_id is defined"""
        dicts = [a.problem_dict(problem_size=problem_size, n_carry=n_carry)
                 for a in self.list]
        rtn = pd.DataFrame(dicts)
        if first_id is not None:
            rtn['problem_id'] = range(first_id, first_id+len(rtn))
        return rtn

    def to_csv(self, filename: Union[Path, str],
               first_id: Optional[int] = None,
               problem_size=False,
               n_carry=False,
               rounding_digits:int=2) -> pd.DataFrame:
        """pandas data frame, includes problem ids, if first_id is defined"""
        df = self.data_frame(
            first_id=first_id, problem_size=problem_size, n_carry=n_carry)
        df = df.round(rounding_digits)
        df.to_csv(filename, sep="\t", index=False, lineterminator="\n")
        return df

    #def to_toml(self, filename: Union[Path, str]) -> pd.DataFrame:
    #    """pandas data frame, includes problem ids, if first_id is defined"""
    #    # FIXME categories are lots

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


        method c:

            [category]
            problems = [ "1 + 5 = 8",
                        "1/2 + 1/4 = 9"]

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
                    if isinstance(x, list):
                        p = MathProblem(x[0], x[1], x[2])
                    else:
                        p = MathProblem.parse(x)
                    p.update_properties(prop)
                    self.append(p)
            if 'op1' in d and 'op2' in d and 'operation' in d:
                for op1 in d['op1']:
                    for op2 in d['op2']:
                        p = MathProblem(op1, d['operation'], op2,
                                        properties=prop)
                        self.append(p)
