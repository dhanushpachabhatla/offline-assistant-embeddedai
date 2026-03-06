from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json


class SpeechToText:

    def __init__(self, model_path="models/vosk-model-small-en-us-0.15"):

        print("Loading speech model...")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)

    def listen(self):

        print("Listening for command...")

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1
        ) as stream:

            while True:

                data, _ = stream.read(4000)

                # FIX HERE
                if self.recognizer.AcceptWaveform(bytes(data)):

                    result = json.loads(self.recognizer.Result())

                    text = result.get("text", "")

                    if text != "":
                        print("Command:", text)
                        return text