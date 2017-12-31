from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, Handler
from telegram.ext.dispatcher import run_async
from telegram.ext import messagequeue as mq
from geme_lucky_numbers import Game_laky_numbers as Gln
import telegram.bot

TOKEN = ''

#состояния диалога
CHOOSING = 0 #выбор игры и ее запуск
LUCKY_NUM = 1 #игра в LUCKY_NUM
    
#класс бота поддерживающего очердь сообщений
class MQBot(telegram.bot.Bot):
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass
        super(MQBot, self).__del__()

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        super(MQBot, self).send_message(*args, **kwargs)

#Похорошему надо использовать Webhooks, но мне показалось это не очень удобным
#в моем случае

#ключи используемые для хранения данных в user_data
KEY_GAME = "game"
KEY_STATE = "state"

#доступные команды для запуска игр
games_key_luckynum = "luckynum"
#доступыне игры и их описание
GAMES = [
    [games_key_luckynum, "lucky numbers","угадай четырех значное число\n"],
    ]
#ключи для коанд бота
commands_key_start = "start"
commands_key_games = "games"
commands_key_stop = "stop"
commands_key_restart = "restart"
commands_key_new = "new"
commands_key_help = "help"
#список доступных команд бота
COMMANDS =[
    [commands_key_games, "список доступных игр"],
    [commands_key_stop, "завершить игру (доступна только в игре)"],
    [commands_key_restart, "начать игру занаво cо старым заданием (доступна только в игре)"],
    [commands_key_new, "начать игру занаво c новым заданием (доступна только в игре)"],
    [commands_key_help, "список доступных команд"],
    ]
#формируем сообщения которые будет использоваться ботом постоянно
#сообщение выводимое при старте диалога
msg_text_start = "Я бот поиграй со мной\nКоманды:\n"
#Список доступных команд
msg_text_help = "Доступные команды:\n"

temp_list = "\n".join(list(map(lambda com :"/{} - {}".format(com[0], com[1]), COMMANDS)))

msg_text_start += temp_list
msg_text_help  += temp_list
    
#сообщение выводимое при вызове команды /games
msg_text_games = "Доступные игры:\n"

temp_list = "\n".join(list(map(lambda com :"{}(/{}) - {}".format(com[1], com[0], com[2]), GAMES)))

msg_text_games += temp_list              
#правила игры в lucky_num
msg_text_manual_lucky_num = "Я загадал четырехзначное число.\nУгадай его.\nВведи число.\nЕсли цифра стоит на правильном месте, я заменю ее на В.\nЕсли цифра стоит не на своем месте, но есть в загаданом числе, то я заменю ее на К.\nЕсли цифры нет в числе, то я оставлю ее без изменеий."
#сообщение об ошибке (Паническое)
msg_text_panic = "A!А!А! Что-то пошло не так!\n"
#сообщение о том, что юзер не запустил игру
msg_text_no_game = "Ты не начал игру! Набери /games чтобы увидеть полный список игр"
#сообщение о перезапуске игры с преждним заданием
msg_text_restart = "Ок! Начнем все сначало. Ничего не было"
#сообщение об окончание игры по желанию пользователя
msg_text_stop = "Ок! Заканчиваем. Если что ты знаешь, что делать. Просто набери /games"
#сообщение о перезапуске игры с новым заднием
msg_text_new_game = "Новое задание"
#сообщение о том что пришло что-то непонятное
msg_text_understand = "Я не знаю, что на это ответить."

#приветственное сообщение бота
@run_async
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text_start)
    return CHOOSING#переводим диалог в состояние выбоа игры

@run_async
def bot_help(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text_help)
    
#сообщаем список доступных игр
@run_async
def games(bot, update, user_data):
    ret = CHOOSING#переводим диалог в состояние выбоа игры
    #если игра уже не идет
    #если иде даем возможность продлжть игру
    if KEY_GAME in user_data and KEY_STATE in user_data:
        ret = user_data[KEY_STATE]
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text_games)
    return ret

#запускаем игру LUCKY_NUM
@run_async
def lucky_num_start(bot, update, user_data):
    #сообщаем здесь правила игры
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text_manual_lucky_num)
    #создаем экземпляр игры и сохраняем его в уникальном для юзера словоре
    user_data[KEY_GAME] = Gln()
    #вкакое состояние возвращать вслучае перезапуска игры
    user_data[KEY_STATE] = LUCKY_NUM
    return LUCKY_NUM#переводим диалог в состояние игры

@run_async
def lucky_num(bot, update, user_data):
    #обрабатываем ответы пользователя
    msg_text = msg_text_no_game
    ret = ConversationHandler.END
    if KEY_GAME in user_data and KEY_STATE in user_data:
        t_game = user_data[KEY_GAME]
        #берем текст из сообщения и передаем его в игру
        t_game.add_answer_player(update.message.text)
        win, amendment = t_game.check()
        if win:
            del user_data[KEY_GAME]
            del user_data[KEY_STATE]
            msg_text = "Ты победил!\nТвой игровой счет: {}".format(t_game.get_score());
        else:
            msg_text = amendment
            #рано завершать диалог поэтому
            #копируем состояние в которое надо перейти
            ret = user_data[KEY_STATE]

    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text)
    return ret

