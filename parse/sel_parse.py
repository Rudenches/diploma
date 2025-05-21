import time  # Импортируем библиотеку для остановки кода на время
import undetected_chromedriver as uc  # Импортируем изменённый Selenium
from selenium.webdriver.common.by import By  # Импортируем By для нахождения по типу
from fake_useragent import UserAgent  # Импортируем рандомайзер Юзерагента
from bs4 import BeautifulSoup  # Импортируем библиотеку для обработкиHTML кода
from parse.levenstein import levenshtein_distance  # Импортируем из файла levenstain нужную фунуцию
from selenium.webdriver.support.ui import Select  # Импортируем из Seleniumметод для обработки выбора
from cyrtranslit import to_latin  # Импортируем из cyrtranslit функцию дляперевода на латинский
from random import randint  # Импортируем библиотеку для псевдослучайной Integer
import re  # Импортируем библиотеку для работы с regex
from parse.env import env_login  # Получаем объект из env.py для чтения .env файла
import chromedriver_autoinstaller  # Для автоматической установки chromedriver
import pdb  # Для отладки
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

LOGIN = env_login.login  # Логин
PASSWORD = env_login.password  # Пароль
print("Логин:", LOGIN)
print("Пароль:", PASSWORD)
NAMES = [
    '',
    '',
]


def check_page_state(driver):
    try:
        print("\nПроверка состояния страницы:")
        print("URL:", driver.current_url)
        print("Заголовок:", driver.title)
        print("Источник страницы:", driver.page_source[:500] + "...")  # Первые 500 символов
        print("Куки:", driver.get_cookies())
        print("Статус загрузки:", driver.execute_script("return document.readyState"))
    except Exception as e:
        print("Ошибка при проверке состояния:", str(e))


def check_block(driver: uc.Chrome):  # Функция для проверки на блокировку
    while True:  # Повторяем, пока не введут капчу
        if len(driver.find_elements(By.XPATH, '/html/body/div[2]/div[3]')) != 0:  # Если это страница капчи x
            time.sleep(5)  # То ждём и повторяем
            continue
        return  # Если нет, то выходим из цикла


def find_text(arr, search):  # Получаем расстояние левенштейна
    distance = False  # Сразу объявляем, что не нашли дистанцию
    for row in arr:  # читаем tr из массива
        text = row.find_all('td')[1].find_all('font')[0].text  # Получаем текст из каждой строки
        search_word = search.split(' ')[
            0]  # Превращаем нужный нам текст в массивы через пробел и выбираем первый полученный вариант (фамилию)
        search_latin = to_latin(search_word,"ru")  # Переводим нужную фамилию в латиницу
        texts = [
            f'[{search_word[0].upper()}|{search_word[0].lower()}]{search_word[1:]}',
            f'[{(search_latin[0].upper())}|{search_latin[0].lower()}]{search_latin[1:]}'
        ]  # записываем для regex слова на русском и латинском
        find = [re.findall(i, text) for i in NAMES]
        find = re.findall(fr'({texts[0]}.*?|{texts[1]}.*?)[ |,|.]',
                          text)  # Находим совпадение из текста с помощью regex
        if find == []:  # Если не нашли, начинаем заново
            continue
        distance = levenshtein_distance(search_word, find[0])  # Получаем расстояние левенштейна из текста
        if distance[1] == 0.0: distance = levenshtein_distance(search_latin,
                                                               find[0])  # Если расстояние левенштейна 0.0,
        # то сравниваем с латинским
        return distance  # Возвращаем первое нахождение
    return distance  # В случае ошибки возвращаем False


