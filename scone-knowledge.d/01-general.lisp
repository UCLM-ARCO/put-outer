(in-context {general})

(new-type {user} {person})
(new-type {system} {thing})
(new-type {light} {thing})
(new-type {light source} {thing})

;; ----------------------- BUILDINGS
(new-type {building element} {tangible})
(new-type {wall} {building element})
(new-type {room} {building element})
(new-type {stairs} {building element})
(new-type {elevator} {building element})
(new-type {door} {building element})
(new-type {window} {building element})

(new-type {boundary} {thing})
(new-type {virtual boundary} {boundary})
(new-is-a {door} {boundary})
(new-is-a {window} {boundary})
(new-is-a {wall} {boundary})

(new-type {cell} {thing})
(new-type {space} {cell})
(new-is-a {room} {cell})
(new-is-a {stairs} {cell})
(new-is-a {elevator} {cell})

(new-type {usage} {thing})
(new-type-role {room usage} {cell} {usage})
(new-indv {corridor} {room usage})
(new-indv {toilet} {room usage})
(new-indv {kitchen} {room usage})
(new-indv {dinning room} {room usage})

(new-relation {is adjacent to}
        :a-inst-of {cell}
        :b-inst-of {cell}
        :c-inst-of {boundary}
        :symmetric t)

(new-relation {is connected to}
          :a-inst-of {cell}
          :b-inst-of {cell}
          :c-inst-of {boundary})

;; ----------------------- LOCATIONS

(new-type {coordinate} {thing})
(new-type {point} {thing})
(new-type-role {x-coordinate} {point} {coordinate} :n 1)
(new-type-role {y-coordinate} {point} {coordinate} :n 1)
(new-type-role {z-coordinate} {point} {coordinate} :n 1)

(new-type {locatable thing} {thing})
(new-type-role {physical location} {locatable thing} {point})
(new-type-role {logical location} {locatable thing} {cell})

(new-is-a {user} {locatable thing})

;; ----------------------- DEVICES

(new-type {device} {thing})
(new-intersection-type {service} '({device} {intangible}))
(new-intersection-type {transducer} '({device} {physical object}))
(new-is-a {transducer} {locatable thing})

(new-type {sensor} {transducer})
(new-type {actuator} {transducer})

(new-type {lamp} {actuator})
(new-is-a {lamp} {light source})

(new-type {range} {thing})
(new-type-role {action range} {device} {range})
(new-is-a {action range} {cell})

;; ----------------------- ACTORS
(new-type {actor} {thing})
(new-is-a {user} {actor})
(new-is-a {system} {actor})

;; ----------------------- MATERIALS
(new-indv {glass} {material})
(new-indv {wood} {material})
(new-indv {gypsum} {material})
(new-indv {metal} {material})

(new-indv {element with material} {tangible})
(new-intersection-type {glass element} '({element with material} {glass}))
(new-intersection-type {wood element} '({element with material} {wood}))
(new-intersection-type {metal element} '({element with material} {metal}))
(new-intersection-type {gypsum element} '({element with material} {gypsum}))