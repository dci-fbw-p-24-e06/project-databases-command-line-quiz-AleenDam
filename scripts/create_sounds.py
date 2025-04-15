import os
import numpy as np
from scipy.io.wavfile import write

def apply_envelope(audio, attack=0.1, decay=0.1, sustain=0.7, release=0.2, sustain_level=0.8):
    """Apply ADSR envelope to audio"""
    total_samples = len(audio)
    attack_samples = int(attack * total_samples)
    decay_samples = int(decay * total_samples)
    release_samples = int(release * total_samples)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    envelope = np.zeros_like(audio)
    
    # Attack phase - linear ramp up
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay phase - exponential decay to sustain level
    if decay_samples > 0:
        envelope[attack_samples:attack_samples+decay_samples] = \
            np.linspace(1, sustain_level, decay_samples)
    
    # Sustain phase - constant level
    if sustain_samples > 0:
        envelope[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = sustain_level
    
    # Release phase - exponential decay to zero
    if release_samples > 0:
        envelope[attack_samples+decay_samples+sustain_samples:] = \
            np.linspace(sustain_level, 0, release_samples)
    
    return audio * envelope

def create_harp_sound(filename, notes, duration=1.0, volume=0.3, sample_rate=44100):
    """Create a harp-like sound with multiple notes"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = np.zeros_like(t, dtype=float)
    
    # Create each note with a slight delay
    for i, note in enumerate(notes):
        # Delay each note slightly
        delay = i * 0.1
        if delay >= duration:
            continue
            
        # Create a mask for the delayed start
        mask = t >= delay
        
        # Create the note with a fast attack and long decay (harp-like)
        note_t = t[mask] - delay
        note_env = np.exp(-2 * note_t)  # Exponential decay
        
        # Add some harmonics for a richer sound
        note_audio = np.zeros_like(note_t)
        for h, strength in [(1, 1.0), (2, 0.5), (3, 0.25), (4, 0.1)]:
            note_audio += np.sin(note * h * note_t * 2 * np.pi) * strength
        
        # Apply the envelope
        note_audio *= note_env * volume
        
        # Add to the main audio
        audio[mask] += note_audio
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save as WAV file
    write(filename, sample_rate, (audio * 0.7).astype(np.float32))
    print(f"Created sound file: {filename}")

def create_soft_click(filename, duration=0.1, volume=0.2, sample_rate=44100):
    """Create a soft click sound"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a short click with fast attack and decay
    env = np.exp(-30 * t)
    
    # Mix a few frequencies for a natural sound
    audio = np.zeros_like(t)
    for freq in [800, 1200, 1600]:
        audio += np.sin(freq * t * 2 * np.pi) * volume * 0.3
    
    # Apply envelope
    audio *= env
    
    # Add a bit of noise for a more natural sound
    noise = np.random.normal(0, 0.05, len(t))
    audio += noise * env * volume * 0.1
    
    # Normalize
    audio = audio / np.max(np.abs(audio))
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save as WAV file
    write(filename, sample_rate, (audio * 0.7).astype(np.float32))
    print(f"Created sound file: {filename}")

def create_simple_tone(filename, frequency, duration=0.5, volume=0.3, sample_rate=44100):
    """Create a simple tone with a gentle envelope"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a simple sine wave
    audio = np.sin(frequency * t * 2 * np.pi) * volume
    
    # Apply a gentle envelope
    env = np.ones_like(t)
    attack = int(0.1 * len(t))
    release = int(0.3 * len(t))
    
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    
    audio *= env
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save as WAV file
    write(filename, sample_rate, audio.astype(np.float32))
    print(f"Created sound file: {filename}")

# Create sounds directory
sounds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Create a harp-like welcome sound (ascending arpeggio)
create_harp_sound(
    os.path.join(sounds_dir, "welcome.wav"),
    [262, 330, 392, 523],  # C4, E4, G4, C5 (C major arpeggio)
    duration=1.2,
    volume=0.025  # Further reduced volume
)

# Create a soft click sound
create_soft_click(
    os.path.join(sounds_dir, "click.wav"),
    duration=0.08,
    volume=0.015  # Further reduced volume
)

# Create a pleasant correct answer sound
create_harp_sound(
    os.path.join(sounds_dir, "correct.wav"),
    [392, 523],  # G4, C5 (perfect fifth - very pleasant)
    duration=0.6,
    volume=0.02  # Further reduced volume
)

# Create a gentle wrong answer sound
create_simple_tone(
    os.path.join(sounds_dir, "wrong.wav"),
    330,  # E4
    duration=0.4,
    volume=0.015  # Further reduced volume
)

# Create a completion sound (descending arpeggio)
create_harp_sound(
    os.path.join(sounds_dir, "complete.wav"),
    [523, 392, 330, 262],  # C5, G4, E4, C4 (descending C major)
    duration=1.0,
    volume=0.02  # Further reduced volume
)

# Create a victory sound (more elaborate arpeggio)
create_harp_sound(
    os.path.join(sounds_dir, "victory.wav"),
    [262, 330, 392, 523, 659, 784],  # C4, E4, G4, C5, E5, G5 (extended C major)
    duration=1.5,
    volume=0.025  # Further reduced volume
)

print("All simple, pleasant sound files created successfully!")