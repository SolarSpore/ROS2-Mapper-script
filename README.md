# Steam Deck `/joy` Mapper for ROS 2

If you're trying to use a Steam Deck's built-in controller for ROS 2 teleop, you'll hit the same wall I did: the controller shows up in Linux as

```
/dev/input/event10
Microsoft X-Box 360 pad 0
```

...which makes you think you can just use a standard Xbox mapping. You can't. The Deck's `/joy` output doesn't line up with the usual layout, and there's no official mapping published anywhere. So I sat down with a controller in one hand and `ros2 topic echo /joy` in the other and mapped every control by hand.

This repo has that mapping, plus the script I used to get it, in case you want to re-verify it on your own hardware or adapt it for a different controller entirely.

## The mapping

`/joy` reports 20 buttons and 8 axes. Here's what maps to what:

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

One issue: the sticks and D-pad are inverted from what you'd expect - right and down are usually positive, here they're negative. Just flip the sign in your `teleop_twist_joy` config and move on.

More detail in [`docs/steamdeck_joy_mapping.md`](docs/steamdeck_joy_mapping.md) if you want it.

## What's included

```
.
├── README.md
├── LICENSE
├── scripts/
│   ├── joy_mapper.py           # the interactive mapper
│   └── joy_node.launch.py      # launch wrapper for joy_node
└── docs/
    └── steamdeck_joy_mapping.md
```

Quick note: `joy_node` comes with ROS 2's standard `joy` package. The launch file here just wraps it for convenience.

## Using it

Start `joy_node` first:

```bash
source install/setup.bash
ros2 run joy joy_node
```

Make sure it's actually publishing:

```bash
ros2 topic echo /joy
```

You should see the arrays move when you touch the controller. If nothing moves, stop here and sort that out first.

Then run the mapper:

```bash
python3 scripts/joy_mapper.py
```

It'll ask you to press one control at a time — "press A," you press A, it tells you which index just changed. Ten second window per control, and if nothing happens in that window it logs it as not registered instead of hanging forever. At the end you get a full summary you can paste straight into a doc.

## Why it's built this way

My first attempt tried to guess what kind of input was coming - "wait for a button press," "wait for an axis to move." However buttons stay held down, axes barely ever land exactly on zero, the D-pad reports as axes instead of buttons, triggers are analog, and the Deck's layout just isn't a normal Xbox layout. So instead of guessing, the script just asks the simplest possible question - "what's the first thing that's different from a line ago?" - and lets ROS answer that itself. Much less fragile.

## License

MIT, see [LICENSE](LICENSE).
