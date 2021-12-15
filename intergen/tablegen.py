import sys
sys.path.append('./table_gen')

from intergen import pl0_grammar3, Lark
from lark.grammar import NonTerminal, Terminal
from lark import Transformer
from parsing.grammar import NonTerminal as NT, Grammar
from generator import describe_grammar, describe_parsing_table, lalr_one
import json

import re

def to_str(i):
    if isinstance(i, NonTerminal):
        return i.name
    if isinstance(i, Terminal):
        return i.name
    elif i.data == 'literal':
        assert len(i.children) == 1
        c = i.children[0]
        m = re.match(r'"(.+)"i?', c)
        s = m[1]
        return f"'{s}'"

def process_rule(r):
    head, _, tree, options = r
    assert tree.data == 'expansions'
    prods = []
    for e in tree.children:
        if e.data == 'alias':
            assert len(e.children) == 2
            e = e.children[0]
        assert e.data == 'expansion'
        children = [c.children[0] for c in e.children]
        strs = [to_str(c) for c in children]
        # prods.append('"' + ' '.join(strs) + '"')
        prods.append(' '.join(strs))

    # return f"NonTerminal('{head}', " + ', '.join(prods) + ")"
    return NT(str(head), prods)


def main():
    parser = Lark(pl0_grammar3, parser='lalr')
    rules = []
    for r in parser.grammar.rule_defs:
        r = process_rule(r)
        rules.append(r)
    gr = Grammar(rules)
    print(gr.terminals)
    productions = []
    for p in gr.productions:
        productions.append((p[0], len(p[1]), p[0]))
    with open("productions.json", "w") as f:
        json.dump(productions, f, indent=4)

    table = lalr_one.ParsingTable(gr)
    print("I'm done.")

    output_filename = 'parsing-table'

    with open(output_filename + '.txt', 'w') as textfile:
        textfile.write(describe_grammar(gr))
        textfile.write('\n\n')
        textfile.write(describe_parsing_table(table))

    table.save_to_csv(output_filename + '.csv')
    

if __name__ == '__main__':
    main()