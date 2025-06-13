from production import AND, OR, NOT, IF, THEN, match, populate, simplify, forward_chain

def transitive_rule():
    rule = IF(
        AND('(?x) beats (?y)', '(?y) beats (?z)'),
        THEN('(?x) beats (?z)')
    )
    return rule

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

def backchain_to_goal_tree(rules, hypothesis):
    alternatives = [hypothesis]
    
    for rule in rules:
        consequent = rule.action()[0] if rule.action() else None
        bindings = match(consequent, hypothesis)
        if bindings is not None:
            if isinstance(rule.antecedent(), str):
                instantiated = populate(rule.antecedent(), bindings)
                alternatives.append(backchain_to_goal_tree(rules, instantiated))
            else:
                instantiated_ant = populate(rule.antecedent(), bindings)
                if isinstance(instantiated_ant, AND):
                    subgoals = []
                    for condition in instantiated_ant:
                        subgoals.append(backchain_to_goal_tree(rules, condition))
                    alternatives.append(AND(subgoals))
                elif isinstance(instantiated_ant, OR):
                    subgoals = []
                    for condition in instantiated_ant:
                        subgoals.append(backchain_to_goal_tree(rules, condition))
                    alternatives.append(OR(subgoals))
    
    return simplify(OR(alternatives))

poker_data = [
    'two-pair beats pair',
    'three-of-a-kind beats two-pair',
    'straight beats three-of-a-kind',
    'flush beats straight',
    'full-house beats flush',
    'straight-flush beats full-house'
]

simpsons_data = [
    'person bart', 'person lisa', 'person maggie', 
    'person marge', 'person homer', 'person abe', 'person mona',
    'parent marge bart', 'parent marge lisa', 'parent marge maggie',
    'parent homer bart', 'parent homer lisa', 'parent homer maggie',
    'parent abe homer', 'parent mona homer'
]

black_family_data = [
    'person sirius', 'person regulus', 'person bellatrix', 'person andromeda', 
    'person narcissa', 'person nymphadora', 'person draco',
    'person orion', 'person walburga', 'person cygnus', 'person druella',
    'parent orion sirius', 'parent orion regulus',
    'parent walburga sirius', 'parent walburga regulus', 
    'parent cygnus bellatrix', 'parent cygnus andromeda', 'parent cygnus narcissa',
    'parent druella bellatrix', 'parent druella andromeda', 'parent druella narcissa',
    'parent andromeda nymphadora', 'parent narcissa draco'
]

zookeeper_rules = [
    IF('(?x) is a bird', THEN('(?x) is a vertebrate')),
    IF('(?x) has feathers', THEN('(?x) is a bird')),
    IF(AND('(?x) flies', '(?x) lays eggs'), THEN('(?x) is a bird')),
    IF(AND('(?x) is a bird', '(?x) does not fly', '(?x) swims', '(?x) has black and white color'), 
       THEN('(?x) is a penguin'))
]

poker_results = forward_chain([transitive_rule()], poker_data)
print(len(poker_results))

simpsons_results = forward_chain(family_rules(), simpsons_data)
print(len(simpsons_results))

black_results = forward_chain(family_rules(), black_family_data)
cousin_relationships = [r for r in black_results if 'cousin' in r]
print(len(cousin_relationships))

goal_tree = backchain_to_goal_tree(zookeeper_rules, 'opus is a penguin')
print(goal_tree)
