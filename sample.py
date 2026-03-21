import random
from time import sleep

import vk
import datetime


def input_date_to_timestamp(prompt: str) -> int:
    """
    Converts input value to a unix timestamp
    :param prompt: String prompt for user to input date
    :return:  unix timestamp
    """
    sep = ''
    raw_date_input = input(prompt)
    if '.' in raw_date_input:
        sep = '.'
    elif '/' in raw_date_input:
        sep = '/'
    elif '-' in raw_date_input:
        sep = '-'
    elif ' ' in raw_date_input:
        sep = ' '
    else:
        print("Не могу распознать формат даты. Завершение работы с ошибкой")
        exit()
    _day, _month, _year = raw_date_input.split(sep)
    _date = datetime.datetime(int(_year), int(_month), int(_day))
    _timestamp = int(_date.timestamp())
    return _timestamp


def get_liked_posts(raw_posts_list: list) -> list:
    active_list = []
    print("Определяем, за какой период производить отбор.")
    from_ts = input_date_to_timestamp("Введите начальную дату: ")
    till_ts = input_date_to_timestamp("Введите конечную дату: ")
    # This allows to remove all unnecessary data from post dictionary and bind it to a time interval
    for post in raw_posts_list:
        if int(post['likes']['count']) > 0 and from_ts <= post['date'] <= till_ts:
            clear_record = {
                'id': post['id'],
                'likes': post['likes']['count']
            }
            active_list.append(clear_record)
    return active_list


class Selector:

    api = None

    group_name: str = 'club128629560'
    group_id: str = group_name[4:]
    owner_id: str = f'-{group_id}'

    domain: str = 'petr_fevronya_penza'

    members = {}
    members_count = 0

    post_list = []
    members_list = []

    def __init__(self):
        vk_api_token = "f5fb7becf5fb7becf5fb7bece4f589f7fcff5fbf5fb7becab1b8692e9887b40c93c8172"
 
        self.api = vk.API(access_token=vk_api_token)
        print('Программа для определения призёра среди активных участников группы')
        self.members_count = self.count_members()
        self.create_dict_members()
        raw_list = self.walk_by_posts()
        print('Записи со стены получены. Отсеиваем необходимые')
        self.post_list = get_liked_posts(raw_list)  # Remove posts with no likes and comments
        print(f"Готово. Конечный список содержит {len(self.post_list)} записей.")

    # Quantity of all posts on the wall
    def count_wall_posts(self) -> int:
        posts = self.api.wall.get(
            domain=self.domain,
            count=1,
            v=5.107
        )
        return posts['count']

    # Number of all members
    def count_members(self) -> int:
        return int(
            self.api.groups.getMembers(
                group_id=self.group_id,
                count=1,
                v=5.107
            )['count']
        )

    # Get all posts to a raw list
    def walk_by_posts(self) -> list:
        raw_list_post = []
        posts_total = posts_left = self.count_wall_posts()
        offset = 0
        while posts_left > 100:
            raw_list_post += self.api.wall.get(
                domain=self.domain,
                count=100,
                offset=offset,
                lang='ru',
                v=5.107
            )['items']
            offset += 101
            posts_left -= 100
            print(f"Получаем записи со стены группы... Осталось {posts_left} из {posts_total}")
        return raw_list_post

    # Returns a list of users who liked the post with 'post_id'
    def get_members_who_liked(self, post_id):
        members_list = self.api.likes.getList(
            type='post',
            item_id=post_id,
            owner_id=self.owner_id,
            count=1000,
            lang='ru',
            v=5.107
        )
        return members_list['items']

    # Picks all members of a certain group and puts them into a dictionary
    #           {member_id : {name: 'Ivan Ivanov', likes: 0, comments: 0} }
    def create_dict_members(self) -> dict:
        raw_list = []
        counter = self.members_count
        offset = 0
        while counter > 1000:
            iter_list = self.api.groups.getMembers(
                group_id=self.group_id,
                count=1000,
                offset=offset,
                fields='first_name, last_name',
                lang='ru',
                v=5.107
            )
            offset += 1001
            counter -= 1000
            raw_list += iter_list['items']
        else:
            raw_list = self.api.groups.getMembers(
                group_id=self.group_id,
                count=1000,
                fields='first_name, last_name',
                lang='ru',
                v=5.107
            )['items']
        # dictionary
        for group_member in raw_list:
            if group_member.get('deactivated'):
                continue
            self.members[group_member['id']] = {
                'name': f"{group_member['first_name']} {group_member['last_name']}",
                'likes': 0
            }
        print(f'В группе зарегистрировано {self.members_count} участников, из них {len(self.members)} активных')
        return self.members

    # Adds value of likes to a dictionary
    def count_likes(self):
        for post in self.post_list:
            ids_active_members = self.get_members_who_liked(post_id=post['id'])
            sleep(0.2)
            for member_id in ids_active_members:
                _member = self.members.get(member_id)
                if _member is not None:
                    _member['likes'] += 1
        return


if __name__ == '__main__':
    sel = Selector()
    if len(sel.post_list) == 0:
        print('В заданном периоде нет записей')
    else:
        print('Считаем число лайков в выбранных записях. Это может быть долго, смиритесь')
        sel.count_likes()
        dictionary = dict()
        likes_min_value = input('Какое минимальное количество лайков должно быть у претендента? ')
        try:
            likes_min_value = int(likes_min_value)
        except ValueError:
            print('Не могу преобразовать в число. Ставлю значение по умолчанию, 1')
            likes_min_value = 1
        for x in sel.members:
            member = sel.members.get(x)
            if member['likes'] >= likes_min_value:
                dictionary[member['name']] = member['likes']
        print('Почти всё. Выстраиваем участников по порядку')
        for i in sorted(dictionary.items(), key=lambda pair: pair[1], reverse=True):
            sel.members_list.append(i)
        applicants_amount = len(sel.members_list)
        print(f'Претендентов на приз: {applicants_amount}')
        print('Наиболее активные участники за выбранный период: ')
        for i in sel.members_list:
            print(f'{i[0]} ==> {i[1]} лайков')
        print('Бросаем жребий')
        winner = random.choice(sel.members_list)
        print(f"Победитель - {winner[0]} ({winner[1]} лайков). Поздравляем! ")

        accepted = int(input('continue?'))
        tries = 1
        while accepted != 1:
            tries += 1
            winner = random.choice(sel.members_list)
            print(f"Попытка {tries}. Победитель - {winner[0]} ({winner[1]} лайков). Поздравляем! ")
            accepted = int(input('continue?'))

    input('Нажмите ENTER для завершения работы')
