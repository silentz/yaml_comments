# Yaml Comments

A python library containing pyyaml custom dumper to write comments (oneline or multiline) before and after any entity in YAML documents.
Also supports style choosing for string scalars, lists and mappings. See examples and tests to better understand what is going on here.

## Examples

You can find more examples on using this lib in [tests/test_dumper.py](/tests/test_dumper.py). These examples
include different corner cases, like adding a comment to N-th list element or to a specific dict key or value.

### Basic case

In this example descriptor for writing a comment looks like this: `$a/b/c/d/1$`. This path
is composed of dict keys and list indexes, and `/` delimiter. If you want to use some other delimiter, you
should pass it to `create_dumper` function like this: `yaml_comments.create_dumper(..., delimiter="#")`

Code:
```python
import yaml
import yaml_comments

data = {"a": {"b": {"c": {"d": [1, 2]}}}}
before = {"^a/b/c/d/1$": "# test comment"}

with open("result.yml", "w") as file:
    dumper = yaml_comments.create_dumper(before=before)
    yaml.dump(data, file, dumper)
```

Result:
```yaml
a:
  b:
    c:
      d:
      - 1
      # test comment
      - 2
```

### Before and after comments

Code:
```python
import yaml
import yaml_comments

data = {"a": {"b": {"c": {"d": 1}}}}
before = {"a$": "# ba", "b$": "# bb", "c$": "# bc", "d$": "# bd"}
after = {"a$": "# aa", "b$": "# ab", "c$": "# ac", "d$": "# ad"}

with open("result.yml", "w") as file:
    dumper = yaml_comments.create_dumper(before=before, after=after)
    yaml.dump(data, file, dumper)
```

Result:
```yaml
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
```

### List styles

Code:
```python
import yaml
import yaml_comments

data = {"a": [1, 2, 3], "b": [1, 2, 3]}
flow_style = {"a": yaml_comments.EXPAND, "b": yaml_comments.INLINE}

with open("result.yml", "w") as file:
    dumper = yaml_comments.create_dumper(flow_style=flow_style)
    yaml.dump(data, file, dumper)
```

Result:
```yaml
a:
- 1
- 2
- 3
b: [1, 2, 3]
```

### Dict styles

Code:
```python
import yaml
import yaml_comments

data = {"a": {"k1": "v1", "k2": "v2"}, "b": {"k1": "v1", "k2": "v2"}}
flow_style = {"a": yaml_comments.EXPAND, "b": yaml_comments.INLINE}

with open("result.yml", "w") as file:
    dumper = yaml_comments.create_dumper(flow_style=flow_style)
    yaml.dump(data, file, dumper)
```

Result:
```yaml
a:
  k1: v1
  k2: v2
b: {k1: v1, k2: v2}
```

### String scalar styles

Code:
```python
import yaml
import yaml_comments

data = {"a": "test",
        "b": "test",
        "c": "multiline string n1\ntest",
        "d": "multiline string n2\ntest"}

style = {"a": yaml_comments.SINGLE_QUOTE,
         "b": yaml_comments.DOUBLE_QUOTE,
         "c": yaml_comments.FOLDED,
         "d": yaml_comments.LITERAL}

with open("result.yml", "w") as file:
    dumper = yaml_comments.create_dumper(style=style)
    yaml.dump(data, file, dumper)
```

Result:
```yaml
a: 'test'
b: "test"
c: >-
  multiline string n1

  test
d: |-
  multiline string n2
  test
```
