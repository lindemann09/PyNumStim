from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from random import randint, shuffle
from typing import List, Optional, Set, Tuple, Union
import re

import numpy as np
import pandas as pd
import toml

from ._number import TNum
from ._problem import MathProblem, TProperties


class MathProblemList(object):

    def __init__(self):
        self._list: List[MathProblem] = []
        self.number_types: Set[type] = set()  # involved number types

    def __str__(self):
        rtn = ""
        for x in self._list:
            rtn += str(x) + "\n"
        return rtn

    @property
    def list(self) -> List[MathProblem]:
        return self._list

    @list.setter
    def list(self, val: List[MathProblem]):
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

    def add(self, first_operand: TNum | str,
            operation: str,
            second_operand: TNum | str,
            result: Optional[TNum | str] = None,
            properties: Optional[Optional[TProperties]] = None):

        self.append(MathProblem(operand1=first_operand, operation=operation,
                                operand2=second_operand, result=result,
                                properties=properties))

    def get_random(self, n: int = 1,
                   dev_corr: Optional[int | float] = None) -> MathProblemList:
        """Get x random problems

        Optionally set results via `dev_cor`, which defined the deviation from
        correct (see `set_results`)
        """
        lst = deepcopy(self._list)
        shuffle(lst)
        rtn = MathProblemList()
        rtn.list = lst[0:n]
        if dev_corr is not None:
            rtn.set_results(dev_corr=dev_corr)
        return rtn

    def pop_random(self, n: int = 1,
                   dev_corr: Optional[int | float] = None) -> MathProblemList:
        """Pop x random problems

        Optionally set results via `dev_cor`, which defined the deviation from
        correct (see `set_results`)
        """

        rtn = MathProblemList()
        for _ in range(n):
            index = randint(0, len(self._list)-1)
            p = self._list.pop(index)
            if dev_corr is not None:
                p.result = p.calc() + dev_corr
            rtn.append(p)
        return rtn

    def set_results(self, dev_corr: int | float):
        """Sets results of all problem to a value that deviation from
        correct result by `dev_corr`. Thus, `dev_corr=0` returns correct problems.

        Note
        ----
        Setting results does not work (yet) for fractions
        """  # TODO

        for x in range(len(self._list)):
            self._list[x].result = self._list[x].calc() + dev_corr


    def find(self,
             first_operand: Optional[TNum] = None,
             operation: Optional[str] = None,
             second_operand: Optional[TNum] = None,
             correct: Optional[bool] = None,
             result: Optional[TNum] = None,
             deviation: Optional[TNum] = None,
             n_carry: Optional[int] = None,
             negative_result: Optional[bool] = None,
             same_operands: Optional[bool] = None,
             same_parities: Optional[bool] = None,
             decade_solution: Optional[bool] = None,
             problem_size: Optional[float] = None,
             properties: Optional[TProperties] = None) -> MathProblemList:

        lst = self.list
        if first_operand is not None:
            lst = [x for x in lst if x.operand1 == first_operand]
        if operation is not None:
            lst = [x for x in lst if x.operation == operation]
        if second_operand is not None:
            lst = [x for x in lst if x.operand2 == second_operand]
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
        if same_operands is not None:
            lst = [x for x in lst if x.same_operands() == same_operands]
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

    def update_properties(self, properties: TProperties):
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

        return rtn

    def to_csv(self, filename: Union[Path, str],
               first_id: Optional[int] = None,
               problem_size=False,
               n_carry=False,
               rounding_digits: int = 2,
               sep: str = '\t') -> pd.DataFrame:
        """pandas data frame, includes problem ids, if first_id is defined"""
        df = self.data_frame(
            first_id=first_id, problem_size=problem_size, n_carry=n_carry)
        df = df.round(rounding_digits)
        df.to_csv(filename, sep=sep, index=False, lineterminator="\n")
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

    def import_markdown_text(self, text: str):
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

    def import_data_frame(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            self.add(first_operand=row['op1'],
                     operation=row['operation'],
                     second_operand=row['op2'],
                     result=row['result'])

    def rand_selection(self,
                       n_correct: int,
                       n_smaller: int,
                       n_larger: int,
                       dev_corr: List[int | float] | int | float = 1,
                       dev_mean_operand: Optional[float] = None,
                       min_result: Optional[int | float] = None,
                       max_result: Optional[int | float] = None,
                       max_iterations: int = 10000
                       ) -> MathProblemList:
        """select problems with correct and incorrect results and with a maximum
        deviation of mean operands between correct and incorrect problems

        dev_corr: number or list of number
                list of specifies the deviations from correct result

        min_result and max_result: the minimum and maximum value of the
        correct and incorrect results

        returns a new MathProblemList with a copies of the selected problems
        """

        # make lists deviation lists: dcorr
        if isinstance(dev_corr, (int, float)):
            dcorr = np.asarray([dev_corr])
        elif isinstance(dev_corr, (list, tuple)):
            dcorr = np.asarray(dev_corr)
        else:
            raise ValueError("dev_corr has to be a int, float or list of int or float")

        for x in dcorr:
            if x <= 0:
                raise RuntimeError("dev_corr has to be large 0")
        # enlarge list
        while len(dcorr) < n_smaller or len(dcorr)<n_larger:
            dcorr = np.append(dcorr, dcorr)

        # copy all problem, set as correct and create df
        pl = deepcopy(self)
        pl.set_results(dev_corr=0)
        df = pl.data_frame()
        if max_result is not None:
            df = df[df['result'] <= max_result]
        if min_result is not None:
            df = df[df['result'] >= min_result]

        n = 0
        while True:
            if n > max_iterations:
                raise RuntimeError("Can't find a solution")
            n = n + 1
            # smaller
            df_smaller = df.sample(n=n_smaller, replace=False)
            df_smaller['result'] = df_smaller['result'] - dcorr[:n_smaller]
            if min_result and (df_smaller['result'] < min_result).any():
                continue
            # larger
            df_larger = df.sample(n=n_larger, replace=False)
            df_larger['result'] = df_larger['result'] + dcorr[:n_larger]
            if max_result and (df_larger['result'] > max_result).any():
                continue
            # correct
            df_c = df.sample(n=n_correct, replace=False)

            if dev_mean_operand is not None:
                # calc means
                m_op = df_c['op1'].mean()
                m_op_s = df_smaller['op1'].mean()
                m_op_l = df_larger['op1'].mean()
                if (abs(m_op - m_op_s) > dev_mean_operand or
                        abs(m_op - m_op_l) > dev_mean_operand):
                    continue

                m_op = df_c['op2'].mean()
                m_op_s = df_smaller['op2'].mean()
                m_op_l = df_larger['op2'].mean()
                if (abs(m_op - m_op_s) > dev_mean_operand or
                        abs(m_op - m_op_l) > dev_mean_operand):
                    continue

            break

        rtn = MathProblemList()
        rtn.import_data_frame(df_c)
        rtn.import_data_frame(df_smaller)
        rtn.import_data_frame(df_larger)
        return rtn
