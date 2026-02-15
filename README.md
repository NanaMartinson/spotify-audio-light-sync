# Spotify Audio-Reactive USB Light Sync

A Python application that syncs USB RGB lights with audio playback from Spotify (or any system audio) in real-time. The light reacts dynamically to music's frequency content, creating an immersive audio-visual experience.

## Features

- **Spotify API Integration (Recommended)**: Use Spotify Web API to sync lights with currently playing track based on audio features
- **Real-time Audio Capture**: Captures system audio output on Windows, macOS, and Linux
- **Frequency Analysis**: Performs FFT analysis and splits audio into bass, mids, and highs
- **Dynamic Color Mapping**: Maps frequency bands to RGB channels (Bass→Red, Mids→Green, Highs→Blue)
- **USB Light Control**: Generic USB HID device interface for RGB lights
- **Simulation Mode**: Test without physical hardware using terminal visualization
- **Cross-Platform**: Supports Windows (WASAPI), macOS (BlackHole), and Linux (PulseAudio)
- **Configurable**: YAML-based configuration with CLI overrides
- **Multiple Presets**: Balanced, bass-heavy, and treble-focus modes (audio capture) / Mood, energy, genre_feel (Spotify)

## Spotify API Mode (Recommended)

The Spotify API mode connects directly to your Spotify account to read what you're currently playing and maps the track's audio features (energy, valence, danceability, etc.) to beautiful, dynamic RGB colors. This is the **recommended** approach for most users.

### Why Use Spotify Mode?

- ✅ **No Complex Audio Setup**: Works instantly with OAuth, no audio loopback configuration needed
- ✅ **Works with Headphones**: Unlike audio capture, Spotify mode doesn't need system audio routing
- ✅ **Spotify Jam Compatible**: Start a Spotify Jam session and the lights follow along
- ✅ **Intelligent Colors**: Maps mood, energy, and genre characteristics to colors
- ✅ **Cross-Platform**: Same experience on all operating systems

### Quick Start

1. **Register a Spotify App** (one-time setup):
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Click "Create an App"
   - Name it anything (e.g., "Light Sync")
   - Set Redirect URI to: `http://localhost:8888/callback`
   - Note your **Client ID** and **Client Secret**

2. **Set Environment Variables**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your credentials
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```

3. **Run in Spotify Mode**:
   ```bash
   cd src
   python main.py --spotify --simulate
   ```

   On first run, your browser will open for Spotify OAuth. Log in and authorize the app.

4. **Play Music**: Start playing any track on Spotify and watch the lights change!

### Spotify Color Modes

The Spotify mode offers three color mapping strategies:

- **`mood` (default)**: Maps valence (happiness) to hue - sad songs get cool blues/purples, happy songs get warm yellows/oranges. Brightness based on energy, saturation based on danceability.

- **`energy`**: Emphasizes energy levels - low energy tracks get cool blues, high energy tracks get hot reds. Perfect for workout playlists.

- **`genre_feel`**: Nuanced palette that emphasizes acousticness and instrumentalness. Acoustic tracks shift towards warm greens, instrumental tracks get ambient, less saturated colors.

Change mode with:
```bash
python main.py --spotify --spotify-color-mode energy --simulate
```

### Configuration Options

**Via Command Line**:
```bash
python main.py --spotify \
  --spotify-client-id YOUR_ID \
  --spotify-client-secret YOUR_SECRET \
  --spotify-redirect-uri http://localhost:8888/callback \
  --spotify-color-mode mood \
  --simulate
```

**Via Environment Variables** (recommended):
```bash
# .env file
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

**Via Config File**:
```yaml
# config/settings.yaml
spotify:
  client_id: your_id
  client_secret: your_secret
  redirect_uri: "http://localhost:8888/callback"
  poll_interval: 3      # Seconds between API polls
  color_mode: "mood"    # mood, energy, genre_feel
```

**Priority**: CLI args > Environment variables > Config file

### How It Works

1. Authenticates with Spotify using OAuth 2.0 (opens browser on first run)
2. Polls Spotify API every 3 seconds to check what's currently playing
3. When a new track starts, fetches its audio features (energy, valence, tempo, danceability, acousticness, instrumentalness, speechiness, liveness)
4. Maps features to RGB color using HSV color space transformations
5. Sends color to your USB light (or displays in terminal with `--simulate`)

### Spotify Jam Sessions

Just start a Jam on Spotify and have the host run the app. The lights will sync to whatever's playing in the Jam!

### Troubleshooting Spotify Mode

**"Error: Spotify client_id and client_secret are required"**
- Make sure you've set credentials via CLI, environment variables, or config file
- Check that your .env file is in the repository root

**Browser doesn't open for OAuth**
- OAuth will print a URL - copy it and open manually in your browser
- After authorizing, you'll be redirected to localhost - copy the full URL and paste it back in the terminal

**"Could not fetch audio features"**
- Some tracks (especially very new or local files) may not have audio features
- The app will continue working when you play a different track

**401 Unauthorized errors**
- Your token may have expired - delete `.spotify_cache` and re-authenticate
- Verify your Client ID and Secret are correct

## Requirements

- Python 3.8 or higher
- USB RGB light (optional - works in simulate mode without hardware)
- **For Spotify API mode**: Spotify account and registered app (free)
- **For Audio Capture mode**: System audio loopback capability (see Platform-Specific Setup below)

## Installation

### 1. Install System Dependencies

**Note**: For **Spotify API mode only**, you don't need system audio dependencies (portaudio). You can skip step 1 if you only plan to use Spotify mode.

**Windows:**
```bash
# PyAudio wheel will be installed via pip
# No additional system dependencies needed
```

