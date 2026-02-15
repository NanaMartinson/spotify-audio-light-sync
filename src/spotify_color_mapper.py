"""
Color mapping module for converting Spotify audio features to RGB values.
"""

import colorsys
from typing import Tuple, Dict


class SpotifyColorMapper:
    """Maps Spotify audio features to RGB color values using HSV color space."""
    
    # Color mode configurations
    MODES = {
        'mood': {
            'description': 'Maps valence (mood) to hue, energy to brightness',
            'use_valence_hue': True,
            'use_energy_brightness': True,
            'use_danceability_saturation': True,
            'apply_acoustic_shift': True,
            'apply_instrumental_ambient': True
        },
        'energy': {
            'description': 'Emphasizes energy levels - low energy = cool blues, high energy = hot reds',
            'use_valence_hue': False,
            'use_energy_brightness': True,
            'use_danceability_saturation': False,
            'apply_acoustic_shift': False,
            'apply_instrumental_ambient': False
        },
        'genre_feel': {
            'description': 'Emphasizes acousticness and instrumentalness for nuanced palette',
            'use_valence_hue': True,
            'use_energy_brightness': True,
            'use_danceability_saturation': True,
            'apply_acoustic_shift': True,
            'apply_instrumental_ambient': True
        }
    }
    
    def __init__(self, mode: str = 'mood'):
        """
        Initialize Spotify color mapper.
        
        Args:
            mode: Color mapping mode ('mood', 'energy', 'genre_feel')
        """
        self.mode = mode if mode in self.MODES else 'mood'
        self.mode_config = self.MODES[self.mode]
    
    def set_mode(self, mode: str):
        """
        Set color mapping mode.
        
        Args:
            mode: Mode name ('mood', 'energy', 'genre_feel')
        """
        if mode in self.MODES:
            self.mode = mode
            self.mode_config = self.MODES[mode]
    
    def map_to_rgb(self, audio_features: Dict[str, float]) -> Tuple[int, int, int]:
        """
        Map Spotify audio features to RGB values.
        
        Args:
            audio_features: Dictionary with audio features (energy, valence, tempo, etc.)
            
        Returns:
            Tuple of (R, G, B) values (0-255)
        """
        # Extract features with defaults
        energy = audio_features.get('energy', 0.5)
        valence = audio_features.get('valence', 0.5)
        danceability = audio_features.get('danceability', 0.5)
        acousticness = audio_features.get('acousticness', 0.5)
        instrumentalness = audio_features.get('instrumentalness', 0.5)
        
        # Calculate HSV values based on mode
        hue = self._calculate_hue(valence, energy, acousticness)
        saturation = self._calculate_saturation(danceability, instrumentalness)
        value = self._calculate_value(energy)
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        
        # Scale to 0-255 range
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        
        # Ensure values are in valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return r, g, b
    
    def _calculate_hue(self, valence: float, energy: float, acousticness: float) -> float:
        """
        Calculate hue value based on audio features.
        
        Args:
            valence: Valence value (0.0-1.0)
            energy: Energy value (0.0-1.0)
            acousticness: Acousticness value (0.0-1.0)
            
        Returns:
            Hue value (0.0-1.0)
        """
        if self.mode == 'energy':
            # Energy mode: map energy to hue
            # Low energy (0) -> blue (0.65), high energy (1) -> red (0.0)
            # We need to wrap around: 0.65 -> 1.0 -> 0.0
            hue = 0.65 - (energy * 0.65)
            if hue < 0:
                hue += 1.0
        else:
            # Mood/genre_feel modes: map valence to hue
            # Valence 0 (sad) -> blue-purple (0.65)
            # Valence 1 (happy) -> warm orange-yellow (0.1)
            # We map valence inversely since we want to go from 0.65 to 0.1
            hue = 0.65 - (valence * 0.55)
            if hue < 0:
                hue += 1.0
        
        # Apply acoustic shift if enabled (shift towards green/warm tones)
        if self.mode_config['apply_acoustic_shift'] and acousticness > 0.7:
            # Shift hue slightly towards green (0.33)
            shift_amount = (acousticness - 0.7) * 0.1  # Max shift of 0.03
            hue = (hue + shift_amount) % 1.0
        
        return hue
    
    def _calculate_saturation(self, danceability: float, instrumentalness: float) -> float:
        """
        Calculate saturation value based on audio features.
        
        Args:
            danceability: Danceability value (0.0-1.0)
            instrumentalness: Instrumentalness value (0.0-1.0)
            
        Returns:
            Saturation value (0.0-1.0)
        """
        if self.mode == 'energy':
            # Energy mode: use fixed medium-high saturation
            saturation = 0.8
        else:
            # Mood/genre_feel: base saturation on danceability
            if self.mode_config['use_danceability_saturation']:
                saturation = 0.4 + (danceability * 0.6)
            else:
                saturation = 0.7
        
        # Apply instrumental ambient feel if enabled
        if self.mode_config['apply_instrumental_ambient'] and instrumentalness > 0.7:
            # Reduce saturation for more ambient feel
            reduction = (instrumentalness - 0.7) * 0.3  # Max reduction of 0.09
            saturation = max(0.3, saturation - reduction)
        
        return saturation
    
    def _calculate_value(self, energy: float) -> float:
        """
        Calculate brightness/value based on energy.
        
        Args:
            energy: Energy value (0.0-1.0)
            
        Returns:
            Value/brightness (0.0-1.0)
        """
        if self.mode_config['use_energy_brightness']:
            # Map energy to brightness: 0.3 (low energy) to 1.0 (high energy)
            value = 0.3 + (energy * 0.7)
        else:
            # Fixed medium-high brightness
            value = 0.8
        
        return value
    
    def get_mode_description(self) -> str:
        """
        Get description of current color mode.
        
        Returns:
            Mode description string
        """
        return self.mode_config.get('description', 'No description available')
