With GUI
####
Start schedule

'if __name__ == "__main__"':
#four spaces after __main__


    root = tk.Tk()
    file = ""
    name = ""
    app = DictionaryClassifierGUI(root)
    app.get_data()
    #file is the parent folder holding the file_name
    app.next_key()
    app.save(file,name)
    root.mainloop()

    app.process_data(7)

    
update schedule

'if __name__ == "__main__"':
#four spaces after __main__

    
    root = tk.Tk()
    file = ""
    name = ""
    app = DictionaryClassifierGUI(root)
    #file is the parent folder holding the file_name
    #period = amount of days left in schedule
    app.update(file,name,period)
    root.mainloop()

###


With Administrator
You need to copy paste all of GUI file "DictionaryClassifierGUI" into the console.
The button Make employee schedule sometimes pulls up two windows, the first is to be deleted, the second is to be used.
if __name__ == "__main__":

    root = tk.Tk()
    a = Administrator(root)
    # Start the main event loop
    root.mainloop()
