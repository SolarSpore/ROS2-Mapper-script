# Steam Deck → ROS 2 → ESP32 Rover Teleoperation

Teleoperation system that uses a Steam Deck's built-in controls as the
input device for a ROS 2-controlled rover, with an ESP32 acting as the
hardware endpoint over Wi-Fi/UDP.

```
Steam Deck built-in controls
        ↓
Linux controller input
        ↓
ROS 2 joy_node
        ↓
/joy
        ↓
teleop / controller mapping
        ↓
/cmd_vel
        ↓
ROS 2 rover UDP bridge
        ↓
Wi-Fi / UDP
        ↓
ESP32 rover
        ↓
4 motor drivers
        ↓
Wheels
```

The longer-term goal is for the Steam Deck to act as the central
robot computer/UI, with ROS 2 handling the robotics side and ESP32s
acting as hardware endpoints.

## Status

| Component                                     | Status                 |
| ---------------------------------------------- | ---------------------- |
| Steam Deck controller hardware                 | ✅ Working              |
| Linux sees controller (`evtest`)               | ✅ Working              |
| ROS 2 workspace                                | ✅ Working              |
| `joy` package                                  | ✅ Installed            |
| `joy_node`                                     | ✅ Working when started |
| `/joy` topic                                   | ✅ Working              |
| Exact Steam Deck `/joy` mapping                | ✅ Confirmed — see [`docs/steamdeck_joy_mapping.md`](docs/steamdeck_joy_mapping.md) |
| ESP32 rover (motors, UDP, OTA, mDNS)            | ✅ Working              |
| ROS 2 rover UDP bridge (`rover_udp_bridge`)     | ✅ Working              |
| Foxglove Bridge                                | ✅ Working              |
| `teleop_twist_joy` configuration                | ⏳ Next step            |
| Final Steam Deck → `/cmd_vel` → rover control   | ⏳ Final integration    |

The Steam Deck controller shows up in Linux/evdev as:

```
/dev/input/event10
Microsoft X-Box 360 pad 0
```

That's the evdev name for the built-in Steam Deck controller in this
mode — it isn't an external Xbox controller.

## Repo contents

```
.
├── README.md
├── scripts/
│   ├── joy_mapper.py           # Interactive /joy button & axis mapper
│   └── joy_node.launch.py      # Convenience launch wrapper for the stock `joy` package's joy_node
└── docs/
    └── steamdeck_joy_mapping.md  # Confirmed button/axis mapping + open items
```

> **Note:** `joy_node` itself is part of ROS 2's standard `joy` package
> (`sudo apt install ros-<distro>-joy` or via your workspace's package
> manager) — it's not custom code. `joy_node.launch.py` is just a thin
> convenience wrapper so it can be launched the same way as the rest of
> this project if you prefer `ros2 launch` over `ros2 run`.

## Prerequisites

- ROS 2 (tested in a workspace at `~/Robotics/ros2_ws`)
- ROS packages: `joy`, `teleop_twist_joy`, `teleop_twist_keyboard`
- Python 3 with `rclpy` and `sensor_msgs` available (comes with the
  ROS 2 Python environment)

## Usage

### 1. Start `joy_node`

In one terminal:

```bash
cd ~/Robotics/ros2_ws
pixi shell
source install/setup.bash
ros2 run joy joy_node
```

(or `ros2 launch scripts/joy_node.launch.py` if you'd rather use the
included launch wrapper)

This reads the controller and publishes `sensor_msgs/msg/Joy` on
`/joy`. Leave it running.

Sanity check it's working:

```bash
ros2 topic echo /joy
```

You should see `buttons` and `axes` arrays change as you touch the
controller.

### 2. Run the interactive mapper

In a second terminal:

```bash
cd ~/Robotics/ros2_ws
pixi shell
source install/setup.bash
python3 scripts/joy_mapper.py
```

The script walks through a list of controls one at a time:

1. Prompts you with the control to press (e.g. `A`).
2. Captures a clean baseline of `/joy` while your hands are off the
   controller.
3. Gives you **10 seconds** to press/move that control.
4. Diffs the new `/joy` message against the baseline and logs
   whichever `buttons[]`/`axes[]` index actually changed — it doesn't
   assume whether the control is a button or an axis, it just reports
   what ROS says changed.
5. If nothing changes within 10 seconds, it logs `NOT REGISTERED` for
   that control and moves on.

At the end it prints a full summary table plus a list of any controls
that didn't register, so you know what to retest.

### 3. Record the results

The confirmed mapping from the last full run is checked in at
[`docs/steamdeck_joy_mapping.md`](docs/steamdeck_joy_mapping.md).
Re-run the mapper any time the mapping needs re-verifying (e.g. after
a Steam input config change), and update that file.

## Why the mapper works this way

Earlier attempts at a mapper tried to guess what *kind* of input to
expect (e.g. "wait for a button press") and broke down because:

- buttons can remain held
- axes don't necessarily return exactly to zero
- multiple controls can produce related events
- the D-pad is represented as axes, not buttons
- triggers are analog
- the Steam Deck's mapping isn't a clean generic Xbox layout

This version instead asks the simplest possible question: **"What is
the first thing in the entire `/joy` message that changes after a
clean baseline?"** ROS reports the answer directly, which avoids all
of the above assumptions.

## License

MIT — see [LICENSE](LICENSE).

## Status note

The button indices and axis assignments in the mapping doc are
confirmed against a live `/joy` capture. The exact neutral/rest values
for the left stick and triggers are currently **assumed** rather than
independently re-verified (see "Known open items" in
[`docs/steamdeck_joy_mapping.md`](docs/steamdeck_joy_mapping.md)) —
published now so the repo is usable, to be tightened up in a follow-up
pass. PRs / issues welcome if you test this on your own Steam Deck and
get different results.

## Next steps

1. Verify true neutral/rest values for the sticks and triggers (see
   "Known open items" in the mapping doc).
2. Use the confirmed mapping to configure `teleop_twist_joy` (accounting
   for inverted stick/D-pad polarity).
3. Wire up `teleop_twist_joy` → `/cmd_vel` → `rover_udp_bridge` for full
   Steam Deck → rover control.
