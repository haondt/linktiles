from lark import Lark, Transformer, UnexpectedCharacters, UnexpectedToken, v_args

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

_parser = Lark(GRAMMAR, start='groups')




