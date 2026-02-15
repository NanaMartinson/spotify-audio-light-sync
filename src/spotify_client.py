"""
Spotify Web API client for fetching currently playing track and audio features.
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Optional, Dict, Any
import os


class SpotifyClient:
    """Client for interacting with Spotify Web API."""
    
    # Required Spotify API scopes
    REQUIRED_SCOPES = [
        'user-read-currently-playing',
        'user-read-playback-state'
    ]
    
    def __init__(self, client_id: str, client_secret: str, 
                 redirect_uri: str = "http://localhost:8888/callback",
                 cache_path: str = ".spotify_cache"):
        """
        Initialize Spotify client with OAuth credentials.
        
        Args:
            client_id: Spotify app client ID
            client_secret: Spotify app client secret
            redirect_uri: OAuth redirect URI
            cache_path: Path to cache file for token persistence
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.cache_path = cache_path
        
        # Initialize OAuth handler
        self.auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=' '.join(self.REQUIRED_SCOPES),
            cache_path=cache_path,
            open_browser=True
        )
        
        # Initialize Spotify client
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)
        
        # Cache for current track
        self._current_track_id = None
        self._current_track_name = None
        self._current_artist = None
    
    def is_playing(self) -> bool:
        """
        Check if user is currently playing music.
        
        Returns:
            True if music is playing, False otherwise
        """
        try:
            playback = self.spotify.current_playback()
            if playback is None:
                return False
            return playback.get('is_playing', False)
        except Exception as e:
            print(f"Error checking playback status: {e}")
            return False
    
    def get_current_track(self) -> Optional[tuple[str, str, str]]:
        """
        Get currently playing track information.
        
        Returns:
            Tuple of (track_id, track_name, artist_name) if playing, None otherwise
        """
        try:
            current = self.spotify.current_user_playing_track()
            
            if current is None or not current.get('is_playing', False):
                return None
            
            item = current.get('item')
            if item is None:
                return None
            
            track_id = item.get('id')
            track_name = item.get('name', 'Unknown Track')
            
            # Get artist names
            artists = item.get('artists', [])
            artist_name = ', '.join([artist.get('name', '') for artist in artists])
            if not artist_name:
                artist_name = 'Unknown Artist'
            
            # Update cache
            self._current_track_id = track_id
            self._current_track_name = track_name
            self._current_artist = artist_name
            
            return track_id, track_name, artist_name
            
        except Exception as e:
            print(f"Error fetching current track: {e}")
            return None
    
    def get_audio_features(self, track_id: str) -> Optional[Dict[str, float]]:
        """
        Get audio features for a track from Spotify API.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Dictionary with audio features (energy, valence, tempo, etc.) or None on error
            Features include:
                - energy: 0.0-1.0
                - valence: 0.0-1.0 (happiness/positivity)
                - tempo: BPM (beats per minute)
                - danceability: 0.0-1.0
                - acousticness: 0.0-1.0
                - instrumentalness: 0.0-1.0
                - speechiness: 0.0-1.0
                - liveness: 0.0-1.0
        """
        try:
            features = self.spotify.audio_features(track_id)
            
            if not features or len(features) == 0 or features[0] is None:
                return None
            
            # Extract relevant features
            raw_features = features[0]
            return {
                'energy': raw_features.get('energy', 0.5),
                'valence': raw_features.get('valence', 0.5),
                'tempo': raw_features.get('tempo', 120.0),
                'danceability': raw_features.get('danceability', 0.5),
                'acousticness': raw_features.get('acousticness', 0.5),
                'instrumentalness': raw_features.get('instrumentalness', 0.5),
                'speechiness': raw_features.get('speechiness', 0.5),
                'liveness': raw_features.get('liveness', 0.5)
            }
            
        except Exception as e:
            print(f"Error fetching audio features: {e}")
            return None
    
    @property
    def current_track_id(self) -> Optional[str]:
        """Get cached current track ID."""
        return self._current_track_id
    
    @property
    def current_track_name(self) -> Optional[str]:
        """Get cached current track name."""
        return self._current_track_name
    
    @property
    def current_artist(self) -> Optional[str]:
        """Get cached current artist name."""
        return self._current_artist
