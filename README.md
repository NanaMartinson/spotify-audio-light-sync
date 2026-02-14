# Spotify Audio-Reactive USB Light Sync

A Python application that syncs USB RGB lights with audio playback from Spotify (or any system audio) in real-time. The light reacts dynamically to music's frequency content, creating an immersive audio-visual experience.

## Features

- **Real-time Audio Capture**: Captures system audio output on Windows, macOS, and Linux
- **Frequency Analysis**: Performs FFT analysis and splits audio into bass, mids, and highs
- **Dynamic Color Mapping**: Maps frequency bands to RGB channels (Bass→Red, Mids→Green, Highs→Blue)
- **USB Light Control**: Generic USB HID device interface for RGB lights
- **Simulation Mode**: Test without physical hardware using terminal visualization
- **Cross-Platform**: Supports Windows (WASAPI), macOS (BlackHole), and Linux (PulseAudio)
- **Configurable**: YAML-based configuration with CLI overrides
- **Multiple Presets**: Balanced, bass-heavy, and treble-focus modes

## Requirements

- Python 3.8 or higher
- USB RGB light (optional - works in simulate mode without hardware)
- System audio loopback capability (see Platform-Specific Setup below)

## Installation

### 1. Install System Dependencies

**Windows:**
```bash
# PyAudio wheel will be installed via pip
# No additional system dependencies needed
```

**macOS:**
```bash
brew install portaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio libusb-1.0-0
```

### 2. Clone Repository

```bash
git clone https://github.com/NanaMartinson/spotify-audio-light-sync.git
cd spotify-audio-light-sync
```

### 3. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

## Platform-Specific Audio Setup

### Windows - WASAPI Loopback

1. Open **Sound Settings** → **Sound Control Panel**
2. Go to **Recording** tab
3. Right-click and enable **Show Disabled Devices**
4. Find **Stereo Mix** and enable it
5. Set it as the default recording device (or note its device index)

### macOS - BlackHole Virtual Audio Device

1. Install BlackHole:
   ```bash
   brew install blackhole-2ch
   ```

2. Configure Audio MIDI Setup:
   - Open **Audio MIDI Setup** (Applications → Utilities)
   - Create a **Multi-Output Device**
   - Check both your speakers and BlackHole
   - Set this as your system output device

3. Set Spotify to output to the Multi-Output Device

### Linux - PulseAudio Monitor

PulseAudio monitor sources are usually available by default. List devices to find the monitor:

```bash
python src/main.py --list-devices
```

Look for devices with "monitor" in the name.

## USB Device Setup

### Finding Your USB Device IDs

1. Connect your USB RGB light

2. List USB devices:
   ```bash
   python src/main.py --list-usb
   ```

3. Identify your device's Vendor ID (VID) and Product ID (PID)

4. Update `config/settings.yaml`:
   ```yaml
   usb:
     vendor_id: 0x1234  # Replace with your VID
     product_id: 0x5678  # Replace with your PID
     simulate: false     # Disable simulation mode
   ```

### Common USB RGB Lights

The application uses a generic USB HID protocol that works with many common USB RGB lights. If your device uses a different protocol, you may need to modify `usb_controller.py`.

### Linux USB Permissions

On Linux, you may need to add a udev rule for USB access:

```bash
# Create udev rule
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1234", ATTR{idProduct}=="5678", MODE="0666"' | sudo tee /etc/udev/rules.d/99-usb-light.rules

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Replace `1234` and `5678` with your device's VID and PID.

## Usage

### Basic Usage (Simulation Mode)

Test the application without USB hardware:

```bash
cd src
python main.py --simulate
```

This will display real-time audio analysis in your terminal with color visualization.

### With USB Device

After configuring your USB device in `config/settings.yaml`:

```bash
cd src
python main.py
```

### List Audio Devices

Find available audio input devices:

```bash
cd src
python main.py --list-devices
```

### Command-Line Arguments

```bash
python main.py [options]