**macOS:**
```bash
brew install portaudio  # Only needed for audio capture mode
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio libusb-1.0-0  # portaudio only for audio capture mode
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

### Spotify API Mode (Recommended)

See the [Spotify API Mode section](#spotify-api-mode-recommended) above for setup instructions.

```bash
cd src
# First time - browser will open for authentication
python main.py --spotify --simulate

# Subsequent runs
python main.py --spotify --simulate

# With different color mode
python main.py --spotify --spotify-color-mode energy --simulate
```

### Audio Capture Mode

#### Basic Usage (Simulation Mode)

Test the application without USB hardware:

```bash
cd src
python main.py --simulate
```

This will display real-time audio analysis in your terminal with color visualization.

#### With USB Device

After configuring your USB device in `config/settings.yaml`:

```bash
cd src
python main.py
```

#### List Audio Devices

Find available audio input devices:

```bash
cd src
python main.py --list-devices
```

### Command-Line Arguments

```bash
python main.py [options]

Options:
  --config PATH              Path to configuration file (default: config/settings.yaml)
  --list-devices             List available audio devices and exit
  --list-usb                 List available USB devices and exit
  --simulate                 Run in simulation mode (no USB device)
  --sensitivity FLOAT        Override sensitivity setting (0.1 to 5.0) [audio capture mode]
  --verbose                  Enable verbose debug output
  
  Spotify Mode:
  --spotify                  Use Spotify API mode instead of audio capture
  --spotify-client-id ID     Spotify app client ID (or set SPOTIFY_CLIENT_ID)
  --spotify-client-secret S  Spotify app client secret (or set SPOTIFY_CLIENT_SECRET)
  --spotify-redirect-uri U   OAuth redirect URI (default: http://localhost:8888/callback)
  --spotify-color-mode MODE  Color mapping mode: mood, energy, genre_feel (default: mood)
```

### Examples

```bash
# Audio capture mode (original)
python main.py --config my_config.yaml

# Increase sensitivity in audio capture mode
python main.py --sensitivity 2.0

# Verbose mode with simulation
python main.py --simulate --verbose

# Spotify mode with simulation
python main.py --spotify --simulate

# Spotify mode with custom credentials
python main.py --spotify \
  --spotify-client-id YOUR_ID \
  --spotify-client-secret YOUR_SECRET \
  --spotify-color-mode energy \
  --simulate
```

## Configuration

Edit `config/settings.yaml` to customize behavior:

```yaml
audio:
  sample_rate: 44100        # Audio sample rate [audio capture mode]
  chunk_size: 2048          # Samples per chunk (affects latency) [audio capture mode]
  device_index: null        # null for auto-detect, or specific device number [audio capture mode]

analysis:
  bass_range: [0, 50]       # FFT bin range for bass [audio capture mode]
  mids_range: [50, 150]     # FFT bin range for mids [audio capture mode]
  highs_range: [150, 300]   # FFT bin range for highs [audio capture mode]
  smoothing_window: 5       # Frames to average (higher = smoother) [audio capture mode]

colors:
  sensitivity: 1.0          # Global sensitivity multiplier [audio capture mode]
  brightness: 1.0           # Brightness control (0.0 - 1.0) [audio capture mode]
  mode: "balanced"          # balanced, bass_heavy, treble_focus [audio capture mode]

usb:
  vendor_id: null           # USB Vendor ID (hex)
  product_id: null          # USB Product ID (hex)
  simulate: true            # Set false to use real USB device

spotify:
  client_id: null           # Your Spotify app client ID [Spotify mode]
  client_secret: null       # Your Spotify app client secret [Spotify mode]
  redirect_uri: "http://localhost:8888/callback"  # OAuth redirect URI [Spotify mode]
  poll_interval: 3          # Seconds between polling Spotify API [Spotify mode]
  color_mode: "mood"        # mood, energy, genre_feel [Spotify mode]
```

### Audio Capture Color Modes

- **balanced**: Equal emphasis on all frequencies
- **bass_heavy**: Emphasizes low frequencies (great for EDM, hip-hop)
- **treble_focus**: Emphasizes high frequencies (great for vocals, acoustic)

### Spotify Color Modes

See [Spotify Color Modes section](#spotify-color-modes) above for details on `mood`, `energy`, and `genre_feel`.

## Troubleshooting

### Spotify Mode Issues

See [Troubleshooting Spotify Mode section](#troubleshooting-spotify-mode) above.

### Audio Capture Mode Issues

#### No Audio Detected

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
│   ├── __init__.py              # Package initialization
│   ├── audio_capture.py         # Audio input handling [audio capture mode]
│   ├── audio_analysis.py        # FFT and frequency analysis [audio capture mode]
│   ├── color_mapper.py          # Frequency to RGB mapping [audio capture mode]
│   ├── spotify_client.py        # Spotify Web API client [Spotify mode]
│   ├── spotify_color_mapper.py  # Audio features to RGB mapping [Spotify mode]
│   ├── usb_controller.py        # USB light control
│   └── main.py                  # Main application loop
├── tests/
│   └── test_spotify_color_mapper.py  # Unit tests for Spotify color mapper
├── config/
│   └── settings.yaml            # Configuration file
├── .env.example                 # Example environment variables for Spotify
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── .gitignore                   # Git ignore rules
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
- Real-time track lyrics display alongside colors
- Support for multiple lights
- Preset save/load functionality
- Audio visualization graphs
- Machine learning for adaptive color mapping
- Integration with smart home systems (HomeAssistant, etc.)
- Apple Music / YouTube Music API integration

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Spotify Web API integration via Spotipy library
- Uses PyAudio for cross-platform audio capture
- FFT analysis powered by SciPy
- USB communication via PyUSB

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Refer to the Troubleshooting section above
