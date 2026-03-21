# get all posts 
# get all users and filter deleted. Get users from city
# fetch data from posts

from datetime import datetime

from vk_collector import VKCollector

if __name__ == '__main__':
    a = VKCollector()
    likes_dict = {}
    str_date_from =  "01.07.2024"  # input("Введите дату начала интервала: ")
    str_date_till = "08.08.2024" # input("Введите дату конца интервала: ")
    date_from = datetime.strptime(str_date_from, "%d.%m.%Y")
    date_till = datetime.strptime(str_date_till, "%d.%m.%Y")
    print('Выбираем релевантные посты')
    posts = a.select_posts(date_from, date_till)
    print('Составляем список членов группы')
    members = a.get_members()
    print('Считаем лайки постов')
    for p in posts:
        (a.get_members_liked(p, members))    
    # print(a.likes_dict)
    
    limited_likes = {}

    likes_limit = 5
    print('Фильтруем по лимиту лайков =', likes_limit)
    for x in a.likes_dict:
        if a.likes_dict[x]["like"] >= likes_limit:
            limited_likes[a.likes_dict[x]["name"]] = a.likes_dict[x]["like"]

    print("Список претендентов ",limited_likes)