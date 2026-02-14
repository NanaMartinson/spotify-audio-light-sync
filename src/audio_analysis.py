"""
Audio analysis module for FFT and frequency band analysis.
"""

import numpy as np
from scipy import fft
from collections import deque
from typing import Tuple, List


class AudioAnalyzer:
    """Performs frequency analysis on audio data."""
    
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 2048,
                 bass_range: Tuple[int, int] = (0, 50),
                 mids_range: Tuple[int, int] = (50, 150),
                 highs_range: Tuple[int, int] = (150, 300),
                 smoothing_window: int = 5):
        """
        Initialize audio analyzer.
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Size of audio chunks
            bass_range: FFT bin range for bass frequencies
            mids_range: FFT bin range for mid frequencies
            highs_range: FFT bin range for high frequencies
            smoothing_window: Number of frames to average for smoothing
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.bass_range = bass_range
        self.mids_range = mids_range
        self.highs_range = highs_range
        
        # Rolling average buffers for smoothing
        self.smoothing_window = smoothing_window
        self.bass_history = deque(maxlen=smoothing_window)
        self.mids_history = deque(maxlen=smoothing_window)
        self.highs_history = deque(maxlen=smoothing_window)
    
    def analyze(self, audio_data: np.ndarray) -> Tuple[float, float, float]:
        """
        Analyze audio data and extract frequency band amplitudes.
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Tuple of (bass, mids, highs) amplitude values (0.0 to 1.0)
        """
        if audio_data is None or len(audio_data) == 0:
            return 0.0, 0.0, 0.0
        
        # Perform FFT
        fft_data = fft.fft(audio_data)
        fft_magnitude = np.abs(fft_data[:len(fft_data)//2])  # Only positive frequencies
        
        # Normalize
        if np.max(fft_magnitude) > 0:
            fft_magnitude = fft_magnitude / np.max(fft_magnitude)
        
        # Extract frequency bands
        bass = self._extract_band(fft_magnitude, self.bass_range)
        mids = self._extract_band(fft_magnitude, self.mids_range)
        highs = self._extract_band(fft_magnitude, self.highs_range)
        
        # Apply smoothing
        bass = self._smooth(bass, self.bass_history)
        mids = self._smooth(mids, self.mids_history)
        highs = self._smooth(highs, self.highs_history)
        
        return bass, mids, highs
    
    def _extract_band(self, fft_magnitude: np.ndarray, band_range: Tuple[int, int]) -> float:
        """
        Extract average amplitude for a frequency band.
        
        Args:
            fft_magnitude: FFT magnitude data
            band_range: Tuple of (start_bin, end_bin)
            
        Returns:
            Average amplitude for the band
        """
        start, end = band_range
        end = min(end, len(fft_magnitude))
        
        if start >= end:
            return 0.0
        
        band_data = fft_magnitude[start:end]
        return np.mean(band_data) if len(band_data) > 0 else 0.0
    
    def _smooth(self, value: float, history: deque) -> float:
        """
        Apply rolling average smoothing to a value.
        
        Args:
            value: Current value
            history: Deque of historical values
            
        Returns:
            Smoothed value
        """
        history.append(value)
        return np.mean(history) if len(history) > 0 else value
    
    def get_frequency_bins(self) -> np.ndarray:
        """
        Get the frequency values for each FFT bin.
        
        Returns:
            Array of frequency values in Hz
        """
        return fft.fftfreq(self.chunk_size, 1.0/self.sample_rate)[:self.chunk_size//2]
