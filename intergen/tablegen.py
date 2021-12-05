from intergen import pl0_grammar3, Lark
from lark.grammar import NonTerminal, Terminal
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
        prods.append('"' + ' '.join(strs) + '"')

    return f"NonTerminal('{head}', " + ', '.join(prods) + ")"

def main():
    parser = Lark(pl0_grammar3, parser='lalr')
    rules = []
    for r in parser.grammar.rule_defs:
        r = process_rule(r)
        rules.append(r)
    print(",\n".join(rules))

if __name__ == '__main__':
    main()