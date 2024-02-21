# Import all necessary modules for the program

import datetime 
import sqlite3
from tkcalendar import DateEntry
from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import matplotlib.pyplot as plt
import requests

# Create a database and connect to it

connector = sqlite3.connect('expense_tracker.db')
cursor = connector.cursor()

# Create a table to store the data for expense tracker program

cursor.execute("""
    CREATE TABLE IF NOT EXISTS expense_tracker (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT NOT NULL,
        Description TEXT NOT NULL,
        Categories TEXT NOT NULL,
        Amount REAL NOT NULL,
        Payee TEXT NOT NULL,
        ModeOfPayment TEXT NOT NULL             
    )
""")
connector.commit()  

# Create a table to store the data for user's monthl budget

cursor.execute("CREATE TABLE IF NOT EXISTS User (Id INTEGER PRIMARY KEY AUTOINCREMENT, Budget REAL NOT NULL)")
connector.commit()

# Create all functions for the program

# Function to list all expenses and display the expense on the table tkinter

def list_all_expenses():
    
    # Set global variable 
    global cursor, connector

    # Clearing table using table.delete
    table.delete(*table.get_children())

    # Selecting all data from database
    all_data = cursor.execute("SELECT * FROM expense_tracker")
    data = all_data.fetchall()

    # Inserting data into the table
    for row in data:
        table.insert('', 'end', values=row)


# Function to clear the entry boxes

def clear_fields():
    # Set global variable
    global description, categories, amount, payee, mode_of_payment
    global date, table

    # Get today's date
    today_date = datetime.datetime.now().date()

    # Set all entry boxes to empty
    description.set("")
    categories.set("")
    amount.set("")
    payee.set("")
    mode_of_payment.set("Cash")
    date.set_date(today_date)

    Button(data_entry_frame, text="Add Expense", bg=button_bg, font=button_font, width=11 , command=add_expense).place(x=20, y=470)
    Button(data_entry_frame, text="Add Budget", bg=button_bg, font=button_font, width=11, command=window_add_budget).place(x=160, y=470)

    # Clear selection on the table
    table.selection_remove(table.selection())


# Function to delete all expesnes from the database

def delete_all_expenses():
    # Set global variable
    global cursor, connector
    global table

    # Ask for user confirmation
    user_confirmation = mb.askyesno("Delete All Expenses", "Are you sure you want to delete all expenses?")

    # If user confirms, delete all expenses from the database
    if user_confirmation == True:
        
        # Delete all expenses from the table
        table.delete(*table.get_children())

        # Delete all expenses from the database
        cursor.execute("DELETE FROM expense_tracker")
        connector.commit()

        # Clear all entry boxes and then list all expense on table
        clear_fields()
        list_all_expenses()

        # Show message box to user
        mb.showinfo("Delete All Expenses", "All expenses have been deleted successfully.")

    else:
        mb.showinfo("No Changes Made", "No changes have been made.")


# Function to delete a single expense from the database

def delete_expense():
    # Set global variable
    global cursor, connector
    global table

    # Check if a row is selected on the table

    if not table.selection():
        # Show error
        mb.showerror("Error", "Please select an expense to delete.")
    else:
        # Get value of the selected row
        selected_row = table.item(table.focus())
        row_id = selected_row['values'][0]

        # Ask for user confirmation
        user_confirmation = mb.askyesno("Delete Expense", "Are you sure you want to delete this expense?")

        # If user confirms, delete the expense from the database
        if user_confirmation == True:
            # Delete expense from database
            cursor.execute("DELETE FROM expense_tracker WHERE Id=?", (row_id,))
            connector.commit()

            # Invoke list_all_expense() funtion to list all expense on the table with the updated database
            list_all_expenses()
            
            # Show message box to user
            mb.showinfo("Delete Expense", "Expense has been deleted successfully.")


# Function to edit expense

