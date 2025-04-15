import os
import numpy as np
from scipy.io.wavfile import write

def create_beep(filename, frequency=440, duration=0.5, volume=0.5, sample_rate=44100):
    """Create a simple beep sound and save it as a WAV file"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    note = np.sin(frequency * t * 2 * np.pi)
    audio = note * volume
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save as WAV file
    write(filename, sample_rate, audio.astype(np.float32))
    print(f"Created sound file: {filename}")

# Create sounds directory
sounds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Create different sounds
create_beep(os.path.join(sounds_dir, "correct.wav"), frequency=880, duration=0.3, volume=0.7)  # Higher pitch for correct
create_beep(os.path.join(sounds_dir, "wrong.wav"), frequency=220, duration=0.5, volume=0.7)    # Lower pitch for wrong
create_beep(os.path.join(sounds_dir, "click.wav"), frequency=440, duration=0.1, volume=0.5)    # Short click sound
create_beep(os.path.join(sounds_dir, "welcome.wav"), frequency=660, duration=0.7, volume=0.6)  # Welcome sound
# Create a more complex completion sound
def create_completion_sound(filename, duration=0.8, volume=0.7, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create three different tones
    note1 = np.sin(440 * t * 2 * np.pi) * volume * np.linspace(1, 0.3, len(t))
    note2 = np.sin(550 * t * 2 * np.pi) * volume * np.linspace(0.3, 1, len(t))
    note3 = np.sin(660 * t * 2 * np.pi) * volume * np.linspace(0, 1, len(t))
    
    # Combine them
    audio = note1 + note2 + note3
    audio = audio / np.max(np.abs(audio))  # Normalize
    
    # Save as WAV file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    write(filename, sample_rate, (audio * 0.7).astype(np.float32))
    print(f"Created sound file: {filename}")

create_completion_sound(os.path.join(sounds_dir, "complete.wav"))

print("All sound files created successfully!")