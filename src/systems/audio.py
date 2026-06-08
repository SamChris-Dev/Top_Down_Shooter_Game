import pygame
from systems.save_manager import save_manager

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music = None
        self.update_volumes()

    def update_volumes(self):
        self.master_vol = save_manager.get("volume_master", 1.0)
        self.music_vol = save_manager.get("volume_music", 0.5) * self.master_vol
        self.sfx_vol = save_manager.get("volume_sfx", 0.8) * self.master_vol
        
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_vol)
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_vol)

    def play_sound(self, sound, volume_scale=1.0):
        if sound:
            sound.set_volume(self.sfx_vol * volume_scale)
            sound.play()

audio_manager = AudioManager()
