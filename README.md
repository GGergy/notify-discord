# Discord-версия бота
## Бот будет доступен [здесь](https://discord.com/developers/applications/1072969774285471814/information)
## Бот умеет искать музыку в яндекс.музыке и ютубе, создавать и воспроизводить очереди, чтобы узнать больше - пишите .commands

## Структура проекта

    ├─ source/                      Исходный код приложения
    │  ├─ discord_bot/              Файлы бота
    |  |  ├─ assets/                Материалы для бота
    |  |  |  ├─ bin/                Папка с ffmpeg.exe
    |  |  |  ├─ secure/             Данные, хранщиеся только на сервере
    |  |  ├─ utils/                 Функции для бота Telegram
    |  |  |  ├─ config.py           Работа с данными из assets/secure/config.json
    |  |  |  ├─ connect_creater.py  Создание соединения с базой данных
    |  |  |  ├─ music_api.py        Работа с api Яндекс.Музыки
    |  |  |  ├─ yt_api.py           Работа с api YouTube
    |  |  |  ├─ sqlast_hope.py      Работа с базой данных
    |  |  |  ├─ server.py           Модель сервера в базе данных
    └─ ds.py                        Main файл
