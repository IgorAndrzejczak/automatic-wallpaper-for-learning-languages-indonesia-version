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
from screeninfo import get_monitors


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
        play(pronunciation + 10)

    def get_color(x, y):
        monitor_count = ctypes.windll.user32.GetSystemMetrics(80)
        vertical_setup = False

        delta_height = abs(min([monitor.y for monitor in get_monitors()]))
        bbox = (x, y, x + 1, y + 1)
        im = ImageGrab.grab(bbox=bbox, all_screens=True)
        cursor_color = im.getpixel((0, 0))

        screen = ImageGrab.grab(all_screens=True)
        if screen.width <= max([monitor.width for monitor in get_monitors()]) and monitor_count > 1:
            vertical_setup = True
        x_offset = 0
        x_offset_mouse = 0
        y_offset_vertical = 0

        for index, monitor in enumerate(get_monitors()):
            y_offset = monitor.y+delta_height if not vertical_setup else 0
            y_offset += y_offset_vertical if vertical_setup else 0
            corners = [screen.getpixel((int(monitor.width*.34375)+x_offset, int(monitor.height*.61)+y_offset)),
                       screen.getpixel((int(monitor.width*.648)+x_offset, int(monitor.height*.61)+y_offset)),
                       screen.getpixel((int(monitor.width*.34375)+x_offset, int(monitor.height*.811)+y_offset)),
                       screen.getpixel((int(monitor.width*.648)+x_offset, int(monitor.height*.811)+y_offset))]

            corners_visible = 0

            button_colors = ((153, 0, 0), (250, 0, 0), (80, 80, 80), (1, 1, 1))

            cursor_on_button = False

            for color in button_colors:
                if cursor_color == color:
                    cursor_on_button = True
                    break

            for i in corners:
                if i == (153, 0, 0):
                    corners_visible += .25

            mouse_add_x = monitor.x if monitor.x < 0 else 0
            if delta_height > 0:
                mouse_add_y = delta_height if monitor.y <= 0 and not monitor.is_primary else 0
            else:
                mouse_add_y = -max([monitor.y for monitor in get_monitors()]) if monitor.y > 0 else 0
            try:
                x_offset_mouse += get_monitors()[index - 1].width if monitor.x > 0 and not vertical_setup else 0
            except IndexError:
                pass

            correct_mouse_x = int(monitor.width*.34375) < x-mouse_add_x-x_offset_mouse < int(monitor.width*.65)
            correct_mouse_y = int(monitor.height*.6) < y+mouse_add_y < int(monitor.height*.81)
            correct_mouse_position = correct_mouse_x and correct_mouse_y

            if correct_mouse_position and corners_visible > .4 and cursor_on_button:
                thread_play = threading.Thread(target=play_sound())
                thread_play.start()
            x_offset += monitor.width if not vertical_setup else 0
            y_offset_vertical += monitor.height if vertical_setup else 0

    queue = []

    def on_click(x, y, pressed_button, pressed):
        if pressed and pressed_button == mouse.Button.left:
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

    draw.rectangle(xy=(660, 650, 660+588, 650+227), fill=(153, 0, 0))
    draw.rectangle(xy=(670, 660, 660+578, 650+217), fill=(250, 0, 0))
    draw.text(xy=(682, 702), text="pronunciation",
              font=ImageFont.truetype("arial.ttf", size=92), fill=(80, 80, 80))
    draw.text(xy=(680, 700), text="pronunciation",
              font=ImageFont.truetype("arial.ttf", size=92), fill=(1, 1, 1))

    img.save(f"{tempdir}\\language_wallpaper.png", "PNG")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, f"{tempdir}\\language_wallpaper.png", 0x1)

    while True:
        if len(queue):
            queue[0].start()
            queue = []
        time.sleep(1)


if __name__ == "__main__":
    main()
