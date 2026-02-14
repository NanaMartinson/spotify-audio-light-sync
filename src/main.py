"""
Main application for Spotify Audio-Reactive USB Light Sync.
"""

import argparse
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, Any

from audio_capture import AudioCapture
from audio_analysis import AudioAnalyzer
from color_mapper import ColorMapper
from usb_controller import USBController


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
    
    # Create and run application
    app = AudioLightSync(config)
    
    if app.start(verbose=args.verbose):
        app.run()


if __name__ == '__main__':
    main()
