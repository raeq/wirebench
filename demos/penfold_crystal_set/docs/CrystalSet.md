# Build Guide: CrystalSet

A four-component MW crystal radio: aerial, tuned tank, detector

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| A1 | Antenna | Antenna | 1 |  |
| BZ1 | CrystalEarpiece | CrystalEarpiece | 1 |  |
| C1 | VariableCapacitor | VariableCapacitor | 1 |  |
| D1 | D_OA90 | D_OA90 | 1 |  |
| E1 | Earth | Earth | 1 |  |
| L1 | FerriteAerial | FerriteAerial | 1 |  |
| R1 | Resistor | 100000 Ω | 1 | ¼ W carbon film is fine |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### BZ1 — CrystalEarpiece

```
t1 ─┤▮ CrystalEarpiece ▮├─ t2
```

### C1 — VariableCapacitor

```
t1 ─┤▮ VariableCapacitor ▮├─ t2
```

### D1 — D_OA90

```
anode ─▶├─ cathode   [D_OA90]
```

### L1 — FerriteAerial

```
t1 ─┤▮ FerriteAerial ▮├─ t2
```

### R1 — Resistor

```
t1 ─┤▮ 100000 Ω ▮├─ t2
```


## How to verify

Before you start wiring, take five minutes to confirm each part actually works. A multimeter on the diode-test and resistance settings catches most pre-install failures: dead LEDs, mis-bagged parts, transistors damaged in shipping, batteries below their safe-discharge limit. The checks below cover what you can verify with a basic multimeter; chips and complex modules generally need a working test rig instead, so they're not listed here.

- **For a crystal radio, the antenna is the longer the better** — practical sets work with anything from a 3 m whip up to a 30 m long-wire stretched across the loft.  Hang it as high as you can; the higher the average position the larger the EM-field capture and the louder the station-in-the-earphone signal.  Mount the antenna terminal as a screw post or insulated banana socket so the wire can be removed when the radio is stored.
- **Confirm the earpiece is the high-impedance crystal kind, not a moving-coil headphone.** The DC resistance of a crystal earpiece is essentially infinite (open circuit on a multimeter); a moving-coil dynamic earpiece reads a few ohms to a few hundred ohms.  Crystal earpieces are still available from radio-restoration suppliers (look for the old 'crystal earphone' from a 1960s catalogue); modern piezo buzzers are the same physics in a different case.  Crystal radios need the high-impedance kind — driving a low-impedance speaker from a crystal-set detector means no audible sound.
- **Use your multimeter's diode-test mode to confirm the OA90's forward drop.** Red probe on the anode (unmarked end), black on the cathode (banded end): a healthy germanium diode reads about 0.2 V — much lower than a silicon 1N4148's 0.6 V.  If you measure 0.6 V you've grabbed a silicon diode by mistake.  Both legs showing 0.2 V means the diode is shorted; both showing OL means it's open.
- **A good earth is one of the two things that makes a crystal radio audible.**  Test the candidate earth point with a continuity meter to a known good earth (a mains-earth socket pin); the reading should be under 1 Ω.  A cold-water pipe is usually fine if it's metallic *all the way to the supply main*; modern plastic-piped houses won't work.  A copper rod driven 1 m into damp soil is the classical option.  Avoid mains protective earth — see the first GOTCHA below.
- **Check the coil's DC continuity with a multimeter.** Probe across the two enamelled-wire leads — the resistance should be a few ohms to a few tens of ohms (the wire is thin and many turns long).  OL means a broken wire (look for a snag where the wire leaves the rod); a hard short means the wire has chafed against the rod's varnish.
- **Confirm the ferrite rod itself is intact.**  Hold the rod up to a magnet — a healthy ferrite is mildly attracted but not magnetic in the strong-iron sense.  A cracked rod (common after a drop) looks fine externally but tunes weakly and across a narrower range; replace it.
- **Measure the resistance with your multimeter before installing.** Set the meter to the Ω (ohms) range, probe one lead, then the other; the reading should match the value printed on the part (or decoded from its colour bands) to within a few percent. A reading of OL (open / infinity) means the resistor is broken inside; a value wildly different from what's marked usually means someone has swapped parts in the bin and you've grabbed the wrong one.
- **Use a capacitance meter to confirm the rotor sweeps between the stated min and max values.**  Connect the meter across the two terminals, turn the rotor fully one way and note the reading; turn it fully the other way and note the reading.  A typical 300 pF tuning cap reads ~5–10 pF at the low end (plates fully open) and 280–300 pF at the high end (plates fully meshed).  Out-of-range readings mean the part is mis-labelled or damaged.


## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug L1 (FerriteAerial): one lead at position 12 (any of 12A–12E), the
   other at position 14 (any of 14A–14E).
3. Plug C1 (VariableCapacitor): one lead at position 16 (any of 16A–16E), the
   other at position 18 (any of 18A–18E).
4. Plug D1 (D_OA90): one lead at position 20 (any of 20A–20E), the other at
   position 21 (any of 21A–21E).
5. Plug R1 (Resistor): one lead at position 23 (any of 23A–23E), the other at
   position 26 (any of 26A–26E).
6. Plug BZ1 (CrystalEarpiece): one lead at position 28 (any of 28A–28E), the
   other at position 30 (any of 30A–30E).
7. Run a jumper from C1 t1 to D1 anode — position 16 (any of 16A–16E) to
   position 20 (any of 20A–20E).
8. Run a jumper from D1 anode to L1 t1 — position 20 (any of 20A–20E) to
   position 12 (any of 12A–12E).
9. Run a jumper from BZ1 t1 to D1 cathode — position 28 (any of 28A–28E) to
   position 21 (any of 21A–21E).
10. Run a jumper from D1 cathode to R1 t1 — position 21 (any of 21A–21E) to
   position 23 (any of 23A–23E).
11. Run a jumper from BZ1 t2 to C1 t2 — position 30 (any of 30A–30E) to
   position 18 (any of 18A–18E).
12. Run a jumper from C1 t2 to L1 t2 — position 18 (any of 18A–18E) to
   position 14 (any of 14A–14E).
13. Run a jumper from L1 t2 to R1 t2 — position 14 (any of 14A–14E) to
   position 26 (any of 26A–26E).
14. Verify nothing is shorted by inspecting the rails with a multimeter
   (continuity beep between `+` and `-` means trouble). Then connect the
   supply and observe.

## Notes & Gotchas

### General

- **Double-check the supply voltage before powering up.** Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V from a bench supply destroys every chip on the board in microseconds. Set the supply, measure it with a multimeter, and only then connect.
- **Resistor wattage matters.** Standard ¼-W carbon-film resistors are fine below ~60 V across the part. Power resistors (½ W, 1 W) are needed for current-sense or load-dump positions; the BOM lists value only, not wattage — confirm against the schematic's expected current.
- **Tie unused CMOS inputs.** Any input pin not driven by the circuit must be wired to VCC or GND. Floating CMOS inputs drift unpredictably and can cause oscillation, excess supply current, or random behaviour. If your design has unused gates on a multi-gate chip, ground their inputs explicitly with a jumper.
- **Power-rail continuity.** Some 830-pin breadboards split each power rail into two segments at the middle of the board, with a visible break in the colored stripe. If your circuit uses the full rail length, bridge the gap with a jumper before powering on.

### Per-component

