import io
from typing import Any, Dict, Union

import yaml

import yaml_hooks

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
#   * multiline strings in comments
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
        dumper = yaml_hooks.create_dumper(
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
        data = {"a": "1", "b": [1, 1], "c": None, "d": True}
        after = {
            "^a$": "# after a",
            "^b$": "# after b",
            "^c$": "# after c",
            "^d$": "# after d",
        }
        result = self.dump_with_args(data, after=after)
        print(result)
        assert (
            result
            == """
a: '1'
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
