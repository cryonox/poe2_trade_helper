from playsound import playsound
from threading import Thread
from datetime import datetime


def play(path):
    def play_thread_function():
        playsound(path)

    play_thread = Thread(target=play_thread_function)
    play_thread.start()


def nowstr():
    now = datetime.now()
    dt_str = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_str
