class ProgressTracker:
    def __init__(self):
        self.progress = 0

    def update_progress(self, increment):
        self.progress += increment
        if self.progress > 100:
            self.progress = 100
        print(f"Progress: {self.progress}%")

    def reset_progress(self):
        self.progress = 0
        print("Progress Reset")
