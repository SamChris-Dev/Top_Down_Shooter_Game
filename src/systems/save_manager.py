import json
import os

class SaveManager:
    def __init__(self, filename="save.json"):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.filepath = os.path.join(self.base_dir, filename)
        self.data = {
            "high_score": 0,
            "best_wave": 1,
            "kills": 0,
            "volume_master": 1.0,
            "volume_music": 0.5,
            "volume_sfx": 0.8
        }
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
            except Exception as e:
                print(f"Failed to load save file: {e}")

    def save(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Failed to save file: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def update(self, key, value):
        self.data[key] = value
        self.save()

save_manager = SaveManager()
