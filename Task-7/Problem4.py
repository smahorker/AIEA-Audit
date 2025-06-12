def transitive_rule():
    rule = IF(
        AND('(?x) beats (?y)', '(?y) beats (?z)'),
        THEN('(?x) beats (?z)')
    )
    return rule
