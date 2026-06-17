import serial
import serial.tools.list_ports
import math
import time


DMX_CHANNEL = 142
SERIAL_PORT = None
SERIAL_BAUDRATE = 19200
UHI_effect = 2.0
adjusted_UHI_effect = 0


ENTTEC_START = 0x7E
ENTTEC_END = 0xE7
ENTTEC_LABEL = 100


def find_dmx_port():
    """Auto-detect the first USB-serial port (likely the DMX adapter)."""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(f"[info] Found serial port: {p.device} - {p.description}")
        if any(k in p.description.lower() for k in ("enttec", "dmx", "ftdi", "usb serial")):
            return p.device
    # Fallback: return first available port
    if ports:
        print(f"[warn] No obvious DMX adapter found. Using first port: {ports[0].device}")
        return ports[0].device
    raise RuntimeError("No serial ports found")


def build_enttec_packet(dmx_data: list[int]) -> bytes:
    """
    Wrap a list of 512 DMX values in an Enttec USB DMX Pro packet.
    dmx_data: list of 512 ints, index 0 = DMX channel 1.
    """
    assert len(dmx_data) == 512
    payload = bytes([0x00] + dmx_data)  # start code + 512 channel values
    length_lsb = len(payload) & 0xFF
    length_msb = (len(payload) >> 8) & 0xFF
    packet = bytes([
        ENTTEC_START,
        ENTTEC_LABEL,
        length_lsb,
        length_msb,
        *payload,
        ENTTEC_END
    ])
    return packet


class HeatLampController:
    def __init__(self, channel: int = DMX_CHANNEL, port: str = None):
        self.channel = channel  # 1-indexed DMX channel
        self.dmx_universe = [0] * 512  # All channels off by default
        port = port or find_dmx_port()
        print(f"[info] Opening DMX port: {port}")
        self.ser = serial.Serial(port, baudrate=SERIAL_BAUDRATE, timeout=1)

    def set_brightness(self, value: int):
        """
        Set lamp brightness.
        value: 0 (off) to 255 (full brightness / maximum heat).
        """
        value = int(round(max(0, min(255, value))))
        self.dmx_universe[self.channel - 1] = value
        packet = build_enttec_packet(self.dmx_universe)
        self.ser.write(packet)
        # print(f"packet: {len(packet)} bytes, first 10 bytes: {packet[:10]}")
        print(f"[dmx] Channel {self.channel} → {value}  ({value / 255 * 100:.1f}%)")

    def set_percent(self, percent: float):
        """Set brightness as a percentage (0.0 – 100.0)."""
        self.set_brightness(int(percent / 100 * 255))

    def off(self):
        self.set_brightness(0)

    def close(self):
        self.off()
        self.ser.close()
        print("[info] DMX connection closed.")

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# ── Demo / Wave Loop ─────────────────────────────────────────────────────────

def run_brightness_wave(
    lamp: HeatLampController,
    min_effect: float = 0.0,
    max_effect: float = 2.75,
    period_seconds: float = 4.0,
):
    """Continuously move the lamp brightness in a smooth wave."""
    if period_seconds <= 0:
        raise ValueError("period_seconds must be greater than 0")

    phase = 0.0
    step = (2 * math.pi) / max(1, int(period_seconds * 20))

    while True:
        wave = (math.sin(phase) + 1) / 2
        UHI_effect = min_effect + (max_effect - min_effect) * wave
        adjusted_UHI_effect = 265 / 3 * UHI_effect
        lamp.set_brightness(adjusted_UHI_effect)
        phase += step
        time.sleep(period_seconds / max(1, int(period_seconds * 20)))

def set_brightness(lamp: HeatLampController,
    brightness: int
):
    lamp.set_brightness(brightness)


if __name__ == "__main__":
    with HeatLampController(channel=DMX_CHANNEL, port=SERIAL_PORT) as lamp:
        # run_brightness_wave(lamp)
        while True:
            set_brightness(lamp, 255)  # Set to ~50% brightness for testing
