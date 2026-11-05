from dataclasses import dataclass
from datetime import date

@dataclass
class Member:
    id: str
    name: str
    likes: int 

    def __str__(self):
        return f"{self.name} ({self.likes} likes)"


@dataclass
class Post:
    id: str
    post_date: date
    likes_count: int 

    def __str__(self):
        return f"{self.id} at {self.post_date} ({self.likes_count} likes)"

