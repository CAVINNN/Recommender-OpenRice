import requests
import random
import time
from bs4 import BeautifulSoup

UA_List = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
]
headers = {
    'User-Agent': random.choice(UA_List)
}


def process_shop_rating(page_url, shop_name, rating_data):
    try:
        rating_html = requests.get(page_url, headers=headers)
        rating_bs = BeautifulSoup(rating_html.text, 'lxml')

        rating_containers = rating_bs.select('div.js-sr2-review-main.sr2-review-main div.sr2-review-list-container.full.clearfix.js-sr2-review-list-container')
        for rating_container in rating_containers:
            # 评分用户的name
            username = rating_container.select_one('section.sr2-review-list2-profile-section > div.name > a').get_text().strip()
            rating_meta = rating_container.select_one('section.sr2-review-list2-detailed-rating-section').find('meta', attrs={"content": True})
            if rating_meta is not None:
                rating = rating_meta.attrs['content']

                if username in rating_data:
                    rating_data[username][shop_name] = float(rating)
                else:
                    rating_data[username] = {}
                    rating_data[username][shop_name] = rating

            else:
                continue

        rating_nextbutt = rating_bs.select_one('div.pagination.js-pagination a.pagination-button.next.js-next')
        if rating_nextbutt is not None:
            next_page_url = 'https://www.openrice.com' + rating_nextbutt.attrs['href']
            print(next_page_url)
            time.sleep(2)
            process_shop_rating(next_page_url, shop_name, rating_data)

    except requests.exceptions.RequestException:
        print('Cannot request one page ratings of a shop.')


shops_cate = {}
_100_top_shops_rating = {}

for index in range(7):
    print('Current Page: ' + str(index + 1))
    url = 'https://www.openrice.com/api/pois?uiLang=zh&uiCity=hongkong&page=' + str(index + 1) + '&&sortBy=Default'
    try:
        onePage_res = requests.get(url, headers=headers)
        onePage_json = onePage_res.json()
        onePage_shops = onePage_json['searchResult']['paginationResult']['results']
        for shop in onePage_shops:
            # 店铺的名字
            shop_name = shop['nameUI']
            # 店铺的url
            shop_url = 'https://www.openrice.com' + shop['urlUI'] + '/reviews?page=1'
            # 店铺的标签 [string, string, ...]
            shop_cate = list()
            for category in shop['categories']:
                shop_cate.append(category['name'])
            shops_cate[shop_name] = shop_cate

            # 处理店铺中的所有评分
            process_shop_rating(shop_url, shop_name, _100_top_shops_rating)
            
    except requests.exceptions.RequestException:
        print('Cannot request one page shops.')

# 输出所有评分至txt
rating_outputStream = open("./100_top_shops_rating.txt", "w", encoding='utf-8')
rating_outputStream_num = rating_outputStream.write(str(_100_top_shops_rating))

# 输出所有店铺标签至txt
shops_cate_outputStream = open("./100_top_shops_cate.txt", "w", encoding='utf-8')
shops_cate_outputStream_num = shops_cate_outputStream.write(str(shops_cate))
