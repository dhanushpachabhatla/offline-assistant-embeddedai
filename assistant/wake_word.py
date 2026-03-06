import pvporcupine
import sounddevice as sd
import numpy as np
import os
from dotenv import load_dotenv


class WakeWordDetector:

    def __init__(self):

        # Load environment variables
        load_dotenv()

        # Read access key from .env
        self.access_key = os.getenv("PORCUPINE_ACCESS_KEY")

        if not self.access_key:
            raise ValueError("PORCUPINE_ACCESS_KEY not found in .env")

        self.keywords = ["jarvis"]

        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keywords=self.keywords
        )

    def detect(self):

        print("Listening for wake word...")

        with sd.InputStream(
            samplerate=self.porcupine.sample_rate,
            channels=1,
            dtype="int16"
        ) as stream:

            while True:

                audio, _ = stream.read(self.porcupine.frame_length)

                pcm = np.frombuffer(audio, dtype=np.int16)

                result = self.porcupine.process(pcm)

                if result >= 0:
                    print("Wake word detected!")
                    return True