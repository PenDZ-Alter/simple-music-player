import json

class Queue():
    def __init__(self) -> None:
        self.queue = []
        self.file_path = ".\\Playlist.json"
        
        with open(self.file_path, 'r+') as file:
            self.data = json.load(file)
        
        self.queue = self.data.get("playlist", [])
            
    def is_empty(self):
        return len(self.queue) == 0

    def enqueue(self, title: str, path: str):
        node = {
            "title": title,
            "path": path
        }
        self.queue.append(node)
        self.data["playlist"] = self.queue.copy()
        self._update_json_file()

    def dequeue(self):
        if not self.is_empty():
            dequeued_file = self.queue.pop(0)
            self.data["playlist"] = self.queue.copy()
            self._update_json_file()
            return dequeued_file
        else:
            raise IndexError("The queue is empty!")

    def size(self):
        return len(self.queue)
    
    def get_titles(self):
        titles = [node["title"] for node in self.queue]
        return titles
    
    def _update_json_file(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=2)
    
    def get_queue(self) :
        return self.queue
    
