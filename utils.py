from playsound import playsound
from threading import Thread


def play(path):
    def play_thread_function():
        playsound(path)

    play_thread = Thread(target=play_thread_function)
    play_thread.start()
