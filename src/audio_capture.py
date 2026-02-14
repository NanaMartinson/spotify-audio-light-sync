"""
Audio capture module for capturing system audio in real-time.
Supports Windows (WASAPI), macOS (BlackHole/Soundflower), and Linux (PulseAudio).
"""

import pyaudio
import numpy as np
from typing import Optional, List, Tuple


class AudioCapture:
    """Handles real-time audio capture from system audio output."""
    
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 2048, 
                 device_index: Optional[int] = None):
        """
        Initialize audio capture.
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per chunk
            device_index: Specific audio device index, None for default
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.device_index = device_index
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    def list_devices(self) -> List[Tuple[int, str, int]]:
        """
        List all available audio input devices.
        
        Returns:
            List of tuples (index, name, max_input_channels)
        """
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append((
                    i,
                    info['name'],
                    info['maxInputChannels']
                ))
        return devices
    
    def find_loopback_device(self) -> Optional[int]:
        """
        Attempt to find a loopback/monitor device for system audio.
        
        Returns:
            Device index if found, None otherwise
        """
        keywords = ['stereo mix', 'wave out', 'loopback', 'monitor', 'blackhole']
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            name_lower = info['name'].lower()
            if any(keyword in name_lower for keyword in keywords):
                if info['maxInputChannels'] > 0:
                    return i
        return None
    
    def start(self) -> bool:
        """
        Start audio capture stream.
        
        Returns:
            True if stream started successfully, False otherwise
        """
        try:
            # If no device specified, try to find loopback device
            if self.device_index is None:
                self.device_index = self.find_loopback_device()
            
            # Open stream
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=2,  # Stereo
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            return True
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            return False
    
    def read(self) -> Optional[np.ndarray]:
        """
        Read audio data from stream.
        
        Returns:
            Numpy array of audio samples (mono), or None if error
        """
        if self.stream is None or not self.stream.is_active():
            return None
        
        try:
            # Read audio data
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            
            # Convert to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Convert stereo to mono by averaging channels
            if len(audio_data) >= 2:
                audio_data = audio_data.reshape(-1, 2).mean(axis=1)
            
            # Normalize to -1.0 to 1.0
            audio_data = audio_data.astype(np.float32) / 32768.0
            
            return audio_data
        except Exception as e:
            print(f"Error reading audio: {e}")
            return None
    
    def stop(self):
        """Stop audio capture stream."""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def close(self):
        """Clean up audio resources."""
        self.stop()
        self.audio.terminate()
