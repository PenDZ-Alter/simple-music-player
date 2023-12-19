from Player import MusicPlayer
import tkinter as tk

if __name__ == '__main__':
    bgcolor = "orange"
    
    root = tk.Tk()
    music_player = MusicPlayer(root, bgcolor)
    music_player.load_elements()
    music_player.update_playlist()
    root.mainloop()