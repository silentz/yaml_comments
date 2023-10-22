# Yaml Comments

A python library containing pyyaml custom dumper to write comments (oneline or multiline) before and after any entity in YAML documents.
Also supports style choosing for string scalars, lists and mappings. See examples and tests to better understand what is going on here.

## Examples

### TLDR

Code:
```python
data = {"a": {"b": {"c": {"d": 1}}}}

before = {"a$": "# ba", "b$": "# bb", "c$": "# bc", "d$": "# bd"}
after = {"a$": "# aa", "b$": "# ab", "c$": "# ac", "d$": "# ad"}

dumper = yaml_comments.create_dumper(
    before=before,
    after=after,
)

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
