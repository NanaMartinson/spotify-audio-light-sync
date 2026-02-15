"""
Unit tests for SpotifyColorMapper.
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from spotify_color_mapper import SpotifyColorMapper


class TestSpotifyColorMapper(unittest.TestCase):
    """Test cases for SpotifyColorMapper class."""
    
    def test_mapper_initialization(self):
        """Test that mapper initializes with correct modes."""
        mapper = SpotifyColorMapper(mode='mood')
        self.assertEqual(mapper.mode, 'mood')
        
        mapper = SpotifyColorMapper(mode='energy')
        self.assertEqual(mapper.mode, 'energy')
        
        mapper = SpotifyColorMapper(mode='genre_feel')
        self.assertEqual(mapper.mode, 'genre_feel')
        
        # Test invalid mode defaults to 'mood'
        mapper = SpotifyColorMapper(mode='invalid')
        self.assertEqual(mapper.mode, 'mood')
    
    def test_rgb_range(self):
        """Test that RGB values are always in 0-255 range."""
        mapper = SpotifyColorMapper(mode='mood')
        
        # Test various feature combinations
        test_cases = [
            {'energy': 0.0, 'valence': 0.0, 'danceability': 0.0, 'acousticness': 0.0, 'instrumentalness': 0.0},
            {'energy': 1.0, 'valence': 1.0, 'danceability': 1.0, 'acousticness': 1.0, 'instrumentalness': 1.0},
            {'energy': 0.5, 'valence': 0.5, 'danceability': 0.5, 'acousticness': 0.5, 'instrumentalness': 0.5},
            {'energy': 0.2, 'valence': 0.8, 'danceability': 0.3, 'acousticness': 0.9, 'instrumentalness': 0.1},
            {'energy': 0.9, 'valence': 0.1, 'danceability': 0.7, 'acousticness': 0.2, 'instrumentalness': 0.8},
        ]
        
        for features in test_cases:
            r, g, b = mapper.map_to_rgb(features)
            self.assertGreaterEqual(r, 0, f"Red value {r} below 0 for {features}")
            self.assertLessEqual(r, 255, f"Red value {r} above 255 for {features}")
            self.assertGreaterEqual(g, 0, f"Green value {g} below 0 for {features}")
            self.assertLessEqual(g, 255, f"Green value {g} above 255 for {features}")
            self.assertGreaterEqual(b, 0, f"Blue value {b} below 0 for {features}")
            self.assertLessEqual(b, 255, f"Blue value {b} above 255 for {features}")
            self.assertIsInstance(r, int)
            self.assertIsInstance(g, int)
            self.assertIsInstance(b, int)
    
    def test_mood_mode(self):
        """Test mood mode color mapping."""
        mapper = SpotifyColorMapper(mode='mood')
        
        # High energy + high valence should be bright and warm
        features_happy = {
            'energy': 0.9,
            'valence': 0.9,
            'danceability': 0.8,
            'acousticness': 0.1,
            'instrumentalness': 0.1
        }
        r1, g1, b1 = mapper.map_to_rgb(features_happy)
        brightness1 = (r1 + g1 + b1) / 3
        
        # Low energy + low valence should be darker and cooler
        features_sad = {
            'energy': 0.2,
            'valence': 0.2,
            'danceability': 0.3,
            'acousticness': 0.1,
            'instrumentalness': 0.1
        }
        r2, g2, b2 = mapper.map_to_rgb(features_sad)
        brightness2 = (r2 + g2 + b2) / 3
        
        # Happy song should be brighter
        self.assertGreater(brightness1, brightness2)
    
    def test_energy_mode(self):
        """Test energy mode color mapping."""
        mapper = SpotifyColorMapper(mode='energy')
        
        # High energy
        features_high = {
            'energy': 0.9,
            'valence': 0.5,
            'danceability': 0.5,
            'acousticness': 0.1,
            'instrumentalness': 0.1
        }
        r1, g1, b1 = mapper.map_to_rgb(features_high)
        brightness1 = (r1 + g1 + b1) / 3
        
        # Low energy
        features_low = {
            'energy': 0.1,
            'valence': 0.5,
            'danceability': 0.5,
            'acousticness': 0.1,
            'instrumentalness': 0.1
        }
        r2, g2, b2 = mapper.map_to_rgb(features_low)
        brightness2 = (r2 + g2 + b2) / 3
        
        # High energy should be brighter
        self.assertGreater(brightness1, brightness2)
    
    def test_genre_feel_mode(self):
        """Test genre_feel mode color mapping."""
        mapper = SpotifyColorMapper(mode='genre_feel')
        
        # Acoustic song
        features_acoustic = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.4,
            'acousticness': 0.9,
            'instrumentalness': 0.2
        }
        r1, g1, b1 = mapper.map_to_rgb(features_acoustic)
        
        # Electronic song
        features_electronic = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.8,
            'acousticness': 0.1,
            'instrumentalness': 0.2
        }
        r2, g2, b2 = mapper.map_to_rgb(features_electronic)
        
        # Both should produce valid colors
        self.assertIsInstance(r1, int)
        self.assertIsInstance(r2, int)
    
    def test_edge_case_all_zeros(self):
        """Test edge case with all features at 0."""
        mapper = SpotifyColorMapper(mode='mood')
        
        features = {
            'energy': 0.0,
            'valence': 0.0,
            'danceability': 0.0,
            'acousticness': 0.0,
            'instrumentalness': 0.0
        }
        
        r, g, b = mapper.map_to_rgb(features)
        
        # Should produce valid RGB values
        self.assertGreaterEqual(r, 0)
        self.assertGreaterEqual(g, 0)
        self.assertGreaterEqual(b, 0)
        self.assertLessEqual(r, 255)
        self.assertLessEqual(g, 255)
        self.assertLessEqual(b, 255)
    
    def test_edge_case_all_ones(self):
        """Test edge case with all features at 1."""
        mapper = SpotifyColorMapper(mode='mood')
        
        features = {
            'energy': 1.0,
            'valence': 1.0,
            'danceability': 1.0,
            'acousticness': 1.0,
            'instrumentalness': 1.0
        }
        
        r, g, b = mapper.map_to_rgb(features)
        
        # Should produce valid RGB values
        self.assertGreaterEqual(r, 0)
        self.assertGreaterEqual(g, 0)
        self.assertGreaterEqual(b, 0)
        self.assertLessEqual(r, 255)
        self.assertLessEqual(g, 255)
        self.assertLessEqual(b, 255)
    
    def test_edge_case_mid_range(self):
        """Test edge case with all features at 0.5."""
        mapper = SpotifyColorMapper(mode='mood')
        
        features = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.5,
            'acousticness': 0.5,
            'instrumentalness': 0.5
        }
        
        r, g, b = mapper.map_to_rgb(features)
        
        # Should produce valid RGB values
        self.assertGreaterEqual(r, 0)
        self.assertGreaterEqual(g, 0)
        self.assertGreaterEqual(b, 0)
        self.assertLessEqual(r, 255)
        self.assertLessEqual(g, 255)
        self.assertLessEqual(b, 255)
    
    def test_missing_features_use_defaults(self):
        """Test that missing features use default values."""
        mapper = SpotifyColorMapper(mode='mood')
        
        # Empty features dict
        features = {}
        r, g, b = mapper.map_to_rgb(features)
        
        # Should still produce valid RGB values
        self.assertGreaterEqual(r, 0)
        self.assertGreaterEqual(g, 0)
        self.assertGreaterEqual(b, 0)
        self.assertLessEqual(r, 255)
        self.assertLessEqual(g, 255)
        self.assertLessEqual(b, 255)
    
    def test_set_mode(self):
        """Test changing color mode."""
        mapper = SpotifyColorMapper(mode='mood')
        self.assertEqual(mapper.mode, 'mood')
        
        mapper.set_mode('energy')
        self.assertEqual(mapper.mode, 'energy')
        
        mapper.set_mode('genre_feel')
        self.assertEqual(mapper.mode, 'genre_feel')
        
        # Invalid mode should not change current mode
        mapper.set_mode('invalid')
        self.assertEqual(mapper.mode, 'genre_feel')
    
    def test_high_acousticness_shift(self):
        """Test that high acousticness affects color."""
        mapper = SpotifyColorMapper(mode='mood')
        
        # Low acousticness
        features_low = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.5,
            'acousticness': 0.1,
            'instrumentalness': 0.1
        }
        r1, g1, b1 = mapper.map_to_rgb(features_low)
        
        # High acousticness (should apply shift)
        features_high = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.5,
            'acousticness': 0.9,
            'instrumentalness': 0.1
        }
        r2, g2, b2 = mapper.map_to_rgb(features_high)
        
        # Colors should be different
        self.assertNotEqual((r1, g1, b1), (r2, g2, b2))
    
    def test_high_instrumentalness_ambient(self):
        """Test that high instrumentalness affects color."""
        mapper = SpotifyColorMapper(mode='mood')
        
        # Low instrumentalness
        features_low = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.5,
            'acousticness': 0.1,
            'instrumentalness': 0.1
        }
        r1, g1, b1 = mapper.map_to_rgb(features_low)
        
        # High instrumentalness (should reduce saturation)
        features_high = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.5,
            'acousticness': 0.1,
            'instrumentalness': 0.9
        }
        r2, g2, b2 = mapper.map_to_rgb(features_high)
        
        # Colors should be different
        self.assertNotEqual((r1, g1, b1), (r2, g2, b2))


if __name__ == '__main__':
    unittest.main()
