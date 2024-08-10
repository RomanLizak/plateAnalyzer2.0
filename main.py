from notepad import NotepadApp
from tkinterdnd2 import DND_FILES, TkinterDnD

if __name__ == "__main__":
    
    root = TkinterDnD.Tk()
    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set the window size to match the screen size
    root.geometry(f"{int(screen_width * 0.8)}x{int(screen_height * 0.8)}")
    #
    # Maximize the window
    root.state('zoomed')
    notepad = NotepadApp(root)
    root.mainloop()