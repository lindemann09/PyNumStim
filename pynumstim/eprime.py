"""creating trial list from data_frame for e-prime"""
import pandas as _pd

def write_trial_list(math_problem_data_frame: _pd.DataFrame,
                     filename: str,
                     procedure: str,
                     weight: int = 1,
                     nested: str = '',
                     rounding_digits: int = 2):
    """save as as tab limited file compatible with e-prime

    Note: Pandas `to_csv()`method adds an line terminator at the last row,
    which causes problems in e-prime
    """

    df = math_problem_data_frame.round(rounding_digits)
    df.insert(0, "Weight", weight)
    df.insert(1, "Nested", nested)
    df.insert(2, "Procedure", procedure)
    # create csv
    content = df.to_csv(sep="\t", index=False, lineterminator="\n")
    with open(filename, "w", encoding='utf-8') as fl:
        fl.write(content[:-1])