import datetime
import pickle
import re
import time
import traceback
from multiprocessing import Process
from setting import *
from bs4 import BeautifulSoup
from selenium import webdriver

from save_to_file import save_to_file


class topic_thread(Process):
    def __init__(self, name, num_post=0):
        super(topic_thread, self).__init__()
        self.name = name
        self.url = 'https://www.quora.com/topic/' + self.name + '/all_questions'
        self.data = set()
        self.driver = phantomjs_path
        self.num_post = num_post
        self.total = 0
        self.saved = 0
        self.file_path = save_path
        self.pickle_path = pickle_path
        self.dict = {}
        self.tried = 0

    def save_to_sets(self, soup):
        my_divs = soup.findAll("a", {"class": "question_link"})
        now = len(self.dict)
        for index, div in enumerate(my_divs):
            key = div.findAll("span", {"class": "rendered_qtext"})[0].text
            url = div['href']
            self.dict[key] = url
        after = len(self.dict)
        return after - now

    def save_to_data(self, soup):
        my_divs = soup.findAll("a", {"class": "question_link"})
        now = len(self.data)
        for index, div in enumerate(my_divs):
            key = div.findAll("span", {"class": "rendered_qtext"})[0].text
            self.data.add(key)
        after = len(self.data)
        return after - now

    def save_to_file(self):
        total = len(self.data)
        process_save = save_to_file(path=self.file_path, name=self.name, data=self.data)
        process_save.run()
        self.data = set()
        return total

    def save_to_pickle(self):
        print('len of {name} '.format(name=self.name) + str(len(self.dict)))
        with open(self.pickle_path + self.name + '_pickle', 'wb') as f:
            pickle.dump(self.dict, f)

    def run(self):
        browser = None
        try:
            if proxy_or_not:
                args = service_args
            else:
                args = ['--load-images=false']
            browser = webdriver.PhantomJS(executable_path=self.driver, service_args=args)
            browser.set_page_load_timeout(30)
            browser.set_script_timeout(30)
            self.main_function(browser)
            browser.close()
        except:
            print(traceback.format_exc())
            self.save_to_pickle()
            if browser:
                browser.close()

    def get_total_number(self, page):
        data = page.encode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        total = soup.find('a', {'class': 'StatsRow TopicQuestionsStatsRow'}).text.replace('Questions', '')
        total = total.replace('k', '000')
        total = total.replace('.', '')
        total = int(total)
        self.total = total

    def main_function(self, browser):
        try:
            browser.get(self.url)
            time.sleep(5)
        except:
            self.tried += 1
            if self.tried <= 10:
                self.main_function(browser=browser)
            else:
                print(self.url + ' failed: ' + str(self.tried))
        if not re.search('All Questions', browser.title):
            return
        else:
            self.tried = 0
        default_page = browser.page_source
        self.get_total_number(default_page)
        print('total number in {title}: '.format(title=self.name) + str(self.total))
        print(browser.title.replace('All Questions on ', '').replace(' - Quora', ''))
        run = 0
        success = 0
        failed = 0
        save_operation = 0
        if not self.num_post:
            self.num_post = self.total
        while self.saved <= self.num_post:
            try:
                if self.tried >= 10:
                    break
                if failed > 10:
                    self.tried += 1
                    failed = 0
                browser.execute_script("window.scrollTo(document.body.scrollWidth* 0.5, document.body.scrollHeight * 0.5)")
                browser.execute_script("window.scrollTo(document.body.scrollWidth* 0.5, document.body.scrollHeight * 2)")
                time.sleep(2)
                print('Scrolling for %s %d' % (self.name, success + 1))
                print(datetime.datetime.now())
                run += 1
                try:
                    if run >= 10:
                        run = 0
                        html_source = browser.page_source
                        data = html_source.encode('utf-8')
                        soup = BeautifulSoup(data, 'html.parser')
                        len_div = self.save_to_data(soup)
                        if len_div == 0:
                            print('nothing found now in %s' % self.name)
                            failed += 1
                            continue
                        else:
                            failed = 0
                        print('saved {len_div} {name} into set'.format(len_div=str(len_div), name=self.name))
                        browser.execute_script("jQuery('.PagedList.TopicAllQuestionsList .pagedlist_item').slice(0,{remove}).remove()".format(remove=len_div))
                        print('{remove} questions in {name} page now was removed'.format(name=self.name, remove=str(int(len_div*1.2))))
                        if save_operation == 3:
                            try:
                                saved = self.save_to_file()
                                self.saved += saved
                                print('total saved in {title}: '.format(title=self.name) + str(self.saved))
                                print('saving {title} {operation} now'.format(title=self.name, operation=saved))
                                save_operation = 0
                            except:
                                print(traceback.format_exc())
                                continue
                        else:
                            save_operation += 1
                except:
                    continue
                success += 1
            except:
                self.tried += 1
                continue


if __name__ == "__main__":
    topic = input('Enter a name of topic\n')
    process = topic_thread(topic)
    process.run()
