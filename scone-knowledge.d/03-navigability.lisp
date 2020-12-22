(in-context {general})

(new-type {_navigable} {thing})
(new-is-a {boundary} {_navigable})
(new-is-a {cell} {_navigable})

(new-type {navigator} {thing})
(new-is-a {person} {navigator})
(new-is-a {light} {navigator})

(new-relation {is navigable by}
        :a-inst-of {_navigable}
        :b-inst-of {navigator})

(new-not-statement {closed element} {is navigable by} {user})
;;(new-statement {open door} {is navigable by} {user})
(new-statement {open element} {is navigable by} {light})

(new-statement {glass element} {is navigable by} {light})
(new-not-statement {wood element} {is navigable by} {light})
(new-not-statement {gypsum element} {is navigable by} {light})
(new-not-statement {metal element} {is navigable by} {light})

;; ----------------------- IN A DANGER CONTEXT
(new-context {danger situation} {general})
(in-context {danger situation})
(new-statement {open window} {is navigable by} {user})

(in-context {general})