def edit_expense():
    # Set global variable
    global table, data_entry_frame, button_bg, button_font

    # Function to edit the expense
    def edit():
        # Set global variable
        global description, categories, amount, payee, mode_of_payment
        global date, table
        global cursor, connector

        # Get value of the selected row
        selected_row = table.item(table.focus())
        row_id = selected_row['values']

        # Update database with new edited expense
        cursor.execute("UPDATE expense_tracker SET Date=?, Description=?, Categories=?, Amount=?, Payment=?, ModeOfPayment=? WHERE Id=?", (date.get(), description.get(), categories.get(), amount.get(), payee.get(), mode_of_payment.get(), row_id[0]))
        connector.commit()

        # Clear all the data fields
        clear_fields()
        
        # Invoke list_all_expense() funtion to list all expense on the table with the updated database
        list_all_expenses()

        # Show message box to user
        mb.showinfo("Edit Expense", "Expense has been edited successfully.")
        
        # Destroy edit_button
        edit_button.destroy()  

        return

    # Check if a row is selected on the table
    if not table.selection():
        # Show error
        mb.showerror("Error", "Please select an expense to edit.")
        return
    
    view_expense()

    # Create button to overlap the add expense button
    edit_button = Button(data_entry_frame, text="Edit Expense", bg=button_bg, font=button_font, width=25, command=edit)
    edit_button.place(x=20, y=470)


# Validate input

def validate_input():
    # Set global variable
    global description, categories, amount, payee, mode_of_payment

    # Check if all entry boxes are filled
    if not date.get() or not description.get() or not categories.get() or not amount.get() or not payee.get() or not mode_of_payment.get():
        # Show error
        mb.showerror("Error", "Please fill all the entry boxes.")
        return
    
    # Validate amount is number
    try:
        amount_value = float(amount.get())
    except ValueError:
        mb.showerror("Error", "Amount must be a number.")
        return
    
    # Validate amount is positive
    if amount_value <= 0:
        mb.showerror("Error", "Amount must be positive.")
        return
    
    return True


# Function to add expense

def add_expense():
    # Set global variable
    global cursor, connector, date
    global description, categories, amount, payee, mode_of_payment

    # Validate input
    is_valid = validate_input()

    if not is_valid:
        return
    
    # Insert added data to the database
    # Convert amount.get() to float since It is in StringVar()

    cursor.execute("INSERT INTO expense_tracker VALUES (NULL, ?, ?, ?, ?, ?, ?)", (date.get(), description.get(), categories.get(), float(amount.get()), payee.get(), mode_of_payment.get()))
    connector.commit()

    # Clear all the data fields
    clear_fields()

    # Invoke list_all_expense() funtion to list all expense on the table with the updated database
    list_all_expenses()

    # Show message box to user
    mb.showinfo("Add Expense", "Expense has been added successfully.")


    # Invoke send_message() function to send message to telegram bot
    send_message()

# Function to send message to telegram bot

def send_message():
    # Set global variable
    global cursor, connector

    # Select amount from database
    cursor.execute("SELECT Amount FROM expense_tracker")
    values = cursor.fetchall()
    value = values[-1][0]

    # Select categories from database
    cursor.execute("SELECT Categories FROM expense_tracker")
    categories = cursor.fetchall()
    category = categories[-1][0]

    # Select date from database
    cursor.execute("SELECT Date FROM expense_tracker")
    dates = cursor.fetchall()
    date = dates[-1][0]

    TOKEN = "6882514985:AAFceBMJOi-o_pa-JFR802UaiyBLQsolSUA"
    chat_id = "824421770"
    message = str(value) + " has been added to your expense tracker." + "\n" + " Category: " + category + "\n" + " Date: " + date
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"

    print(requests.get(url).json())


# Function to view expense in detail when selected on the table tkinter

def view_expense():
    # Set global variable
    global cursor, connector
    global table, date
    global description, categories, amount, payee, mode_of_payment

    # Check if a row is selected on the table
    if not table.selection():
        # Show error
        mb.showerror("Error", "Please select an expense to view.")
    
    # Get value of the selected row
    selected_row = table.item(table.focus())
    row_id = selected_row['values']

    # Get expense date
    cursor.execute("SELECT Date FROM expense_tracker WHERE Id=?", (row_id[0],))
    values = cursor.fetchall()
    for value in values:
        list_value = value[0].split("/")
        month = list_value[0]
        day = list_value[1]
        year = list_value[2]
        expenditure_date = datetime.date(int(year), int(month), int(day))

    # Set all entry boxes to the selected expense
    date.set_date(expenditure_date); description.set(row_id[2]); categories.set(row_id[3]); amount.set(row_id[4]); payee.set(row_id[5]); mode_of_payment.set(row_id[6])


