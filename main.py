"""
DMX Dimmer Controller
Hardware: Work Duo Dim Series 2 + MINI-USB-DMX-INTERFACE (Eurolite/compatible)

The MINI-USB-DMX-INTERFACE uses the FT232R chip and appears as a serial port.
It uses a DMX break signal followed by 512 channels of data.

Install dependencies:
    pip install pyserial

Find your device:
    Linux:   ls /dev/ttyUSB*
    Windows: check Device Manager for COMx
    macOS:   ls /dev/tty.usbserial*
"""

import serial
import time
import sys

# ─── Configuration ────────────────────────────────────────────────────────────

# Change this to match your system
SERIAL_PORT = "/dev/ttyUSB0"   # Linux default; Windows: "COM3", macOS: "/dev/tty.usbserial-XXXX"

# Work Duo Dim Series 2 DMX start address (set via DIP switches on the unit)
# Channel 1 = dimmer output 1, Channel 2 = dimmer output 2
DMX_START_ADDRESS = 1   # First channel (1-512)

# ─── DMX Interface ────────────────────────────────────────────────────────────

class MiniUSBDMX:
    """
    Driver for MINI-USB-DMX-INTERFACE (FT232R-based).
    Sends a DMX512 frame over the serial port using a break + mark sequence.
    """

    DMX_BAUD     = 250_000   # DMX standard baud rate
    DMX_CHANNELS = 512

    def __init__(self, port: str):
        self.port = port
        self._universe = [0] * (self.DMX_CHANNELS + 1)  # index 0 = start code
        self._ser = None

    def open(self):
        self._ser = serial.Serial(
            port=self.port,
            baudrate=self.DMX_BAUD,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            timeout=1,
        )
        print(f"[DMX] Opened {self.port} at {self.DMX_BAUD} baud")

    def close(self):
        if self._ser and self._ser.is_open:
            # Fade to black before closing
            self.blackout()
            self._ser.close()
            print("[DMX] Port closed")

    def set_channel(self, channel: int, value: int):
        """Set a single DMX channel (1-512) to a value (0-255)."""
        if not (1 <= channel <= self.DMX_CHANNELS):
            raise ValueError(f"Channel must be 1-512, got {channel}")
        value = max(0, min(255, value))
        self._universe[channel] = value

    def get_channel(self, channel: int) -> int:
        return self._universe[channel]

    def send(self):
        """Transmit one DMX frame."""
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("Serial port is not open")

        # DMX BREAK: hold line low for ≥88 µs
        # We do this by temporarily dropping to a low baud rate and sending a null byte.
        self._ser.baudrate = 76_800
        self._ser.write(b'\x00')
        self._ser.flush()

        # Restore DMX baud rate (Mark After Break is handled by serial framing)
        self._ser.baudrate = self.DMX_BAUD

        # Send start code (0x00) + 512 channel bytes
        frame = bytes(self._universe)
        self._ser.write(frame)
        self._ser.flush()

    def blackout(self):
        """Set all channels to 0 and send."""
        self._universe = [0] * (self.DMX_CHANNELS + 1)
        self.send()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()


# ─── Work Duo Dim Series 2 helper ─────────────────────────────────────────────

