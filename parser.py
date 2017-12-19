import requests
from bs4 import BeautifulSoup
import pymongo


URL = ['https://baza-otvetov.ru/user/view_questions/56/', 'https://baza-otvetov.ru/user/view_questions/396/']


class Client():
    step = 15
    url = None
    connection = pymongo.MongoClient()
    db = connection.questions

    def __init__(self, _url):
        self.url = _url

    def _get_page_url(self):
        """Генератор доступных страниц"""

        res = requests.get(self.url)
        parsed_html = BeautifulSoup(res.text, "html.parser")
        nav = parsed_html.body.find('div', {'class': 'q-list__nav'}).findAll('a')
        last_page = nav[-1].attrs['href'].split('/')[-1]
        yield self.url
        for i in range(0, int(last_page)+self.step, self.step):
            yield '{}{}'.format(self.url, i)

    @classmethod
    def parse_page_quest(cls, page_url):
        """Распарсить страницу с вопросами и ответами ответов"""

        res = requests.get(page_url)
        if res.status_code != 200:
            raise requests.exceptions.RequestException('Not 200')
        parsed_html = BeautifulSoup(res.text, "html.parser")
        items = parsed_html.body.findAll('tr', {'class': 'tooltip'})
        for item in items:
            _id = item.attrs['id']
            quest = item.find('a').text
            _pos_answer_items = item.find('div', {'class':'q-list__quiz-answers'})
            if _pos_answer_items:
                _pos_answer = _pos_answer_items.text
                _pos_answer = _pos_answer.replace('Ответы для викторин:', '')
                pos_answer = _pos_answer.strip().split(',')
            else:
                pos_answer = []
            answ = item.findAll('td')[-1].text
            print('id: {_id} \n quest:{quest}\n  pos_answer: {pos_answer} \n answ: {answer}'.format(
                _id=_id,
                quest=quest,
                pos_answer=pos_answer,
                answer=answ
            ))
            # Добавление документов в колекцию 'questions'
            print('url: {}'.format(page_url))
            try:
                cls.db.questions.save({
                    'quest_id':_id,
                    'quest':quest,
                    'pos_answer':pos_answer,
                    'answer':answ
                })
            except Exception as exc:
                print ('except : {}'.format(exc))


if __name__ == '__main__':
    cli = Client(URL[1])
    for url in cli._get_page_url():
        Client.parse_page_quest(url)
    print ('Finish !')
