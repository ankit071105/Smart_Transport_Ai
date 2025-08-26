from gtts import gTTS
import pygame
import io
import tempfile
import os

def text_to_speech(text, lang='en'):
    """Convert text to speech and play it"""
    try:
        # Create text-to-speech object
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            temp_file = fp.name
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Load and play the audio
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # Clean up
        pygame.mixer.quit()
        os.unlink(temp_file)
        
        return True
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return False