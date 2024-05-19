import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import threading

import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os

from pydub.utils import which

AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

Window.size = (450, 800)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        with layout.canvas.before:
            Color(1, 1, 1, 0.9)
            self.rect = Rectangle(size=(1920,1080), pos=layout.pos)

        self.label = Label(text="Elige una opción",
                           font_size='24sp',
                           color=[0, 0, 0, 1])
        layout.add_widget(self.label)

        btn_speech_to_text = Button(
            text="Voz a texto",
            font_size='24sp',
            background_color=[0.741, 0.894, 0.655, 1],
            color=[1, 1, 1, 1]
        )
        btn_speech_to_text.bind(on_press=self.speech_to_text)
        layout.add_widget(btn_speech_to_text)

        btn_text_to_speech = Button(
            text="Texto a voz",
            font_size='24sp',
            background_color=[0.478, 0.612, 0.776, 0.8],
            color=[1, 1, 1, 1]
        )
        btn_text_to_speech.bind(on_press=self.show_text_input)
        layout.add_widget(btn_text_to_speech)

        self.text_input = TextInput(
            hint_text="Escribe aquí el texto",
            multiline=False,
            font_size='24sp',
            background_color=[1, 1, 1, 0.5],

        )
        layout.add_widget(self.text_input)
        self.text_input.bind(on_text_validate=self.text_to_speech)
        self.text_input.opacity = 0

        self.add_widget(layout)

    def speech_to_text(self, instance):
        self.label.text = "Por favor, habla ahora..."
        threading.Thread(target=self._perform_speech_to_text).start()

    def _perform_speech_to_text(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="es-ES")
            Clock.schedule_once(lambda dt: self.update_label(f"Texto reconocido: {text}"), 0)
        except sr.UnknownValueError:
            Clock.schedule_once(lambda dt: self.update_label("No se pudo entender el audio"), 0)
        except sr.RequestError:
            Clock.schedule_once(lambda dt: self.update_label("Error con el servicio de reconocimiento"), 0)

    def update_label(self, text):
        self.label.text = text

    def show_text_input(self, instance):
        self.text_input.opacity = 1

    def text_to_speech(self, instance):
        text = self.text_input.text
        if text:
            threading.Thread(target=self._perform_text_to_speech, args=(text,)).start()

    def _perform_text_to_speech(self, text):
        tts = gTTS(text=text, lang='es')
        filename = "temp_audio.mp3"
        tts.save(filename)
        audio = AudioSegment.from_mp3(filename)
        play(audio)
        os.remove(filename)
        Clock.schedule_once(lambda dt: self.update_label("Reproducción completada"), 0)


class SpeechApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == "__main__":
    SpeechApp().run()
