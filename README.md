# VRLiveStreaming_MachineControlScript

A Python library for controlling broadcast and AV hardware devices over the network. Supports the full **Blackmagic HyperDeck Ethernet Protocol** (TCP) and AJA KUMO router control (HTTP).

---

## Supported Devices

| Class | Device | Protocol |
|---|---|---|
| `AJA_Control` | AJA KUMO Video Router | HTTP |
| `Hyperdeck8K_Control` | Blackmagic HyperDeck Extreme 8K | TCP (port 9993) |
| `HyperdeckHD_Control` | Blackmagic HyperDeck HD | TCP (port 9993) |

---

## Requirements

- Python 3.10+
- [`requests`](https://pypi.org/project/requests/)

```bash
pip install requests
```

---

## Usage

### Factory (recommended entry point)

```python
from factory import ControlScriptFactory

factory = ControlScriptFactory()
```

---

### HyperDeck (context manager — recommended)

```python
with factory.create_hyperdeck8K_control("192.168.1.100") as deck:
    print(deck.device_info())
    deck.record(name="scene_01")
    deck.stop()
```

### HyperDeck (manual connection)

```python
deck = factory.create_hyperdeckHD_control("192.168.1.101", port=9993)
deck.connect()

deck.play(speed=100, loop=False)
deck.goto_timecode("01:00:30:00")
deck.stop()

deck.disconnect()
```

---

### AJA KUMO Router

```python
aja = factory.create_aja_control("192.168.1.200")
aja.connect(input=1, output=2)   # Route input 1 → output 2
```

---

## HyperDeck API Reference

All HyperDeck commands return a raw protocol response string. Both `Hyperdeck8K_Control` and `HyperdeckHD_Control` share the same `HyperdeckBase` interface.

### Connection

| Method | Description |
|---|---|
| `connect()` | Open TCP connection, returns greeting banner |
| `disconnect()` | Send `quit` and close socket |
| `ping()` | Check device is responding |
| `send_command(cmd)` | Send raw protocol command, returns response |

### Transport Control

| Method | Parameters | Description |
|---|---|---|
| `play(speed, loop, single_clip)` | all optional | Start playback |
| `stop()` | — | Stop playback or recording |
| `record(name)` | `name` optional | Start recording, optionally named |
| `record_spill(slot_id)` | `slot_id` optional | Spill recording to next/specified slot |
| `preview(enable)` | `bool` | Toggle preview / output mode |

### Goto / Jog / Shuttle

| Method | Parameters | Description |
|---|---|---|
| `goto_clip_id(clip_id)` | int or `'start'`/`'end'` | Jump to a clip |
| `goto_clip_id_relative(offset)` | int (±) | Jump forward/backward by N clips |
| `goto_clip(position)` | int or `'start'`/`'end'` | Seek within current clip |
| `goto_timecode(timecode)` | `'HH:MM:SS:FF'` | Seek to absolute timecode |
| `goto_timeline(position)` | int or `'start'`/`'end'` | Seek to timeline frame |
| `jog(timecode)` | timecode string | Jog by timecode (prefix `+`/`-` for relative) |
| `shuttle(speed)` | -5000 to 5000 | Shuttle at speed |

### Playrange

| Method | Parameters | Description |
|---|---|---|
| `playrange()` | — | Query current play range |
| `playrange_set_clip(clip_id, count)` | `count` optional | Set range to N clips from clip |
| `playrange_set_timecode(in_tc, out_tc)` | timecodes | Set range by timecode |
| `playrange_set_timeline(frame_in, frame_out)` | ints | Set range by timeline frame |
| `playrange_clear()` | — | Clear play range |

### Clip Management

| Method | Parameters | Description |
|---|---|---|
| `clips_count()` | — | Number of clips on timeline |
| `clips_get(clip_id, count, version)` | all optional | Query timeline clips |
| `clips_add(name, clip_id)` | `clip_id` optional | Append or insert clip |
| `clips_remove(clip_id)` | int | Remove clip from timeline |
| `clips_clear()` | — | Empty timeline |
| `clip_info(clip_id, name)` | one optional | Info for a clip |

### Slot & Disk

| Method | Parameters | Description |
|---|---|---|
| `slot_info(slot_id)` | optional | Query slot status |
| `slot_select(slot_id, video_format)` | both optional | Switch slot/format |
| `disk_list(slot_id)` | optional | Clip list on disk |

### Device & Configuration

| Method | Parameters | Description |
|---|---|---|
| `device_info()` | — | Device model, firmware info |
| `transport_info()` | — | Current transport state |
| `configuration(**kwargs)` | keyword args | Query or set configuration |
| `remote(enable, override)` | both optional | Remote control state |
| `uptime()` | — | Time since last boot |
| `identify(enable)` | `bool` | Flash front-panel LED |
| `reboot()` | — | Reboot device |

**Configuration example:**
```python
deck.configuration()                           # query all
deck.configuration(video_input="HDMI")         # set video input
deck.configuration(file_format="QuickTimeProRes", audio_codec="AAC")
```

### Notifications

```python
deck.notify()                           # query notification settings
deck.notify(transport=True, slot=True)  # enable specific notifications
deck.watchdog(period=30)                # disconnect if idle >30s
```

---

## Project Structure

```
VRLiveStreaming_MachineControlScript/
├── factory.py      # HyperdeckBase, device classes, AJA_Control, factory
└── README.md
```

---

## License

This project is licensed under the terms found in [LICENSE](LICENSE).
