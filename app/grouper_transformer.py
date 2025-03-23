from typing import Callable
from lark import Transformer, v_args

from . import group_parser

class GrouperGroupTransformer(Transformer):
    def _unescape(self, text):
        """Unescape special characters in a tag."""
        result = ""
        i = 0
        while i < len(text):
            if text[i] == '\\' and i + 1 < len(text):
                i += 1
                result += text[i]
            else:
                result += text[i]
            i += 1
        return result

    @v_args(inline=True)
    def single_tag_group(self, tag):
        target = self._unescape(str(tag))
        matcher = lambda tags, _: target in tags
        return _Grouper(matcher)

    @v_args(inline=True)
    def ungrouped(self):
        return _Grouper(lambda _, x: x)

    @v_args(inline=True)
    def all_group(self, *composable_group_set):
        # every first item will be a _Grouper, and every other item will be a separator
        checks = []
        for i, group in enumerate(composable_group_set):
            if i%2 != 0:
                continue
            checks.append(group.matcher)
        matcher = lambda tags, g: all([m(tags, g) for m in checks])
        return _Grouper(matcher)

    @v_args(inline=True)
    def WS(self, *_):
        return None

    @v_args(inline=True)
    def any_group(self, *composable_group_set):
        # every first item will be a _Grouper, and every other item will be a separator
        checks = []
        for i, group in enumerate(composable_group_set):
            if i%2 != 0:
                continue
            checks.append(group.matcher)
        def matcher(tags, g):
            for check in checks:
                if check(tags, g):
                    return True
            return False
        return _Grouper(matcher)

    @v_args(inline=True)
    def named_group(self, title, _, nameable_group):
        return _Grouper(nameable_group.matcher, title=self._unescape(str(title)))

    @v_args(inline=True)
    def groups(self, *groupers):
        return Grouper(list(groupers))

class _Grouper:
    def __init__(self, matcher: Callable[[list[str], bool], bool], title: str | None = None):
        self.matcher = matcher
        self.title = title

class Grouper:
    def __init__(self, groupers: list[_Grouper]):
        self.groupers = groupers
    def get_groups(self) -> list[str | None]:
        return [i.title for i in self.groupers]
    def get_group_index(self, tags: list[str]) -> int | None:
        # grouped search
        for i, grouper in enumerate(self.groupers):
            if grouper.matcher(tags, False):
                return i
        # ungrouped search
        for i, grouper in enumerate(self.groupers):
            if grouper.matcher(tags, True):
                return i
        return None

_grouper_transformer = GrouperGroupTransformer()

def create_grouper(group_string) -> Grouper:
    tree = group_parser._parser.parse(group_string)
    return _grouper_transformer.transform(tree)

def _test_cases():
    s = "tag\\ 1"
    _test(s, ["tag 1"], 0)
    _test(s, ["tag2"], None)
    _test(s, ["tag 1", "tag 2"], 0)
    _test(s, ["tag 12"], None)

    s = "t1 t2"
    _test(s, ["t1"], 0)
    _test(s, ["t2"], 1)
    _test(s, ["t3"], None)
    _test(s, ["t1", "t2"], 0)

    s = "$all(t1 t2) $any(t2 t3) t4"
    _test(s, ["t1"], None)
    _test(s, ["t2"], 1)
    _test(s, ["t1", "t2"], 0)
    _test(s, ["t1", "t2", "t3"], 0)
    _test(s, ["t3"], 1)
    _test(s, ["t4"], 2)
    _test(s, ["t5"], None)

    s = "$named(Some\\ Name t1) t2"
    _test(s, ["t1"], 0)
    _test(s, ["t2"], 1)
    _test(s, ["t1", "t2"], 0)
    _test(s, ["t3"], None)

    s = "t1 $ungrouped t2"
    _test(s, ["t1"], 0)
    _test(s, ["t2"], 2)
    _test(s, ["t1", "t2"], 0)
    _test(s, ["t3"], 1)
    _test(s, ["t3", "t2"], 2)

    s = "$ungrouped"
    _test(s, ["t1"], 0)

    s = "$named(Name $any($all(t1 t2) t3)) $named(Other $ungrouped) t4"
    _test(s, ["t1"], 1)
    _test(s, ["t2"], 1)
    _test(s, ["t1", "t2"], 0)
    _test(s, ["t3"], 0)
    _test(s, ["t4"], 2)
    _test(s, ["t5"], 1)

    s = "$all(t1 t2 t3 t4 t5) $any(t1 t2 t3 t4 t5)"
    _test(s, ["t1"], 1)
    _test(s, ["t2"], 1)
    _test(s, ["t3"], 1)
    _test(s, ["t4"], 1)
    _test(s, ["t5"], 1)
    _test(s, ["t1", "t2", "t3", "t4", "t5"], 0)
    _test(s, ["t1", "t2", "t3", "t4", "t5", "t6"], 0)

def _test(group_string: str, tags: list[str], expected: int | None):
    verbose = True
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

    m = f"group string: {group_string}\n"
    tree = group_parser._parser.parse(group_string)
    grouper = _grouper_transformer.transform(tree)
    groups = grouper.get_groups()
    m += f"groups: {groups} ({len(groups)})\n"
    group = grouper.get_group_index(tags)
    m += f'tags: {tags}\n'
    m += f'group {group}, expected {expected}, '

    passed = group == expected
    m += (f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}")
    if verbose or not passed:
        print(m)
        print('-'*50)

if __name__ == "__main__":
    _test_cases()

