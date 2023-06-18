import functools
import io
import re
from dataclasses import dataclass
from typing import IO, Any, Callable, Dict, Iterable, List, Tuple, Type, Union

import yaml


@dataclass
class AbstractKey:
    index: Any

    def __str__(self) -> str:
        return str(self.index) if self.index is not None else ""


@dataclass
class _Mapping(AbstractKey):
    index: Union[str, None]


@dataclass
class _Sequence(AbstractKey):
    index: Union[int, None]


class _StreamWrapper(io.StringIO):
    def __init__(self, stream: IO):
        self._origin = stream
        self._sync = io.StringIO()

    def close(self) -> None:
        self._myflush()
        self._sync.close()

    @property
    def closed(self) -> bool:
        return self._sync.closed

    def fileno(self) -> int:
        return self._origin.fileno()

    def _myflush(self) -> None:
        self._sync.seek(0, 0)
        self._origin.write(self._sync.read())
        self._origin.flush()

    def flush(self) -> None:
        self._origin.flush()

    def isatty(self) -> bool:
        return self._origin.isatty()

    def readable(self) -> bool:
        return self._sync.readable()

    def readline(self, __size: int = -1) -> str:
        return self._sync.readline(__size)

    def readlines(self, __hint: int = -1) -> List[str]:
        return self._sync.readlines(__hint)

    def seek(self, __cookie: int, __whence: int = 0) -> int:
        return self._sync.seek(__cookie, __whence)

    def seekable(self) -> bool:
        return self._sync.seekable()

    def tell(self) -> int:
        return self._sync.tell()

    def truncate(self, __size: Union[int, None] = ...) -> int:
        return self._sync.truncate(__size)

    def writable(self) -> bool:
        return self._sync.writable()

    def writelines(self, __lines: Iterable[str]) -> None:
        return self._sync.writelines(__lines)

    def write(self, __s: str) -> int:
        return self._sync.write(__s)

    def read(self, __size: Union[int, None] = ...) -> str:
        return self._sync.read(__size)

    def lastchar(self) -> Union[str, None]:
        pos = self.tell()
        if pos <= 0:
            return None
        self.seek(pos - 1, 0)
        char = self.read(1)
        self.seek(0, 2)
        return char

    def seek_prev_line(self) -> None:
        while self.tell() > 0:
            self.seek(self.tell() - 1)
            if self.read(1) == "\n":
                return
            self.seek(self.tell() - 1)

    def __del__(self) -> None:
        if not self.closed:
            self.close()


