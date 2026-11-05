import sys
from config import load_config
from vk_client import VkClient
from analyzer import ContestAnalyzer
from raffle import Raffle
from ui import get_date_range, input_min_likes, print_applicants, ask_continue

def main():
    print("🚀 Запуск программы определения победителя конкурса VK")
    
    try:
        config = load_config()
        
        from_ts, till_ts = get_date_range()
        min_likes = input_min_likes()
        
        client = VkClient(config)
        analyzer = ContestAnalyzer(client, from_ts, till_ts)
        
        print("\nСбор данных из группы...")
        analyzer.collect_data()
        analyzer.count_likes()
        
        applicants = analyzer.get_applicants(min_likes)
        print_applicants(applicants)
        
        if not applicants:
            print("❌ Нет участников, соответствующих условиям. Завершение работы.")
            return

        # 6. Жеребьёвка
        print("\n" + "="*30)
        print("🎲 НАЧАЛО ЖЕРЕБЬЁВКИ")
        print("="*30)
        
        raffle = Raffle(applicants)
        winners = []
        
        while True:
            winner = raffle.next_winner()
            if winner is None:
                print("Все кандидаты были выбраны!")
                break
                
            winners.append(winner)
            print(f"🎉 Победитель #{len(winners)}: {winner}")
            
            if not ask_continue(raffle.remaining()):
                break
                
        if winners:
            print("\nИТОГОВЫЙ ПРОТОКОЛ:")
            for i, w in enumerate(winners, 1):
                print(f"{i}. {w.name} (ID: {w.id}, Лайков: {w.likes})")
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Работа прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