# Function to get all monthly expense

def get_monthly_expense():
    # Set global variable
    global cursor

    def jan_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '1/01/23' AND '1/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    
    def feb_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '2/01/23' AND '2/9/23'")
        values = cursor.fetchall()
        return values[0][0]

    def mar_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '3/01/23' AND '3/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    
    def apr_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '4/01/23' AND '4/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    
    def may_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '5/01/23' AND '5/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    
    def jun_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '6/01/23' AND '6/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    

    def jul_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '7/01/23' AND '7/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    

    def aug_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '8/01/23' AND '8/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    

    def sep_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '9/01/23' AND '9/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    
    def oct_expense():

        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '10/01/23' AND '10/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    

    def nov_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '11/01/23' AND '11/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    

    def dec_expense():
        global cursor
        
        cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN '12/01/23' AND '12/9/23'")
        values = cursor.fetchall()
        return values[0][0]
    
    expenses = [jan_expense(), feb_expense(), mar_expense(), apr_expense(), may_expense(), jun_expense(), jul_expense(), aug_expense(), sep_expense(), oct_expense(), nov_expense(), dec_expense()]

    return expenses


# Function to view graph of the expense tracker program

# This function has four small functions that use matplotlib to plot the graph

def view_graph():
    
    global graph_window

    # Initialize graph window
    graph_window = Tk()
    graph_window.title("Expense Chart")
    graph_window.geometry("700x400")
    graph_window.resizable(False, False)
    graph_window.configure(bg="#FF8080")

    # Set heading
    Label(graph_window, text="Expense Chart", font=('Georgia', 20, 'bold')).place(x=230, y=40)

    # Create button
    Button(graph_window, text="Daily Expense Chart", font=('Georgia', 15), width=23, bg="#78BCC4", command=daily_expense).place(x=25, y=120)
    Button(graph_window, text="Monthly Expense Chart", font=('Georgia', 15), width=23, bg="#78BCC4", command=monthly_expense).place(x=25, y=200)
    Button(graph_window, text="Category Expense Chart", font=('Georgia', 15), width=23, bg="#78BCC4", command=expense_categories).place(x=360, y=120)
    Button(graph_window, text="Expense Analysis", font=('Georgia', 15), width=23, bg="#78BCC4", command=categories_percentage).place(x=360, y=200)


# Function to view expense categories that have been spent on

def expense_categories():
    # Set global variable
    global cursor, connector
    global graph_window

    # Select Categories from database by summing up the amount group by categories
    cursor.execute("SELECT Categories, SUM(Amount) FROM expense_tracker GROUP BY Categories")
    values = cursor.fetchall()
    
    categories = []
    expenses = []

    for value in values:
        categories.append(value[0])
        expenses.append(value[1])

    # Plot the graph

    plt.figure(figsize=(10, 6))

    plt.bar(categories, expenses, color="Green")

    plt.title("Expense Categories")
    plt.xlabel("Categories")
    plt.ylabel("Expenses")

    plt.show()

    graph_window.destroy()


# Function to view the daily expense of the program

def daily_expense():
    # Set global variable
    global cursor, connector
    global graph_window

    # Select Amount and Date from database
    cursor.execute("SELECT Amount, Date FROM expense_tracker GROUP BY Date")
    values = cursor.fetchall()

    expenses = []
    dates = []

    for value in values:
        expenses.append(value[0])
        dates.append(value[1])

    # Plot the graph

    plt.figure(figsize=(10, 6))
    plt.plot(dates, expenses, color="Green")

    plt.title("Daily Expense")
    plt.xlabel("Date")
    plt.ylabel("Expenses")

    plt.xticks(fontsize=5)

    plt.show()

    graph_window.destroy()


# Function to view the monthly expense of the program


