# ТГ бот, с функцией парсинга сайта [OLX.UA](https://www.olx.ua)

Поиск обьявлений о сдаче квартир в г. Киев (по районам) за последние 14 дней, с последующим мониторингом каждые 15 минут.

1. После запуска бота выбираем район.
2. Далее вводим цену в грн ОТ и ДО (например, 10000-20000).
3. Бот проверяет каждое обьявление по заданному фильтру. Новые обьявления отправляет в чат, повторы пропускает. После вывода всех текущих обьявлений бот будет мониторить новые обьявления каждые 15 минут.
4. Для перезапуска бота и выбора нового района нужно ввести команду /start
