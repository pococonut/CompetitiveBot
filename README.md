
# CompetitiveBot

## Описание проекта

CompetitiveBot - это телеграм бот, предоставляющий возможности соревновательной системы по программированию на основе сервиса DOMjudge. CompetitiveBot предоставляет список доступных задач по программированию трех уровней сложности. Решения принимаются на нескольких доступных языках, благодаря чему, вы можете проверить свои навыки в каждом из них. Также бот выводит рейтинговую таблицу, где вы можете увидеть свое место среди других пользователей. Это поможет вам отслеживать свой прогресс и стремиться к новым результатам.


CompetitiveBot объеденяет в себе разработанный интерфейс в виде телеграм-бота, серверную часть, предоставляющую веб-интерфейс для работы с данными (domserver), сервер судьи, необходимый для оценки и тестирования решений пользователей (judgehost) и базу данных

## Руководство по установке и настройке сервиса CompetitiveBot

### Установка необходимых контейнеров и исходного кода проекта.

При установке используются образы docker и код проекта из github. Для проекта была использована ОС Ubuntu 20.04.

1. Установка docker.
\
Руководство по установке dpcker вы можете найти на [странице официальной документации](https://docs.docker.com/engine/install/ubuntu/).

2. Установка контейнера базы данных.
\
MariaDB container:

```
sudo docker run -it --name dj-mariadb -e MYSQL_ROOT_PASSWORD=rootpw -e MYSQL_USER=domjudge -e MYSQL_PASSWORD=djpw -e MYSQL_DATABASE=domjudge -p 13306:3306 mariadb --max-connections=1000
```

3. Установка контейнера сервера.
\
DOMserver container:

```
docker run --link dj-mariadb:mariadb -it -e MYSQL_HOST=mariadb -e MYSQL_USER=domjudge -e MYSQL_DATABASE=domjudge -e MYSQL_PASSWORD=djpw -e MYSQL_ROOT_PASSWORD=rootpw -p 12345:80 --name domserver domjudge/domserver:latest
```

После установки DOMserver, в консоль будут выведены пароли для пользователей admin и judgehost, их необходимо сохранить, будтье внимательны.

Так же их можно будет найти используя:

```
docker exec -it domserver cat /opt/domjudge/domserver/etc/initial_admin_password.secret
docker exec -it domserver cat /opt/domjudge/domserver/etc/restapi.secret
```

4. Установка контейнера судьи.
\
Внимание, В ключе JUDGEDAEMON_PASSWORD необходимо будет указать пароль judgehost.

Judgehost container:

```
sudo docker run -itd --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro --name judgehost-0 --link domserver:domserver --hostname judgedaemon-0 -e DAEMON_ID=0 -e CONTAINER_TIMEZONE=Asia/Shanghai -e JUDGEDAEMON_PASSWORD= domjudge/judgehost:8.2.1
```

5. Клонирование проекта CompetitiveBot из репозитория.

Вы можете это сделать используя

```
git clone https://github.com/pococonut/CompetitiveBot.git
```

6. Создание виртуального окружения.
\
В среде PyCharm:

```
Settings -> Project: CompetitiveBot -> Python Interpreter -> Python 3.x
```

7. Установка необходимых библиотек.
\
Откройте косоль в корневой папке проекта и выполните команду:
```
pip install -r requirements.txt
```
При возникновении ошибок в связи с особенностями вашей системы, будет необходимо исправить их самостоятельно.

8. Создание файла config.py 
\
Для правильной работы программы и ее взаимодействия с другими сервисами, необходимо в корневой папке проекта указать данные в файле config.py.

Пример файла config.py:

```
import requests
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    api: str = "TOKEN"
    admin_username = "admin" # Данное поле можно оставить без изменений, если вы не указывали другого имени для пользователя admin
    admin_password = "ADMIN_PASSWORD"


settings = Settings()


def admin_authorization(uname, passw):
    session = requests.Session()
    session.auth = (uname, passw)
    return session
```

9. Запуск контейнеров

```
docker start dj-mariadb
docker start domserver
docker start judgehost-0
```

После правильной установки, вам будет доступен веб-интерфейс DOMjudge по адресу http://localhost:12345, для входа нужно будет указать имя и пароль пользователя admin.

![веб-интерфейс DOMjudge](images/снимок1.png)

#### Заполнение базы данных сервиса

Для корректной работы с CompetitiveBot, вам будет необходимо добавить данные в определенном формате

1. Создание нового соревнования (Contests).
\
По умолчанию будет создано тестовое соревнование с тестовыми задачами. Для правильного отображения задач нужно либо удалить задачи в тестовом соревновании, либо создать новое соревнование и добавлять задачи в него. Рассмотрим второй вариант.

Во вкладке Contests выберите Add new contest

![Add new contest](images/снимок2.png)

Укажите параметры Shortname, Name, Start time, End time

После добавления соревнования, его id будет равен 2, если вы не создавали  больше соревнований. CompetitiveBot использует id соревнования равным 2, если вы хотите использовать другое соревнование, укажите его id в файле commands/url_requests.py в параметре ```CONTEST_ID = "2"```

2. Создание задач.
\
Внимание! Для корректного отображения задач необходимо создавать pdf-файл с описанием в определенном формате, примеры готовых задач в формате docx и pdf, а так же входных-выходных тестовых данных в формате txt вы сожете найти [по этой ссылке](https://disk.yandex.ru/client/disk/CompetitiveBot/problems)
\
\
Телеграм бот принимает задачи трех уровней сложности - A, B, C

Для создания задачи перейдите во вкладку Problems и выберите Add new problem.

![Add new problem](images/снимок3.png)

Введите название задачи (Name)
\
Ограничение по времени на запуск и исполнение решения (Timelimit)
\
Описание задачи в виде pdf-файла (Problem text)
\
После добавления задачи, нужно добавить входные-выходные тестовые данные для задачи. 
\
В параметре Testcases нажмите details/ edit

![details/ edit](images/снимок4.png)

Добавте тестовые данные в формате txt

![txt](images/снимок5.png)

3. Добавление задач в соревнование.

После того как вы создали соревнование и добавили несколько задач с тестовыми данными, необходимо добавить задачи в соревнование.
\
\
Перейдите во вкладку Contests и внизу страницы в All available contests нажмите на соревнование, в которое вы хотите добавить задачи.

![All available contests](images/снимок6.png)

Далее пролистайте вниз страницы и в Problems нажмите на кнопку Edit

![Edit](images/снимок7.png)

Внизу страницы нажмите на знак "+" для добавления задачи в соревнование.

![Edit](images/снимок8.png)

В первой колонке выберите задачу которую хотите добавить. Далее необходимо указать короткое название задачи (Short name).
\
\
Внимание! В CompetitiveBot для разделения задач по уровню сложности исользуется короткое название задачи (Short name). Необходимо дать задаче короткое название в таком форате:
\
p1_A - Легкая задача
\
p1_B - Средняя задача
\
p1_C - Сложная задача

где p - сокращение от problem, 1  - номер задачи в категории, A/B/C - уровень задачи.
\
\
Далее укажите баллы за задачу (Points)
\
\
После нажмите кнопку Save для добавления задачи в соревнование.
