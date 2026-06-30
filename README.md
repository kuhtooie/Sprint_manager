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
The button Make employee schedule pulls up a false window, the first is to be entered gibberish and then the second window
it pulls up; asking for a "key" is to be exited, the third and fourth window are to be used. Working on fixing the bug. The save function is still not working
if __name__ == "__main__":

    root = tk.Tk()
    a = Administrator(root)
    # Start the main event loop
    root.mainloop()
