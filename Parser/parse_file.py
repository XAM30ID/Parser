import requests
from bs4 import BeautifulSoup
import wget
from CON_BD import schedule_refresh


def refresh():
    url = 'http://www.rshu.ru/university/stud/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('Расписание занятий ')

    start = str(soup).find("Расписание занятий")
    finish = str(start).rfind("Расписание")
    files = str(soup)[start:finish].split("\n")[2:3][0].split('<img align="absmiddle" src="/img/pdf.gif"/> ')[1:]

    for file in files:
        link = "http://www.rshu.ru/university/stud/" + file[file.find('<a href="') + len('<a href="'):
                                                            file.find('.pdf') + len('.pdf')]
        name = file[file.find('target="_blank">') + len('target="_blank">'):file.find('</a><br/><br/>')]

        wget.download(link, f'schedules/{name}.pdf')
    schedule_refresh()
