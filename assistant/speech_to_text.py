import json
import queue

import sounddevice as sd
import vosk

from assistant.parser import build_grammar_vocab

SAMPLE_RATE = 16000
DEFAULT_LISTEN_TIMEOUT_SECONDS = 3.0


class SpeechToText:
    def __init__(self, model_path: str):
        self.model = vosk.Model(model_path)
        grammar_json = json.dumps(build_grammar_vocab())
        self.recognizer = vosk.KaldiRecognizer(self.model, SAMPLE_RATE, grammar_json)
        self.audio_queue: queue.Queue = queue.Queue()

    def _audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(bytes(indata))

    def listen(self, timeout_seconds: float = DEFAULT_LISTEN_TIMEOUT_SECONDS) -> str:
        """Block until speech is detected or timeout. Returns transcribed text."""
        self.recognizer.Reset()
        frames_per_block = int(SAMPLE_RATE * 0.1)
        max_blocks = int(timeout_seconds / 0.1)
        result_text = ""

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=frames_per_block,
            dtype="int16",
            channels=1,
            callback=self._audio_callback,
        ):
            for _ in range(max_blocks):
                try:
                    data = self.audio_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text and text != "[unk]":
                        result_text = text
                        break

        if not result_text:
            partial = json.loads(self.recognizer.PartialResult())
            result_text = partial.get("partial", "").strip()

        return result_text
