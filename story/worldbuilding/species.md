# Species — the cast

Fifteen named species form the starting cast. Most are products of the
Vyrnari uplift program on the Crèche Worlds; a few evolved independently;
two arose from the Vyrnari's *technology* rather than their biology.

The hybrid content model means: each species below is **one YAML entry**
in `content/species/`, plus (for those with non-stat traits) **one Python
behavior class** in `src/ftl/crew/species_behaviors/`. New subspecies and
hybrid variants are pure YAML.

This document gives the in-game stat hooks (`stat_hooks`) and the in-fiction
identity for each. Stats are starting suggestions; tuning happens in
Phase 2.

---

## 1. Sapien

> Baseline humanoids. Generalists. Found in every faction.

**Origin:** Either a forgotten Vyrnari uplift or an independent evolution
on a Crèche-adjacent world. The Choral Order is divided on the matter.
The Sapien themselves no longer care.

**Identity:** The galaxy's *default* species. Sapiens are the merchants,
the soldiers, the captains, the smugglers, the priests, the parents. They
make up a plurality of the Consilium and roughly half of the Iron Concordat.
They are the **only** species with no faction that excludes them.

**Stat hooks:** All stats baseline. No special trait. Universally
compatible crew.

---

## 2. Choir

> Silver-pupiled mystics born sensitive to the Echo.

**Origin:** A Sapien-adjacent lineage born on worlds where the Echo is
unusually strong (typically near old Vyrnari ruins). Genetic; one in
maybe ten thousand Sapien children are born Choir.

**Identity:** Choir lives are short and intense. They hear fragments of
Vyrnari thought as background noise. Most go mad in their thirties unless
they take Choral Order vows and learn to *channel* the Echo. Those who
master it can occasionally **predict an incoming projectile** by a
fraction of a second.

**Stat hooks:** +25% piloting skill (Echo-precognition aids evasion);
+15% sensor effectiveness when manning sensors; suffers a slow morale
decay tick if the ship has more than two systems destroyed (the Echo
gets louder in chaos).

---

## 3. Ferran

> Crystalline. Heavy. Survive vacuum. Lock down rooms by their presence.

**Origin:** Crèche World **Vol-Karran**, high gravity, dense atmosphere.
The Ferran are silicate-based, technically alive, technically mineral.

**Identity:** Slow walkers, fast thinkers. Famously polite, famously
patient. Their bodies do not respect doors — when a Ferran is in a room,
they can briefly *lock it down* against teleporters and intrusion. Vyrnari
ruins in Vol-Karran were the first places the Choral Order documented
the Echo.

**Stat hooks:** Immune to suffocation and vacuum decompression; move
speed 0.5×; while in a room, that room cannot be teleported to/from for
6 seconds on a 30s cooldown; cannot occupy a teleporter pad.

---

## 4. Mhirsa

> Engineered ape-descended warriors, formerly enslaved.

**Origin:** Bred by House Andrachen as a worker-soldier species. Won the
Slave Wars. Founded the Mhirsa Compact.

**Identity:** Powerful, fast, short-lived (a Mhirsa rarely lives past
sixty). Every Mhirsa carries the weight of a hundred-fifty years of
liberation history. They distrust most non-Mhirsa, and especially distrust
anything that smells of Andrachen patronage. Some try to live past their
genetics; some embrace the brevity.

**Stat hooks:** +50% melee damage; +20% move speed; -30% max HP relative
to Sapien; gains skill 25% faster; receives no XP from manning piloting
(cultural taboo against deferring to ship-machine).

---

## 5. Argonite

> Silicon-based. Eat metal. Drain oxygen by breathing.

**Origin:** A Crèche World whose biosphere ran on metallic respiration.
Their lungs are not lungs; they are catalytic exchangers that consume
free oxygen as a *waste byproduct* of metal-oxide extraction. Breathing
in the same room as an Argonite makes oxygen-breathers light-headed.

**Identity:** Pragmatic, soft-spoken, often loners. Excellent engineers
(their bodies *intuit* metallurgy). Despised in oxygen-breathing crews
unless quartered separately. Universally welcomed in the Lattice for
their tolerance of harsh environments.

**Stat hooks:** Slowly drains oxygen from any room they occupy (-1%/sec);
takes no suffocation damage themselves; +40% system repair speed; cannot
benefit from medbay healing (their wounds reseal in a vacuum chamber, not
a medbay — must be in an unoccupied airless room to heal).

