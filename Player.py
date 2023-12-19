import pygame
import threading
import tkinter as tk
import os

from QueueNode import Queue
from tkinter import filedialog, ttk, Label
from typing import Callable

class MusicPlayer:
    def __init__(self, root, bgcolor):
        self.playlist = Queue()
        self.is_playing = False
        self.is_paused = False
        self.stop_requested = False
        self.next_requested = False
        self.paused_position = 0
        
        self.play_lock = threading.Lock()
        
        self.play_music_thread: Callable[[str], None] = self.default_play_music_thread
        self.bgcolor = bgcolor
    
        self.root = root
        self.root.title("Music Player")
        self.root.configure(bg=self.bgcolor)
        self.root.geometry("720x500")
    
    def load_elements(self) :
        # Color Settings
        button_color = "#4CAF50"
        playlist_bgcolor = "#f0f0f0"

        # Elements Config
        self.playing_label = Label(self.root, text="Playing : ", bg=self.bgcolor)
        self.playing_label.place(x=0, y=0)
        
        self.playback_title = Label(self.root, text="", bg=self.bgcolor)
        self.playback_title.place(x=50, y=1)
        
        self.length_info = Label(self.root, text="Length : ", bg=self.bgcolor)
        self.length_info.place(x=254, y=128)
        
        self.duration_info = Label(self.root, text="", bg=self.bgcolor)
        self.duration_info.place(x=302, y=128)
        
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=200)
        self.progress_bar.place(x=255, y=150)
        
        self.add_button = tk.Button(self.root, text="Browse", command=self.add_song, bg=button_color)
        self.add_button.place(x=218, y=268)

        self.play_button = tk.Button(self.root, text="Play", command=self.play_selected_song, bg=button_color)
        self.play_button.place(x=267, y=200)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_music, bg=button_color)
        self.pause_button.place(x=314, y=200)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_music, bg=button_color)
        self.stop_button.place(x=364, y=200)

        self.next_button = tk.Button(self.root, text="Next", command=self.play_next_song, bg=button_color)
        self.next_button.place(x=410, y=200)
        
        self.queue_label = Label(self.root, text="List of the Song : ", bg=self.bgcolor)
        self.queue_label.place(x=118, y=269)
        
        self.playlist_box = tk.Listbox(self.root, width=80, height=10, bg=playlist_bgcolor)
        self.playlist_box.place(x=118, y=300)

    # Defining Function
    def add_song(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        if file_path:
            title_path = file_path.split("/")[-1]   # Removing Path from String
            title = os.path.splitext(title_path)[0] # Removing Extensions from String
            self.playlist.enqueue(title, file_path)
            self.update_playlist()

    def update_playlist(self):
        self.playlist_box.delete(0, tk.END)
        for title in self.playlist.get_titles():
            self.playlist_box.insert(tk.END, title)

    def play_selected_song(self):
        selected_index = self.playlist_box.curselection()
        if selected_index:
            self.play_music(selected_index[0])

    def play_music(self, index):
        if 0 <= index < self.playlist.size():
            selected_song = self.playlist.dequeue()
            title = selected_song["title"]
            print(f"Playing: {title}")
            self.play_button.config(text="Playing", state=tk.DISABLED)
            self.playback_title.config(text=title)
            
            # Recalling Function while it busy
            self.play_music_thread = lambda file_path=selected_song["path"]: self.default_play_music_thread(file_path)
            threading.Thread(target=self.play_music_thread).start()
            self.update_playlist()
        elif not self.playlist_is_empty() and not self.is_playing:
            self.is_playing = True
            self.play_next_song()
            self.is_playing = False

    def default_play_music_thread(self, file_path: str) -> None:
        pygame.mixer.init()

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

        sound = pygame.mixer.Sound(file_path)
        pygame.mixer.music.load(file_path)
        
        # Set an event to be triggered when the music playback completes
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        
        pygame.mixer.music.play()
        self.is_playing = True
        
        self.total_time = sound.get_length()
        formatted_time = self.format_duration(self.total_time)
        self.duration_info.config(text=formatted_time)

        while pygame.mixer.music.get_busy() and not self.stop_requested:            
            current_time = pygame.mixer.music.get_pos() / 1000
            self.update_progress_bar(current_time, self.total_time)
            pygame.time.Clock().tick(10)         

        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_button.config(text="Play", state=tk.NORMAL)

    def resume_music_thread(self):
        pygame.mixer.music.play(start=self.paused_position)
        
        while pygame.mixer.music.get_busy() and not self.stop_requested : 
            current_time = pygame.mixer.music.get_pos() / 1000
            self.update_progress_bar(current_time, self.total_time)
            pygame.time.Clock().tick(10)    

    def stop_music(self):
        self.stop_requested = True
        pygame.mixer.music.stop()
        self.playback_title.config(text="")
        self.duration_info.config(text="")
        self.stop_requested = False

    def pause_music(self):
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.paused_position = pygame.mixer.music.get_pos() / 1000
        else : 
            self.is_paused = False
            self.is_playing = True
            threading.Thread(target=self.resume_music_thread).start()

    def play_next_song(self):
        self.next_requested = True

        if not self.playlist_is_empty():
            next_song = self.playlist.dequeue()
            title = next_song["title"]
            print(f"Playing next: {title}")
            self.play_button.config(text="Playing", state=tk.DISABLED)
            self.playback_title.config(text=title)
            
            # Recalling Function while it busy
            self.play_music_thread = lambda file_path=next_song["path"]: self.default_play_music_thread(file_path)
            threading.Thread(target=self.play_music_thread).start()
            self.update_playlist()
        else:
            print("Playlist is empty. Cannot play next song.")
        
        self.next_requested = False

    def playlist_is_empty(self):
        return not self.playlist
    
    def update_progress_bar(self, current_time, total_time):
        progress_percentage = (current_time / total_time) * 100
        self.progress_bar['value'] = progress_percentage
        self.root.update()
    
    def format_duration(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02d}:{int(seconds):02d}"


# Note! To make the Callable function, use threading and Callable (From typing library)
# ex. : 
# in init :
# self.play_music_thread: Callable[[str], None] = self.default_play_music_thread
# in exec : 
# self.play_music_thread = lambda file_path=next_song["path"]: self.default_play_music_thread(file_path)
# threading.Thread(target=self.play_music_thread).start()