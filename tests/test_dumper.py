import io
import os
import sys
from typing import Any, Dict, Union

sys.path.insert(0, os.path.abspath(os.curdir))

import yaml

import yaml_utils

# TODO lists:
#   * test before/after first list iter
#   * test before/after last list iterm
#   * test before/after inner list item
#   * test on empty lists
#   * test on single-item lists

# TODO indents:
#   * test different indents

# TODO misc:
#   * high depth of data structures
#   * comment before list vs comment before first list item
#   * before/after list item inside a dict
#   * before/after dict item inside a list


class Tests:
    def dump_with_args(
        self,
        data: Any,
        before: Union[Dict[str, Any], None] = None,
        after: Union[Dict[str, Any], None] = None,
        style: Union[Dict[str, Any], None] = None,
    ) -> str:
        # run custom dumper with args and return result
        dumper = yaml_utils.create_dumper(
            before=before,
            after=after,
            style=style,
            delimiter="/",
        )
        buffer = io.StringIO(initial_value="")
        yaml.dump(data, buffer, dumper)
        buffer.seek(0)
        return buffer.getvalue()

    def test_before_global_keys(self) -> None:
        data = {"a": "1", "b": [1, 1], "c": None, "d": True}
        before = {
            "^a$": "# before a",
            "^b$": "# before b",
            "^c$": "# before c",
            "^d$": "# before d",
        }
        result = self.dump_with_args(data, before=before)
        assert (
            result
            == """
# before a
a: '1'
# before b
b:
- 1
- 1
# before c
c: null
# before d
d: true
""".lstrip()
        )

    def test_after_global_keys(self) -> None:
        data = {"a": {"test": 1}, "b": [1, 1], "c": None, "d": True}
        after = {
            "^a$": "# after a",
            "^b$": "# after b",
            "^c$": "# after c",
            "^d$": "# after d",
        }
        result = self.dump_with_args(data, after=after)
        assert (
            result
            == """
a:
  test: 1
# after a
b:
- 1
- 1
# after b
c: null
# after c
d: true
# after d
""".lstrip()
        )

    def test_multiple_lines(self) -> None:
        data = {"a": {"test": 1}, "b": [1, 1], "c": None, "d": True}
        before = {
            "^a$": "# before a 1\n# before a 2",
            "^b$": "# before b 1\n# before b 2",
            "^c$": "# before c 1\n# before c 2",
            "^d$": "# before d 1\n# before d 2",
        }
        after = {
            "^a$": "# after a 1\n# after a 2",
            "^b$": "# after b 1\n# after b 2",
            "^c$": "# after c 1\n# after c 2",
            "^d$": "# after d 1\n# after d 2",
        }
        result = self.dump_with_args(data, after=after, before=before)
        assert (
            result
            == """
# before a 1
# before a 2
a:
  test: 1
# after a 1
# after a 2
# before b 1
# before b 2
b:
- 1
- 1
# after b 1
# after b 2
# before c 1
# before c 2
c: null
# after c 1
# after c 2
# before d 1
# before d 2
d: true
# after d 1
# after d 2
""".lstrip()
        )

    def test_high_depth(self) -> None:
        data = {"a": {"b": {"c": {"d": 1}}}}
        before = {"a": "# ba", "b": "# bb", "c": "# bc", "d": "#bd"}
        after = {"a": "# aa", "b": "# ab", "c": "# ac", "d": "# ad"}
        result = self.dump_with_args(data, after=after, before=before)

        assert (
            result
            == """
# ba
a:
  # bb
  b:
    # bc
    c:
      # bd
      d: 1
      # ad
    # ac
  # ab
# aa
        """.lstrip()
        )
