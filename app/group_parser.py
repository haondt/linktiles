from lark import Lark, Transformer, UnexpectedCharacters, UnexpectedToken, v_args

# Define the updated Lark grammar
GRAMMAR = """
groups: _group*

_group: _composable_group | ungrouped | named_group

single_tag_group: TAG
all_group: "$all(" _composable_group_set ")"
any_group: "$any(" _composable_group_set ")"

_composable_group: single_tag_group | all_group | any_group
_composable_group_set: _composable_group (WS _composable_group)*

ungrouped: "$ungrouped"
_nameable_group: _composable_group | ungrouped
named_group: "$named(" _title WS _nameable_group ")"
_title: TAG

// Basic terminals
TAG: /(([^$()\\s\\\\])|(\\\\[$()\\s\\\\]))+/  // Match any non-special char or escaped special char
WS: /\\s+/

%ignore WS  // Ignore whitespace between elements
"""

class PrettyPrintGroupTransformer(Transformer):
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
        return str(tag)
        # return ('simple', self._unescape(str(tag)))

    @v_args(inline=True)
    def ungrouped(self):
        return "$ungrouped"
        # return ('ungrouped', None)

    @v_args(inline=True)
    def all_group(self, *composable_group_set):
        return f"$all({''.join(composable_group_set)})"
        # return ('all_of', composable_group_set)

    @v_args(inline=True)
    def WS(self, *_):
        return ' '

    @v_args(inline=True)
    def any_group(self, *composable_group_set):
        return f"$any({''.join(composable_group_set)})"
        # return ('any_of', composable_group_set)

    @v_args(inline=True)
    def named_group(self, title, _, nameable_group):
        return f"$named({title} {nameable_group})"

        # return ('named', {'title': self._unescape(str(title)), 'tag': nameable_group})

    @v_args(inline=True)
    def groups(self, *group_list):
        return ' '.join(group_list)

    # composable_group = lambda self, x: x[0]  # Pass through single item
    # group = lambda self, x: x[0]  # Pass through single item
    # groups = lambda self, x: x  # Return list of groups

_parser = Lark(GRAMMAR, start='groups')
_pretty_print_transformer = PrettyPrintGroupTransformer()


def validate(group_string):
    tree = _parser.parse(group_string)
    return _pretty_print_transformer.transform(tree)

__all__ = ['validate']

if __name__ == "__main__":
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

    test_cases = [
        "t$ag1 tag2 tag3",
        "tag1 $ungrouped tag2",
        "$all(tag1 tag2\\ baz) simple_tag",
        "$named(Section1 tag1) $named(Section\\ Title $any(tag2 tag3))",
        "\\$literal another",
        "$any(tag1 $all(tag2 tag3)) $ungrouped",
        "$named(Section\\ Title $ungrouped) $named(Foo $any(bar $all(baz qux)))",
        "$all(tag1 $any(tag2 tag3)) $any(foo\\ bar $all(bar baz\\ qux))",
        "tag\\(with\\)parens tag\\$with\\$dollar tag\\\\with\\\\slash",
        "",
        "   ",
    ]

    for test in test_cases:
        print(test)
        try:
            result = validate(test)
            passed = (test.strip() == "" and result == "") or (test.strip() != "" and result != "")
            status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
            print(status)
        except Exception as e:
            print(e)
            print(f"{RED}FAIL{RESET}\n")
        print('-'*50)
