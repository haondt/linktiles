from lark import Transformer, v_args
from . import group_parser

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

    @v_args(inline=True)
    def ungrouped(self):
        return "$ungrouped"

    @v_args(inline=True)
    def all_group(self, *composable_group_set):
        return f"$all({''.join(composable_group_set)})"

    @v_args(inline=True)
    def WS(self, *_):
        return ' '

    @v_args(inline=True)
    def any_group(self, *composable_group_set):
        return f"$any({''.join(composable_group_set)})"

    @v_args(inline=True)
    def named_group(self, title, _, nameable_group):
        return f"$named({title} {nameable_group})"

    @v_args(inline=True)
    def groups(self, *group_list):
        return ' '.join(group_list)

_pretty_print_transformer = PrettyPrintGroupTransformer()

def pretty_print(group_string):
    tree = group_parser._parser.parse(group_string)
    return _pretty_print_transformer.transform(tree)

if __name__ == "__main__":
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

    test_cases = [
        "tag1 tag2 tag3",
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
            result = pretty_print(test)
            passed = (test.strip() == "" and result == "") or (test.strip() != "" and result != "")
            status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
            print(status)
        except Exception as e:
            print(e)
            print(f"{RED}FAIL{RESET}\n")
        print('-'*50)
