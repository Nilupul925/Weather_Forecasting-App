import os
import tkinter as tk
from datetime import datetime
from tkinter import *
from tkinter import messagebox

import pytz
import requests
from dotenv import load_dotenv
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

root = Tk()
root.title("Weather Forecaster")
root.geometry("750x470+300+200")
root.resizable(False, False)
root.config(bg="#202731")

# API connect
load_dotenv()
api_key = os.getenv("API_key")


# Weather processing function
def getWeather():
    city = textField.get().strip()
    if not city:
        messagebox.showwarning("Weather", "Please enter a location.")
        return

    try:
        geoLocator = Nominatim(user_agent="weather-app-api")
        location = geoLocator.geocode(city, timeout=10)
    except GeopyError as e:
        messagebox.showerror("Weather", f"Location service error:\n{e}")
        return

    if location is None:
        messagebox.showerror("Weather", f"Location '{city}' not found.")
        return

    obj = TimezoneFinder()
    result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
    timezone.config(text=result)

    long_lat.config(
        text=f"{round(location.latitude,4)}°N {round(location.longitude,4)}°E"
    )

    home = pytz.timezone(result)
    local_time = datetime.now(home)
    current_time = local_time.strftime("%I:%M %p")

    clock.config(text=current_time)

    # Weather details
    if not api_key:
        messagebox.showerror("Weather", "API_key is missing.")
        return

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": location.latitude,
                "lon": location.longitude,
                "appid": api_key,
                "units": "metric",  # temperatures in °C, wind in m/s
            },
            timeout=10,
        )
        json_data = response.json()
        print(json_data)

    except (requests.RequestException, ValueError) as e:
        messagebox.showerror("Weather", f"Could not reach weather service:\n{e}")
        return

    # On failure OpenWeather returns e.g. {"cod": 401, "message": "Invalid API key..."}
    if response.status_code != 200:
        messagebox.showerror(
            "Weather",
            f"Weather API error: {json_data.get('message', response.text)}",
        )
        return

    description = json_data["weather"][0]["description"]
    temp = round(json_data["main"]["temp"])
    pressure = json_data["main"]["pressure"]
    humidity = json_data["main"]["humidity"]
    wind = json_data["wind"]["speed"]

    temperature_value.config(text=f"{temp}°C")
    wind_speed_value.config(text=f"{wind} m/s")
    humidity_value.config(text=f"{humidity}%")
    description_value.config(text=description)
    pressure_value.config(text=f"{pressure} hPa")


# icons
application_icon = PhotoImage(file="Images/logo.png")
root.iconphoto(False, application_icon)

round_box = PhotoImage(file="Images/Rounded Rectangle 1.png")
Label(root, image=round_box, bg="#202731").place(x=30, y=60)

# Details labels
temperature = Label(
    root, text="Temperature", font=("Helvetica", 11), fg="#323661", bg="#aad1c8"
)
temperature.place(x=40, y=120)

humidity = Label(
    root, text="Humidity", font=("Helvetica", 11), fg="#323661", bg="#aad1c8"
)
humidity.place(x=40, y=140)

pressure = Label(
    root, text="Pressure", font=("Helvetica", 11), fg="#323661", bg="#aad1c8"
)
pressure.place(x=40, y=160)

wind = Label(
    root, text="Wind Speed", font=("Helvetica", 11), fg="#323661", bg="#aad1c8"
)
wind.place(x=40, y=180)

description = Label(
    root, text="Description", font=("Helvetica", 11), fg="#323661", bg="#aad1c8"
)
description.place(x=40, y=200)

# Search box
searchBox = PhotoImage(file="Images/Rounded Rectangle 3.png")
search_box = Label(root, image=searchBox, bg="#202731")
search_box.place(x=270, y=122)

weatIcon = PhotoImage(file="Images/Layer 7.png")
weat_icon = Label(root, image=weatIcon, bg="#333c4c")
weat_icon.place(x=300, y=125)

searchIcon = PhotoImage(file="Images/search_icon.png")
search_icon = Button(
    root,
    image=searchIcon,
    borderwidth=0,
    cursor="hand2",
    bg="#333c4c",
    command=getWeather,
)
search_icon.place(x=645, y=135)