def get_distance_by_quotes(driver: uc.Chrome, search: str,
                           number: int):  # Получаем нужные секции для вычисления расстояния левенштейна
    try:
        if len(driver.find_elements(By.XPATH, f'//*[@id="list_refs"]')) != 0:
            # Если была нажата кнопка "Показать весь список литературы...", тоищемоднимпутем, иначеищемдругимпутемquotes
            quotes = driver.find_element(By.XPATH,
                                         f'/html/body/table/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td[1]/div[2]/table[{number}]/tbody[1]')
        else:
            quotes = driver.find_element(By.XPATH,
                                         f'/html/body/table/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td[1]/div[2]/table[{number}]/tbody')

        quotes = quotes.get_attribute('innerHTML')  # Получаем HTML код
        bs = BeautifulSoup(quotes, "html.parser")  # Объявляем библиотеку дляобработкиHTMLкода
        arr = bs.find_all('tr')  # Находим tr и выводим в массив

        text = find_text(arr, search)  # Получаем расстояние левенштейна
        if len(driver.find_elements(By.XPATH, f'//*[@id="list_refs"]')) != 0 and not text:
            # Если была нажата кнопка "Показать весь список литературы..." и впрошлойсекцииненайденнужныйрезултат, тоищемвдругойсекции
            quotes = driver.find_element(By.XPATH,
                                         f'/html/body/table/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td[1]/div[2]/table[{number}]/tbody[2]')
            quotes = quotes.get_attribute('innerHTML')  # Получаем HTML код

            bs = BeautifulSoup(quotes, "html.parser")  # Объявляем библиотеку дляобработкиHTMLкода
            arr = bs.find_all('tr')  # Находим tr и выводим в массив
            text = find_text(arr, search)  # Получаем расстояние левенштейна
        return text  # Возвращаем расстояние левенштейна

    except Exception as e:
        print(e)
        return False