@run_async
def restart(bot, update, user_data):
    #перезапускаем игру со старым заданием
    msg_text = msg_text_no_game
    ret = ConversationHandler.END
    
    if KEY_GAME in user_data and KEY_STATE in user_data:
        t_game = user_data[KEY_GAME]
        t_game.restart()
        ret = user_data[KEY_STATE]
        msg_text=msg_text_restart
        
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text)
    return ret#выходим из диалога

@run_async
def stop(bot, update, user_data):
    #останавливаем игру и выходим из диалога
    msg_text = msg_text_no_game
    if KEY_GAME in user_data and KEY_STATE in user_data:
        del user_data[KEY_GAME]
        del user_data[KEY_STATE]
        msg_text = msg_text_stop
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text)
    return ConversationHandler.END#выходим из диалога

@run_async
def new_game(bot, update, user_data):
    msg_text = msg_text_no_game
    ret = ConversationHandler.END
    
    if KEY_GAME in user_data and KEY_STATE in user_data:
        t_game = user_data[KEY_GAME]
        t_game.new_game()
        ret = user_data[KEY_STATE]
        msg_text = msg_text_new_game
        
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text)
    return ret#выходим из диалога

@run_async
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text_understand)
@run_async
def error(bot, update, error):
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg_text_panic)
def start_bot(burst_limit=10, time_limit=1000, count_workers=32):
    #устанавливаем лимит отправки сообщений в секунду
    #нельзя более 30 сообщений всекунду
    #проверка происходит настороне сервера
    #поэтому стоит отправлять меньше чем можно
    #при плохом соединение возможна большая задержка
    #10 сообщений в секунду, чтобы был терх кратный запас
    q = mq.MessageQueue(all_burst_limit=burst_limit, all_time_limit_ms=time_limit)

    bot_mq = MQBot(TOKEN, mqueue=q)#бот с очередью
    
    updater = Updater(bot = bot_mq, workers = count_workers)#передаем бот и количество которых можно одновременно обслуживать

    dp = updater.dispatcher
    #ConversationHandler позволяет создать диалог с конкретным пользователем
    #гарантирует что сообщения от одного пользователя будут обрабатываться в порядке
    #поступления
    #сообщения разных пользователей будут обрабатываться асинхронно

    handler_start = CommandHandler(commands_key_start, start)
    
    handler_help = CommandHandler(commands_key_help, bot_help)
    
    handler_games = CommandHandler(commands_key_games, games,
                                   pass_user_data=True)
    
    handler_luckynum_start = CommandHandler(games_key_luckynum,
                                    lucky_num_start, pass_user_data=True)
    
    handler_luckynum_play = RegexHandler('^[0-9][0-9][0-9][0-9]$',
                                           lucky_num,
                                           pass_user_data=True)
    
    handler_stop = CommandHandler(commands_key_stop, stop, pass_user_data=True)

    handler_restart = CommandHandler(commands_key_restart, restart, pass_user_data=True)

    handler_new = CommandHandler(commands_key_new, new_game, pass_user_data=True)

    handler_unknown_msg = MessageHandler(Filters.all, unknown)
    
    
    conv_handler = ConversationHandler(
        #точка входа в диалог
        entry_points=[handler_start,
                      handler_games,
                      handler_luckynum_start,
                      ],
        #возможные состояния диалога
        states={
            #пользователь выбирает в какую игру сыграть
            CHOOSING: [handler_luckynum_start,
                       ],
            #обрабытываем сообшения подьзователя состоящие из 4 цифр
            #если пльзователь выбрал игру luckynum
            LUCKY_NUM: [handler_luckynum_play,
                                     ],
            },
        #обрабатываем команды неизвестные и не понятные
        fallbacks=[handler_games,
                   handler_luckynum_start,
                   handler_stop,
                   handler_restart,
                   handler_new,
                   ]
        )

    #dp.add_handler(handler_help)
    #dp.add_handler(handler_games)
    #dp.add_handler(handler_luckynum_start)
    #dp.add_handler(handler_luckynum_play)
    #dp.add_handler(handler_stop)
    #dp.add_handler(handler_restart)
    #dp.add_handler(handler_new)
    #dp.add_handler(handler_unknown_msg)
    
    dp.add_handler(conv_handler)
    dp.add_handler(handler_help)
    dp.add_handler(handler_unknown_msg)
    dp.add_error_handler(error)

    updater.start_polling()
    print("Бот запущен для остановки (ctrl+break)")
    updater.idle()       
    
if __name__ == '__main__':
    start_bot();
