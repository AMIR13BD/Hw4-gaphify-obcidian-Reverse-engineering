"""Tests for deterministic patch recipes."""

from __future__ import annotations

from ex04_agent.patching.recipes import apply_mathsquiz, apply_polygons, apply_step2, apply_step3
from ex04_agent.patching.validator import validate_text

MATHSQUIZ_BROKEN = """\
print "Hello!"
score = 0
answer = input("? ")
if answer = 55:
    print("Correct!")
else:
    print("Wrong!")
if score < 5:
    print("low")
else if score < 8:
    print("ok")
else if score = 10:
    print("great")
"""

POLYGONS_BROKEN = """\
import turtle
class Polygon(Object):
    def __init__(self, sides):
        self.sides = sides
def calc(sides):
    poly = new Polygon(sides)
    return poly
sides = int(input("sides? "))
calc(sides)
"""

STEP2_ALREADY_FIXED = """\
def print_final_scores(final_score):
    print("You scored", final_score, "out of 10.")
if __name__ == "__main__":
    score = 0
    print_final_scores(score)
"""


def test_mathsquiz_recipe_fixes_syntax() -> None:
    result = apply_mathsquiz(MATHSQUIZ_BROKEN)
    assert result is not None
    ok, _ = validate_text(result)
    assert ok, "Fixed mathsquiz should be valid Python 3"
    assert "score += 1" in result
    assert 'print("Hello!")' in result


def test_mathsquiz_recipe_returns_none_when_already_fixed() -> None:
    already_fixed = 'print("Hello!")\nscore = 0\nif int(answer) == 55:\n    score += 1\n    print("Correct!")\n'
    assert apply_mathsquiz(already_fixed) is None


def test_polygons_recipe_fixes_object_and_new() -> None:
    result = apply_polygons(POLYGONS_BROKEN)
    assert result is not None
    assert "class Polygon:" in result
    assert "new Polygon" not in result
    ok, _ = validate_text(result)
    assert ok


def test_polygons_recipe_adds_main_guard() -> None:
    result = apply_polygons(POLYGONS_BROKEN)
    assert result is not None
    assert 'if __name__ == "__main__"' in result


def test_step2_recipe_fixes_global_score() -> None:
    """step2 recipe replaces global score with parameter and adds main guard."""
    assert apply_step2(STEP2_ALREADY_FIXED) is None

    broken = (
        'def print_final_scores(final_score):\n'
        '    print("You scored", score, "points out of a possible 10.")\n'
        '    if score < 5:\n'
        '        print("low")\n'
        '\n# display welcome message\nwelcome_message()\n'
    )
    result = apply_step2(broken)
    assert result is not None
    assert 'print("You scored", final_score,' in result
    assert 'if final_score < 5:' in result
    assert 'if __name__ == "__main__"' in result
    ok, _ = validate_text(result)
    assert ok


def test_step3_recipe_fixes_global_score() -> None:
    """step3 recipe replaces global score with parameter and adds main guard."""
    broken = (
        'def print_final_scores(final_score, max_possible_score):\n'
        '    print("You scored", score, "points out of a possible", max_possible_score)\n'
        '    percentage = (score/max_possible_score)*100\n'
        '    if percentage < 50:\n'
        '        print("low")\n'
        '\n# display welcome message\nwelcome_message()\n'
    )
    result = apply_step3(broken)
    assert result is not None
    assert 'print("You scored", final_score,' in result
    assert 'percentage = (final_score/max_possible_score)*100' in result
    assert 'if __name__ == "__main__"' in result
    ok, _ = validate_text(result)
    assert ok