textField = tk.Entry(
    root,
    justify="center",
    width=15,
    font=("poppins", 25, "bold"),
    bg="#333c4c",
    border=0,
    fg="white",
)
textField.place(x=370, y=130)

# Details box
frame_box = Frame(root, width=900, height=180, bg="#7094d4")
frame_box.pack(side="bottom")

first_box = PhotoImage(file="Images/Rounded Rectangle 2.png")
second_box = PhotoImage(file="Images/Rounded Rectangle 2 copy.png")

Label(frame_box, image=first_box, bg="#7094d4").place(x=30, y=20)

Label(frame_box, image=second_box, bg="#7094d4").place(x=300, y=30)
Label(frame_box, image=second_box, bg="#7094d4").place(x=400, y=30)
Label(frame_box, image=second_box, bg="#7094d4").place(x=500, y=30)
Label(frame_box, image=second_box, bg="#7094d4").place(x=600, y=30)

# Clock
clock = Label(root, font=("Helvetica", 20), bg="#202731", fg="white")
clock.place(x=30, y=20)

# Time-zone
timezone = Label(root, font=("Helvetica", 20), bg="#202731", fg="white")
timezone.place(x=500, y=20)

long_lat = Label(root, font=("Helvetica", 10), bg="#202731", fg="white")
long_lat.place(x=500, y=50)

# Weather values
temperature_value = Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
temperature_value.place(x=150, y=120)

humidity_value = Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
humidity_value.place(x=150, y=140)

pressure_value = Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
pressure_value.place(x=150, y=160)

wind_speed_value = Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
wind_speed_value.place(x=150, y=180)

description_value = Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
description_value.place(x=150, y=200)

# Forecasting cells
# First cell
first_frame = Frame(root, width=230, height=132, bg="#eeefea")
first_frame.place(x=35, y=315)

first_image = Label(first_frame, bg="#323661")
first_image.place(x=1, y=15)

day_1 = Label(first_frame, font=("arial", 20), bg="#323661", fg="white")
day_1.place(x=100, y=50)

day_1_temp = Label(first_frame, font=("arial", 15, "bold"), bg="#323661", fg="white")
day_1_temp.place(x=100, y=50)

# Second cell
second_frame = Frame(root, width=70, height=115, bg="#eeefea")
second_frame.place(x=305, y=325)

second_image = Label(second_frame, bg="#eeefea")
second_image.place(x=7, y=20)

day_2 = Label(second_frame, bg="#eeefea", fg="#000000")
day_2.place(x=10, y=5)

day_2_temp = Label(second_frame, bg="#eeefea", fg="#000000")
day_2_temp.place(x=2, y=70)

# third cell
third_frame = Frame(root, width=70, height=115, bg="#eeefea")
third_frame.place(x=405, y=325)

third_image = Label(third_frame, bg="#eeefea")
third_image.place(x=7, y=20)

day_3 = Label(third_frame, bg="#eeefea", fg="#000000")
day_3.place(x=10, y=5)

day_3_temp = Label(third_frame, bg="#eeefea", fg="#000000")
day_3_temp.place(x=2, y=70)

# fourth cell
fourth_frame = Frame(root, width=70, height=115, bg="#eeefea")
fourth_frame.place(x=505, y=325)

fourth_image = Label(fourth_frame, bg="#eeefea")
fourth_image.place(x=7, y=20)

day_4 = Label(fourth_frame, bg="#eeefea", fg="#000000")
day_4.place(x=10, y=5)

day_4_temp = Label(fourth_frame, bg="#eeefea", fg="#000000")
day_4_temp.place(x=2, y=70)

# fifth cell
fifth_frame = Frame(root, width=70, height=115, bg="#eeefea")
fifth_frame.place(x=605, y=325)

fifth_image = Label(fifth_frame, bg="#eeefea")
fifth_image.place(x=7, y=20)

day_5 = Label(fifth_frame, bg="#eeefea", fg="#000000")
day_5.place(x=10, y=5)

day_5_temp = Label(fifth_frame, bg="#eeefea", fg="#000000")
day_5_temp.place(x=2, y=70)

root.mainloop()
