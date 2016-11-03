import requests
from bs4 import BeautifulSoup
import time
import pymysql

conn = pymysql.connect(host='127.0.0.1',
                       user='localhost',
                       passwd='123456',
                       db='swjtu',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

headers = {

    'Referer': 'http://sist.swjtu.edu.cn/download.do?action=file',
    'Host': 'sist.swjtu.edu.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; /'
                 'Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) /'
                 'Chrome/53.0.2785.143 Safari/537.36',
}

class crawler(object):

    #设置每12小时爬取一次
    def sleep_time(self):
        sleep = time.sleep(12 * 60 * 60)
        return sleep

    # 去重(还没搞清楚， 但是不能这么匹配，一旦出现匹配值就会多个一起）
    def clean(self, tmp_info):
        sql = "select title from xinxi"
        cursor.execute(sql)
        conn.commit()
        rss = cursor.fetchall()
        print(rss[0])
        final_info = []
        # for item in tmp_info:
        #     for i in range(len(rss)):
        #         print(rss[i]['title'] == item['title'])
        #         # if item['title'] not in rss[i]['title']:
        #         #     final_info.append(item)
        #         # else:
        #         #     pass
        for i in rss:
            for item in tmp_info:
                print(i['title'] == item['title'])
                # if item['title'] not in rss[i]['title']:
                #     final_info.append(item)
                # else:
                #     pass
        return final_info

    # 存储数据到mysql
    def save(self, tmp_info):
        for item in tmp_info:
            date = item['date']
            title = item['title']
            link = item['link']
            # print(date, title, link)
            sql = 'INSERT INTO xinxi(date, title, link) VALUES ("%s", "%s", "%s")' % (date, title, link)
            cursor.execute(sql)
            conn.commit()
        print('all saved!')


    #爬虫主函数
    def craw(self, start_url):

        #有异常时抛出错误并继续执行
        try:
            html = requests.get(start_url, headers=headers)
            soup = BeautifulSoup(html.text, 'lxml')
            info = soup.select('#rightPageContent > dl > dd')
            tmp_info = []
            for item in info:
                date = item.select('span')[0].text
                title = item.select('div a')[0].text
                link = item.select('div a')[0].get('href')
                # print(date, title, link)
                data = {
                    'date': date,
                    'title': title,
                    'link': link,
                }

                tmp_info .append(data)
            #去重并保存数据到数据库
            final = self.clean(tmp_info)
            self.save(final)

        except Exception as e:
            print(e)

        # #调用slepp_time,每过12小时执行爬虫
        # finally:
        #     self.sleep_time()
        #     self.craw(start_url)

#启动爬虫
if __name__ == "__main__":
    start_url = 'http://sist.swjtu.edu.cn/download.do?action=file&navId=55'
    xinxi = crawler()
    xinxi.craw(start_url)
