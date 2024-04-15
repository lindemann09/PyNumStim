import os
from pathlib import Path
from typing import Optional, Union
from sympy import preview

from ._problem import MathProblem, LATEX_SYMBOL_NAMES
from ._mplist import MathProblemList


def create_images(
        source: Union[str, MathProblem, MathProblemList],
        path: Optional[Union[Path, str]] = None,
        segmented=False,
        resolution: int = 400,
        fg: str = "White",
        bg: str = "Transparent"):

    if path is None:
        if isinstance(source, MathProblem):
            path = source.label() + ".png"  # use label
        else:
            raise ValueError(
                f"Path is required, if you create images from {type(source)}"
            )

    if isinstance(source, MathProblem):
        return _from_problem(source, folder=path, segmented=segmented,
                             resolution=resolution, fg=fg, bg=bg)
    elif isinstance(source, MathProblemList):
        return _from_problem_list(source, folder=path, segmented=segmented,
                                  resolution=resolution, fg=fg, bg=bg)
    elif isinstance(source, str):
        return _from_tex(source, filename=path, resolution=resolution, fg=fg, bg=bg)


def _from_tex(
        tex_str: str,
        filename: Union[Path, str],
        resolution: int = 400,
        fg: str = "White",
        bg: str = "Transparent"):
    """latex to PNG"""
    return preview(tex_str,
                   dvioptions=["-D", str(resolution), "-fg", fg, "-bg", bg],
                   viewer="file", filename=filename,
                   euler=False)


def _from_problem(
        problem: MathProblem,
        folder: Union[Path, str],
        segmented: bool = False,
        resolution: int = 400,
        fg: str = "White",
        bg: str = "Transparent") -> str:
    """returns the filename, if not segmented"""

    os.makedirs(folder, exist_ok=True)
    flname = os.path.join(folder, "p" + f"{problem.label()}.png")
    if not segmented:
        _from_tex(f"$${problem.tex()}$$", filename=flname,
                  resolution=resolution, fg=fg, bg=bg)
    else:
        # segmented
        os.makedirs(folder, exist_ok=True)
        _create_latex_symbols(folder, resolution=resolution, fg=fg, bg=bg)
        stim = set()
        stim.add((problem.operant1.tex(), problem.operant1.label()))
        stim.add((problem.operant2.tex(), problem.operant2.label()))
        if problem.result is not None:
            stim.add((problem.result.tex(), problem.result.label()))
        for tex, label in stim:
            print("png: " + label)
            _from_tex(f"$${tex}$$",
                      filename=os.path.join(folder, "n" + f"{label}.png"),
                      resolution=resolution, fg=fg, bg=bg)

    return flname


def _from_problem_list(
        problems: MathProblemList,
        folder: Union[Path, str],
        segmented=False,
        resolution: int = 400,
        fg: str = "White",
        bg: str = "Transparent"):
    """segmented: single files for each number and operation"""
    # make pictures
    os.makedirs(folder, exist_ok=True)
    if not segmented:
        done = set()
        for x in problems.list:
            print("png: ", x.label())
            if x.label() not in done:
                _from_problem(x, folder=folder, segmented=False,
                              resolution=resolution, fg=fg, bg=bg)
                done.add(x.label())
    else:
        _create_latex_symbols(folder=folder,
                              resolution=resolution, fg=fg, bg=bg)
        # problem_stimuli
        stim = set()
        for x in problems.list:
            stim.add((x.operant1.tex(), x.operant1.label()))
            stim.add((x.operant2.tex(), x.operant2.label()))
            if x.result is not None:
                stim.add((x.result.tex(), x.result.label()))

        for tex, label in stim:
            print("png: " + label)
            _from_tex(f"$${tex}$$",
                      filename=os.path.join(folder, "n" + f"{label}.png"),
                      resolution=resolution,
                      fg=fg, bg=bg)


def _create_latex_symbols(folder: Union[Path, str],
                          resolution: int = 400,
                          fg: str = "White",
                          bg: str = "Transparent"):
    # create symbols, segmented
    for symbol, name in LATEX_SYMBOL_NAMES.items():
        _from_tex(f"$${symbol}$$",
                  filename=os.path.join(folder, f"{name}.png"),
                  resolution=resolution, fg=fg, bg=bg)
