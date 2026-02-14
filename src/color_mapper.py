"""
Color mapping module for converting frequency bands to RGB values.
"""

import numpy as np
from typing import Tuple, Dict


class ColorMapper:
    """Maps frequency band amplitudes to RGB color values."""
    
    # Preset modes
    MODES = {
        'balanced': {'bass': 1.0, 'mids': 1.0, 'highs': 1.0},
        'bass_heavy': {'bass': 1.5, 'mids': 0.8, 'highs': 0.6},
        'treble_focus': {'bass': 0.6, 'mids': 0.8, 'highs': 1.5}
    }
    
    def __init__(self, sensitivity: float = 1.0, brightness: float = 1.0,
                 mode: str = 'balanced'):
        """
        Initialize color mapper.
        
        Args:
            sensitivity: Global sensitivity multiplier (0.1 to 5.0)
            brightness: Overall brightness control (0.0 to 1.0)
            mode: Preset mode ('balanced', 'bass_heavy', 'treble_focus')
        """
        self.sensitivity = max(0.1, min(5.0, sensitivity))
        self.brightness = max(0.0, min(1.0, brightness))
        self.mode = mode if mode in self.MODES else 'balanced'
        self.mode_multipliers = self.MODES[self.mode]
    
    def map_to_rgb(self, bass: float, mids: float, highs: float) -> Tuple[int, int, int]:
        """
        Map frequency band amplitudes to RGB values.
        
        Args:
            bass: Bass amplitude (0.0 to 1.0)
            mids: Mids amplitude (0.0 to 1.0)
            highs: Highs amplitude (0.0 to 1.0)
            
        Returns:
            Tuple of (R, G, B) values (0-255)
        """
        # Apply mode multipliers
        bass *= self.mode_multipliers['bass']
        mids *= self.mode_multipliers['mids']
        highs *= self.mode_multipliers['highs']
        
        # Apply sensitivity
        bass *= self.sensitivity
        mids *= self.sensitivity
        highs *= self.sensitivity
        
        # Clamp to 0-1 range
        bass = min(1.0, bass)
        mids = min(1.0, mids)
        highs = min(1.0, highs)
        
        # Map to RGB channels
        # Bass -> Red, Mids -> Green, Highs -> Blue
        r = int(bass * 255 * self.brightness)
        g = int(mids * 255 * self.brightness)
        b = int(highs * 255 * self.brightness)
        
        return r, g, b
    
    def set_mode(self, mode: str):
        """
        Set color mapping mode.
        
        Args:
            mode: Mode name ('balanced', 'bass_heavy', 'treble_focus')
        """
        if mode in self.MODES:
            self.mode = mode
            self.mode_multipliers = self.MODES[mode]
    
    def set_sensitivity(self, sensitivity: float):
        """
        Set sensitivity multiplier.
        
        Args:
            sensitivity: Sensitivity value (0.1 to 5.0)
        """
        self.sensitivity = max(0.1, min(5.0, sensitivity))
    
    def set_brightness(self, brightness: float):
        """
        Set brightness control.
        
        Args:
            brightness: Brightness value (0.0 to 1.0)
        """
        self.brightness = max(0.0, min(1.0, brightness))
    
    def get_color_string(self, r: int, g: int, b: int) -> str:
        """
        Get ANSI color code string for terminal display.
        
        Args:
            r, g, b: RGB values (0-255)
            
        Returns:
            ANSI escape sequence for RGB color
        """
        return f"\033[48;2;{r};{g};{b}m"
    
    @staticmethod
    def reset_color() -> str:
        """Get ANSI reset code."""
        return "\033[0m"
