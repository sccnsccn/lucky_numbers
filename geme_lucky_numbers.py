from game import Game
import random

class Game_laky_numbers(Game):
    max_score = 10
    def __init__(self):
        self.new_game()
               
    def add_answer_player(self, answer):
        self.player_answer = answer#сохраняем ответ пользователя
        
    def get_score(self):
        return self.score #возвращаем текущий игровой счет
        
    def get_answer(self):
        return self.lucky_num#возвращаем правильный ответ ввиде строки
    
    def check(self):
        if self.lucky_num != self.player_answer:
            self.score-=1
            amendment = "{} = ".format(self.player_answer) 
            for i in range(4):
                if self.lucky_num[i] == self.player_answer[i]:
                    amendment += 'В'
                elif self.player_answer[i] in self.lucky_num:
                    amendment += 'K'
                else:
                    amendment += self.player_answer[i]
            return False, amendment
        else:
              return True, "Угадал"
        
    
    def restart(self):
        self.score = self.max_score#делаем вид что ничего небыло и даем пользователю возможность играть дальше с обновленным счетом

    def new_game(self):
        #генерируем новое число и обновляем счет
        num = random.randint(0,9999)#генерируем случайное число из четырех цифр
        self.lucky_num = '{:0>4}'.format(num)#переводим его в строку из четырех символов
        self.score = self.max_score#за каждую неудачную попытку будем списывать по одному балу
