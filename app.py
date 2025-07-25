from flask import Flask, request, jsonify, send_file
import os
import requests
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from urllib.parse import urlparse
import io
from fish_audio import clone_voice_with_fish
import uuid
from dotenv import load_dotenv
import tempfile
import shutil
from pydub import AudioSegment

# Load environment variables from a .env file if it exists.
# This is particularly useful for local development.
load_dotenv()

app = Flask(__name__)

def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes

        content_type = response.headers.get('content-type')

        if 'epub' in content_type:
            book = epub.read_epub(io.BytesIO(response.content))
            text_content = ""
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_body_content(), 'html.parser')
                text_content += soup.get_text() + "\n"
            return text_content
        elif 'html' in content_type:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text()
        elif 'text' in content_type:
            return response.text
        else:
            # Fallback for other content types or if content-type is not specific
            # You might want to add more sophisticated handling here
            return response.text
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching URL: {e}")
        return None

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

@app.route('/api/voice-transfer', methods=['POST'])
def voice_transfer():
    temp_dir = tempfile.mkdtemp()
    try:
        file = None
        voice_file_path = None

        # # 1. Check for file upload
        # if 'voice_file' in request.files:
        #     file = request.files['voice_file']
        #     if file.filename == '':
        #         return jsonify({"error": "No selected file"}), 400
        #     voice_file_path = os.path.join(temp_dir, file.filename)
        #     file.save(voice_file_path)
        # 2. Check for file URL
        if 'cid' in request.form:
            cid = request.form.get('cid')
            if not cid:
                return jsonify({"error": "No cid (for voice file) provided"}), 400
            # Construct the IPFS URL from the CID
            file_url = f"http://ipfs.io/ipfs/{cid}"
            response = requests.get(file_url)
            if response.status_code != 200:
                return jsonify({"error": "Failed to download voice file from IPFS"}), 400
            # Save as webm first
            webm_path = os.path.join(temp_dir, "input.webm")
            with open(webm_path, "wb") as f:
                f.write(response.content)
            # Convert to mp3
            mp3_path = os.path.join(temp_dir, "input.mp3")
            audio = AudioSegment.from_file(webm_path, format="webm")
            audio.export(mp3_path, format="mp3")
            voice_file_path = mp3_path
        else:
            return jsonify({"error": "No voice file or voice_file_url provided"}), 400

        text_input = request.form.get('text')
        app.logger.info(f"Received text input: {text_input}")
        if not text_input:
            return jsonify({"error": "No text or text_url provided"}), 400

        text_content = ""
        if is_url(text_input):
            text_content = get_text_from_url(text_input)
            if text_content is None:
                return jsonify({"error": "Failed to retrieve or parse content from URL"}), 400
        else:
            app.logger.info("Input is not a URL, using as raw text.")
            text_content = text_input

        # --- Perform Voice Cloning using Fish Audio ---
        app.logger.info("Starting voice cloning process with Fish Audio...")

        output_filename = f"output_cloned_{uuid.uuid4().hex}.mp3"
        output_file_path = os.path.join(temp_dir, output_filename)

        try:
            clone_voice_with_fish(
                text=text_content,
                reference_audio_path=voice_file_path,
                output_path=output_file_path,
                reference_text="This is a reference audio for voice cloning."
            )
        except Exception as e:
            app.logger.error(f"Error during voice cloning with Fish Audio: {e}")
            return jsonify({"error": "Failed to generate voice file."}), 500

        app.logger.info(f"Successfully generated audio file at: {output_file_path}")

        with open(output_file_path, 'rb') as f:
            audio_buffer = io.BytesIO(f.read())

        return send_file(
            audio_buffer,
            as_attachment=True,
            download_name=output_filename,
            mimetype='audio/mpeg'
        )

    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# if __name__ == '__main__':
#     app.run(debug=True, port=5001) 

