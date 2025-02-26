import asyncio
import edge_tts
import pyaudio

class OutputVoice:
    def __init__(self, voice='fr-FR-EloiseNeural', rate="+10%", pitch="-5Hz"):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.p = pyaudio.PyAudio()  # Instance PyAudio

    async def _feed_ffmpeg(self, communicate, ffmpeg_proc):
        # Envoi des données audio encodées vers ffmpeg
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                ffmpeg_proc.stdin.write(chunk["data"])
                await ffmpeg_proc.stdin.drain()
        # Fin de l'entrée pour ffmpeg
        ffmpeg_proc.stdin.close()

    async def _read_ffmpeg_output(self, ffmpeg_proc, stream):
        # Lecture continue du flux décodé par ffmpeg et envoi à PyAudio
        while True:
            pcm_data = await ffmpeg_proc.stdout.read(1024)
            if not pcm_data:
                break
            stream.write(pcm_data)

    async def _stream_audio(self, text):
        # Ouverture d'un flux PyAudio avec les paramètres attendus (PCM 16 bits, mono, 24000 Hz)
        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=24000,
                             output=True)

        # Lancement de ffmpeg pour décoder le flux audio
        ffmpeg_proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-loglevel", "quiet",
            "-i", "pipe:0",    # lecture depuis stdin
            "-f", "s16le",     # sortie en PCM 16 bits little endian
            "-ar", "24000",    # fréquence d'échantillonnage
            "-ac", "1",        # mono
            "pipe:1",          # sortie sur stdout
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )

        # Création de l'objet de communication edge_tts
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)

        # Exécution simultanée des tâches d'envoi et de lecture
        await asyncio.gather(
            self._feed_ffmpeg(communicate, ffmpeg_proc),
            self._read_ffmpeg_output(ffmpeg_proc, stream)
        )

        await ffmpeg_proc.wait()
        stream.stop_stream()
        stream.close()

    def speak(self, text):
        # Méthode publique pour faire parler le LLM via un texte fourni
        asyncio.run(self._stream_audio(text))

    def __del__(self):
        # Assurer la fermeture de PyAudio lors de la destruction de l'objet
        self.p.terminate()

# Exemple d'utilisation
if __name__ == "__main__":
    tts_player = OutputVoice()
    tts_player.speak("Bonjour, je suis un LLM qui vous parle. Comment puis-je vous aider aujourd'hui ?")
