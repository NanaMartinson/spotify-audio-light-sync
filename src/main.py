"""
Main application for Spotify Audio-Reactive USB Light Sync.
"""

import argparse
import os
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from audio_capture import AudioCapture
from audio_analysis import AudioAnalyzer
from color_mapper import ColorMapper
from usb_controller import USBController
from spotify_client import SpotifyClient
from spotify_color_mapper import SpotifyColorMapper


class AudioLightSync:
    """Main application class for audio-reactive light sync."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize application with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.running = False
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Initialize components
        audio_config = config.get('audio', {})
        self.audio_capture = AudioCapture(
            sample_rate=audio_config.get('sample_rate', 44100),
            chunk_size=audio_config.get('chunk_size', 2048),
            device_index=audio_config.get('device_index')
        )
        
        analysis_config = config.get('analysis', {})
        self.audio_analyzer = AudioAnalyzer(
            sample_rate=audio_config.get('sample_rate', 44100),
            chunk_size=audio_config.get('chunk_size', 2048),
            bass_range=tuple(analysis_config.get('bass_range', [0, 50])),
            mids_range=tuple(analysis_config.get('mids_range', [50, 150])),
            highs_range=tuple(analysis_config.get('highs_range', [150, 300])),
            smoothing_window=analysis_config.get('smoothing_window', 5)
        )
        
        colors_config = config.get('colors', {})
        self.color_mapper = ColorMapper(
            sensitivity=colors_config.get('sensitivity', 1.0),
            brightness=colors_config.get('brightness', 1.0),
            mode=colors_config.get('mode', 'balanced')
        )
        
        usb_config = config.get('usb', {})
        self.usb_controller = USBController(
            vendor_id=usb_config.get('vendor_id'),
            product_id=usb_config.get('product_id'),
            simulate=usb_config.get('simulate', True)
        )
        
        self.verbose = False
    
    def start(self, verbose: bool = False) -> bool:
        """
        Start the audio-reactive light sync.
        
        Args:
            verbose: Enable verbose output
            
        Returns:
            True if started successfully, False otherwise
        """
        self.verbose = verbose
        
        # Connect to USB device
        if not self.usb_controller.connect():
            print("Failed to connect to USB controller")
            return False
        
        # Start audio capture
        if not self.audio_capture.start():
            print("Failed to start audio capture")
            return False
        
        print("\n" + "=" * 60)
        print("Spotify Audio-Reactive USB Light Sync - STARTED")
        print("=" * 60)
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        return True
    
    def run(self):
        """Main event loop."""
        try:
            while self.running:
                # Read audio data
                audio_data = self.audio_capture.read()
                
                if audio_data is not None:
                    # Analyze audio
                    bass, mids, highs = self.audio_analyzer.analyze(audio_data)
                    
                    # Map to RGB
                    r, g, b = self.color_mapper.map_to_rgb(bass, mids, highs)
                    
                    # Update USB light
                    self.usb_controller.set_color(r, g, b)
                    
                    # Update FPS counter
                    self.update_fps()
                    
                    # Display status
                    self.display_status(bass, mids, highs, r, g, b)
                else:
                    time.sleep(0.01)
                    
        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            self.stop()
    
    def update_fps(self):
        """Update FPS counter."""
        self.fps_counter += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def display_status(self, bass: float, mids: float, highs: float,
                       r: int, g: int, b: int):
        """
        Display current status in terminal.
        
        Args:
            bass, mids, highs: Frequency band values
            r, g, b: RGB values
        """
        # Create color bar visualization
        color_str = self.color_mapper.get_color_string(r, g, b)
        reset_str = self.color_mapper.reset_color()
        color_bar = f"{color_str}{'  ' * 10}{reset_str}"
        
        # Create frequency bars
        bass_bar = self._create_bar(bass, 20)
        mids_bar = self._create_bar(mids, 20)
        highs_bar = self._create_bar(highs, 20)
        
        # Clear line and print status
        output = (
            f"\r"
            f"FPS: {self.current_fps:5.1f} | "
            f"RGB: ({r:3d}, {g:3d}, {b:3d}) {color_bar} | "
            f"Bass: {bass_bar} | "
            f"Mids: {mids_bar} | "
            f"Highs: {highs_bar}"
        )
        
        print(output, end='', flush=True)
        
        if self.verbose:
            print()  # New line for verbose mode
    
    @staticmethod
    def _create_bar(value: float, width: int = 20) -> str:
        """
        Create ASCII bar visualization.
        
        Args:
            value: Value between 0.0 and 1.0
            width: Width of bar in characters
            
        Returns:
            ASCII bar string
        """
        filled = int(value * width)
        bar = '█' * filled + '░' * (width - filled)
        return f"{bar} {value:4.2f}"
    
    def stop(self):
        """Stop the application."""
        self.running = False
        self.audio_capture.stop()
        self.audio_capture.close()
        self.usb_controller.disconnect()
        print("\n\n" + "=" * 60)
        print("Stopped")
        print("=" * 60)


class SpotifyLightSync:
    """Spotify API mode for light sync using track audio features."""
    
    def __init__(self, config: Dict[str, Any], spotify_config: Dict[str, Any]):
        """
        Initialize Spotify light sync application.
        
        Args:
            config: Main configuration dictionary
            spotify_config: Spotify-specific configuration
        """
        self.config = config
        self.spotify_config = spotify_config
        self.running = False
        
        # Initialize Spotify client
        client_id = spotify_config.get('client_id')
        client_secret = spotify_config.get('client_secret')
        redirect_uri = spotify_config.get('redirect_uri', 'http://localhost:8888/callback')
        
        if not client_id or not client_secret:
            raise ValueError("Spotify client_id and client_secret are required")
        
        self.spotify_client = SpotifyClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )
        
        # Initialize color mapper
        color_mode = spotify_config.get('color_mode', 'mood')
        self.color_mapper = SpotifyColorMapper(mode=color_mode)
        
        # Initialize USB controller
        usb_config = config.get('usb', {})
        self.usb_controller = USBController(
            vendor_id=usb_config.get('vendor_id'),
            product_id=usb_config.get('product_id'),
            simulate=usb_config.get('simulate', True)
        )
        
        # Polling configuration
        self.poll_interval = spotify_config.get('poll_interval', 3)
        
        # State tracking
        self.last_track_id = None
        self.current_rgb = (0, 0, 0)
        self.verbose = False
    
    def start(self, verbose: bool = False) -> bool:
        """
        Start the Spotify light sync.
        
        Args:
            verbose: Enable verbose output
            
        Returns:
            True if started successfully, False otherwise
        """
        self.verbose = verbose
        
        # Connect to USB device
        if not self.usb_controller.connect():
            print("Failed to connect to USB controller")
            return False
        
        print("\n" + "=" * 60)
        print("Spotify API Light Sync - STARTED")
        print("=" * 60)
        print(f"Color mode: {self.color_mapper.mode}")
        print(f"Poll interval: {self.poll_interval}s")
        print("\nWaiting for Spotify playback...")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        return True
    
    def run(self):
        """Main event loop for Spotify mode."""
        try:
            while self.running:
                # Check if playing
                if not self.spotify_client.is_playing():
                    if self.verbose:
                        print("\rNo playback detected...", end='', flush=True)
                    time.sleep(self.poll_interval)
                    continue
                
                # Get current track
                track_info = self.spotify_client.get_current_track()
                if track_info is None:
                    time.sleep(self.poll_interval)
                    continue
                
                track_id, track_name, artist_name = track_info
                
                # Check if track changed
                if track_id != self.last_track_id:
                    self.last_track_id = track_id
                    
                    # Fetch audio features for new track
                    audio_features = self.spotify_client.get_audio_features(track_id)
                    
                    if audio_features is not None:
                        # Map to RGB
                        r, g, b = self.color_mapper.map_to_rgb(audio_features)
                        self.current_rgb = (r, g, b)
                        
                        # Update USB light
                        self.usb_controller.set_color(r, g, b)
                        
                        # Display status
                        self.display_status(track_name, artist_name, audio_features, r, g, b)
                    else:
                        print(f"\nCould not fetch audio features for: {track_name}")
                
                # Wait before next poll
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            self.stop()
    
    def display_status(self, track_name: str, artist_name: str,
                      audio_features: Dict[str, float], r: int, g: int, b: int):
        """
        Display current status in terminal.
        
        Args:
            track_name: Name of current track
            artist_name: Artist name
            audio_features: Audio features dictionary
            r, g, b: RGB values
        """
        # Create color bar visualization
        color_str = f"\033[48;2;{r};{g};{b}m"
        reset_str = "\033[0m"
        color_bar = f"{color_str}{'  ' * 10}{reset_str}"
        
        # Clear terminal
        print("\n" + "=" * 60)
        print(f"🎵  Now Playing: {track_name}")
        print(f"👤  Artist: {artist_name}")
        print("=" * 60)
        
        # Display RGB color
        print(f"\nRGB: ({r:3d}, {g:3d}, {b:3d}) {color_bar}")
        
        # Display audio features
        print(f"\nAudio Features:")
        print(f"  Energy:          {audio_features['energy']:.2f} {self._create_bar(audio_features['energy'], 15)}")
        print(f"  Valence (mood):  {audio_features['valence']:.2f} {self._create_bar(audio_features['valence'], 15)}")
        print(f"  Danceability:    {audio_features['danceability']:.2f} {self._create_bar(audio_features['danceability'], 15)}")
        print(f"  Acousticness:    {audio_features['acousticness']:.2f} {self._create_bar(audio_features['acousticness'], 15)}")
        print(f"  Instrumentalness: {audio_features['instrumentalness']:.2f} {self._create_bar(audio_features['instrumentalness'], 15)}")
        print(f"  Tempo:           {audio_features['tempo']:.1f} BPM")
        print("\n")
    
    @staticmethod
    def _create_bar(value: float, width: int = 15) -> str:
        """
        Create ASCII bar visualization.
        
        Args:
            value: Value between 0.0 and 1.0
            width: Width of bar in characters
            
        Returns:
            ASCII bar string
        """
        filled = int(value * width)
        bar = '█' * filled + '░' * (width - filled)
        return bar
    
    def stop(self):
        """Stop the application."""
        self.running = False
        self.usb_controller.disconnect()
        print("\n" + "=" * 60)
        print("Stopped")
        print("=" * 60)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def list_audio_devices():
    """List all available audio devices."""
    capture = AudioCapture()
    devices = capture.list_devices()
    
    print("\nAvailable audio input devices:")
    print("-" * 60)
    for idx, name, channels in devices:
        print(f"[{idx}] {name} ({channels} channels)")
    print("-" * 60)
    
    loopback = capture.find_loopback_device()
    if loopback is not None:
        print(f"\nDetected loopback/monitor device: [{loopback}]")
    else:
        print("\nNo loopback/monitor device detected")
        print("You may need to enable one for system audio capture:")
        print("  - Windows: Enable 'Stereo Mix' in sound settings")
        print("  - macOS: Install BlackHole virtual audio device")
        print("  - Linux: Use PulseAudio monitor source")
    
    capture.close()


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description='Spotify Audio-Reactive USB Light Sync',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/settings.yaml',
        help='Path to configuration file (default: config/settings.yaml)'
    )
    
    parser.add_argument(
        '--list-devices',
        action='store_true',
        help='List available audio devices and exit'
    )
    
    parser.add_argument(
        '--list-usb',
        action='store_true',
        help='List available USB devices and exit'
    )
    
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Run in simulation mode (no USB device required)'
    )
    
    parser.add_argument(
        '--sensitivity',
        type=float,
        help='Override sensitivity setting (0.1 to 5.0)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose debug output'
    )
    
    # Spotify mode arguments
    parser.add_argument(
        '--spotify',
        action='store_true',
        help='Use Spotify API mode instead of audio capture'
    )
    
    parser.add_argument(
        '--spotify-client-id',
        type=str,
        help='Spotify app client ID (or set SPOTIFY_CLIENT_ID env var)'
    )
    
    parser.add_argument(
        '--spotify-client-secret',
        type=str,
        help='Spotify app client secret (or set SPOTIFY_CLIENT_SECRET env var)'
    )
    
    parser.add_argument(
        '--spotify-redirect-uri',
        type=str,
        help='OAuth redirect URI (default: http://localhost:8888/callback, or set SPOTIFY_REDIRECT_URI env var)'
    )
    
    parser.add_argument(
        '--spotify-color-mode',
        type=str,
        choices=['mood', 'energy', 'genre_feel'],
        help='Spotify color mapping mode (mood, energy, genre_feel)'
    )
    
    args = parser.parse_args()
    
    # List devices and exit if requested
    if args.list_devices:
        list_audio_devices()
        return
    
    if args.list_usb:
        USBController.list_usb_devices()
        return
    
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        print("Creating default configuration...")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create default config
        default_config = {
            'audio': {
                'sample_rate': 44100,
                'chunk_size': 2048,
                'device_index': None
            },
            'analysis': {
                'bass_range': [0, 50],
                'mids_range': [50, 150],
                'highs_range': [150, 300],
                'smoothing_window': 5
            },
            'colors': {
                'sensitivity': 1.0,
                'brightness': 1.0,
                'mode': 'balanced'
            },
            'usb': {
                'vendor_id': None,
                'product_id': None,
                'simulate': True
            },
            'spotify': {
                'client_id': None,
                'client_secret': None,
                'redirect_uri': 'http://localhost:8888/callback',
                'poll_interval': 3,
                'color_mode': 'mood'
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"Created default configuration at: {config_path}")
        print("Please edit the configuration file and run again.")
        return
    
    config = load_config(str(config_path))
    
    # Apply command-line overrides
    if args.simulate:
        config['usb']['simulate'] = True
    
    if args.sensitivity is not None:
        config['colors']['sensitivity'] = args.sensitivity
    
    # Handle Spotify mode
    if args.spotify:
        # Prepare Spotify configuration with environment variables and CLI overrides
        spotify_config = config.get('spotify', {})
        
        # Environment variables take precedence over config, CLI args take precedence over all
        spotify_config['client_id'] = (
            args.spotify_client_id or 
            os.getenv('SPOTIFY_CLIENT_ID') or 
            spotify_config.get('client_id')
        )
        
        spotify_config['client_secret'] = (
            args.spotify_client_secret or 
            os.getenv('SPOTIFY_CLIENT_SECRET') or 
            spotify_config.get('client_secret')
        )
        
        spotify_config['redirect_uri'] = (
            args.spotify_redirect_uri or 
            os.getenv('SPOTIFY_REDIRECT_URI') or 
            spotify_config.get('redirect_uri', 'http://localhost:8888/callback')
        )
        
        if args.spotify_color_mode:
            spotify_config['color_mode'] = args.spotify_color_mode
        
        # Validate required credentials
        if not spotify_config.get('client_id') or not spotify_config.get('client_secret'):
            print("Error: Spotify client_id and client_secret are required for --spotify mode")
            print("\nProvide them via:")
            print("  1. Command line: --spotify-client-id ID --spotify-client-secret SECRET")
            print("  2. Environment: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
            print("  3. Config file: config/settings.yaml")
            print("\nGet credentials at: https://developer.spotify.com/dashboard")
            return
        
        # Create and run Spotify app
        try:
            app = SpotifyLightSync(config, spotify_config)
            if app.start(verbose=args.verbose):
                app.run()
        except Exception as e:
            print(f"Error: {e}")
            return
    else:
        # Create and run audio capture app (original mode)
        app = AudioLightSync(config)
        
        if app.start(verbose=args.verbose):
            app.run()


if __name__ == '__main__':
    main()
