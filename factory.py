import requests
import socket
import threading


# ---------------------------------------------------------------------------
# HyperDeck Base – full HyperDeck Ethernet Protocol (TCP port 9993)
# ---------------------------------------------------------------------------

class HyperdeckBase:
    """
    Persistent-connection controller for Blackmagic HyperDeck devices using
    the HyperDeck Ethernet Protocol (TCP port 9993).

    Usage (context-manager, recommended):
        with Hyperdeck8K_Control("192.168.1.100", 9993) as deck:
            deck.record()
            deck.stop()

    Usage (manual):
        deck = Hyperdeck8K_Control("192.168.1.100", 9993)
        deck.connect()
        deck.record()
        deck.disconnect()
    """

    DEFAULT_PORT = 9993

    def __init__(self, ip_address: str, port: int = DEFAULT_PORT):
        self.ip_address = ip_address
        self.port = port
        self._sock: socket.socket | None = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> str:
        """Open a persistent TCP connection. Returns the greeting banner."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5)
        self._sock.connect((self.ip_address, self.port))
        banner = self._recv_response()
        return banner

    def disconnect(self):
        """Close the connection."""
        if self._sock:
            try:
                self._sock.sendall(b"quit\r\n")
            except Exception:
                pass
            self._sock.close()
            self._sock = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def send_command(self, command: str) -> str:
        """
        Send a raw protocol command and return the full response string.
        Thread-safe.
        """
        if self._sock is None:
            raise ConnectionError("Not connected. Call connect() first.")
        with self._lock:
            self._sock.sendall((command.strip() + "\r\n").encode())
            return self._recv_response()

    def _recv_response(self) -> str:
        """Read until a blank line (protocol response terminator)."""
        data = b""
        while True:
            chunk = self._sock.recv(4096)
            if not chunk:
                break
            data += chunk
            # Responses end with \r\n\r\n or a single \r\n for one-liners
            if data.endswith(b"\r\n\r\n") or data.endswith(b"\n\n"):
                break
            # Single-line responses (e.g. "200 ok\r\n") end immediately
            decoded = data.decode(errors="replace")
            lines = [l for l in decoded.splitlines() if l.strip()]
            if lines and not lines[-1].endswith(":"):
                # No continuation expected
                break
        return data.decode(errors="replace").strip()

    # ------------------------------------------------------------------
    # Transport Control
    # ------------------------------------------------------------------

    def play(self, speed: int | None = None,
             loop: bool | None = None,
             single_clip: bool | None = None) -> str:
        """
        Start playback.

        Args:
            speed:       Playback speed, -5000 to 5000 (100 = normal).
            loop:        Loop playback.
            single_clip: Play only the current clip.
        """
        cmd = "play"
        if speed is not None:
            cmd += f": speed: {speed}"
        if loop is not None:
            cmd += f" loop: {'true' if loop else 'false'}"
        if single_clip is not None:
            cmd += f" single clip: {'true' if single_clip else 'false'}"
        return self.send_command(cmd)

    def stop(self) -> str:
        """Stop playback or recording."""
        return self.send_command("stop")

    def record(self, name: str | None = None) -> str:
        """
        Start recording.

        Args:
            name: Optional clip name for the recorded file.
        """
        if name:
            return self.send_command(f"record: name: {name}")
        return self.send_command("record")

    def record_spill(self, slot_id: int | None = None) -> str:
        """
        Spill current recording to the next slot (or a specified slot).

        Args:
            slot_id: Target slot ID. Omit to spill to the next available slot.
        """
        if slot_id is not None:
            return self.send_command(f"record spill: slot id: {slot_id}")
        return self.send_command("record spill")

    def preview(self, enable: bool) -> str:
        """Switch between preview and output mode."""
        return self.send_command(f"preview: enable: {'true' if enable else 'false'}")

    # ------------------------------------------------------------------
    # Goto / Jog / Shuttle
    # ------------------------------------------------------------------

    def goto_clip_id(self, clip_id: int | str) -> str:
        """
        Jump to a specific clip.

        Args:
            clip_id: Clip number, or 'start' / 'end'.
        """
        return self.send_command(f"goto: clip id: {clip_id}")

    def goto_clip_id_relative(self, offset: int) -> str:
        """
        Jump forward (+) or backward (-) by a number of clips.

        Args:
            offset: Positive = forward, negative = backward.
        """
        sign = "+" if offset >= 0 else ""
        return self.send_command(f"goto: clip id: {sign}{offset}")

    def goto_clip(self, position: int | str) -> str:
        """
        Jump to a frame position within the current clip.

        Args:
            position: Frame number, or 'start' / 'end'.
        """
        return self.send_command(f"goto: clip: {position}")

    def goto_timecode(self, timecode: str) -> str:
        """
        Jump to an absolute timecode position in the timeline.

        Args:
            timecode: Timecode string, e.g. '01:00:00:00'.
        """
        return self.send_command(f"goto: timecode: {timecode}")

    def goto_timeline(self, position: int | str) -> str:
        """
        Jump to a frame position in the timeline.

        Args:
            position: Frame number, or 'start' / 'end'.
        """
        return self.send_command(f"goto: timeline: {position}")

    def jog(self, timecode: str) -> str:
        """
        Jog to or by a timecode.

        Args:
            timecode: Absolute timecode or relative with leading '+'/'-'.
        """
        return self.send_command(f"jog: timecode: {timecode}")

    def shuttle(self, speed: int) -> str:
        """
        Shuttle at the given speed.

        Args:
            speed: -5000 to 5000.
        """
        return self.send_command(f"shuttle: speed: {speed}")

    # ------------------------------------------------------------------
    # Playrange
    # ------------------------------------------------------------------

    def playrange_set_clip(self, clip_id: int, count: int | None = None) -> str:
        """
        Set play range to a specific clip, or a number of clips from that clip.

        Args:
            clip_id: Starting clip ID.
            count:   Number of clips to play (optional).
        """
        if count is not None:
            return self.send_command(f"playrange set: clip id: {clip_id} count: {count}")
        return self.send_command(f"playrange set: clip id: {clip_id}")

    def playrange_set_timecode(self, in_tc: str, out_tc: str) -> str:
        """
        Set play range between two timecodes.

        Args:
            in_tc:  In-point timecode, e.g. '00:01:00:00'.
            out_tc: Out-point timecode, e.g. '00:02:00:00'.
        """
        return self.send_command(f"playrange set: in: {in_tc} out: {out_tc}")

    def playrange_set_timeline(self, frame_in: int, frame_out: int) -> str:
        """
        Set play range in timeline frames.

        Args:
            frame_in:  In-point frame number.
            frame_out: Out-point frame number.
        """
        return self.send_command(
            f"playrange set: timeline in: {frame_in} timeline out: {frame_out}"
        )

    def playrange_clear(self) -> str:
        """Clear/reset the play range."""
        return self.send_command("playrange clear")

    def playrange(self) -> str:
        """Query current play range setting."""
        return self.send_command("playrange")

    # ------------------------------------------------------------------
    # Clip Management
    # ------------------------------------------------------------------

    def clips_count(self) -> str:
        """Query the number of clips on the timeline."""
        return self.send_command("clips count")

    def clips_get(self, clip_id: int | None = None, count: int | None = None,
                  version: int | None = None) -> str:
        """
        Query clip information from the timeline.

        Args:
            clip_id: First clip to retrieve (omit for all clips).
            count:   Number of clips to retrieve.
            version: Output format version (1, 2, or 3).
        """
        cmd = "clips get"
        if clip_id is not None:
            cmd += f": clip id: {clip_id}"
            if count is not None:
                cmd += f" count: {count}"
        if version is not None:
            cmd += f": version: {version}"
        return self.send_command(cmd)

    def clips_add(self, name: str, clip_id: int | None = None) -> str:
        """
        Append (or insert) a clip to the timeline.

        Args:
            name:    Clip filename (supports subfolders, e.g. 'folder/clip.mp4').
            clip_id: Insert before this clip ID (omit to append).
        """
        if clip_id is not None:
            return self.send_command(f"clips add: clip id: {clip_id} name: {name}")
        return self.send_command(f"clips add: name: {name}")

    def clips_remove(self, clip_id: int) -> str:
        """
        Remove a clip from the timeline.

        Args:
            clip_id: ID of the clip to remove.
        """
        return self.send_command(f"clips remove: clip id: {clip_id}")

    def clips_clear(self) -> str:
        """Empty the timeline clip list."""
        return self.send_command("clips clear")

    def clip_info(self, clip_id: int | None = None, name: str | None = None) -> str:
        """
        Query clip info for the current, or a specific clip.

        Args:
            clip_id: Timeline clip ID (optional).
            name:    Clip filename on the active disk (optional).
        """
        if clip_id is not None:
            return self.send_command(f"clip info: clip id: {clip_id}")
        if name is not None:
            return self.send_command(f"clip info: name: {name}")
        return self.send_command("clip info")

    # ------------------------------------------------------------------
    # Slot & Disk
    # ------------------------------------------------------------------

    def slot_info(self, slot_id: int | None = None) -> str:
        """
        Query slot information.

        Args:
            slot_id: Slot number (omit for the active slot).
        """
        if slot_id is not None:
            return self.send_command(f"slot info: slot id: {slot_id}")
        return self.send_command("slot info")

    def slot_select(self, slot_id: int | None = None,
                    video_format: str | None = None) -> str:
        """
        Switch to a slot and/or select a video format.

        Args:
            slot_id:      Target slot ID.
            video_format: Video format string, e.g. '1080p25'.
        """
        parts = []
        if slot_id is not None:
            parts.append(f"slot id: {slot_id}")
        if video_format is not None:
            parts.append(f"video format: {video_format}")
        return self.send_command("slot select: " + " ".join(parts))

    def disk_list(self, slot_id: int | None = None) -> str:
        """
        Query the clip list on disk.

        Args:
            slot_id: Slot number (omit for the active disk).
        """
        if slot_id is not None:
            return self.send_command(f"disk list: slot id: {slot_id}")
        return self.send_command("disk list")

    # ------------------------------------------------------------------
    # Device & Configuration
    # ------------------------------------------------------------------

    def device_info(self) -> str:
        """Return device information."""
        return self.send_command("device info")

    def transport_info(self) -> str:
        """Query current transport state."""
        return self.send_command("transport info")

    def configuration(self, **kwargs) -> str:
        """
        Query or update device configuration.

        Called with no arguments returns current configuration.
        Pass keyword arguments to set parameters, e.g.:
            configuration(video_input="HDMI")
            configuration(file_format="QuickTimeProRes")
            configuration(audio_codec="AAC")

        Underscores in key names are replaced with spaces automatically.
        """
        if not kwargs:
            return self.send_command("configuration")
        params = " ".join(
            f"{k.replace('_', ' ')}: {v}" for k, v in kwargs.items()
        )
        return self.send_command(f"configuration: {params}")

    def uptime(self) -> str:
        """Return time since last boot."""
        return self.send_command("uptime")

    def remote(self, enable: bool | None = None,
               override: bool | None = None) -> str:
        """
        Query or set remote control state.

        Args:
            enable:   Enable or disable remote control.
            override: Override remote control for this session.
        """
        if enable is None and override is None:
            return self.send_command("remote")
        parts = []
        if enable is not None:
            parts.append(f"enable: {'true' if enable else 'false'}")
        if override is not None:
            parts.append(f"override: {'true' if override else 'false'}")
        return self.send_command("remote: " + " ".join(parts))

    def ping(self) -> str:
        """Check the device is responding."""
        return self.send_command("ping")

    def identify(self, enable: bool) -> str:
        """Flash the front-panel LED to identify the device."""
        return self.send_command(f"identify: enable: {'true' if enable else 'false'}")

    def reboot(self) -> str:
        """Reboot the device."""
        return self.send_command("reboot")

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def notify(self, remote: bool | None = None,
               transport: bool | None = None,
               slot: bool | None = None,
               configuration: bool | None = None,
               dropped_frames: bool | None = None,
               display_timecode: bool | None = None,
               timeline_position: bool | None = None,
               playrange: bool | None = None,
               cache: bool | None = None,
               dynamic_range: bool | None = None,
               clips: bool | None = None,
               disk: bool | None = None) -> str:
        """
        Configure asynchronous notifications from the device.

        Called with no arguments returns current notification settings.
        Pass True/False for any notification type to enable or disable it.
        """
        mapping = {
            "remote": remote,
            "transport": transport,
            "slot": slot,
            "configuration": configuration,
            "dropped frames": dropped_frames,
            "display timecode": display_timecode,
            "timeline position": timeline_position,
            "playrange": playrange,
            "cache": cache,
            "dynamic range": dynamic_range,
            "clips": clips,
            "disk": disk,
        }
        active = {k: v for k, v in mapping.items() if v is not None}
        if not active:
            return self.send_command("notify")
        params = " ".join(
            f"{k}: {'true' if v else 'false'}" for k, v in active.items()
        )
        return self.send_command(f"notify: {params}")

    def watchdog(self, period: int) -> str:
        """
        Configure connection watchdog.

        Args:
            period: Timeout in seconds. 0 or less disables monitoring.
        """
        return self.send_command(f"watchdog: period: {period}")


# ---------------------------------------------------------------------------
# Device-specific subclasses (protocol is identical; subclasses allow
# for future model-specific overrides or metadata)
# ---------------------------------------------------------------------------

class Hyperdeck8K_Control(HyperdeckBase):
    """Controller for Blackmagic HyperDeck Extreme 8K."""
    pass


class HyperdeckHD_Control(HyperdeckBase):
    """Controller for Blackmagic HyperDeck HD."""
    pass


# ---------------------------------------------------------------------------
# AJA KUMO Router — HTTP-based control (unchanged)
# ---------------------------------------------------------------------------

class AJA_Control:
    """HTTP-based controller for AJA KUMO video routers."""

    def __init__(self, ip_address: str):
        self.ip_address = ip_address

    def connect(self, input: int, output: int) -> requests.Response:
        """
        Route a source input to a destination output.

        Args:
            input:  Source input number.
            output: Destination output number.

        Returns:
            requests.Response from the KUMO HTTP API.
        """
        url = (
            f"http://{self.ip_address}"
            f"/config?action=set&config=0"
            f"&paramid=eParamID_XPT_Destination{output}_Status"
            f"&value={input}"
        )
        return requests.get(url)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class ControlScriptFactory:
    """Factory for creating machine control instances."""

    def create_aja_control(self, ip_address: str) -> AJA_Control:
        return AJA_Control(ip_address)

    def create_hyperdeck8K_control(self, ip_address: str,
                                   port: int = HyperdeckBase.DEFAULT_PORT
                                   ) -> Hyperdeck8K_Control:
        return Hyperdeck8K_Control(ip_address, port)

    def create_hyperdeckHD_control(self, ip_address: str,
                                   port: int = HyperdeckBase.DEFAULT_PORT
                                   ) -> HyperdeckHD_Control:
        return HyperdeckHD_Control(ip_address, port)