- **Disconnect the antenna during thunderstorms.**  A long-wire antenna can pick up induced voltages from nearby lightning strikes that exceed several hundred volts.  Modern crystal radios with no active components have nothing to damage, but the same antenna feeding a transistor receiver destroys input semiconductors.  A spark gap or gas-discharge tube across the antenna-to-earth pair provides cheap protection.
- **Don't run the antenna lead near mains wiring.**  Mains hum (50 / 60 Hz and its harmonics) couples into the antenna and overwhelms the signal of any but the strongest stations.  Keep the lead at least a metre from any mains cabling and route it perpendicular to (rather than parallel with) ceiling joists or wall studs that may carry mains behind them.
- **Don't put a crystal earpiece in your ear at full volume from a powered amplifier — it will be uncomfortably loud.** Crystal earpieces are designed for the microwatt outputs of passive detectors (crystal radios, foxhole receivers).  An audio-amp output that drives a moving-coil speaker happily will drive a piezo earpiece to painfully loud levels — and may damage the crystal itself.  Use a piezo buzzer / speaker with proper level matching for amplifier outputs.
- **The crystal is fragile — the case is rugged but the transducer element inside is not.** Don't drop the earpiece, don't apply more than a few volts AC across its terminals, and don't expose it to temperatures above 60 °C for any length of time.  The ferroelectric ceramic depoles permanently above ~150 °C and the part stops working entirely — an irreversible failure.
- **Use the OA90 specifically because its forward voltage is low.**  In a crystal radio, the antenna delivers tens of microvolts of RF signal — too little to forward-bias a silicon diode at all.  Germanium's 0.2 V V_F just barely rectifies it.  Drop a 1N4148 in here and the radio is *completely* silent; substitute a Schottky 1N5817 and you get the same low V_F as germanium with better reverse characteristics — a modern equivalent.
- **The OA90 is fragile.** Point-contact germanium diodes don't tolerate the soldering heat that silicon DO-35 parts shrug off.  Use a heat sink (a crocodile clip on the lead between the iron and the body) while soldering, and don't leave the iron on the lead for more than 2–3 seconds.  An overheated germanium diode reads short or open afterwards — the junction has failed permanently.
- **Original OA90s are increasingly rare.** New old stock from radio-restoration suppliers is the only reliable source; pulled-from-broken-radios specimens are common but often degraded.  For new builds, the 1N34A is the closest modern equivalent and is still in production; a Schottky 1N5817 substitutes electrically with slightly different RF behaviour.
- **Don't use the mains protective earth in a crystal radio.**  Connecting an antenna lead to the protective-earth wire (via a wall socket's earth pin) introduces a path for induced antenna currents to flow through the household mains earth — which can trip RCDs and, in the worst case, carry harmful currents during nearby lightning strikes.  Use a dedicated radio earth (cold-water pipe, copper rod, balcony railing) that's electrically separate from the house mains.
- **A poor earth makes the radio sound noisy, not silent.**  If your set picks up strong stations but with significant background hiss / hum, the earth is the first thing to improve.  Wetting the soil around the earth rod, lengthening the earth lead, or substituting a cold-water pipe (if metallic) for the rod each makes a measurable difference.
- **Aerial coil orientation matters.** Lay the ferrite rod horizontally and rotate it to peak the signal from your chosen station; the rod has a null along its long axis (no signal at all from a station directly off the end of the rod) and a maximum broadside to the station.  Mount the rod loosely on the breadboard so it can be re-aimed.
- **Don't add an external long-wire antenna and an earth in parallel with the ferrite-aerial-only design unless you know what you're doing.**  An external aerial swamps the ferrite rod's directional null and degrades selectivity; the design becomes susceptible to local interference.  Penfold's BP107 P27 is deliberately *ferrite-only*: simpler to build, quieter, more selective.
- **Variable capacitors are mechanically delicate.**  The plates are spaced by hundredths of a millimetre; dropping the part can warp the plates so they short.  Test the part with a continuity / Ω meter across the terminals before installing — anything below ~100 MΩ at the closed-plate end means the rotor is touching the stator, and the cap is shorted across part of its range.
- **The rotor (shaft) is the high-impedance contact in most designs.**  Connect the rotor to the lowest-noise side of the tuned tank (typically the antenna side, not the ground side); the rotor's shaft makes a fine accidental antenna for hum and stray RF.  Crystal-set practice is to ground the rotor frame so the human hand's capacitance to ground (when adjusting the dial) doesn't detune the tank.
