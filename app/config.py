import os
from dataclasses import dataclass, field
from dotenv import load_dotenv


CLUB_PREFIX = "club"


def get_value(attribute: str) -> str:
    value = os.getenv(attribute)
    if value:
        return value
    else:
        raise EnvironmentError(f"Variable `{attribute}` not found")

@dataclass
class Config:
    group_name: str
    domain: str 
    vk_api_token: str 
    group_id: str = field(init=False)
    owner_id: str = field(init=False)
   
    def __post_init__(self):

        if self.group_name.startswith(CLUB_PREFIX):
            self.group_id = self.group_name[len(CLUB_PREFIX):]
        else:
            raise EnvironmentError("Unexpected group_id format")
        self.owner_id = f'-{self.group_id}'


def load_config() -> Config:
    load_dotenv()
    group_name: str = get_value("GROUP_NAME")    # 'club128629560'
    domain: str = get_value("DOMAIN")
    vk_api_token: str = get_value("TOKEN") 
    return Config(group_name, domain, vk_api_token)
