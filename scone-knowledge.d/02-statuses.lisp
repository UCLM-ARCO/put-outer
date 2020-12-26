(in-context {general})

(new-type {quality} {thing})
(new-type {status} {quality})

(new-indv {inoperative} {status})

;; ----------------------- SWITCHABLE ELEMENTS
(new-type {on device} {device})
(new-type {off device} {device})
(new-complete-split {device}
 '({on device}
   {off device}))

(new-indv {on} {status})
(new-indv {off} {status})

(new-type-role {device status} {device} {status})
(x-is-the-y-of-z {on} {device status} {on device})
(x-is-the-y-of-z {off} {device status} {off device})

(new-intersection-type {on lamp} '({on device} {lamp}))
(new-intersection-type {off lamp} '({off device} {lamp}))

;; ----------------------- OPENABLE ELEMENTS
(new-type {openable element} {thing})

(new-type {open element} {openable element})
(new-type {closed element} {openable element})
(new-complete-split {openable element}
 '({open element}
   {closed element}))

(new-indv {open} {status})
(new-indv {closed} {status})

(new-type-role {openable element status} {openable element} {status})
(x-is-the-y-of-z {open} {openable element status} {open element})
(x-is-the-y-of-z {closed} {openable element status} {closed element})

(new-intersection-type {open door} '({open element} {door}))
(new-intersection-type {closed door} '({closed element} {door}))

(new-intersection-type {open window} '({open element} {window}))
(new-intersection-type {closed window} '({closed element} {window}))
