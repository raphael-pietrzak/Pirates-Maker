
from pygame import mixer


class Sound:
    def __init__(self):
        self.music_channel = mixer.Channel(0)
        self.music_channel.set_volume(0.2)
        self.sfx_channel = mixer.Channel(1)
        self.sfx_channel.set_volume(0.2)

        self.allowSFX = True
        self.allowMusic = True
        
        # sfx
        self.coin = mixer.Sound('../audio/coin.wav')
        self.hit = mixer.Sound('../audio/hit.wav')
        self.jump = mixer.Sound('../audio/jump.wav')

        # music
        self.super_hero = mixer.Sound('../audio/SuperHero.ogg')
        self.super_hero.set_volume(0.5)
        self.explorer = mixer.Sound('../audio/Explorer.ogg')
    
    def play_sfx(self, sfx):
        if self.allowSFX:
            self.sfx_channel.play(sfx)
    
    def play_music(self, music):
        if self.allowMusic:
            self.music_channel.play(music, loops=-1)