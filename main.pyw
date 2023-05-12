from pynput import mouse
import json
from PIL import Image, ImageDraw, ImageFont, ImageGrab
import ctypes
from pydub import AudioSegment
from pydub.playback import play
from datetime import date
import threading
import time
import tempfile


def main():
    words = json.load(open("words.json", "r"))
    if words[-1] == 814:
        words[-1] = -1
    words[-1] += 1

    with open("date.txt", "r") as f:
        if f.read() == str(date.today()):
            words[-1] -= 1
        else:
            with open("date.txt", "w") as f1:
                f1.write(str(date.today()))

    json.dump(words, open("words.json", "w"))
    today = words[words[-1]]
    today_word_id = today[1]
    today_word_en = today[2]

    def play_sound():
        pronunciation = AudioSegment.from_mp3(words[words[-1]][0])
        play(pronunciation+10)

    def get_color(x, y):
        bbox = (x, y, x + 1, y + 1)
        im = ImageGrab.grab(bbox=bbox, all_screens=True)
        cursor_color = im.getpixel((0, 0))

        screen = ImageGrab.grab(all_screens=True)
        corners = [screen.getpixel((2842, 875)),
                   screen.getpixel((2265, 875)),
                   screen.getpixel((2265, 655)),
                   screen.getpixel((2842, 655))]
        corners1 = [screen.getpixel((555, 795)),
                    screen.getpixel((1035, 795)),
                    screen.getpixel((555, 610)),
                    screen.getpixel((1035, 610))]

        corners_visible = 0
        corners1_visible = 0

        button_colors = ((153, 0, 0), (255, 0, 0), (0, 0, 0), (48, 48, 48))

        cursor_on_button = False

        for color in button_colors:
            if cursor_color == color:
                cursor_on_button = True
                break

        for i in corners:
            if i == (153, 0, 0):
                corners_visible += .25

        for i in corners1:
            if i == (153, 0, 0):
                corners1_visible += .25

        if 660 < x < 1248 and 650 < y < 877 and corners_visible > .4 and cursor_on_button:
            thread_play = threading.Thread(target=play_sound())
            thread_play.start()
        elif -1048 < x < -567 and 610 < y < 788 and corners1_visible > .4 and cursor_on_button:
            thread_play = threading.Thread(target=play_sound())
            thread_play.start()

    queue = []

    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            thread = threading.Thread(target=get_color, args=(x, y))
            queue.append(thread)

    listener = mouse.Listener(on_click=on_click)
    listener.start()

    tempdir = tempfile.mkdtemp()

    img = Image.new(mode="RGB", size=(1920, 1080), color="black")
    draw = ImageDraw.Draw(img)
    _, _, w, h = draw.textbbox((0, 0), today_word_id, font=ImageFont.truetype("arial.ttf", size=128))
    draw.text(xy=((1920 - w) / 2, (1080 - h * 2) / 2), text=today_word_id,
              font=ImageFont.truetype("arial.ttf", size=128), fill="red")
    _, _, w, h = draw.textbbox((0, 0), today_word_en, font=ImageFont.truetype("arial.ttf", size=128))
    draw.text(xy=((1920 - w * 86 / 128) / 2, 1080 / 2), text=today_word_en,
              font=ImageFont.truetype("arial.ttf", size=86),
              fill="red")
    button = Image.open("przycisk.png")
    img.paste(button, (660, 650))

    img.save(f"{tempdir}/language_wallpaper.png", "PNG")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, f"{tempdir}\language_wallpaper.png", 0x1)

    while True:
        if len(queue):
            queue[0].start()
            queue = []
        time.sleep(1)


if __name__ == "__main__":
    main()
