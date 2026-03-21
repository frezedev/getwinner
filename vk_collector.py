import os
from time import sleep
from datetime import datetime
from typing import Any

from vk import API
from dotenv import load_dotenv

load_dotenv()

V = 5.107


class VKCollector:
    vk: API
    token: str
    domain: str
    group_name: str

    def __init__(self) -> None:
        env_variables = ("token", "domain", "group_name")
        for v in env_variables:
            if value := os.getenv(v.upper()):
                setattr(self, v, value)
            else:
                err_message = f"Required value {v} wasn't found in .env"
                raise Exception(err_message)
        self.group_id = self.group_name[4:]
        self.vk = API(access_token=self.token)
        self.get_group_info()
        self.likes_dict = {}

    
    def select_posts(self, date_from: datetime, date_till:datetime) -> dict[int, Any]:
        """
        Get wall posts within certain date range.
        Result format {post_uid : {"is_repost": bool, "date": date}}
        """
        limit = 100 
        offset = 0
        left = self.wall_posts_count()
        result = {}
        flag_out_of_range = False

        while left >= 0:
            if flag_out_of_range:
                break
            sleep(0.33)
            request = self.vk.wall.get(            
                domain=self.domain,
                owner=f"-{self.group_id}",
                offset=offset,
                count=limit,
                filter="owner",
                v=V
            )
       
            for item in request["items"]:
                post_date = datetime.fromtimestamp(item["date"])
                data = {
                    item["id"]:{ 
                        "is_repost": bool(item.get("copy_history")),
                        "date": post_date
                    }
                }
                if post_date >= date_from and post_date <= date_till:
                    result.update(data)
                    
                elif post_date < date_from: 
                    flag_out_of_range = True
                    break
                else:
                    # post_date > date_till
                    ...
                
            left -= limit
            offset += limit
        return result

    def wall_posts_count(self) -> int:
        """
        Returns total number of posts
        """
        posts = self.vk.wall.get(
            domain=self.domain,
            owner=f"-{self.group_id}",
            count=1,
            filter="owner",
            v=V
        )
        return (posts['count'])

    def get_members(self) -> dict[str, Any]:
        left = self.members_count
        limit = 100
        offset = 0
        result = {}
        while left >= 0:
            sleep(0.33)
            item_list =self.vk.groups.getMembers(
                v=V,
                group_id=self.group_id,
                offset=offset,
                count=limit,
                lang="ru",
                fields="first_name, last_name, city"
            )["items"]

            for r in item_list:
                if ((city:= r.get("city")) and city == self.city) and (r["first_name"] != "DELETED"):
                    result.update(
                        {r["id"]: f'{r["first_name"]} {r["last_name"]}'}
                    )
            left -= limit
            offset += limit
        return result

    def get_members_liked(self, post_uid: int, members: dict[int, Any]):
        sleep(0.33)
        members_list = self.vk.likes.getList(
            type='post',
            item_id=post_uid,
            owner_id=f"-{self.group_id}",
            count=1000,
            lang='ru',
            v=V
        )
        for item in [r for r in  members_list['items'] if r in members]:
            if item in self.likes_dict:
                self.likes_dict[item]["like"] += 1
            else:
                self.likes_dict[item] = {"name": members[item], "like": 1}

    def get_group_info(self):
        """
        Method collects general information about group 
        such as name, city, number of members, description and age limits.

        """
        request_fields = (
            "city", 
            "members_count",
            "description",
            "age_limits"
        )

        response = self.vk.groups.getById(
            group_id=self.group_id, fields=request_fields, v=V
        )

        if len(response) == 1:
            response = response[0]
        
        self.public_name = response["name"]
        self.public_description = response["description"]
        self.members_count = response["members_count"]
        self.city = response["city"]
        self.age_limits = response["age_limits"] # 1 - no_limits 2 - 16+ 3 - 18+
        
