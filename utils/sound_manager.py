import os
from pathlib import Path
from config import BASE_DIR, SOUND_ENABLED


class SoundManager:
    """
    Manage sound effects
    """
    _enabled = SOUND_ENABLED
    _player = None
    
    SOUNDS_DIR = BASE_DIR / "resources" / "sounds"
    
    @classmethod
    def initialize(cls):
        """Initialize sound system"""
        try:
            from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
            from PyQt6.QtCore import QUrl
            cls._player = QMediaPlayer()
            cls._audio_output = QAudioOutput()
            cls._player.setAudioOutput(cls._audio_output)
            cls._qt_version = 6
        except ImportError:
            try:
                from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
                from PyQt6.QtCore import QUrl
                cls._player = QMediaPlayer()
                cls._qt_version = 5
            except ImportError:
                cls._player = None
                cls._qt_version = 0
    
    @classmethod
    def play_timeout(cls):
        """Play timeout sound"""
        cls._play_sound("timeout.mp3")
    
    @classmethod
    def play_warning(cls):
        """Play warning sound"""
        cls._play_sound("warning.mp3")
    
    @classmethod
    def play_start(cls):
        """Play session start sound"""
        cls._play_sound("start.mp3")
    
    @classmethod
    def play_end(cls):
        """Play session end sound"""
        cls._play_sound("end.mp3")
    
    @classmethod
    def _play_sound(cls, filename: str):
        """Play a sound file"""
        if not cls._enabled or cls._player is None:
            return
        
        sound_path = cls.SOUNDS_DIR / filename
        if not sound_path.exists():
            # Create a simple beep if sound file doesn't exist
            cls._simple_beep()
            return
        
        try:
            if cls._qt_version == 6:
                from PyQt6.QtCore import QUrl
                cls._player.setSource(QUrl.fromLocalFile(str(sound_path)))
                cls._player.play()
            # elif cls._qt_version == 5:
            #     from PyQt6.QtMultimedia import QMediaContent
            #     from PyQt6.QtCore import QUrl
            #     cls._player.setMedia(QMediaContent(QUrl.fromLocalFile(str(sound_path))))
            #     cls._player.play()
        except Exception:
            cls._simple_beep()
    
    @classmethod
    def _simple_beep(cls):
        """Play a simple system beep"""
        try:
            import winsound
            winsound.Beep(800, 200)
        except:
            print('\a')  # ASCII bell
    
    @classmethod
    def set_enabled(cls, enabled: bool):
        """Enable or disable sounds"""
        cls._enabled = enabled
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if sounds are enabled"""
        return cls._enabled