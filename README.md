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
The button Make employee pulls up two different windows that asks for a number each time. The first one is to make the schedule and is what will be saved to every
file. The second asks for the the employees names and will then prompt a window for each name after each has been entered and will ask for the action progress of each name in order provided.
if __name__ == "__main__":

    root = tk.Tk()
    a = Administrator(root)
    # Start the main event loop
    root.mainloop()
