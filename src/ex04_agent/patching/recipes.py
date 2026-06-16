"""Deterministic patch recipes for broken-python target files."""

from __future__ import annotations

import re
from collections.abc import Callable

WHITELIST: tuple[str, ...] = (
    "mathsquiz/mathsquiz.py",
    "polygons/polygons.py",
    "mathsquiz/mathsquiz-step2.py",
    "mathsquiz/mathsquiz-step3.py",
)


def apply_mathsquiz(text: str) -> str | None:
    """Fix Python 2 print, assignment-in-if, else-if; add score tracking."""
    if "print(" in text and "else if" not in text and "if answer =" not in text:
        return None
    out = text
    # Fix Python 2 bare print statements (not already parenthesised)
    out = re.sub(r'^(print) "([^"]*)"', r'\1("\2")', out, flags=re.MULTILINE)
    out = re.sub(r"^(print) '([^']*)'", r"\1('\2')", out, flags=re.MULTILINE)
    # Fix assignment-in-if: `if answer = N:` → `if int(answer) == N:`
    out = re.sub(r'if answer = (\d+):', r'if int(answer) == \1:', out)
    # Add score tracking on Correct! lines (only if not already there)
    def _add_score(m: re.Match) -> str:
        indent = m.group(1)
        line = m.group(2)
        if f"{indent}score += 1" in out:
            return m.group(0)
        return f"{indent}score += 1\n{indent}{line}"
    if "score += 1" not in out:
        out = re.sub(r'( +)(print\("Correct!"\))', _add_score, out)
    # Fix else-if constructs
    out = re.sub(r'else if score = (\d+):', r'elif score == \1:', out)
    out = re.sub(r'else if score < (\d+):', r'elif score < \1:', out)
    out = re.sub(r'else if score <= (\d+):', r'elif score <= \1:', out)
    return out if out != text else None


def apply_polygons(text: str) -> str | None:
    """Fix Object base class, new keyword, add main guard."""
    needs_fix = (
        "class Polygon(Object):" in text
        or "= new Polygon(" in text
        or (
            "\nsides = int(input(" in text
            and "if __name__" not in text
        )
    )
    if not needs_fix:
        return None
    out = text
    out = out.replace("class Polygon(Object):", "class Polygon:")
    out = re.sub(r'= new Polygon\(', '= Polygon(', out)
    # Wrap bare top-level execution block in main guard
    marker = "\nsides = int(input("
    if marker in out and "if __name__" not in out:
        idx = out.index(marker) + 1  # keep leading \n before the block
        preamble = out[:idx]
        block = out[idx:].rstrip()
        indented = "\n".join("    " + ln if ln.strip() else "" for ln in block.splitlines())
        out = preamble + f'\nif __name__ == "__main__":\n{indented}\n'
    return out if out != text else None


def apply_step2(text: str) -> str | None:
    """Fix global score usage in print_final_scores; add main guard."""
    needs_fix = (
        'print("You scored", score,' in text
        or ("# display welcome message" in text and "if __name__" not in text)
    )
    if not needs_fix:
        return None
    out = text
    # Replace global `score` with parameter `final_score` in function body
    out = out.replace(
        'print("You scored", score, "points out of a possible 10.")',
        'print("You scored", final_score, "points out of a possible 10.")',
    )
    out = out.replace("    if score < 5:", "    if final_score < 5:")
    out = out.replace("    elif score < 8:", "    elif final_score < 8:")
    out = out.replace("    elif score < 10:", "    elif final_score < 10:")
    out = out.replace("    elif score == 10:", "    elif final_score == 10:")
    # Wrap top-level execution in main guard
    marker = "# display welcome message"
    if marker in out and "if __name__" not in out:
        idx = out.index(marker)
        preamble = out[:idx].rstrip()
        block = out[idx:].rstrip()
        indented = "\n".join("    " + ln if ln.strip() else "" for ln in block.splitlines())
        out = preamble + f'\n\nif __name__ == "__main__":\n{indented}\n'
    return out if out != text else None


def apply_step3(text: str) -> str | None:
    """Fix global score usage in print_final_scores; add main guard."""
    needs_fix = (
        'print("You scored", score,' in text
        or "percentage = (score/max_possible_score)*100" in text
        or ("# display welcome message" in text and "if __name__" not in text)
    )
    if not needs_fix:
        return None
    out = text
    # Replace global `score` with parameter `final_score` in function body
    out = out.replace(
        'print("You scored", score, "points out of a possible",',
        'print("You scored", final_score, "points out of a possible",',
    )
    out = out.replace(
        "percentage = (score/max_possible_score)*100",
        "percentage = (final_score/max_possible_score)*100",
    )
    # Wrap top-level execution in main guard
    marker = "# display welcome message"
    if marker in out and "if __name__" not in out:
        idx = out.index(marker)
        preamble = out[:idx].rstrip()
        block = out[idx:].rstrip()
        indented = "\n".join("    " + ln if ln.strip() else "" for ln in block.splitlines())
        out = preamble + f'\n\nif __name__ == "__main__":\n{indented}\n'
    return out if out != text else None


RECIPES: dict[str, Callable[[str], str | None]] = {
    "mathsquiz/mathsquiz.py": apply_mathsquiz,
    "polygons/polygons.py": apply_polygons,
    "mathsquiz/mathsquiz-step2.py": apply_step2,
    "mathsquiz/mathsquiz-step3.py": apply_step3,
}


def get_recipe(relative_path: str) -> Callable[[str], str | None] | None:
    return RECIPES.get(relative_path)
