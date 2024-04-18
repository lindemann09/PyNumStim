from __future__ import annotations

from copy import copy
from fractions import Fraction
from pathlib import Path
from random import randint, shuffle
from typing import List, Optional, Set, Tuple, Union
import re

import pandas as pd
import toml

from ._number import TNum
from ._problem import MathProblem, TProperties


class MathProblemList(object):

    def __init__(self):
        self._list: List[MathProblem] = []
        self.number_types: Set[type] = set() # involved number types

    def __str__(self):
        rtn = ""
        for x in self._list:
            rtn += str(x) + "\n"
        return rtn

    @property
    def list(self) -> List[MathProblem]:
        return self._list

    @list.setter
    def list(self, val:List[MathProblem]):
        self._list = val
        self.number_types: Set[type] = set()
        for x in self._list:
            self.number_types = self.number_types | x.number_types

    def append(self, problem: Union[MathProblem, MathProblemList]):
        if isinstance(problem, MathProblem):
            self._list.append(problem)
            self.number_types = self.number_types | problem.number_types
        if isinstance(problem, MathProblemList):
            for x in problem.list:
                self.append(x)

    def add(self, first_operant: TNum | str,
            operation: str,
            second_operant: TNum | str,
            result: Optional[TNum | str] = None,
            properties: Optional[Optional[TProperties]] = None):

        self.append(MathProblem(operant1=first_operant, operation=operation,
                                operant2=second_operant, result=result,
                                properties=properties))


    def get_random(self, n_problems: int = 1) -> MathProblemList:
        # get random problems
        lst = copy(self._list)
        shuffle(lst)
        rtn = MathProblemList()
        rtn.list = lst[0:n_problems]
        return rtn

    def pop_random(self, n_problems: int = 1) -> MathProblemList:
        # pop a random problems
        rtn = MathProblemList()
        for _ in range(n_problems):
            index = randint(0, len(self._list)-1)
            rtn.append(self._list.pop(index))
        return rtn

    def find(self,
             first_operant: Optional[TNum] = None,
             operation: Optional[str] = None,
             second_operant: Optional[TNum] = None,
             correct: Optional[bool] = None,
             result: Optional[TNum] = None,
             deviation: Optional[TNum] = None,
             n_carry: Optional[int] = None,
             negative_result: Optional[bool] = None,
             same_operants: Optional[bool] = None,
             same_parities: Optional[bool] = None,
             decade_solution: Optional[bool] = None,
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
            lst = [x for x in lst
                   if x.result is not None and x.result.py_number == result]
        if deviation is not None:
            lst = [x for x in lst if x.deviation() == deviation]
        if n_carry is not None:
            lst = [x for x in lst if x.n_carry() == n_carry]
        if negative_result is not None:
            lst = [x for x in lst
                   if x.result is not None and (x.result.py_number < 0) == negative_result]
        if same_operants is not None:
            lst = [x for x in lst if x.same_operants() == same_operants]
        if problem_size is not None:
            lst = [x for x in lst if x.problem_size() == problem_size]
        if same_parities is not None:
            lst = [x for x in lst if x.same_parities() == same_parities]
        if decade_solution is not None:
            lst = [x for x in lst if x.decade_solution() == decade_solution]

        if properties is not None:
            lst = [x for x in lst if x.has_properites(properties)]

        rtn = MathProblemList()
        rtn.list = lst
        return rtn

    def shuffel(self):
        shuffle(self._list)

    def update_properties(self, properties:TProperties):
        """updates the properties of all problems"""
        for x in self._list:
            x.update_properties(properties)

    def data_frame(self,
                   first_id: Optional[int] = None,
                   problem_size=False,
                   n_carry=False) -> pd.DataFrame:
        """pandas data frame, includes problem ids, if first_id is defined"""
        dicts = [a.problem_dict(problem_size=problem_size, n_carry=n_carry)
                 for a in self._list]
        rtn = pd.DataFrame(dicts)
        if first_id is not None:
            rtn['problem_id'] = range(first_id, first_id+len(rtn))

        if Fraction not in self.number_types:
            if float in self.number_types:
                t = float
            else:
                t = int
            for x in ['op1', 'op2', 'result']:
                rtn[x] = rtn[x].astype(t, errors='ignore', copy=False)
        self.number_types
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


    def import_toml(self, filename: Union[Path, str]):
        """imports toml

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
        return self.import_dict(toml.load(filename))

    def import_markdown_text(self, text:str):
        """important markdown text.

        see also
        --------
        `import_markdown`
        """
        curr_cat = None
        for l in text.splitlines():
            x = re.match(r"^\s*#+\s+", l)
            if isinstance(x, re.Match):
                curr_cat = l[x.span()[1]:].strip()
            else:
                x = re.match(r"^\s*\*+\s+", l)
                if isinstance(x, re.Match):
                    problem_str = l[x.span()[1]:].strip()
                    p = MathProblem.parse(problem_str)
                    if curr_cat is not None:
                        p.update_properties({"category": curr_cat})
                    self.append(p)

    def import_markdown(self, filename: Union[Path, str]):
        """importing from markdown file

        Example
        -------
        Markdown text:
            ```
            # CATEGORY NAME

            * 1 + 2 = 2
            * 23_26 - 1_2 = 8

            comment
            * 4 / 7 = 19
            ```
        """
        with open(filename, "r", encoding="utf-8") as fl:
            text = fl.read()
        self.import_markdown_text(text)

    def import_dict(self, problem_dict: dict,
                    categories: Union[None, str, Tuple[str], List[str]] = None):
        """see doc import toml for structure of dict"""

        if categories is None:
            categories = list(problem_dict.keys())
        elif isinstance(categories, (tuple, list)):
            categories = list(categories)

        for s in categories:
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

    def import_data_frame(self, df:pd.DataFrame):
        for _, row in df.iterrows():
            self.add(first_operant=row['op1'],
                     operation=row['operation'],
                     second_operant=row['op2'],
                     result=row['result'])

