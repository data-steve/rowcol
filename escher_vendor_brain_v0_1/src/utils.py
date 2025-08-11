import re
import string
from typing import List

def strip_tokens(s: str, tokens: List[str]) -> str:
    out = s
    for t in tokens:
        out = out.replace(t, " ")
    return out

def collapse_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def strip_digits_runs(s: str, n: int = 6) -> str:
    return re.sub(rf"(\d{{{n},}})", " ", s)

def strip_punct(s: str) -> str:
    tbl = str.maketrans({p:" " for p in string.punctuation})
    return s.translate(tbl)
