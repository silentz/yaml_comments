import io
import os
import sys
from typing import Any, Dict, Union

sys.path.insert(0, os.path.abspath(os.curdir))

import yaml

import yaml_comments


class Tests:
    def dump_with_args(
        self,
        data: Any,
        before: Union[Dict[str, Any], None] = None,
        after: Union[Dict[str, Any], None] = None,
        style: Union[Dict[str, Any], None] = None,
        indent: int = 2,
    ) -> str:
        # run custom dumper with args and return result
        dumper = yaml_comments.create_dumper(
            before=before,
            after=after,
            style=style,
            delimiter="/",
        )
        buffer = io.StringIO(initial_value="")
        yaml.dump(data, buffer, dumper, indent=indent)
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
        before = {"a$": "# ba", "b$": "# bb", "c$": "# bc", "d$": "# bd"}
        after = {"a$": "# aa", "b$": "# ab", "c$": "# ac", "d$": "# ad"}
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

    def test_list(self) -> None:
        data = {"a": 1, "b": {"i": [1, 2, 3, 4, 5]}, "c": 1}
        before = {
            "^b/i$": "# before list",
            "^b/i/0$": "# before first item",
            "^b/i/2$": "# before middle item",
            "^b/i/4$": "# before last item",
        }
        after = {
            "^b/i$": "# after list",
            "^b/i/0$": "# after first item",
            "^b/i/2$": "# after middle item",
            "^b/i/4$": "# after last item",
        }
        result = self.dump_with_args(data, before=before, after=after)

        assert (
            result
            == """
a: 1
b:
  # before list
  i:
  # before first item
  - 1
  # after first item
  - 2
  # before middle item
  - 3
  # after middle item
  - 4
  # before last item
  - 5
  # after last item
  # after list
c: 1
""".lstrip()
        )

    def test_single_item_list(self) -> None:
        data = {"a": {"b": {"c": [1]}}}
        before = {
            "^a/b/c$": "# before list",
            "^a/b/c/0$": "# before first item",
        }
        after = {
            "^a/b/c$": "# after list",
            "^a/b/c/0$": "# after first item",
        }
        result = self.dump_with_args(data, before=before, after=after)

        assert (
            result
            == """
a:
  b:
    # before list
    c:
    # before first item
    - 1
    # after first item
    # after list
""".lstrip()
        )

    def test_empty_list(self) -> None:
        data = {"a": {"b": {"c": []}}}
        before = {
            "^a/b/c$": "# before list",
            "^a/b/c/0$": "# before first item",
        }
        after = {
            "^a/b/c$": "# after list",
            "^a/b/c/0$": "# after first item",
        }
        result = self.dump_with_args(data, before=before, after=after)

        assert (
            result
            == """
a:
  b:
    # before list
    c: []
    # after list
""".lstrip()
        )

    def test_empty_dict(self) -> None:
        data = {"a": {"b": {"c": {}}}}
        before = {
            "^a/b/c$": "# before dict",
            "^a/b/c/x$": "# before x",
        }
        after = {
            "^a/b/c$": "# after dict",
            "^a/b/c/x$": "# after x",
        }
        result = self.dump_with_args(data, before=before, after=after)

        assert (
            result
            == """
a:
  b:
    # before dict
    c: {}
    # after dict
""".lstrip()
        )

    def test_dict_and_list_combinations(self) -> None:
        data = {"a": [{"b": [{"c": [{"d": [1]}]}]}]}
        before = {
            "^a$": "# before a",
            "^a/0$": "# before a0",
            "^a/0/b$": "# before b",
            "^a/0/b/0$": "# before b0",
            "^a/0/b/0/c$": "# before c",
            "^a/0/b/0/c/0$": "# before c0",
            "^a/0/b/0/c/0/d$": "# before d",
            "^a/0/b/0/c/0/d/0$": "# before d0",
        }
        after = {
            "^a$": "# after a",
            "^a/0$": "# after a0",
            "^a/0/b$": "# after b",
            "^a/0/b/0$": "# after b0",
            "^a/0/b/0/c$": "# after c",
            "^a/0/b/0/c/0$": "# after c0",
            "^a/0/b/0/c/0/d$": "# after d",
            "^a/0/b/0/c/0/d/0$": "# after d0",
        }
        result = self.dump_with_args(data, before=before, after=after)

        assert (
            result
            == """
# before a
a:
# before a0
- # before b
  b:
  # before b0
  - # before c
    c:
    # before c0
    - # before d
      d:
      # before d0
      - 1
      # after d0
      # after d
    # after c0
    # after c
  # after b0
  # after b
# after a0
# after a
""".lstrip()
        )

    def test_different_indent_04(self) -> None:
        data = {"a": [{"b": [{"c": [1]}]}]}
        before = {
            "^a$": "# before a",
            "^a/0$": "# before a0",
            "^a/0/b$": "# before b",
            "^a/0/b/0$": "# before b0",
            "^a/0/b/0/c$": "# before c",
            "^a/0/b/0/c/0$": "# before c0",
        }
        after = {
            "^a$": "# after a",
            "^a/0$": "# after a0",
            "^a/0/b$": "# after b",
            "^a/0/b/0$": "# after b0",
            "^a/0/b/0/c$": "# after c",
            "^a/0/b/0/c/0$": "# after c0",
        }
        result = self.dump_with_args(data, before=before, after=after, indent=4)

        assert (
            result
            == """
# before a
a:
# before a0
-   # before b
    b:
    # before b0
    -   # before c
        c:
        # before c0
        - 1
        # after c0
        # after c
    # after b0
    # after b
# after a0
# after a
""".lstrip()
        )

    def test_different_indent_07(self) -> None:
        data = {"a": [{"b": [{"c": [1]}]}]}
        before = {
            "^a$": "# before a",
            "^a/0$": "# before a0",
            "^a/0/b$": "# before b",
            "^a/0/b/0$": "# before b0",
            "^a/0/b/0/c$": "# before c",
            "^a/0/b/0/c/0$": "# before c0",
        }
        after = {
            "^a$": "# after a",
            "^a/0$": "# after a0",
            "^a/0/b$": "# after b",
            "^a/0/b/0$": "# after b0",
            "^a/0/b/0/c$": "# after c",
            "^a/0/b/0/c/0$": "# after c0",
        }
        result = self.dump_with_args(data, before=before, after=after, indent=7)

        assert (
            result
            == """
# before a
a:
# before a0
-      # before b
       b:
       # before b0
       -      # before c
              c:
              # before c0
              - 1
              # after c0
              # after c
       # after b0
       # after b
# after a0
# after a
""".lstrip()
        )

    def test_different_indent_multiline(self) -> None:
        data = {"a": [{"b": [{"c": [11]}]}]}
        before = {
            "^a$": "# before a\n# before a",
            "^a/0$": "# before a0\n# before a0",
            "^a/0/b$": "# before b\n# before b",
            "^a/0/b/0$": "# before b0\n# before b0",
            "^a/0/b/0/c$": "# before c\n# before c",
            "^a/0/b/0/c/0$": "# before c0\n# before c0",
        }
        after = {
            "^a$": "# after a\n# after a",
            "^a/0$": "# after a0\n# after a0",
            "^a/0/b$": "# after b\n# after b",
            "^a/0/b/0$": "# after b0\n# after b0",
            "^a/0/b/0/c$": "# after c\n# after c",
            "^a/0/b/0/c/0$": "# after c0\n# after c0",
        }
        result = self.dump_with_args(data, before=before, after=after, indent=3)

        assert (
            result
            == """
# before a
# before a
a:
# before a0
# before a0
-  # before b
   # before b
   b:
   # before b0
   # before b0
   -  # before c
      # before c
      c:
      # before c0
      # before c0
      - 11
      # after c0
      # after c0
      # after c
      # after c
   # after b0
   # after b0
   # after b
   # after b
# after a0
# after a0
# after a
# after a
""".lstrip()
        )

    def test_string_style_single_quote(self) -> None:
        data = {"a": [{"b": [{"c": ["11"]}]}]}
        style = {
            "^a/0/b/0/c/0$": yaml_comments.SINGLE_QUOTE,
        }
        result = self.dump_with_args(data, style=style, indent=2)

        assert (
            result
            == """
a:
- b:
  - c:
    - '11'
""".lstrip()
        )

    def test_string_style_double_quote(self) -> None:
        data = {"a": [{"b": [{"c": ["11"]}]}]}
        style = {
            "^a/0/b/0/c/0$": yaml_comments.DOUBLE_QUOTE,
        }
        result = self.dump_with_args(data, style=style, indent=2)

        assert (
            result
            == """
a:
- b:
  - c:
    - "11"
""".lstrip()
        )

    def test_string_style_literal(self) -> None:
        data = {"a": "abc"}
        style = {
            "^a$": yaml_comments.LITERAL,
        }
        result = self.dump_with_args(data, style=style, indent=2)

        assert (
            result
            == """
a: |-
  abc
""".lstrip()
        )

    def test_string_style_literal_newline_01(self) -> None:
        data = {"a": "abc\n"}
        style = {
            "^a$": yaml_comments.LITERAL,
        }
        result = self.dump_with_args(data, style=style, indent=2)

        assert (
            result
            == """
a: |
  abc
""".lstrip()
        )

    def test_string_style_literal_newline_02(self) -> None:
        data = {"a": "abc\n\n"}
        style = {
            "^a$": yaml_comments.LITERAL,
        }
        result = self.dump_with_args(data, style=style, indent=2)

        assert (
            result
            == """
a: |+
  abc

...
""".lstrip()
        )

    def test_string_style_folded(self) -> None:
        data = {"a": "abc"}
        style = {
            "^a$": yaml_comments.FOLDED,
        }
        result = self.dump_with_args(data, style=style, indent=2)

        assert (
            result
            == """
a: >-
  abc
""".lstrip()
        )

    def test_string_style_folded_newline_01(self) -> None:
        data = {"a": "abc\n"}
        style = {
            "^a$": yaml_comments.FOLDED,
        }
        result = self.dump_with_args(data, style=style, indent=2)

        assert (
            result
            == """
a: >
  abc
""".lstrip()
        )

    def test_string_style_folded_newline_02(self) -> None:
        data = {"a": "abc\n\n"}
        style = {
            "^a$": yaml_comments.FOLDED,
        }
        result = self.dump_with_args(data, style=style, indent=2)

        assert (
            result
            == """
a: >+
  abc

...
""".lstrip()
        )

# TODO styles:
#   * test different list styles + comments
#   * test different dict styles + comments
