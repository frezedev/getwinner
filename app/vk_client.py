import vk

from config import Config
from models import Post, Member
from time import sleep

class VkClientError(Exception):
    pass


class VkClient:
    POST_BATCH_SIZE = 100
    MEMBER_BATCH_SIZE = 1000
    LIKES_BATCH_SIZE = 1000
    MAX_RETRIES = 5
    API_VERSION = "5.107"
    TOO_MANY_REQUESTS_CODE = 6


    def __init__(self, config: Config):
        self.config = config
        self.api = vk.API(access_token=config.vk_api_token, v=self.API_VERSION, lang="ru")

    def _safe_call(self, method, **kwargs):
        for attempt in range(self.MAX_RETRIES):
            try:
                return method(**kwargs)
            except vk.exceptions.VkAPIError as e:
                if e.code == self.TOO_MANY_REQUESTS_CODE:
                    wait_time = 2** attempt + 1
                    sleep(wait_time)
                else:
                    raise VkClientError(f"VK API error: {e.message}")
            except Exception as e:
                raise VkClientError(f"Unknown error: {e}")
        raise VkClientError("Attempts number exceeded")


    def get_wall_posts(self, from_ts: int, till_ts:int) -> list[Post]:
        posts = []
        offset = 0

        while True:
            response = self._safe_call(
                self.api.wall.get,
                domain=self.config.domain,
                count=self.POST_BATCH_SIZE,
                offset=offset
            )

            items = response.get("items", [])
            if not items:
                break

            for item in items:
                post = Post(
                    id=item["id"],
                    post_date=item["date"],
                    likes_count=item["likes"]["count"]
                )

                if post.post_date < from_ts:
                    return posts

                if from_ts <= post.post_date <= till_ts:
                    posts.append(post)

            if len(items) < self.POST_BATCH_SIZE:
                break

            offset += self.POST_BATCH_SIZE

        return posts


    def get_group_members(self) -> list[Member]:
        members = []

        info = self._safe_call(
            self.api.groups.getMembers,
            group_id=self.config.group_id,
            count=1,
            v=self.API_VERSION
        )
        total_count = info["count"]

        offset = 0
        while offset < total_count:
            response = self._safe_call(
                self.api.groups.getMembers,
                group_id=self.config.group_id,
                count=self.MEMBER_BATCH_SIZE,
                offset=offset,
                fields="first_name,last_name"
            )


            items = response.get("items", [])
            for item in items:
                if item.get("deactivated"):
                    continue

                members.append(
                    Member(
                        id=item["id"],
                        name=f"{item['first_name']} {item['last_name']}",
                        likes=0
                    )
                )
            offset += len(items)
        
        return members



    def get_post_likes_authors(self, post_id: int) -> list[int]:
        user_ids = []
        offset = 0

        while True:
            response = self._safe_call(
                self.api.likes.getList,
                type="post",
                owner_id=self.config.owner_id,
                item_id=post_id,
                count=self.LIKES_BATCH_SIZE,
                offset=offset
            )

            items = response.get("items", [])
            user_ids.extend(items)

            if len(items) < self.LIKES_BATCH_SIZE:
                break

            offset += len(items)

        return user_ids


    