# transfer_system
Тестовое задание


# Авторизация
POST /login
application/json
{'email': 'email@mail.ma', 'password': password}
## response
Успешно - вернёт 200 и Cookie используется как сессионный для остальных операций. Разумеется, протухающий :)
Иначе - 403

# Создание участника
POST /participant
application/json
{'email: 'email@mail.new', 'password': 'пароль'}
## response:
Успешно - 200
Иначе - 400 и ошибку

# Получение операций участника
POST /transactions
application/json
{['date1' : 'ГГГГ-ММ-ДД[ ЧЧ:ММ:СС]][, 'date2' : 'ГГГГ-ММ-ДД[ ЧЧ:ММ:СС],]}
если параметры не заданы - выводится всё за текущий месяц
## response
Успешно - 200 и список операций
Иначе - 400 и ошибку


# Проведение платежа
POST /transaction
application/json
{'amount': 1000[.00[00]], 'payee': 'email получателя (существующий в системе'[, 'description': 'Описание платежа']}
## response
Успешно - 200
Иначе - 400 и ошибку 

===
Странное требование на счёт подтягивания данных по котировкам, учитывая, что оные обновляются раз в сутки...
