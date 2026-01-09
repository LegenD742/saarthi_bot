import speech_recognition as sr

def speech_to_text():
    r = sr.Recognizer()

    r.pause_threshold = 2.0

    r.energy_threshold = 300

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening... Speak now.")
        audio = r.listen(source)

    try:
        
        return r.recognize_google(audio)

    except sr.UnknownValueError:
        print("Could not understand audio")
        return None

    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return None