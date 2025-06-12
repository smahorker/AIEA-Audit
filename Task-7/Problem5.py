def family_rules():
    rules = [
        IF('person (?x)', THEN('self (?x) (?x)')),
        IF('parent (?x) (?y)', THEN('child (?y) (?x)')),
        IF(AND('parent (?p) (?x)', 'parent (?p) (?y)', NOT('self (?x) (?y)')),
           THEN('sibling (?x) (?y)')),
        IF(AND('parent (?x) (?z)', 'parent (?z) (?y)'),
           THEN('grandparent (?x) (?y)')),
        IF('grandparent (?x) (?y)', THEN('grandchild (?y) (?x)')),
        IF(AND('parent (?px) (?x)', 'parent (?py) (?y)', 
               'sibling (?px) (?py)', NOT('sibling (?x) (?y)')),
           THEN('cousin (?x) (?y)'))
    ]
    return rules
