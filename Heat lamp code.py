import serial
import serial.tools.list_ports
import time
from pynput import keyboard
import threading


DMX_CHANNEL = 1
SERIAL_PORT = None
SERIAL_BAUDRATE = 250000
UHI_effect = 2.0
adjusted_UHI_effect = 0


ENTTEC_START = 0x7E
ENTTEC_END = 0xE7
ENTTEC_LABEL = 6


def find_dmx_port():
    """Auto-detect the first USB-serial port (likely the DMX adapter)."""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
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
        value = max(0, min(255, value))
        self.dmx_universe[self.channel - 1] = value
        packet = build_enttec_packet(self.dmx_universe)
        self.ser.write(packet)
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


# ── Demo / Interactive CLI ───────────────────────────────────────────────────

def Set_brightness_of_lamp(lamp: HeatLampController, UHI_effect: float = UHI_effect):
    while True:
        try:
            adjusted_UHI_effect = 265 / 3 * UHI_effect
            lamp.set_brightness(adjusted_UHI_effect)
        except ValueError:
            print("[warn] Invalid UHI effect")

def on_press(key):
    global UHI_effect
    if key.char == 'g':
        UHI_effect = 0
    if key.char == 'b':
        UHI_effect = 2.75




if __name__ == "__main__":
    with HeatLampController(channel=DMX_CHANNEL, port=SERIAL_PORT) as lamp:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        Set_brightness_of_lamp(lamp, UHI_effect=UHI_effect)
