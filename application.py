import os
import tkinter as tk
from collections import OrderedDict
from datetime import datetime
from tkinter import *
from tkinter import messagebox

import pytz
import requests
from dotenv import load_dotenv
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim
from PIL import Image, ImageEnhance, ImageTk
from timezonefinder import TimezoneFinder

# Colour palette
BG_DARK = "#202731"  # window background
SEARCH_BG = "#333c4c"  # search bar
MINT = "#aad1c8"  # current weather box
NAVY = "#323661"  # first forecast card / caption text
CARD = "#EEEFEA"  # small forecast cards
BLUE = "#7094d4"  # bottom strip / accent
MUTED = "#8a93a6"  # hints & placeholder
ERROR = "#ff8a80"

# Loading status
PLACEHOLDER = "Search city..."
DEFAULT_HINT = "Type a city and press Enter or click the search button"

root = Tk()
root.title("Weather Forecaster")
root.geometry("750x470+300+200")
root.resizable(False, False)
root.config(bg=BG_DARK)

# API connect
load_dotenv()
api_key = os.getenv("API_key")

current_tz = None  # timezone of the searched city (if none then computer's time)
status_text = DEFAULT_HINT  # message the status line returns to after hovering
status_color = MUTED
card_info = [""] * 5  # hover details for each forecast card


# Live clock
def refresh_clock():
    now = datetime.now(current_tz) if current_tz else datetime.now()
    clock.config(text=now.strftime("%I:%M %p"))
    date_label.config(text=now.strftime("%A, %d %B"))


def tick():
    refresh_clock()
    root.after(1000, tick)


# Status line under the search bar
def set_status(text, color=MUTED):
    global status_text, status_color
    status_text, status_color = text, color
    status.config(text=text, fg=color)


# Search box placeholder
def clear_placeholder(event=None):
    if textField.cget("fg") == MUTED:
        textField.delete(0, END)
        textField.config(fg="white")


def show_placeholder(event=None):
    if not textField.get():
        textField.insert(0, PLACEHOLDER)
        textField.config(fg=MUTED)


# Weather processing function
def getWeather(event=None):
    city = "" if textField.cget("fg") == MUTED else textField.get().strip()
    if not city:
        messagebox.showwarning("Weather", "Please enter a location.")
        return

    set_status(f"Searching for '{city}'...")
    root.config(cursor="watch")
    root.update_idletasks()
    try:
        loadWeather(city)
    finally:
        root.config(cursor="")


def loadWeather(city):
    global current_tz

    try:
        geoLocator = Nominatim(user_agent="weather-app-api")
        location = geoLocator.geocode(city, timeout=10)
    except GeopyError as e:
        set_status("Location service error", ERROR)
        messagebox.showerror("Weather", f"Location service error:\n{e}")
        return

    if location is None:
        set_status(f"Location '{city}' not found", ERROR)
        messagebox.showerror("Weather", f"Location '{city}' not found.")
        return

    obj = TimezoneFinder()
    result = obj.timezone_at(lng=location.longitude, lat=location.latitude) or "UTC"
    timezone.config(text=result.replace("_", " "))

    lat, lon = location.latitude, location.longitude
    long_lat.config(
        text=f"{abs(lat):.4f}°{'N' if lat >= 0 else 'S'}  "
        f"{abs(lon):.4f}°{'E' if lon >= 0 else 'W'}"
    )

    current_tz = pytz.timezone(result)
    refresh_clock()

    # Weather details
    if not api_key:
        set_status("API_key is missing in .env", ERROR)
        messagebox.showerror("Weather", "API_key is missing.")
        return

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "metric",  # temperatures in °C, wind in m/s
            },
            timeout=10,
        )
        json_data = response.json()

    except (requests.RequestException, ValueError) as e:
        set_status("Could not reach weather service", ERROR)
        messagebox.showerror("Weather", f"Could not reach weather service:\n{e}")
        return

    # On failure OpenWeather returns e.g. {"cod": 401, "message": "Invalid API key..."}
    if response.status_code != 200:
        set_status("Weather API error", ERROR)
        messagebox.showerror(
            "Weather",
            f"Weather API error: {json_data.get('message', response.text)}",
        )
        return

    forecasts = json_data["list"]
    current = forecasts[0]
    description = current["weather"][0]["description"]
    temp = round(current["main"]["temp"])
    pressure = current["main"]["pressure"]
    humidity = current["main"]["humidity"]
    wind = current["wind"]["speed"]

    temperature_value.config(text=f"{temp}°C")
    wind_speed_value.config(text=f"{wind} m/s")
    humidity_value.config(text=f"{humidity}%")
    description_value.config(text=description.capitalize())
    pressure_value.config(text=f"{pressure} hPa")

    # Daily forecast - group the 3-hourly entries by the city's local date
    offset = json_data.get("city", {}).get("timezone", 0)
    days = OrderedDict()
    for entry in forecasts:
        local = datetime.fromtimestamp(entry["dt"] + offset, tz=pytz.utc)
        days.setdefault(local.date(), []).append((local, entry))

    for i, (date, entries) in enumerate(list(days.items())[:5]):
        img_label, day_label, temp_label = day_widget[i]

        # Today -> current conditions, other days -> forecast closest to midday
        if i == 0:
            rep = current
        else:
            rep = min(entries, key=lambda e: abs(e[0].hour - 12))[1]

        high = round(max(e["main"]["temp_max"] for _, e in entries))
        low = round(min(e["main"]["temp_min"] for _, e in entries))

        size = 80 if i == 0 else 50
        icon_code = rep["weather"][0]["icon"]
        img = Image.open(f"icon/{icon_code}@2x.png").resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        img_label.config(image=photo)
        img_label.image = photo

        weekday = date.strftime("%A")
        day_label.config(text=weekday)
        unit = "°C" if i == 0 else "°"
        temp_label.config(text=f"Day: {high}{unit}\nNight: {low}{unit}")

        card_info[i] = (
            f"{weekday}: {rep['weather'][0]['description'].capitalize()}  •  "
            f"{low}°C - {high}°C  •  Humidity {rep['main']['humidity']}%"
        )

    parts = location.address.split(", ")
    place = parts[0] if len(parts) == 1 else f"{parts[0]}, {parts[-1]}"
    set_status(f"Showing weather for {place}  •  hover a day for details", "white")