def start_sel(search: str):  # Запускаем парсер
    try:
        print("1. Инициализация браузера...")
        chromedriver_autoinstaller.install()
        
        agent = UserAgent(os='windows')
        options = uc.ChromeOptions()
        options.add_argument(f"--user-agent={agent.random}")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 10)  # Добавляем явное ожидание до 10 секунд
        
        print("2. Загрузка страницы...")
        driver.get("https://www.elibrary.ru/")
        print("Страница загружена")
        print("Текущий URL:", driver.current_url)
        print("Заголовок страницы:", driver.title)
        time.sleep(randint(2, 5))
        
        print("3. Проверка на блокировку...")
        check_block(driver)
        print("Проверка блокировки пройдена")
        
        print("4. Попытка авторизации...")
        login_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login"]')))
        print("Поле логина найдено")
        login_field.send_keys(LOGIN)
        print("Логин введен")
        
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
        print("Поле пароля найдено")
        password_field.send_keys(PASSWORD)
        print("Пароль введен")
        
        print("5. Нажатие кнопки входа...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="win_login"]/table[1]/tbody/tr[9]/td/div[2]')))
        print("Кнопка входа найдена")
        login_button.click()
        print("Кнопка входа нажата")
        time.sleep(randint(3, 6))
        
        print("6. Проверка состояния после авторизации...")
        check_page_state(driver)
        check_block(driver)
        
        print("7. Переход на страницу поиска...")
        search_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="win_goto"]/table[1]/tbody/tr[5]/td[2]/a')))
        search_link.click()
        print("Переход выполнен")
        time.sleep(randint(2, 5))
        
        print("8. Проверка состояния страницы поиска...")
        check_page_state(driver)
        check_block(driver)
        
        print("9. Ввод поискового запроса...")
        search_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="surname"]')))
        print("Поле поиска найдено")
        search_field.clear()
        search_field.send_keys(search)
        print("Поисковый запрос введен")
        
        print("10. Ожидание загрузки параметров поиска...")
        try:
            select = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="show_param"]/table[5]/tbody/tr[2]/td[3]/div/select')))
            print("Элемент выбора показателей найден")
            select = Select(select)
            select.select_by_value('1')
            print("Выбран параметр 'по РИНЦ'")
        except TimeoutException:
            print("Предупреждение: Не удалось найти элемент выбора показателей")
            print("Текущее состояние страницы:")
            check_page_state(driver)
            raise

        "Авторы"
        time.sleep(randint(2, 5))  # Ждём 2-5 секунды
        check_block(driver)  # Проверяем на блок

        select = Select(driver.find_element(By.XPATH,
                                            '//*[@id="show_param"]/table[2]/tbody/tr[2]/td[1]/div/select'))  # Получаем Select поля "Город"
        select.select_by_index(0)  # Выбираем пустой вариант (это -- все города)

        select = Select(driver.find_element(By.XPATH,
                                            '//*[@id="show_param"]/table[5]/tbody/tr[2]/td[3]/div/select'))  # Получаем Select поля "Показатели"
        select.select_by_value('1')  # Выбираем "по РИНЦ"

        driver.find_element(By.XPATH,
                            '//*[@id="show_param"]/table[7]/tbody/tr[2]/td[6]/div').click()
        time.sleep(randint(2, 5))  # Ждём 2-5 секунды

        driver.find_element(By.XPATH,
                            '//*[@id="show_param"]/table[7]/tbody/tr[2]/td[6]/div').click()
        time.sleep(randint(4, 8))  # Ждём 4-8 секунд
        check_block(driver)  # Проверяем на блок

        i = 4  # Объявляем переменную для чтения строк
        global_links = []  # Объявляем массив глобальных ссылок
        while True:  # Проходим по списку
            try:

                # link = driver.find_element(By.XPATH,
                #                            f'/html/body/table/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/'
                #                            f'td[1]/table/tbody/tr/td/table/tbody/tr[{i}]/td[5]/div/a').get_attribute('href')  # Получаем ссылку
                href = driver.find_element(By.XPATH, "//a[contains(@href, 'show_author_refs')]").get_attribute('href')

                params = re.findall(r'show_author_refs\((\d+),\s*\'(\w+)\'\)', href)[0]
                author_id, ref_type = params
                url = f"https://www.elibrary.ru/author_refs.asp?id={author_id}&show_refs={ref_type}"
                driver.get(url)


                global_links.append(url)  # Записываем ссылку в массив глобальных ссылок
                i += 1  # Добавляем к переменной i единицу
            except:
                break

        links = []  # Объявляем массив для ссылок
        for row in global_links:
            driver.get(row)  # Открываем ссылку из глобальных ссылок
            time.sleep(randint(7, 10))  # Ждём 4 секунды
            check_block(driver)  # Проверяем на блок

        try:
           # select = Select(driver.find_element(By.XPATH, '//*[@id="show_hash"]'))
                                                # '/html/body/div[3]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/'
                                                #       'table/tbody/tr[2]/td[1]/table/tbody/tr/td/div[2]/div[2]/table[10]/tbody/tr[2]/td/div/select'))

            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="show_hash"]')))
            select = Select(select_element)
            select.select_by_value('1')
            driver.find_element(By.XPATH,'//*[@id="show_param"]/table[12]/tbody/tr[2]/td[6]/div').click()
                            # '/html/body/div[2]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/table/tbody/tr[2]/td[1]'
                            # '/table/tbody/tr/td/div[2]/div[2]/table[12]/tbody/tr[2]/td[6]/div').click()
        except Exception as e:
            print(f"Не удалось найти или использовать select элемент: {str(e)}")
            # Опционально, можно добавить ожидание здесь, чтобы убедиться, что страница загружена
            time.sleep(randint(2, 5))
            # Можно проверить состояние страницы
            check_page_state(driver)

            #time.sleep(randint(2, 5))  # Ждём 2-5 секунды

        k = 4  # Объявляем переменную для чтения строк
        reffered_arcticles = []  # массив неправильных названий статей
        original_articles_links = [] #массиы ссылок исходных статей
        while True:  # Проходим по списку
            try:
                wait = WebDriverWait(driver, 10)
                # Ждем загрузки страницы
                time.sleep(randint(2, 4))
                reffered_article = wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        f'/html/body/div[2]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/table'
                        f'/tbody/tr[2]/td[1]/table/tbody/tr/td/table/tbody/tr[{k}]/td[2]/table/tbody/tr/td[1]/font/span'
                    ))
                ).text
                #reffered_article = driver.find_element(By.XPATH,
                 #                          f'/html/body/div[3]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/table'
                  #                         f'/tbody/tr[2]/td[1]/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]/table/tbody/tr/td[1]/font/span').text
                      # Получаем название статьи на которую ссылаются(упомянутая статья)

                original_article = driver.find_element(By.XPATH, f'/html/body/div[2]/table/tbody/tr/td/table[1]/tbody/tr'
                                                                 f'/td[2]/form/table/tbody/tr[2]/td[1]/table/tbody/tr/td'
                                                                 f'/table/tbody/tr[{k}]/td[2]/table/tbody/tr/td[1]/table[1]'
                                                                 f'/tbody/tr/td[2]/span/a').get_property('href') #получаем ссылку на исходную статью с ошибкой
                reffered_arcticles.append(reffered_article)  # Записываем ссылку в массив глобальных ссылок
                original_articles_links.append(original_article)
                k += 1  # Добавляем к переменной i единицу
            except:
                break

        # for row in original_articles_links:
        #     driver.get(row)  # Открываем ссылку из глобальных ссылок
        #     time.sleep(randint(7, 10))  # Ждём 4 секунды
        #     check_block(driver)  # Проверяем на блок


        # i = 4  # Объявляем переменную для чтения строк
        # global_links = []  # Объявляем массив глобальных ссылок
        # while True:  # Проходим по списку
        #     try:
        #         link = driver.find_element(By.XPATH,
        #                                    f'/html/body/table/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/'
        #                                    f'td[1]/table/tbody/tr/td/table/tbody/tr[{i}]/td[4]/div/a[1]').get_property(
        #             'href')  # Получаем ссылку
        #         global_links.append(link)  # Записываем ссылку в массив глобальных ссылок
        #         i += 1  # Добавляем к переменной i единицу
        #     except:
        #         break
        #
        # links = []  # Объявляем массив для ссылок
        # for row in global_links:
        #     driver.get(row)  # Открываем ссылку из глобальных ссылок
        #     time.sleep(randint(7, 10))  # Ждём 4 секунды
        #     check_block(driver)  # Проверяем на блок

        # i = 4  # Объявляем переменную для чтения строк
        # while True:  # Проходим по списку
        #     try:
        #         if len(driver.find_elements(By.XPATH,
        #                                     f'/html/body/div[3]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/table/tbody'
        #                                     f'/tr[2]/td[1] / table / tbody / tr / td / table /'
        #                                     f' tbody / tr[{i}] / td[2] / span / a')) != 0:
        #             # Страница может выглядеть по-разному, поэтому проверяем на нужные данные
        #
        #             line = driver.find_element(By.XPATH,
        #                                        f'/html/body/div[3]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/'
        #                                        f'table/tbody/tr[2]/td[1]/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]/span/a')
        #             count_quote = driver.find_element(By.XPATH,
        #                                               f'/html/body/div[3]/table/tbody/tr/td/table[1]/tbody'
        #                                               f'/tr/td[2]/form/table/tbody/tr[2]/td[1] / table / tbody '
        #                                               f'/ tr / td / table / tbody / tr[{i}] / td[3]').text  # Получаем количество цитирования
        #         else:
        #             # В любом итоге получаем ссылку
        #             line = driver.find_element(By.XPATH,
        #                                        f'/html/body/div[3]/table/tbody/tr/td/table[1]/tbody'
        #                                        f'/tr/td[2]/form/table/tbody/tr[2]/td[1] / table / tbody '
        #                                        f'/ tr / td / table / tbody / tr[{i}] / td[2] / a')
        #             count_quote = driver.find_element(By.XPATH,
        #                                               f'/html/body/div[3]/table/tbody/tr/td/table[1]/tbody'
        #                                               f'/tr/td[2]/form/table/tbody/tr[2]/td[1] / table / tbody '
        #                                               f'/ tr / td / table / tbody / tr[{i}] / td[3]').text  # Получаем количество цитирования
        #
        #         if count_quote == '0':
        #             # Если количество цитирования 0, то добавляем к переменной i единицу и начинаем заново
        #             i += 1
        #             continue
        #
        #         driver.find_element(By.XPATH,
        #                             f'/html/body/div[3]/table/tbody/tr/td/table[1]/tbody'
        #                             f'/tr/td[2]/form/table/tbody/tr[2]/td[1] / table / tbody '
        #                             f'/ tr / td / table / tbody / tr[{i}] / td[3]'
        #                             ).click()
                # x = 4
                # while True:
                #     try:
                #         if len(driver.find_elements(By.XPATH,
                #                                     f'/html/body/div[2]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/table/tbody'
                #                                     f'/tr[2]/td[1] / table / tbody / tr / td / table /'
                #                                     f' tbody / tr[{x}] / td[2] / span / a')) != 0:
                #             line = driver.find_element(By.XPATH,
                #                                f'/html/body/div[2]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/'
                #                                f'table/tbody/tr[2]/td[1]/table/tbody/tr/td/table/tbody/tr[{x}]/td[2]/span/a')
                #
                #         else:
                #             line = driver.find_element(By.XPATH,
                #                                f'/html/body/div[2]/table/tbody/tr/td/table[1]/tbody'
                #                                f'/tr/td[2]/form/table/tbody/tr[2]/td[1] / table / tbody '
                #                                f'/ tr / td / table / tbody / tr[{x}] / td[2] / a')
                #
                #         links.append(line.get_property('href'))  # Записываем ссылку в массив для ссылок
                #         x += 1  # Добавляем к переменной i единицу
                #     except:
                #         break
                #
                # driver.back();
                #
                # i += 1  # Добавляем к переменной i единицу

            # except:
            #     i = 4  # Объявляем переменную для чтения строк
            #     try:
            #         next = driver.find_element(By.XPATH,
            #                                    "//*[contains(text(), '>>')]")  # Находим кнопку для следующей страницы
            #         if next.get_property('color') == '#aaaaaa':
            #             # Если ссылка неактивна, то заканчиваем проходить по списку
            #             break
            #         next.click()  # Нажимаем на кнопку для перехода на следующую страницу
            #         time.sleep(randint(4, 8))  # Ждём 4-8 секунд
            #         check_block(driver)  # Проверяем на блок
            #     except:
            #         # Если вышла ошибка кода, то заканчиваем проходить по списку
            #         break

        result = {}  # Объявляем словарь для результата
        ix = 0  # Для упрощения объявляем порядок записи в результат
        print(original_articles_links)
        for line in original_articles_links:  # Читаем ссылки
            result.update({ix: {'link': line, 'author': []}})  # Сразу подготавливаем строку в словаре
            try:
                driver.get(line)  # Открываем страницу
            except:
                continue
            time.sleep(randint(5, 8))  # Ждём 5-8 секунд
            check_block(driver)  # Проверяем на блок

            try:
                # Пытаемся нажать на кнопку "Показать весь список литературы...", и если такой кнопки нет, идем дальше4
                driver.find_element(By.XPATH, '//*[@id="show_reflist"]/tr/td[2]/a').click()
                time.sleep(randint(2, 5))  # Ждём 2-5 секунды
            except:
                pass

            try:
                arr = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/table[1]/tbody'
                                                    '/tr/td[2]/ table / tbody / tr[2] / td[1] / div[2] '
                                                    '/ table[1] / tbody / tr / td[2]')  # Подготавливаем блок дляавторов
                html = arr.get_attribute('innerHTML')  # Получаем полученный блок в виде HTML
                bs = BeautifulSoup(html, "html.parser")  # Объявляем обработчик HTML полученного блока

                # Получаем название статьи
                try:
                    title_element = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td[1]/table[2]/tbody/tr/td[2]/span/b/p')
                    article_title = title_element.text
                except:
                    article_title = "Название не найдено"

                arr = bs.find_all('div', style='display: inline-block; white-space: nowrap')  # Находим всех авторов
                arrs = [i.find('font').text for i in arr]  # Получаем их имена и записываем в массив
                for i in reversed(range(1, 13)):  # Находим блок с цитатами
                    distance = get_distance_by_quotes(driver, search, i)  # Получаем расстояние левенштейна
                    if type(distance) == tuple:
                        # если тип ответа - кортеж, то заканчиваем искать блок с цитатами
                        break
                if type(distance) == tuple:
                    # если тип ответа - кортеж, то записываем его процент, иначе "Ссылка отсутствует"
                    arrs.append(f'{round(distance[1], 1)}%')
                else:
                    arrs.append('Ссылка отсутствует')

            except:
                # Если на любом этапе в блоке try возникла ошибка кода (Не найден блок, не нашлись авторы и т.п.)
                arrs = ['Нет автора']  # То записываем, что авторов нет
                article_title = "Название не найдено"

            result[ix]['author'] = ' '.join(arrs)  # Записываем в словаре в строку author всех авторов в виде строки.
            result[ix]['title'] = article_title  # Добавляем название статьи в результат
            ix += 1  # Прибавляем 1 для следующей записи

        mass = []  # Объявляем массив для вывода
        mass = [value for value in result.values()]  # Получаем только значения из массива результата
        print(mass)  # В консоль выводим массив для вывода
        driver.quit()  # Закрываем Selenium
        return mass  # Возвращаем массив

    except Exception as e:
        print("\nКритическая ошибка:")
        print("Тип:", type(e).__name__)
        print("Сообщение:", str(e))
        print("\nТекущее состояние:")
        check_page_state(driver)
        raise

