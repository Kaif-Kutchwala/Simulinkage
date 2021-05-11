from tkinter import messagebox

#Displays error message using tkinter messagebox
def error(mssg, type = 'e'):
    if type == 'e':
        messagebox.showerror(title= 'Error', message= mssg)
    elif type == 'w':
        messagebox.showwarning(title='Warning', message=mssg)