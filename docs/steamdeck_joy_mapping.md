# Steam Deck `/joy` Mapping (Confirmed)

Captured using `scripts/joy_mapper.py` against the built-in Steam Deck
controller, exposed to Linux/evdev as:

```
/dev/input/event10
Microsoft X-Box 360 pad 0   (evdev name, not an actual Xbox controller)
```

`/joy` reports:

- **20 buttons** (indices 0–19, though only the physical controls below were exercised)
- **8 axes** (indices 0–7)

## Buttons

| Control                  | Index        |
|---------------------------|-------------|
| A                          | buttons[0]  |
| B                          | buttons[1]  |
| X                          | buttons[2]  |
| Y                          | buttons[3]  |
| Select / Back / View       | buttons[4]  |
| Guide / Steam button       | buttons[5]  |
| Start / Menu               | buttons[6]  |
| L3 (left stick click)      | buttons[7]  |
| R3 (right stick click)     | buttons[8]  |
| L1 (LB)                    | buttons[9]  |
| R1 (RB)                    | buttons[10] |

## Axes

| Control        | Index      | Notes                                   |
|-----------------|-----------|------------------------------------------|
| Left stick X    | axes[0]   | left = +1, right = -1 (inverted). **Neutral assumed 0.0, unverified.** |
| Left stick Y    | axes[1]   | up = +, down = -1. **Neutral assumed 0.0, unverified.** |
| Right stick X   | axes[2]   | left = +, right = -1 (inverted). Neutral observed ≈ 0.0. |
| Right stick Y   | axes[3]   | up = +, down = -1. Neutral observed ≈ 0.0. |
| L2 (LT)         | axes[4]   | full squeeze = -1. **Rest/neutral value assumed, unverified** (raw capture showed ≈0.42, likely a settling artifact — see below). |
| R2 (RT)         | axes[5]   | full squeeze = -1. **Rest/neutral value assumed, unverified** (raw capture showed ≈0.11, likely a settling artifact — see below). |
| D-pad X         | axes[6]   | left = +1, right = -1 (inverted). Neutral observed ≈ 0.0. |
| D-pad Y         | axes[7]   | up = +1, down = -1. Neutral observed ≈ 0.0. |

> **Status: this table is published with assumed neutral values for
> the items marked above.** The button indices and axis *index
> assignments* (which axis = which control) are solid — they were
> confirmed by direct diff against a live `/joy` feed. What's *not*
> yet independently verified is the true resting/neutral value for
> the left stick and both triggers. Treat those specific values as
> provisional until re-tested (see below).

## Known open items

- **Left/right stick and D-pad polarity is inverted** from the usual
  convention (normally right/down are positive). This is fine, but
  `teleop_twist_joy` (or any downstream mapping node) needs negative
  scale factors to compensate.
- **Trigger and left-stick neutral values were slightly off-center**
  during the initial capture (e.g. left stick baseline read `0.54`
  before "Left stick Left" and `-0.46` before "Left stick Down";
  triggers rested around `0.42` / `0.11` instead of a clean neutral).
  This is most likely a timing artifact — the baseline was captured
  immediately after the previous control was released, before the
  stick/trigger fully settled. **Before trusting these values in a
  teleop config, verify true neutral** by running:

  ```bash
  ros2 topic echo /joy
  ```

  with the controller completely untouched for a few seconds, and
  confirm axes[0], axes[1], axes[4], axes[5] settle at their expected
  resting values.

## Buttons not yet exercised

Only 11 of the 20 reported button indices were mapped to physical
controls (0–10). Indices 11–19 were not exercised in this pass and
remain unknown — likely unused, or mapped to Steam Deck-specific
controls (back grip buttons, trackpad clicks, etc.) not covered in
the initial test list.
