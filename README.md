# VRLiveStreaming_MachineControlScript

A Python library for controlling broadcast and AV hardware devices over the network. Designed to be used as a dependency in larger VR live-streaming workflows, it provides a unified factory interface for connecting to and commanding devices via TCP socket or HTTP.

---

## Supported Devices

| Class | Device | Protocol |
|---|---|---|
| `AJA_Control` | AJA KUMO Video Router | HTTP |
| `Hyperdeck8K_Control` | Blackmagic HyperDeck Extreme 8K | TCP Socket |
| `HyperdeckHD_Control` | Blackmagic HyperDeck HD | TCP Socket |

---

## Requirements

- Python 3.x
- [`requests`](https://pypi.org/project/requests/) library

Install dependencies:

```bash
pip install requests
```

---

## Usage

All instances are created through the `ControlScriptFactory`.

```python
from factory import ControlScriptFactory

factory = ControlScriptFactory()
```

### AJA KUMO Router

Switch an input to an output destination via HTTP:

```python
aja = factory.create_aja_control("192.168.1.100")

# Route input 1 to output 2
aja.connect(input=1, output=2)
```

| Parameter | Description |
|---|---|
| `ip_address` | IP address of the AJA KUMO device |
| `input` | Source input number |
| `output` | Destination output number |

---

### Blackmagic HyperDeck 8K

Control recording on a HyperDeck Extreme 8K via TCP socket (default port: `9993`):

```python
deck8k = factory.create_hyperdeck8K_control("192.168.1.101", port=9993)

deck8k.start_recording()  # Start recording (non-blocking)
deck8k.stop_recording()   # Stop recording (non-blocking)
```

---

### Blackmagic HyperDeck HD

Same interface as HyperDeck 8K:

```python
deckHD = factory.create_hyperdeckHD_control("192.168.1.102", port=9993)

deckHD.start_recording()
deckHD.stop_recording()
```

> **Note:** Recording commands are executed in a background thread so they do not block the calling program.

---

## API Reference

### `ControlScriptFactory`

| Method | Parameters | Returns |
|---|---|---|
| `create_aja_control(ip_address)` | `ip_address: str` | `AJA_Control` |
| `create_hyperdeck8K_control(ip_address, port)` | `ip_address: str`, `port: int` | `Hyperdeck8K_Control` |
| `create_hyperdeckHD_control(ip_address, port)` | `ip_address: str`, `port: int` | `HyperdeckHD_Control` |

### `AJA_Control`

| Method | Parameters | Returns |
|---|---|---|
| `connect(input, output)` | `input: int`, `output: int` | `requests.Response` |

### `Hyperdeck8K_Control` / `HyperdeckHD_Control`

| Method | Parameters | Description |
|---|---|---|
| `start_recording()` | — | Sends `record` command in a background thread |
| `stop_recording()` | — | Sends `stop` command in a background thread |

---

## Project Structure

```
VRLiveStreaming_MachineControlScript/
├── factory.py      # All device control classes and factory
└── README.md
```

---

## License

This project is licensed under the terms found in [LICENSE](LICENSE).
