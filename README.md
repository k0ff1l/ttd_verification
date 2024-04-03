# Что это такое?

Этот бот помогает синхронизировать пользователей Discord с Telegram-каналом. Он позволяет автоматически предоставлять доступ к ролям Discord на основе членства в Telegram-канале.

# Преимущества:

Простота использования: Простая и понятная система верификации.
Автоматизация: Автоматическое предоставление ролей Discord.
Безопасность: Дополнительный уровень безопасности для вашего Discord-сервера.

# Как начать?

1. Установите бота: [приглашение](https://discord.com/oauth2/authorize?client_id=1224382018624684062&permissions=8&scope=bot)
2. Настройте бота в cfg.py:
  Укажите ID Telegram-канала, где должен состоять пользователь (можно получить из web версии телеграмма).
  Укажите токены бота в телеграмме и дискорде.
  Укажите выдаваемую роль.

4. Сообщите пользователям:
  Объявите о боте в Discord-сервере.
  Объясните, как пользоваться ботом.

# Что нужно сделать пользователям?
1. Состоять в соотвествующей беседе в телеграмме.
2. Перейти в [бота](https://t.me/verif_test_bot), нажать кнопку start и следовать инструкции.
# Дополнительная информация:

Команды:

/send {user's id in telegram} - Запустить процесс верификации.

/verify {*****} - Отправить код верификации.
