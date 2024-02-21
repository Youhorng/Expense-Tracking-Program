from tkinter import *
from tkinter import messagebox
from main import *

def login():

    root = Tk()
    root.title("Login")
    root.geometry("925x500+300+200")
    root.resizable(False, False)
    root.config(bg="#fff")

    def sign_in():
        user = username.get()
        passw = password.get()

        if user == "admin" and passw == "admin":
            messagebox.showinfo("Success", "Login Successful")
            root.destroy()
            expense_tracker_window()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")


    img = PhotoImage(file="login.png")
    Label(root, image=img, bg="#fff").place(x=50, y=50)

    frame = Frame(root, width=350, height=350, bg="white")
    frame.place(x=480, y=70)

    heading = Label(frame, text="LOGIN", font=("Microsoft YaHei UI Light", 30, "bold"), fg="#57a1f8", bg="white")
    heading.place(x=115, y=10)


    def on_enter(e):
        username.delete(0, END)


    def on_leave(e):
        name = username.get()
        if name == '':
            username.insert(0, 'Username')


    username = Entry(frame, font=("Microsoft YaHei UI Light", 15), fg="black", bg="white", border=0)
    username.place(x=40, y=100, width=280, height=35)
    username.insert(0, "Username")
    username.bind('<FocusIn>', on_enter)
    username.bind('<FocusOut>', on_leave)


    Frame(frame, width=295, height=2, bg="black").place(x=40, y=140)

    def on_enter(e):
        password.delete(0, END)


    def on_leave(e):
        name = password.get()
        if name == '':
            password.insert(0, 'Password')

    password = Entry(frame, font=("Microsoft YaHei UI Light", 15), fg="black", bg="white", border=0)
    password.place(x=40, y=200, width=280, height=35)
    password.insert(0, "Password")
    password.bind('<FocusIn>', on_enter)
    password.bind('<FocusOut>', on_leave)

    Frame(frame, width=295, height=2, bg="black").place(x=40, y=240)

    login_btn = Button(frame, text="Login", font=("Microsoft YaHei UI Light", 15, "bold"), fg="white", bg="#57a1f8", border=0, cursor="hand2", command=sign_in)
    login_btn.place(x=40, y=290, width=295, height=40)
    login_btn.config(justify=CENTER, anchor=CENTER)

    
    root.mainloop()

