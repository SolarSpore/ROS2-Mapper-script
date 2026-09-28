# Steam Deck `/joy` Mapper for ROS 2

A tool for mapping every physical control on a Steam Deck's built-in
controller to its exact `sensor_msgs/msg/Joy` index in ROS 2 — so you
can configure teleoperation (`teleop_twist_joy` or any custom mapper)
without guessing from generic Xbox-controller documentation.

The Steam Deck controller shows up in Linux as:

```
/dev/input/event10
Microsoft X-Box 360 pad 0
```

That evdev name is misleading — it's the built-in Steam Deck
controller, not an actual Xbox pad, and its `/joy` layout doesn't
match a standard Xbox mapping. This repo gives you the real mapping,
confirmed control-by-control against a live `/joy` feed.

## Mapping

`/joy` reports 20 buttons and 8 axes. The physical controls below were
tested directly:

### Buttons

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

### Axes

| Control        | Index      | Notes                             |
|-----------------|-----------|-------------------------------------|
| Left stick X    | axes[0]   | left = +1, right = -1 (inverted)    |
| Left stick Y    | axes[1]   | up = +1, down = -1                  |
| Right stick X   | axes[2]   | left = +1, right = -1 (inverted)    |
| Right stick Y   | axes[3]   | up = +1, down = -1                  |
| L2 (LT)         | axes[4]   | rest = neutral, full squeeze = -1   |
| R2 (RT)         | axes[5]   | rest = neutral, full squeeze = -1   |
| D-pad X         | axes[6]   | left = +1, right = -1 (inverted)    |
| D-pad Y         | axes[7]   | up = +1, down = -1                  |

Full write-up with additional notes: [`docs/steamdeck_joy_mapping.md`](docs/steamdeck_joy_mapping.md).

**Note on polarity:** left/right stick and D-pad axes are inverted
from the usual convention (normally right/down are positive). Account
for this with negative scale factors in your `teleop_twist_joy` config
or downstream mapping node.

## Repo contents

```
.
├── README.md
├── LICENSE
├── scripts/
│   ├── joy_mapper.py           # Interactive /joy button & axis mapper
│   └── joy_node.launch.py      # Convenience launch wrapper for the stock `joy` package's joy_node
└── docs/
    └── steamdeck_joy_mapping.md  # Full mapping reference
```

> `joy_node` itself is part of ROS 2's standard `joy` package
> (`ros-<distro>-joy`) — it's not custom code. `joy_node.launch.py` is
> just a thin convenience wrapper so it can be launched the same way
> as the rest of this project if you prefer `ros2 launch` over
> `ros2 run`.

## Usage

### 1. Start `joy_node`

```bash
source install/setup.bash
ros2 run joy joy_node
```

(or `ros2 launch scripts/joy_node.launch.py`)

This publishes `sensor_msgs/msg/Joy` on `/joy`. Leave it running.

Sanity check:

```bash
ros2 topic echo /joy
```

You should see `buttons` and `axes` arrays change as you touch the
controller.

### 2. Run the mapper

```bash
python3 scripts/joy_mapper.py
```

The script walks through every control one at a time:

1. Prompts you with the control to press (e.g. `A`).
2. Captures a clean baseline of `/joy` while your hands are off the
   controller.
3. Gives you 10 seconds to press or move that control.
4. Diffs the new `/joy` message against the baseline and reports
   exactly which `buttons[]`/`axes[]` index changed — no assumptions
   about whether the control is digital or analog.
5. Logs `NOT REGISTERED` for anything that doesn't change within the
   time limit.

At the end it prints a full summary table, ready to drop into a
mapping doc like the one in this repo.

## Why it works

Earlier mapping attempts tried to guess what *kind* of input to expect
(e.g. "wait for a button press") and broke down because buttons can
stay held, axes don't return exactly to zero, the D-pad is reported as
axes rather than buttons, triggers are analog, and the Steam Deck's
layout isn't a clean generic Xbox layout. This mapper sidesteps all of
that by asking the simplest possible question — "what's the first
thing in the whole `/joy` message that changes after a clean
baseline?" — and letting ROS answer directly.

## License

MIT — see [LICENSE](LICENSE).
