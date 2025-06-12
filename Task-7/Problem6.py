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
