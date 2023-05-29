import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("500x350")


def buttonf():
    print("Test")


frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="Blessing AI", font=("Roboto", 24))
label.pack(pady=12, padx=10)

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Username", )
entry1.pack(pady=12, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="pass", show="*")
entry2.pack(pady=12, padx=10)

button = customtkinter.CTkEntry(master=frame, placeholder_text="button", command=buttonf)
button.pack(pady=12, padx=10)
checkbox = customtkinter.CTkCheckBox(master=frame, text="checkbox test")
checkbox.pack(pady=12, padx=10)

root.mainloop()