---

## 6. Yssari

> Bioluminescent amphibians. Telepathic. Burn easily.

**Origin:** Crèche World **Tholai**, a shallow-ocean planet. Yssari
"speech" combines bioluminescent pulse and limited telepathy; among
themselves it is faster and more nuanced than spoken language. Across
species lines they are merely fluent in roughly twenty galactic tongues.

**Identity:** Diplomats, interrogators, judges. Yssari can *sense* when
a being in the same room is lying, though they cannot read the underlying
truth — only the dissonance. The Consilium employs them in its courts.
The Black Vein avoids them. They are catastrophically vulnerable to fire,
both as a species reaction and as a cultural horror.

**Stat hooks:** +30% effectiveness when manning piloting or sensors
(communication speed); 2× damage taken from fire; can detect mind-control
attempts on the player's ship one second before they activate.

---

## 7. Vor

> Radiation-eaters. Pulsar-children. Internal clocks more precise than
> any chronometer.

**Origin:** Crèche World **Inrith**, in tight orbit around a young pulsar.
The Vor evolved organs that *eat* high-energy radiation; in normal stellar
space they are slowly starving.

**Identity:** Soft-spoken, perfectionist, often morose. Vor crew often
serve as gunnery officers because their internal clocks let them time
weapon charges to within milliseconds. They are most at home near reactors
and irradiated wreckage. In a clean ship they slowly lose health unless
near a power core.

**Stat hooks:** Heals slowly while manning engines or reactor-room
systems; takes slow damage outside those rooms; +25% weapon charge speed
when manning weapons; +1 evasion when manning engines.

---

## 8. Drevant

> Three-armed, eyeless, echolocating. Read heat and electrical fields
> directly.

**Origin:** Crèche World **Sothan-Vell**, a perpetually clouded ice
giant moon. The Drevant evolved to "see" in absolute darkness via heat
and electrical sensing. The Vyrnari may have specifically engineered them
as engineer-uplifts; their hands are remarkably suited to repair work.

**Identity:** Curious, gentle, dryly funny. The Consilium's premier
engineers and weapons-officers. Slow to navigate unfamiliar terrain (they
have to map a new room by "scanning" it). Many wear a heat-mask over the
upper face — not for vision, but as a cultural sign of seriousness.

**Stat hooks:** +50% system repair speed; +20% weapon charge speed when
manning weapons; -50% move speed in any room they have not been in for
more than 30 seconds.

---

## 9. Halene

> Silver-skinned, fragile, generate power passively.

**Origin:** Disputed. The Halene claim direct descent from the Vyrnari
themselves. Mainstream xenobiologists dismiss this. The Choral Order
sometimes acts as if they believe it.

**Identity:** Tall, frail, low body heat, low metabolic noise. Halene
biology *converts ambient particles into electrical potential* — every
living Halene aboard a ship contributes a small but real boost to the
ship's reactor. They die easily. They are vulnerable to fire, to vacuum,
to almost everything. The few Halene who become soldiers do so out of
spite.

**Stat hooks:** Contributes +1 reactor power while alive and not
suffocating; -40% max HP relative to Sapien; +25% manning bonus on
any system (efficient at every task they live to learn).

---

## 10. Spliced

> Not a species — a *condition*. Bio-modified individuals carrying traits
> from other species.

**Origin:** The Splice movement, primarily in the Outer Verge. Anyone of
any base species can become Spliced.

**Identity:** Each Spliced individual is unique. A Spliced person might
have a Sapien core with Argonite respiration, Vor radiation tolerance,
and Karrukai reflexes. Verdantis refuse to crew with Spliced. Some
Choral Order sects regard them as walking blasphemy. The Splice themselves
celebrate their individuality and treat their bodies as ongoing art.

**Stat hooks:** Generated at crew creation by selecting 1–3 traits from
the base species pool, with offsetting penalties (cost system). Spliced
crew gain XP 15% slower (their bodies are still adjusting).

---

## 11. Karrukai

> Six-legged jungle predators. Fast, vicious, hard to command.

**Origin:** Crèche World **Hak-Hak**, a tropical predator-saturated
planet where the Karrukai evolved to be apex by being *the* fastest
thing in any room.