class WorkDuoDim:
    """
    Abstraction for the Work Duo Dim Series 2 two-channel dimmer pack.

    DMX mapping (relative to start address set on the unit):
        offset 0  →  Output 1 (0=off, 255=full)
        offset 1  →  Output 2 (0=off, 255=full)

    The unit uses linear 8-bit dimming by default.
    """

    def __init__(self, dmx: MiniUSBDMX, start_address: int = 1):
        self.dmx = dmx
        self.start = start_address
        self._levels = [0, 0]   # ch1, ch2

    def set(self, output: int, level: float, send: bool = True):
        """
        Set output brightness.
        output: 1 or 2
        level:  0.0 (off) to 1.0 (full)
        """
        if output not in (1, 2):
            raise ValueError("Output must be 1 or 2")
        dmx_value = round(max(0.0, min(1.0, level)) * 255)
        channel = self.start + (output - 1)
        self._levels[output - 1] = dmx_value
        self.dmx.set_channel(channel, dmx_value)
        if send:
            self.dmx.send()

    def set_both(self, level: float):
        """Set both outputs to the same level."""
        self.set(1, level, send=False)
        self.set(2, level, send=True)

    def fade(self, output: int, target: float, duration: float, steps: int = 50):
        """Smooth fade on a single output."""
        start_val = self._levels[output - 1] / 255.0
        target_val = max(0.0, min(1.0, target))
        step_delay = duration / steps
        for i in range(steps + 1):
            level = start_val + (target_val - start_val) * (i / steps)
            self.set(output, level, send=True)
            time.sleep(step_delay)

    def fade_both(self, target: float, duration: float, steps: int = 50):
        """Smooth fade on both outputs simultaneously."""
        start1 = self._levels[0] / 255.0
        start2 = self._levels[1] / 255.0
        target_val = max(0.0, min(1.0, target))
        step_delay = duration / steps
        for i in range(steps + 1):
            t = i / steps
            self.set(1, start1 + (target_val - start1) * t, send=False)
            self.set(2, start2 + (target_val - start2) * t, send=True)
            time.sleep(step_delay)

    def off(self):
        self.set_both(0.0)

    def full(self):
        self.set_both(1.0)


# ─── Demo / interactive CLI ───────────────────────────────────────────────────

def demo(port: str, start_address: int):
    print(f"\nWork Duo Dim Series 2  —  DMX start address: {start_address}")
    print("=" * 50)

    with MiniUSBDMX(port) as dmx:
        dimmer = WorkDuoDim(dmx, start_address)

        print("\n[1] Fading both channels in over 2 seconds...")
        dimmer.fade_both(1.0, duration=2.0)
        time.sleep(1)

        print("[2] Fading output 1 to 50%...")
        dimmer.fade(1, 0.5, duration=1.0)
        time.sleep(1)

        print("[3] Fading output 2 to 25%...")
        dimmer.fade(2, 0.25, duration=1.0)
        time.sleep(1)

        print("[4] Fading both out over 3 seconds...")
        dimmer.fade_both(0.0, duration=3.0)
        time.sleep(0.5)

        print("\nDemo done. Blackout sent.")


def interactive_cli(port: str, start_address: int):
    print(f"\nWork Duo Dim Series 2  —  interactive mode")
    print(f"Port: {port}  |  DMX start: {start_address}")
    print("Commands:  1 <0-100>   2 <0-100>   both <0-100>   fade <ch> <0-100> <secs>   quit")

    with MiniUSBDMX(port) as dmx:
        dimmer = WorkDuoDim(dmx, start_address)
        dimmer.off()

        while True:
            try:
                raw = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break

            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0]

            try:
                if cmd in ("1", "2") and len(parts) == 2:
                    level = int(parts[1]) / 100.0
                    dimmer.set(int(cmd), level)
                    print(f"  Output {cmd} → {int(parts[1])}%")

                elif cmd == "both" and len(parts) == 2:
                    level = int(parts[1]) / 100.0
                    dimmer.set_both(level)
                    print(f"  Both outputs → {int(parts[1])}%")

                elif cmd == "fade" and len(parts) == 4:
                    ch = int(parts[1])
                    level = int(parts[2]) / 100.0
                    dur = float(parts[3])
                    print(f"  Fading output {ch} to {int(parts[2])}% over {dur}s...")
                    dimmer.fade(ch, level, duration=dur)

                elif cmd in ("quit", "exit", "q"):
                    break

                else:
                    print("  Unknown command. Try: 1 80  |  both 50  |  fade 2 100 3  |  quit")

            except (ValueError, IndexError) as e:
                print(f"  Error: {e}")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Work Duo Dim Series 2 DMX controller")
    parser.add_argument("--port", default=SERIAL_PORT, help="Serial port (e.g. /dev/ttyUSB0 or COM3)")
    parser.add_argument("--address", type=int, default=DMX_START_ADDRESS, help="DMX start address (1-512)")
    parser.add_argument("--demo", action="store_true", help="Run the built-in fade demo")
    args = parser.parse_args()

    if args.demo:
        demo(args.port, args.address)
    else:
        interactive_cli(args.port, args.address)