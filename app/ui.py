from datetime import datetime

from models import Member

DATE_FORMATS = [
    "%d.%m.%Y",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d %m %Y"
]

def input_date(prompt: str) -> int:
    while True:
        raw_string = input(prompt).strip()
        for fmt in DATE_FORMATS:
            try:
                parsed_date =  datetime.strptime(raw_string, fmt)
                return int(parsed_date.timestamp())
            except ValueError:
                continue

        print("Wrong date format")

        
def input_min_likes() -> int:
    while True:
        try:
            result = int(input("Введите минимальное число лайков: "))
            if result >= 0:
                return result
            else:
                print("Positive digit is expected")
        except ValueError:
            print("Digit is expected")

def get_date_range() -> tuple[int, int]:
    from_ts = input_date("Начало интервала (ДД.ММ.ГГГГ): ")
    till_ts = input_date("Конец интервала (ДД.ММ.ГГГГ): ")

    if from_ts < till_ts:
        return from_ts, till_ts
    else:
        print("Dates order was changed")
        return till_ts, from_ts

def print_applicants(applicants: list[Member]):
    for applicant in applicants:
        print(str(applicant))

def ask_continue(remaining_count: int) -> bool:
    if remaining_count == 0:
        print("Все кандидаты уже выбраны!")
        return False
        
    prompt = f"Осталось кандидатов: {remaining_count}. Выбрать ещё? (Enter - да, 'n' - выход): "
    choice = input(prompt).strip().lower()
    return choice != 'n'