import pygame
import numpy as np
from . import globals

def create_sound(frequency, duration, wave_type="sine", decay=True):
    try:
        sample_rate = 44100
        frames = int(sample_rate * duration)
        t = np.arange(frames) / sample_rate
        
        if wave_type == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "noise":
            wave = np.random.uniform(-1, 1, frames)
        elif wave_type == "sawtooth":
             wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:
            wave = np.sin(2 * np.pi * frequency * t)

        if decay:
            envelope = np.exp(-4 * t / duration)
            wave = wave * envelope
        
        wave = (wave * 32767 * 0.3).astype(np.int16)
        sound_array = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(sound_array)
    except Exception as e:
        return None

def generate_background_music():
    try:
        sample_rate = 44100
        duration = 12.0
        frames = int(sample_rate * duration)
        t = np.arange(frames) / sample_rate
        
        # Cyberpunk Bass Line
        freqs = [110, 110, 130.8, 98] # A2, A2, C3, G2
        wave = np.zeros(frames)
        beat_len = frames // 16
        
        for i in range(16):
            # Bass
            f = freqs[(i // 4) % 4]
            start = i * beat_len
            end = (i+1) * beat_len
            sect_t = t[start:end]
            w = np.sign(np.sin(2 * np.pi * f * sect_t)) * 0.5 # Square bass
            w *= np.exp(-3 * (sect_t - sect_t[0])) # Pluck envelope
            wave[start:end] += w
            
            # Hi-hats
            if i % 2 == 0:
                noise = np.random.uniform(-0.1, 0.1, len(sect_t))
                noise *= np.exp(-20 * (sect_t - sect_t[0]))
                wave[start:end] += noise

        # Arpeggios
        arp_freqs = [440, 554, 659, 880]
        for i in range(32):
             f = arp_freqs[i % 4]
             if i % 8 > 4: f *= 1.5 # Variation
             start = int(i * (frames / 32))
             end = int((i+1) * (frames / 32))
             if end > frames: break
             sect_t = t[start:end]
             w = np.sin(2 * np.pi * f * sect_t) * 0.1
             w *= np.exp(-5 * (sect_t - sect_t[0]))
             wave[start:end] += w

        wave = (wave * 32767 * 0.2).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    except:
        return None

def load_all_sounds():
    print("Synthesizing Audio...")
    globals.sounds["shoot"] = create_sound(880, 0.15, "square")
    if globals.sounds["shoot"]: globals.sounds["shoot"].set_volume(0.3)
    
    globals.sounds["enemy_shoot"] = create_sound(220, 0.2, "sawtooth")
    if globals.sounds["enemy_shoot"]: globals.sounds["enemy_shoot"].set_volume(0.25)
    
    globals.sounds["explosion"] = create_sound(50, 0.5, "noise")
    if globals.sounds["explosion"]: globals.sounds["explosion"].set_volume(0.4)
    
    globals.sounds["powerup"] = create_sound(1200, 0.3, "sine")
    if globals.sounds["powerup"]: globals.sounds["powerup"].set_volume(0.4)
    
    globals.sounds["gameover"] = create_sound(100, 2.0, "sawtooth")
    
    globals.sounds["hit"] = create_sound(150, 0.2, "noise")
    globals.sounds["wave"] = create_sound(300, 1.0, "sine")
    
    globals.background_music = generate_background_music()
    print("Audio Ready.")

def play_sound(name):
    if name in globals.sounds and globals.sounds[name]:
        globals.sounds[name].play()

def play_background_music():
    if globals.background_music:
        globals.background_music.set_volume(globals.music_volume)
        globals.background_music.play(-1)

def change_volume(amount):
    globals.music_volume = max(0.0, min(1.0, globals.music_volume + amount))
    if globals.background_music:
        globals.background_music.set_volume(globals.music_volume)
