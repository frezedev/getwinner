from datetime import date

from vk_client import VkClient
from models import Post, Member


class ContestAnalyzer:
    member_list: dict[int, Member]
    post_list: list[Post]

    def __init__(self, vk_client: VkClient, from_ts: date, till_ts: date):
        self.vk_client = vk_client
        self.from_ts = from_ts
        self.till_ts = till_ts
        
        self.member_dict = {}
        self.post_list = []

    def collect_data(self):
        members = self.vk_client.get_group_members()
        self.member_dict = {member.id: member for member in members}
        self.post_list = self.vk_client.get_wall_posts(self.from_ts, self.till_ts)


    def count_likes(self):
        for post in self.post_list:
            post_likes_authors = self.vk_client.get_post_likes_authors(post.id)
            for author_id in post_likes_authors:
                if author_id in self.member_dict:
                    self.member_dict[author_id].likes += 1
                

    def get_applicants(self, likes_min: int) -> list[Member]:
        filtered_members = [
            member for member in self.member_dict.values()
            if member.likes >= likes_min
        ]

        filtered_members.sort(key=lambda m: m.likes, reverse=True)
        return filtered_members


        

    
