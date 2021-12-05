# from table_gen.parsing import Grammar, NonTerminal, lalr_one
from parsing.grammar import Grammar, NonTerminal
from parsing import lalr_one

def test_table_gen():
    sample1 = Grammar([
        NonTerminal('N', [
            "V '=' E", "E"
        ]),
        NonTerminal('E', [
            "V"
        ]),
        NonTerminal('V', [
            "'x'", "'*' E"
        ])
    ])
    table = lalr_one.ParsingTable(sample1)
    print(table)