**Identity:** Karrukai do not speak in any humanoid sense; they
communicate through pheromone, gesture, and a clicking subvocal language.
They make obedient soldiers when the cause is *visceral* and terrible
ones when the cause is *abstract*. The Iron Concordat conscripts them
as shock troops. The Consilium will not. Mhirsa relate to them
uncomfortably — fellow engineered-violent species who took different
paths.

**Stat hooks:** +100% melee damage; +50% move speed; ignores
player orders 10% of the time (will engage nearest perceived threat
instead); +30% intimidation in boarding actions (some boarders flee).

---

## 12. Loam

> Fungal collective. Each "person" is a colony in humanoid frame.

**Origin:** Crèche World **Pellrun**, where the Vyrnari may have been
experimenting with *non-individual* intelligence. Pellrun fungi evolved
self-cohesion; a Loam is a colony that has chosen to organize.

**Identity:** Slow, patient, deeply strange. Loam memories are colony
memories; ask one about their childhood and they may recount events from
two centuries before they were "born" in any conventional sense. They
are functionally immortal as long as a fragment survives in a medbay or
fertile soil. The Verdantis revere them. Most other factions find them
unsettling.

**Stat hooks:** Regenerates HP 3× faster in medbay or clonebay; if a
Loam dies, can be regrown over 30 seconds in a functioning medbay (one
free revive per run per Loam); -30% move speed.

---

## 13. Vellisian / Lirathi

> Twin aristocratic bloodlines from a single homeworld. Same species,
> mutually-exclusive culturally.

**Origin:** Vassirin, the shared homeworld of the Twin Houses.

**Identity:** Tall, mannered, intricately tattooed (the patterns indicate
house lineage). Both bloodlines excel at command — manning a system from
a Vellisian or Lirathi crew member produces a noticeably better bonus.
A Vellisian and a Lirathi will *not crew the same ship* without a major
scripted event (typically the Vellis-Lirath storyline).

**Stat hooks:** +50% manning bonus to all systems; cannot crew with a
member of the opposite house unless the *Tainted Heir* questline has
been completed.

---

## 14. Hollow

> Uploaded minds in synthetic bodies. Lattice defectors.

**Origin:** The Lattice (a posthuman / AI substrate, see
[factions/the_lattice.md](factions/the_lattice.md)). The Hollow are
those who *left* the Lattice — they chose to re-embody, retaining
memory and ego.

**Identity:** Logical, dry, often older than their bodies (in their
heads, decades may have passed in Lattice time). The Lattice considers
them traitors. Verdantis consider them abominations. Most other factions
find them useful, if uncanny. They do not breathe; their "bodies" are
synthetic; they can transfer mind via teleporter pad between Hollow-
compatible chassis.

**Stat hooks:** No suffocation; no vacuum damage; takes 2× ion damage;
cannot benefit from medbay (must be in a functional Drone Control system
to repair); can swap rooms instantly via teleporter (1/min).

---

## 15. Whisperborn

> Rarest species. Born inside an Echo-rift. Brief glimpses of futures.

**Origin:** A child conceived during an *Echo-rift event* — a rare
subspace anomaly near failing Gates — is sometimes born Whisperborn.
There are perhaps a few hundred in the galaxy at any time. The Choral
Order shelters them. The Unmade hunt them.

**Identity:** Visions are involuntary. A Whisperborn may freeze mid-
sentence as the Echo shows them a fragment of *something*: a stranger's
death, a Gate failing, a ship not yet built. Most lose their minds before
thirty. Those who don't are uncanny — kindly, unsettled, accidentally
prophetic.

**Stat hooks:** Occasionally (every 60–90s) "predicts" an enemy action,
giving the player a short on-screen warning; +20% piloting; cannot be
mind-controlled (their minds are too crowded already); enables the
*Whisperborn Awakening* storyline if assigned to a starting ship.

---

## Future species (Phase 5+)

Subspecies, regional variants, and brand-new lines are layered in via
YAML once the base set is balanced. Examples already in concept:

- **Verdant-bound Loam** — Loam adopted into Verdantis culture; refuses
  cross-species grafts; +5 morale to nearby crew.
- **Pulsar-Drowned Vor** — Vor lineage that lived too long in a pulsar
  star field; partial radiation immunity, but visibly luminescent.
- **Iron-Bound Halene** — Concordat-conscripted Halene; armored shells;
  no power generation, +standard HP.
- **Voidshell** — formerly-Loam colonies grown inside abandoned starship
  hulls; semi-mechanical; *probably* a person.

(All Phase 5+. Phase 0 ships only the fifteen above.)
