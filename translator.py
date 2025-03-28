import speech_recognition as sr
from googletrans import Translator
import pyttsx3
import os

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak now!")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None

def translate_text(text, target_lang):
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_lang)
        print(f"Translation: {translation.text}")
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def text_to_speech(text, lang):
    try:
        engine = pyttsx3.init()
        # Set the voice rate and volume
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        print("Speaking translation...")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Text-to-speech error: {e}")

def main():
    # Dictionary of Nigerian languages and their codes
    nigerian_languages = {
        '1': ('Yoruba', 'yo'),
        '2': ('Hausa', 'ha'),
        '3': ('Igbo', 'ig')
    }
    
    print("Welcome to Nigerian Language Translator!")
    print("\nAvailable languages:")
    for key, (name, code) in nigerian_languages.items():
        print(f"{key}. {name}")
    
    while True:
        try:
            choice = input("\nSelect target language (1-3) or 'q' to quit: ")
            if choice.lower() == 'q':
                break
                
            if choice not in nigerian_languages:
                print("Invalid choice. Please try again.")
                continue
                
            lang_name, lang_code = nigerian_languages[choice]
            print(f"\nSelected language: {lang_name}")
            
            # Get speech input
            text = speech_to_text()
            if text:
                # Translate the text
                translated_text = translate_text(text, lang_code)
                if translated_text:
                    # Convert translation to speech
                    text_to_speech(translated_text, lang_code)
                    
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main() 