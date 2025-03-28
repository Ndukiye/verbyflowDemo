from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import base64
import io
import wave
from pydub import AudioSegment

app = Flask(__name__)

# Dictionary of Nigerian languages and their codes
nigerian_languages = {
    '1': ('Yoruba', 'yo'),
    '2': ('Hausa', 'ha'),
    '3': ('Igbo', 'ig')
}

def speech_to_text(audio_data):
    recognizer = sr.Recognizer()
    try:
        # Convert base64 audio to audio data
        audio_bytes = base64.b64decode(audio_data.split(',')[1])
        
        # Save the raw audio data temporarily
        with open('temp_audio.webm', 'wb') as f:
            f.write(audio_bytes)
        
        # Convert webm to wav using pydub
        audio = AudioSegment.from_file('temp_audio.webm', format='webm')
        audio = audio.set_channels(1)  # Convert to mono
        audio = audio.set_frame_rate(16000)  # Set sample rate to 16kHz
        audio.export('temp_audio.wav', format='wav')
        
        # Read the WAV file
        with sr.AudioFile('temp_audio.wav') as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source)
            
            try:
                # Try with Google Speech Recognition
                text = recognizer.recognize_google(audio)
                print(f"Recognized text: {text}")  # Debug print
                return text
            except sr.UnknownValueError:
                return "Could not understand audio. Please speak clearly and try again."
            except sr.RequestError as e:
                return f"Could not request results from speech recognition service; {str(e)}"
            
    except Exception as e:
        print(f"Speech recognition error: {str(e)}")  # Debug print
        return f"Error in speech recognition: {str(e)}"
    finally:
        # Clean up temporary files
        for file in ['temp_audio.webm', 'temp_audio.wav']:
            if os.path.exists(file):
                os.remove(file)

def translate_text(text, target_lang):
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_lang)
        print(f"Translation: {translation.text}")  # Debug print
        return translation.text
    except Exception as e:
        print(f"Translation error: {str(e)}")  # Debug print
        return f"Error in translation: {str(e)}"

def text_to_speech(text, lang):
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=lang)
        
        # Save to temporary file
        audio_file = "temp_audio.mp3"
        tts.save(audio_file)
        
        # Read the audio file and convert to base64
        with open(audio_file, 'rb') as audio:
            audio_base64 = base64.b64encode(audio.read()).decode('utf-8')
            print("Audio generated successfully")  # Debug print
        
        # Clean up the temporary file
        os.remove(audio_file)
        return audio_base64
    except Exception as e:
        print(f"Text-to-speech error: {str(e)}")  # Debug print
        return f"Error in text-to-speech: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html', languages=nigerian_languages)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        audio_data = data.get('audio')
        target_lang = data.get('target_lang')
        
        if not audio_data or not target_lang:
            return jsonify({'error': 'Missing audio data or target language'})
        
        print("Received translation request")  # Debug print
        
        # Convert speech to text
        text = speech_to_text(audio_data)
        if text.startswith('Error') or text.startswith('Could not'):
            return jsonify({'error': text})
        
        # Translate the text
        translated_text = translate_text(text, target_lang)
        if translated_text.startswith('Error'):
            return jsonify({'error': translated_text})
        
        # Convert translation to speech
        audio_base64 = text_to_speech(translated_text, target_lang)
        if audio_base64.startswith('Error'):
            return jsonify({'error': audio_base64})
        
        return jsonify({
            'original_text': text,
            'translated_text': translated_text,
            'audio': audio_base64
        })
    except Exception as e:
        print(f"General error: {str(e)}")  # Debug print
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 