class _Dumper(yaml.Dumper):
    _replace_marker_key = "__loc_dumper_key"
    _replace_marker_item = "__loc_dumper_item"
    _replace_marker_value = "__loc_dumper_value"

    def __init__(
        self,
        *args,
        style: Union[Dict[str, Any], None] = None,
        before: Union[Dict[str, Any], None] = None,
        after: Union[Dict[str, Any], None] = None,
        delimiter: str = "/",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._cache = dict()
        self._path = list()
        self._delim = delimiter
        self._style = style.copy() if isinstance(style, dict) else dict()
        self._after = after.copy() if isinstance(after, dict) else dict()
        self._before = before.copy() if isinstance(before, dict) else dict()
        self._last_hooked_after = None
        self.stream = _StreamWrapper(self.stream)  # type: ignore

    def __del__(self):
        self.stream.__del__()  # type: ignore

    def _repr_path(self) -> str:
        return self._delim.join(str(x) for x in self._path)

    def _is_last_sequence(self, path: str) -> bool:
        try:
            int(path.split(self._delim)[-1])
            return True
        except:
            return False

    def _cache_node(self, prefix: str, node: yaml.Node) -> None:
        cache_path = f"{prefix}:{self._repr_path()}"
        self._cache[cache_path] = node.value
        node.value = cache_path

    def _extract_marker(self, text: str) -> Tuple[Union[str, None], str]:
        if text.startswith(self._replace_marker_key):
            return self._replace_marker_key, text[text.find(":") + 1 :]
        if text.startswith(self._replace_marker_value):
            return self._replace_marker_value, text[text.find(":") + 1 :]
        if text.startswith(self._replace_marker_item):
            return self._replace_marker_item, text[text.find(":") + 1 :]
        return None, ""

    def serialize_node(self, node, parent, index):
        if isinstance(node, yaml.MappingNode):
            if len(self._path) > 0:
                if isinstance(self._path[-1], _Sequence) and isinstance(index, int):
                    self._path[-1].index = index
            self._path.append(_Mapping(None))
        elif isinstance(node, yaml.SequenceNode):
            if len(self._path) > 0:
                if isinstance(self._path[-1], _Sequence) and isinstance(index, int):
                    self._path[-1].index = index
            self._path.append(_Sequence(None))
        elif isinstance(node, yaml.ScalarNode):
            if len(self._path) > 0:
                if isinstance(self._path[-1], _Mapping):
                    if index is None:  # key ScalarNode
                        self._path[-1].index = node.value
                        self._cache_node(self._replace_marker_key, node)
                    else:  # value ScalarNode
                        self._cache_node(self._replace_marker_value, node)
                if isinstance(self._path[-1], _Sequence) and isinstance(index, int):
                    self._path[-1].index = index
                    self._cache_node(self._replace_marker_item, node)

        if isinstance(node, yaml.ScalarNode) and index is not None:
            for rule, style in self._style.items():
                if re.match(rule, self._repr_path()):
                    node.style = style

        super().serialize_node(node, parent, index)

        if isinstance(node, yaml.MappingNode):
            self._path.pop()
        elif isinstance(node, yaml.SequenceNode):
            self._path.pop()
        elif isinstance(node, yaml.ScalarNode):
            if isinstance(self._path[-1], _Mapping):
                if index is not None:
                    self._path[-1].index = None
            if isinstance(self._path[-1], _Sequence) and isinstance(index, int):
                self._path[-1].index = None

    def analyze_scalar(self, scalar: str):
        marker_type, _ = self._extract_marker(scalar)
        if marker_type is not None:
            from_cache = self._cache[scalar]
            result = super().analyze_scalar(from_cache)
            result.scalar = scalar
            return result
        return super().analyze_scalar(scalar)

    def resolve(self, kind, value, implicit):
        if kind is yaml.ScalarNode:
            marker_type, _ = self._extract_marker(value)
            if marker_type is not None:
                from_cache = self._cache[value]
                return super().resolve(kind, from_cache, implicit)
        return super().resolve(kind, value, implicit)

    def _get_level(self, a: str) -> int:
        return a.count(self._delim)

    def _check_same_level(self, a: str, b: str) -> bool:
        return self._get_level(a) == self._get_level(b)

    def _get_path_prev_level(self, path: str) -> str:
        tokens = path.split(self._delim)
        tokens = tokens[:-1]
        return self._delim.join(tokens)

    def represent(self, *args, **kwargs) -> None:
        super().represent(*args, **kwargs)
        if self._last_hooked_after is not None:
            rem_levels = self._get_level(self._last_hooked_after)
            if rem_levels > 0:
                for idx in range(rem_levels):
                    shift = (rem_levels - idx - 1) * self.best_indent
                    self.indents = [shift]
                    self._last_hooked_after = self._get_path_prev_level(
                        self._last_hooked_after
                    )
                    self._process_hook_after(self._last_hooked_after)
                self.indents = []

    def _hook_processor(self, inner: Callable, text: str, *args, **kwargs) -> Any:
        marker_type, path = self._extract_marker(text)

        if marker_type is not None:
            if self._last_hooked_after is not None:
                level_last = self._get_level(self._last_hooked_after)
                level_current = self._get_level(path)
                if level_last != level_current:
                    prev_level = self._get_path_prev_level(self._last_hooked_after)
                    copy_indents = self.indents
                    self.indents = [(level_last - 1) * self.best_indent]
                    self._process_hook_after(prev_level)
                    self._last_hooked_after = prev_level
                    self.indents = copy_indents

            text = self._cache[text]
            if marker_type == self._replace_marker_key:
                self._process_hook_before(path)
            elif marker_type == self._replace_marker_item:
                self._process_hook_before(path)

        inner_out = inner(text, *args, **kwargs)

        if marker_type is not None:
            if marker_type == self._replace_marker_value:
                self._process_hook_after(path)
                self._last_hooked_after = path
            elif marker_type == self._replace_marker_item:
                self._process_hook_after(path)
                self._last_hooked_after = path

        return inner_out

    def write_plain(self, text, split=True):
        return self._hook_processor(super().write_plain, text, split)

    def write_folded(self, text):
        return self._hook_processor(super().write_folded, text)

    def write_literal(self, text):
        return self._hook_processor(super().write_literal, text)

    def write_single_quoted(self, text, split=True):
        return self._hook_processor(super().write_single_quoted, text, split)

    def write_double_quoted(self, text, split=True):
        return self._hook_processor(super().write_double_quoted, text, split)

    def _process_hook_before(self, path: str) -> None:
        for rule, data in self._before.items():
            if re.search(rule, path):
                cur_indent = self.column
                lines = data.split("\n")
                lines = [" " * cur_indent + x for x in lines]
                lines[0] = lines[0].lstrip()

                if self._is_last_sequence(path):
                    self.stream.seek_prev_line()  # type: ignore
                    self.stream.write(" " * self.indents[-1])

                for line in lines:
                    self.stream.write(line + "\n")
                    self.line += 1

                if self._is_last_sequence(path):
                    self.stream.write(" " * max(0, cur_indent - 1))
                    self.stream.write("-")
                else:
                    self.stream.write(" " * cur_indent)

    def _process_hook_after(self, path: str) -> None:
        for rule, data in self._after.items():
            if re.search(rule, path):
                cur_indent = self.indents[-1]
                lines = data.split("\n")
                lines = [" " * cur_indent + x for x in lines]
                lines = [x.rstrip() for x in lines]

                if self.stream.lastchar() != "\n":  # type: ignore
                    self.stream.write("\n")
                    self.line += 1

                for line in lines:
                    self.stream.write(line + "\n")
                    self.line += 1

                self.column = 0
                self.whitespace = True
                self.indention = True


def create_dumper(
    style: Union[Dict[str, Any], None] = None,
    before: Union[Dict[str, Any], None] = None,
    after: Union[Dict[str, Any], None] = None,
    delimiter: str = "/",
) -> Type[_Dumper]:
    return functools.partial(
        _Dumper,
        style=style,
        after=after,
        before=before,
        delimiter=delimiter,
    )  # type: ignore
