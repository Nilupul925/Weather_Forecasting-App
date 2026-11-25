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
root.mainloop()