# Forecast card hover effect
def bind_card_hover(index, widgets, title_label, normal_fg, hover_fg):
    def on_enter(event):
        title_label.config(fg=hover_fg)
        if card_info[index]:
            status.config(text=card_info[index], fg=MINT)

    def on_leave(event):
        under_pointer = root.winfo_containing(*root.winfo_pointerxy())
        if under_pointer in widgets:
            return  # moved between widgets of the same card
        title_label.config(fg=normal_fg)
        status.config(text=status_text, fg=status_color)

    for w in widgets:
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)


# icons
application_icon = PhotoImage(file="Images/logo.png")
root.iconphoto(False, application_icon)

round_box = PhotoImage(file="Images/Rounded Rectangle 1.png")
Label(root, image=round_box, bg=BG_DARK).place(x=30, y=60)

# Details labels (rows aligned inside the mint box)
ROWS = [127, 147, 167, 187, 207]

temperature = Label(root, text="Temperature", font=("Helvetica", 11), fg=NAVY, bg=MINT)
temperature.place(x=38, y=ROWS[0], anchor="w")

humidity = Label(root, text="Humidity", font=("Helvetica", 11), fg=NAVY, bg=MINT)
humidity.place(x=38, y=ROWS[1], anchor="w")

pressure = Label(root, text="Pressure", font=("Helvetica", 11), fg=NAVY, bg=MINT)
pressure.place(x=38, y=ROWS[2], anchor="w")

wind = Label(root, text="Wind Speed", font=("Helvetica", 11), fg=NAVY, bg=MINT)
wind.place(x=38, y=ROWS[3], anchor="w")

description = Label(root, text="Description", font=("Helvetica", 11), fg=NAVY, bg=MINT)
description.place(x=38, y=ROWS[4], anchor="w")

# Search box
searchBox = PhotoImage(file="Images/Rounded Rectangle 3.png")
search_box = Label(root, image=searchBox, bg=BG_DARK)
search_box.place(x=270, y=122)

weatIcon = PhotoImage(file="Images/Layer 7.png")
weat_icon = Label(root, image=weatIcon, bg=SEARCH_BG)
weat_icon.place(x=300, y=152, anchor="w")

searchIcon = PhotoImage(file="Images/search_icon.png")

# Brighter copy of the search icon for the hover effect
_search_img = Image.open("Images/search_icon.png").convert("RGBA")
_r, _g, _b, _a = _search_img.split()
_bright = ImageEnhance.Brightness(Image.merge("RGB", (_r, _g, _b))).enhance(1.3)
searchIconHover = ImageTk.PhotoImage(Image.merge("RGBA", (*_bright.split(), _a)))

search_icon = Button(
    root,
    image=searchIcon,
    borderwidth=0,
    relief=FLAT,
    highlightthickness=0,
    cursor="hand2",
    bg=SEARCH_BG,
    activebackground=SEARCH_BG,
    command=getWeather,
)
search_icon.place(x=700, y=152, anchor="e")
search_icon.bind("<Enter>", lambda e: search_icon.config(image=searchIconHover))
search_icon.bind("<Leave>", lambda e: search_icon.config(image=searchIcon))

textField = tk.Entry(
    root,
    justify="center",
    font=("poppins", 20, "bold"),
    bg=SEARCH_BG,
    border=0,
    fg="white",
    insertbackground="white",
    selectbackground=BLUE,
    highlightthickness=0,
)
textField.place(x=362, y=152, width=286, height=40, anchor="w")
textField.bind("<FocusIn>", clear_placeholder)
textField.bind("<FocusOut>", show_placeholder)
textField.bind("<Return>", getWeather)
show_placeholder()