Options:
  --config PATH        Path to configuration file (default: config/settings.yaml)
  --list-devices       List available audio devices and exit
  --list-usb          List available USB devices and exit
  --simulate          Run in simulation mode (no USB device)
  --sensitivity FLOAT  Override sensitivity setting (0.1 to 5.0)
  --verbose           Enable verbose debug output
```

### Examples

```bash
# Use custom config file
python main.py --config my_config.yaml

# Increase sensitivity
python main.py --sensitivity 2.0

# Verbose mode with simulation
python main.py --simulate --verbose
```

## Configuration

Edit `config/settings.yaml` to customize behavior:

```yaml
audio:
  sample_rate: 44100        # Audio sample rate
  chunk_size: 2048          # Samples per chunk (affects latency)
  device_index: null        # null for auto-detect, or specific device number

analysis:
  bass_range: [0, 50]       # FFT bin range for bass
  mids_range: [50, 150]     # FFT bin range for mids
  highs_range: [150, 300]   # FFT bin range for highs
  smoothing_window: 5       # Frames to average (higher = smoother)

colors:
  sensitivity: 1.0          # Global sensitivity multiplier
  brightness: 1.0           # Brightness control (0.0 - 1.0)
  mode: "balanced"          # balanced, bass_heavy, treble_focus

usb:
  vendor_id: null           # USB Vendor ID (hex)
  product_id: null          # USB Product ID (hex)
  simulate: true            # Set false to use real USB device
```

### Color Modes

- **balanced**: Equal emphasis on all frequencies
- **bass_heavy**: Emphasizes low frequencies (great for EDM, hip-hop)
- **treble_focus**: Emphasizes high frequencies (great for vocals, acoustic)

## Troubleshooting

### No Audio Detected

1. Verify loopback device is configured (see Platform-Specific Setup)
2. List devices: `python main.py --list-devices`
3. Play some audio and check if levels change
4. Specify device manually in config: `device_index: X`

### USB Device Not Found

1. Check device is connected: `python main.py --list-usb`
2. Verify VID/PID in config matches your device
3. On Linux, check USB permissions (see USB Device Setup)
4. Try running with `sudo` (Linux) or as Administrator (Windows)

### Poor Responsiveness

1. Increase sensitivity: `--sensitivity 2.0`
2. Adjust frequency ranges in config
3. Reduce `smoothing_window` for faster response
4. Change color mode to emphasize certain frequencies

### Audio Stuttering

1. Increase `chunk_size` to 4096 (reduces CPU load)
2. Close other audio applications
3. Update audio drivers

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# On Windows, you may need the PyAudio wheel:
pip install pipwin
pipwin install pyaudio
```

## Development

### Project Structure

```
spotify-audio-light-sync/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── audio_capture.py      # Audio input handling
│   ├── audio_analysis.py     # FFT and frequency analysis
│   ├── color_mapper.py       # Frequency to RGB mapping
│   ├── usb_controller.py     # USB light control
│   └── main.py               # Main application loop
├── config/
│   └── settings.yaml         # Configuration file
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Running from Source

```bash
cd src
python main.py --simulate
```

## Performance

- **Target FPS**: 30-60 Hz update rate
- **Latency**: <50ms from audio to light change
- **CPU Usage**: ~5-10% on modern systems
- **Memory**: ~50-100MB

## Future Enhancements

Potential features for future development:

- Beat detection with peak finding algorithm
- Web UI for remote control (Flask/FastAPI)
- Spotify API integration for track metadata display
- Support for multiple lights
- Preset save/load functionality
- Audio visualization graphs
- Machine learning for adaptive color mapping
- Integration with smart home systems (HomeAssistant, etc.)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Uses PyAudio for cross-platform audio capture
- FFT analysis powered by SciPy
- USB communication via PyUSB

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Refer to the Troubleshooting section above
