# 一些别的语法，供参考

"手册草稿上的语法，与网上的差别略大"
pl0_grammar1 = """
    start: begin subprogram 
    begin: "PROGRAM"i identifier 
    subprogram: const_part var_part statement_part 
    const_part: [const_part]
    var_part: [var_part]
    const: INT
    unsigned_integer: unsigned_integer, digit | digit 
    var_part: "VAR"i identifier_list 
    identifier_list: identifier_list, identifier | identifier 
    identifier: CNAME
    statement_part: statement | compound_statement 
    compound_statement: "BEGIN"i statement_list "END"i 
    statement_list: statement_list; statement | statement 
    statement: assignment_statement | conditional_statement | loop_statement | compound_statement   
    assignment_statement: identifier:=expression 
    expression: [+|-] item | expression op1 item 
    item: factor | item op2 factor 
    factor: identifier | const | (expression) 
    op1: + | - 
    op2: * | / 
    conditional_statement: "IF"i condition "THEN"i statement 
    loop_statement: "WHILE"i condition "DO"i statement 
    condition: expression relational_operator expression 
    relational_operator: "=" | "<>" | "<" | "<=" | ">" | ">="

    %import common.INT
    %import common.CNAME
    %import common.WS
    %ignore WS
"""

"维基上的。https://en.wikipedia.org/wiki/PL/0"
pl0_grammar2 = """
    ?start: program

    ?program: block "." 

    ?block: [const_decl] [var_decl] proc* [statement]

    const_decl:  "const"i ident "=" number ("," ident "=" number)* ";"

    var_decl:  "var"i ident ("," ident)* ";"

    proc: "procedure"i ident ";" block ";"

    statement: ident ":=" expression 
        | "call"i ident 
        | "?" ident 
        | "!" expression 
        | "begin"i statement (";" statement )* "end"i 
        | "if"i condition "then"i statement 
        | "while"i condition "do"i statement

    condition: "odd"i expression 
        | expression ("="|"#"|"<"|"<="|">"|">=") expression

    expression: [ "+"|"-"] term ( ("+"|"-") term)*

    term: factor (("*"|"/") factor)*

    factor: ident 
        | number 
        | "(" expression ")"

    number: SIGNED_NUMBER

    ident: CNAME

    %import common.SIGNED_NUMBER
    %import common.CNAME
    %import common.WS
    %ignore WS
"""