# Status / hint line under the search bar
status = Label(root, text=DEFAULT_HINT, font=("Helvetica", 9), bg=BG_DARK, fg=MUTED)
status.place(x=497, y=205, anchor="n")

# Details box
frame_box = Frame(root, width=750, height=180, bg=BLUE)
frame_box.pack(side="bottom")

first_box = PhotoImage(file="Images/Rounded Rectangle 2.png")
second_box = PhotoImage(file="Images/Rounded Rectangle 2 copy.png")

# Cards evenly spaced with a 30px margin on both sides
CARD_X = [302, 415, 529, 643]

first_bg = Label(frame_box, image=first_box, bg=BLUE)
first_bg.place(x=30, y=21)

card_bgs = []
for x in CARD_X:
    bg_label = Label(frame_box, image=second_box, bg=BLUE)
    bg_label.place(x=x, y=30)
    card_bgs.append(bg_label)

# Clock
clock = Label(root, font=("Helvetica", 20), bg=BG_DARK, fg="white")
clock.place(x=30, y=20)

date_label = Label(root, font=("Helvetica", 10), bg=BG_DARK, fg=MUTED)
date_label.place(x=33, y=51)

# Time-zone
timezone = Label(root, font=("Helvetica", 20), bg=BG_DARK, fg="white")
timezone.place(x=720, y=20, anchor="ne")

long_lat = Label(root, font=("Helvetica", 10), bg=BG_DARK, fg=MUTED)
long_lat.place(x=720, y=55, anchor="ne")

# Weather values
VALUE_FONT = ("Helvetica", 10, "bold")

temperature_value = Label(root, text="--", font=VALUE_FONT, bg=MINT, fg=BG_DARK)
temperature_value.place(x=128, y=ROWS[0], anchor="w")

humidity_value = Label(root, text="--", font=VALUE_FONT, bg=MINT, fg=BG_DARK)
humidity_value.place(x=128, y=ROWS[1], anchor="w")

pressure_value = Label(root, text="--", font=VALUE_FONT, bg=MINT, fg=BG_DARK)
pressure_value.place(x=128, y=ROWS[2], anchor="w")

wind_speed_value = Label(root, text="--", font=VALUE_FONT, bg=MINT, fg=BG_DARK)
wind_speed_value.place(x=128, y=ROWS[3], anchor="w")

description_value = Label(
    root,
    text="--",
    font=("Helvetica", 9, "bold"),
    bg=MINT,
    fg=BG_DARK,
    wraplength=84,
    justify="left",
)
description_value.place(x=128, y=ROWS[4] - 8, anchor="nw")

# Forecasting cells
# First cell
first_frame = Frame(root, width=226, height=127, bg=NAVY)
first_frame.place(x=35, y=316)

first_image = Label(first_frame, bg=NAVY)
first_image.place(x=6, rely=0.5, anchor="w")

day_1 = Label(first_frame, font=("arial", 18), bg=NAVY, fg="white")
day_1.place(x=158, y=12, anchor="n")

day_1_temp = Label(
    first_frame, font=("arial", 13, "bold"), bg=NAVY, fg="white", justify="center"
)
day_1_temp.place(x=158, y=56, anchor="n")


# Small cells (second to fifth)
def make_small_card(x):
    frame = Frame(root, width=67, height=111, bg=CARD)
    frame.place(x=x + 5, y=325)

    image = Label(frame, bg=CARD)
    image.place(relx=0.5, y=24, anchor="n")

    day = Label(frame, font=("Segoe UI", 9, "bold"), bg=CARD, fg=NAVY)
    day.place(relx=0.5, y=3, anchor="n")

    temp = Label(frame, font=("Segoe UI", 8), bg=CARD, fg="#000000", justify="center")
    temp.place(relx=0.5, y=76, anchor="n")
    return frame, image, day, temp


second_frame, second_image, day_2, day_2_temp = make_small_card(CARD_X[0])
third_frame, third_image, day_3, day_3_temp = make_small_card(CARD_X[1])
fourth_frame, fourth_image, day_4, day_4_temp = make_small_card(CARD_X[2])
fifth_frame, fifth_image, day_5, day_5_temp = make_small_card(CARD_X[3])

day_widget = [
    (first_image, day_1, day_1_temp),
    (second_image, day_2, day_2_temp),
    (third_image, day_3, day_3_temp),
    (fourth_image, day_4, day_4_temp),
    (fifth_image, day_5, day_5_temp),
]

# Hover effects for the forecast cards
bind_card_hover(
    0, [first_bg, first_frame, first_image, day_1, day_1_temp], day_1, "white", MINT
)
small_cards = [
    (second_frame, second_image, day_2, day_2_temp),
    (third_frame, third_image, day_3, day_3_temp),
    (fourth_frame, fourth_image, day_4, day_4_temp),
    (fifth_frame, fifth_image, day_5, day_5_temp),
]
for i, (frame, image, day, temp) in enumerate(small_cards, start=1):
    bind_card_hover(i, [card_bgs[i - 1], frame, image, day, temp], day, NAVY, BLUE)

tick()
root.mainloop()
