import tkinter as tk
from tkinter import *

root = Tk()
root.title("Weather Forecaster")
root.geometry("750x470+300+200")
root.resizable(False, False)
root.config(bg="#202731")

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
    root, image=searchIcon, borderwidth=0, cursor="hand2", bg="#333c4c"
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


root.mainloop()