def monthly_expense():

    global graph_window
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May','Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    expenses = get_monthly_expense()

    # Plot the graph

    plt.figure(figsize=(10, 6))
    plt.bar(months, expenses, color="Green")

    plt.title("Monthly Expense")
    plt.xlabel("Months")
    plt.ylabel("Expenses")

    plt.show()

    graph_window.destroy()

# Function to view the categories of the expense by percentage

def categories_percentage():
    # Set global variable
    global cursor, connector
    global graph_window

    # Select Categories from database by summing up the amount group by categories
    cursor.execute("SELECT Categories, SUM(Amount) FROM expense_tracker GROUP BY Categories")
    values = cursor.fetchall()

    expenses = []
    labels = []
    threshold = 0.05

    # Calculate the total expense across all categories
    total_expense = 0

    for _, expense in values:
        total_expense += expense
    
    
    # Initialize variables to track expenses for "Others" category
    others_expense = 0
    others_label = "More"

    for value in values:
        expense = value[1]
        if expense / total_expense < threshold:
            others_expense += expense
        else:
            expenses.append(expense)
            labels.append(f"{value[0]} ({expense:.2f})")

    if others_expense > 0:
        expenses.append(others_expense)
        labels.append(f"{others_label} ({others_expense:.2f})")

    plt.pie(expenses, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
    plt.title('Expense by Category')

    plt.show()

    graph_window.destroy()


# Function to view report of the program
# It has four main funtions that generate the report for the program

def view_report():
    
    global report_window

    report_window = Tk()
    report_window.title("Report")
    report_window.geometry("700x400")
    report_window.resizable(False, False)
    report_window.configure(bg="#FF8080")

    # Set heading
    Label(report_window, text="Report", font=('Georgia', 20, 'bold')).place(x=300, y=40)

    # Create button
    Button(report_window, text="Monthly Budget", font=('Georgia', 15), width=23, bg="#78BCC4", command=monthly_budget_report).place(x=25, y=120)
    Button(report_window, text="Remain Budget", font=('Georgia', 15), width=23, bg="#78BCC4", command=remain_budget).place(x=25, y=200)
    Button(report_window, text="Remain Trend", font=('Georgia', 15), width=23, bg="#78BCC4", command=monthly_trend).place(x=360, y=120)
    Button(report_window, text="Budget Report", font=('Georgia', 15), width=23, bg="#78BCC4", command=remain_report).place(x=360, y=200)

    report_window.mainloop()


# Function each remain budget

def remain_monthly_budget():
    # Set global variable
    global cursor, connector
    global report_window

    # Select all from User database
    cursor.execute("SELECT * FROM User")
    values = cursor.fetchall()

    # Reverse the values to get the latest monthly budget and check if it is zero, get the next latest monthly budget

    reverse_values = values[::-1]

    for item in reverse_values:
        if item[1] != 0.0:
            monthly_budget = item[1]
            break

    monthly_expenses = get_monthly_expense()

    jan_remain = monthly_budget - monthly_expenses[0]
    feb_remain = monthly_budget - monthly_expenses[1]
    mar_remain = monthly_budget - monthly_expenses[2]
    apr_remain = monthly_budget - monthly_expenses[3]
    may_remain = monthly_budget - monthly_expenses[4]
    jun_remain = monthly_budget - monthly_expenses[5]
    jul_remain = monthly_budget - monthly_expenses[6]
    aug_remain = monthly_budget - monthly_expenses[7]
    sep_remain = monthly_budget - monthly_expenses[8]
    oct_remain = monthly_budget - monthly_expenses[9]
    nov_remain = monthly_budget - monthly_expenses[10]
    dec_remain = monthly_budget - monthly_expenses[11]

    remain_budget = [jan_remain, feb_remain, mar_remain, apr_remain, may_remain, jun_remain, jul_remain, aug_remain, sep_remain, oct_remain, nov_remain, dec_remain]

    report_window.destroy()

    return remain_budget


# Function to get remain report

def remain_report():

    global report_window

    remain_expenses = remain_monthly_budget()
    
    increasing = 0
    decreasing = 0

    for i in range(1, len(remain_expenses)):
        if remain_expenses[i] > remain_expenses[i-1]:
            increasing += 1
        elif remain_expenses[i] < remain_expenses[i-1]:
            decreasing += 1
    
    if increasing > decreasing:
        mb.showinfo("Budget Analysis", "Your remaining monthly budget is increasing, which means you are saving money. ")
    elif increasing < decreasing:
        mb.showinfo("Budget Analysis", "Your remaining monthly budget is decreasing, which means you are spending more money. ")
    else:
        mb.showinfo("Budget Analysis", "Your remaining monthly budget is constant, which means you are spending the same amount of money.")


# Function to view monthly expense report

def monthly_budget_report():
    # Set global variable
    global cursor, connector
    global report_window

    # Select all from User database
    cursor.execute("SELECT * FROM User")
    values = cursor.fetchall()

    # Reverse the values to get the latest monthly budget and check if it is zero, get the next latest monthly budget

    reverse_values = values[::-1]

    for item in reverse_values:
        if item[1] != 0.0:
            monthly_budget = item[1]
            break

    mb.showinfo("Monthly Budget", f"Your monthly budget is {monthly_budget}.")

    report_window.destroy()


# Function to view remain budget

def remain_budget():
    # Set global variable
    global cursor, connector
    global report_window

    # Select all from User database
    cursor.execute("SELECT * FROM User")
    values = cursor.fetchall()

    # Reverse the values to get the latest monthly budget and check if it is zero, get the next latest monthly budget

    reverse_values = values[::-1]

    for item in reverse_values:
        if item[1] != 0.0:
            monthly_budget = item[1]
            break


    current_month = datetime.datetime.now().month
    current_date1 = f'{current_month}/1/23'
    current_date2 = f'{current_month}/9/23'

    cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN ? AND ?", (current_date1, current_date2))
    values = cursor.fetchall()
    print(values)
    monthly_expense = values[0][0]

    remain = monthly_budget - monthly_expense

    mb.showinfo("Daily Budget", f"Your remain daily budget is {remain}.")


# Function to get monthly trend

def monthly_trend():

    global report_window
    
    months = ['Jan', 'Feb', 'Mar', 'Feb', 'May','Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    remain_expenses = remain_monthly_budget()

    # Plot the graph

    plt.figure(figsize=(10, 6))
    plt.bar(months, remain_expenses)

    plt.xlabel('Month')
    plt.ylabel('Remain Expense')
    plt.title('Expense by Month')

    plt.show()
    

def add_budget_to_database():
    # Set global variable
    global cursor, connector
    global budget

    # Check if all entry boxes are filled
    if not budget.get():
        # Show error
        mb.showerror("Error", "Please fill all the entry boxes.")
    else:
        # Insert added data to the database
        cursor.execute("INSERT INTO User VALUES (NULL, ?)", (budget.get(),))
        connector.commit()

        # Show message box to user
        mb.showinfo("Add Budget", "Budget has been added successfully.")
    
    add_budget_root.destroy()


def window_add_budget():
    # Set global variable
    global budget
    global cursor, connector

    # monthly_budget = DoubleVar()
    global add_budget_root

    add_budget_root = Tk()
    add_budget_root.title("Add Budget")
    add_budget_root.geometry("600x500")
    add_budget_root.resizable(False, False)

    frame = Frame(add_budget_root, width=392, height=392, bg="white")
    frame.place(x=100, y=50)

    heading = Label(frame, text="ADD BUDGET", font=("Microsoft YaHei UI Light", 25, "bold"), fg="#57a1f8", bg="white")
    heading.place(x=77, y=60)

    Label(frame, text="Monthly Budget: ", font=("Microsoft YaHei UI Light", 15), fg="black", bg="white").place(x=50, y=140)

    budget = Entry(frame,font=("Microsoft YaHei UI Light", 15), fg="black", bg="white", border=0)
    budget.place(x=50, y=180, width=280, height=35)
    
    Frame(frame, width=295, height=2, bg="black").place(x=50, y=225)

    login_btn = Button(frame, text="ENTER", font=("Microsoft YaHei UI Light", 15, "bold"), fg="white", bg="#57a1f8", border=0, cursor="hand2" , command=add_budget_to_database)
    login_btn.place(x=50, y=295, width=295, height=40)
    login_btn.config(justify=CENTER, anchor=CENTER)

    add_budget_root.mainloop()


# Function of the main expense tracker program window

def expense_tracker_window():
    
    # Set global variable for budget
    global cursor, connector
    global budget
    global button_bg, button_font
    global description, categories, amount, payee, mode_of_payment
    global data_entry_frame
    global date
    global table

    # Initialize expense tracker window
    window = Tk()
    window.title('Expense Tracker')
    window.geometry("1200x650")
    window.resizable(False, False)

    # Set background color and font for the window
    data_frame_bg = "#FF8080"
    button_frame_bg = "#FF8080"
    button_bg = "Grey"
    button_font = ("Gill Sans MT", 13)
    lable_font = ("Georgia", 13)
    entry_font = "Times 13 bold"
    button_bg = "#78BCC4"

    # Set variable for expense tracker program
    description = StringVar()
    categories = StringVar()
    amount = StringVar()
    payee = StringVar()
    mode_of_payment = StringVar()

    # Set heading
    Label(window, text="Expense Tracker Program", font=('Georgia', 15, 'bold'), bg=button_frame_bg).pack(side=TOP, fill=X)

    # Create frame for the expense tracker window
    
    # Data Entry Frame
    data_entry_frame = Frame(window, bg=data_frame_bg)
    data_entry_frame.place(x=0, y=33, relwidth=0.25, relheight= 0.96)

    # Button Frame
    button_frame = Frame(window, bg=button_frame_bg)
    button_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

    # Table Frame
    tree_frame = Frame(window, bg=data_frame_bg)
    tree_frame.place(relx=0.25, rely=0.27, relwidth=0.75, relheight=0.73)

    # Create data entry frame widgets
    
    # Date label and entry
    Label(data_entry_frame, text="Date (MM/DD/YY): ", font=lable_font, bg=data_frame_bg).place(x=10, y=50)
    date = DateEntry(data_entry_frame, width=8, background='darkblue', foreground='white', borderwidth=2, font=entry_font)
    date.place(x=190, y=50)

    # Description label and entry
    Label(data_entry_frame, text="Description: ", font=lable_font, bg=data_frame_bg).place(x=10, y=100)
    Entry(data_entry_frame, textvariable=description, width=28, font=entry_font).place(x=10, y=150)
    

    # Categories label and entry
    Label(data_entry_frame, text="Categories : ", font=lable_font, bg=data_frame_bg).place(x=10, y=200)
    option_categories = OptionMenu(data_entry_frame, categories, "Food", "Transportation", "Entertainment", "Clothing", "Health", "Education", "Others")
    option_categories.config(width=8, font=entry_font)
    option_categories.place(x=163, y=200)

    # Amount label and entry
    Label(data_entry_frame, text="Amount : ", font=lable_font, bg=data_frame_bg).place(x=10, y=250)
    Entry(data_entry_frame, textvariable=amount, width=13, font=entry_font).place(x=160, y=250)

    # Payee label and entry
    Label(data_entry_frame, text="Payee : ", font=lable_font, bg=data_frame_bg).place(x=10, y=300)
    Entry(data_entry_frame, textvariable=payee, width=28, font=entry_font).place(x=10, y=350)

    # Mode of Payment label and entry
    Label(data_entry_frame, text="Mode of Payment : ", font=lable_font, bg=data_frame_bg).place(x=10, y=400)
    option_mode_of_payment = OptionMenu(data_entry_frame, mode_of_payment, "Cash", "Credit Card", "Debit Card", "Mobile Payment", "Online Payment")
    option_mode_of_payment.config(width=6, font=entry_font)
    option_mode_of_payment.place(x=185, y=400)

    # Create Add Expense button
    Button(data_entry_frame, text="Add Expense", bg=button_bg, font=button_font, width=11 , command=add_expense).place(x=20, y=470)
    Button(data_entry_frame, text="Add Budget", bg=button_bg, font=button_font, width=11, command=window_add_budget).place(x=160, y=470)
    Button(data_entry_frame, text="Clear Fields", bg=button_bg, font=button_font, width=25, command=clear_fields).place(x=20, y=540)

    # Create button_frame widgets

    # Create View Expense button
    Button(button_frame, text="View Expense", bg=button_bg, font=button_font, width=25, command=view_expense).place(x=10, y=10)

    # Create Update Expense button
    Button(button_frame, text="Edit Selected Expense", bg=button_bg, font=button_font, width=25, command=edit_expense).place(x=319, y=10)

    # Create Delete Expense button
    Button(button_frame, text="Delete Expense", bg=button_bg, font=button_font, width=25, command=delete_expense).place(x=630, y=10)

    # Create Delete All Expense button
    Button(button_frame, text="Delete All Expense", bg=button_bg, font=button_font, width=25, command=delete_all_expenses).place(x=10, y=70)

    # Create View Graph button
    Button(button_frame, text="View Graph", bg=button_bg, font=button_font, width=25, command=view_graph).place(x=319, y=70)

    # Create View Report button
    Button(button_frame, text="View Report", bg=button_bg, font=button_font, width=25, command=view_report).place(x=630, y=70)

    # Create tree_frame widgets
    table = ttk.Treeview(tree_frame, columns=("ID", "Date", "Description", "Categories", "Amount", "Payee", "Mode of Payment"), selectmode=BROWSE)

    # Scroll Bar
    # x_scroller = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=table.xview)
    # x_scroller.pack(side=BOTTOM, fill=X)
    y_scroller = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=table.yview)
    y_scroller.pack(side=RIGHT, fill=Y)

    # Headings
    table.heading("ID", text="ID", anchor=CENTER)
    table.heading("Date", text="Date", anchor=CENTER)
    table.heading("Description", text="Description", anchor=CENTER)
    table.heading("Categories", text="Categories", anchor=CENTER)
    table.heading("Amount", text="Amount", anchor=CENTER)
    table.heading("Payee", text="Payee", anchor=CENTER)
    table.heading("Mode of Payment", text="Mode of Payment", anchor=CENTER)

    # Column Width
    table.column('#0', width=0, stretch=NO)
    table.column('#1', width=50, stretch=NO)
    table.column('#2', width=95, stretch=NO)  
    table.column('#3', width=150, stretch=NO)  
    table.column('#4', width=150, stretch=NO)  
    table.column('#5', width=130, stretch=NO)  
    table.column('#6', width=120, stretch=NO) 
    table.column('#7', width=150, stretch=NO) 

    table.place(relx=0, y=0, relheight=1, relwidth=1)

    # Get all expenses from the database and list all in the table when expense_tracker_windwo is opened
    list_all_expenses()


    cursor.execute("SELECT * FROM User")
    values = cursor.fetchall()

    # Reverse the values to get the latest monthly budget and check if it is zero, get the next latest monthly budget
    
    reverse_values = values[::-1]

    for item in reverse_values:
        if item[1] != 0.0:
            monthly_budget = item[1]
            break

    current_month = datetime.datetime.now().month
    current_date1 = f'{current_month}/1/23'
    current_date2 = f'{current_month}/9/23'

    cursor.execute("SELECT SUM(Amount) FROM expense_tracker WHERE Date BETWEEN ? AND ?", (current_date1, current_date2))
    values = cursor.fetchall()

    monthly_expense = values[0][0]

    remain = monthly_budget - monthly_expense

    TOKEN = "6882514985:AAFceBMJOi-o_pa-JFR802UaiyBLQsolSUA"
    chat_id = "824421770"


    if remain < monthly_budget * 0.1:
        mb.showinfo("Budget Alert", "Your remaining monthly budget is less than 10% of your monthly budget, please spend your money wisely.")
        message = "Your remaining monthly budget is less than 10% of your monthly budget, please spend your money wisely."
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        print(requests.get(url).json())
        
    elif remain == monthly_budget * 0.1:
        mb.showinfo("Budget Alert", "Your remaining monthly budget is equal to 10% of your monthly budget, please spend your money wisely.")
        message = "Your remaining monthly budget is equal to 10% of your monthly budget, please spend your money wisely."
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        print(requests.get(url).json())

    elif remain <= 0:
        mb.showinfo("Budget Alert", "Your remaining monthly budget is 0, please spend your money wisely.")
        message = "Your remaining monthly budget is 0, please spend your money wisely."
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        print(requests.get(url).json())

    window.mainloop()





