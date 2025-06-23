import os
import re
from fish_audio_sdk import Session, TTSRequest, ReferenceAudio
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clone_voice_with_fish(text: str, reference_audio_path: str, output_path: str, reference_text: str = "Text in reference audio"):
    """
    Generates speech with a cloned voice using the Fish Audio API.

    :param text: The text to be converted to speech.
    :param reference_audio_path: Path to the reference audio file for voice cloning.
    :param output_path: Path to save the generated audio file.
    :param reference_text: The transcription of the reference audio. This is important for better quality.
    """
    # Restrict the input text to the first 450 characters.
    if len(text) > 100:
        text = '.'.join(text.split('.')[15:16])[:100]
    
    # Remove special words (e.g., __Gutenberg__, _very_)
    text = re.sub(r'__\w+__\s*|_\w+_\s*', '', text)
    logging.info(f"Text for TTS: {text}")

    # Load the API key from an environment variable for security.
    api_key = os.getenv("FISH_AUDIO_API_KEY")
    if not api_key:
        raise ValueError("FISH_AUDIO_API_KEY environment variable not set.")
    
    session = Session(api_key)

    with open(reference_audio_path, "rb") as audio_file:
        with open(output_path, "wb") as f:
            for chunk in session.tts(TTSRequest(
                text=text,
                backend='s1',
                references=[
                    ReferenceAudio(
                        audio=audio_file.read(),
                        text=reference_text,
                    )
                ]
            )):
                f.write(chunk)
    logging.info(f"File output to: {output_path}")

if __name__ == '__main__':
    # This is an example of how to use the function.
    # You would import clone_voice_with_fish from this file into your app.py.
    clone_voice_with_fish(
        text="The water's writing engraves the rocks like the graphite from my pencil engraves this paper.",
        reference_audio_path="example_reference_elon.mp3",
        output_path="output_fish_clone.mp3",
        # It's best to have an accurate transcript of the reference audio for better results.
        reference_text="My name is Elon Musk."
    )