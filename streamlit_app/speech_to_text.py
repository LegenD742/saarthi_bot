import speech_recognition as sr

def speech_to_text():
    r = sr.Recognizer()

    # Stop listening after 2 seconds of silence
    r.pause_threshold = 2.0

    # Let recognizer auto-adjust energy
    r.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening... Speak now.")
        audio = r.listen(source, timeout=None)

    try:
        return r.recognize_google(audio)

    except sr.UnknownValueError:
        print("Could not understand audio")
        return None

    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return None