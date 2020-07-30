import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo

# 用selenium自动化工具爬取
option = webdriver.ChromeOptions()

# 开发者模式的开关，设置一下，打开浏览器就不会识别为自动化测试工具了
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome()
driver.implicitly_wait(10)  #这里设置智能等待10s
# # 等待
wait = WebDriverWait(driver, 10)


# 传入要爬取的商品名称
def search(thing):
    try:
        driver.get('http://search.suning.com/' + thing + '/')
        time.sleep(1)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight/4)')
        time.sleep(1)
        driver.execute_script('window.scrollTo(document.body.scrollHeight/4, document.body.scrollHeight/2)')
        time.sleep(1)
        driver.execute_script('window.scrollTo(document.body.scrollHeight/2, document.body.scrollHeight)')
        time.sleep(10)
        print('开始解析...')
        # 解析数据
        get_products()
    except TimeoutError:
        print('超时！重新开始获取...')
        return search()


# 翻页爬取
def next_page(page_number):
    try:
        print('当前页数' + str(page_number))
        inputs = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#bottomPage"))
        )
        inputs.clear()
        inputs.send_keys(page_number)
        time.sleep(0.5)
        submit = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#bottom_pager > div > a.page-more.ensure"))
        )
        submit.send_keys(Keys.ENTER)
        time.sleep(1)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight/4)')
        time.sleep(1)
        driver.execute_script('window.scrollTo(document.body.scrollHeight/4, document.body.scrollHeight/2)')
        time.sleep(1)
        driver.execute_script('window.scrollTo(document.body.scrollHeight/2, document.body.scrollHeight)')
        time.sleep(10)
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '#bottom_pager > div > a.cur'), str(page_number))
        )
        print('开始解析...')
        get_products()
    except TimeoutError:
        next_page(page_number)


# 解析并获取想要的数据
def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#product-list .item-wrap')))
    html = driver.page_source
    doc = pq(html)
    items = doc('#product-list .item-wrap').items()
    for item in items:
        product = {
            'price': item.find('.def-price').text()[:-3].replace('¥', ""),
            'Sales': item.find('.info-evaluate').text()[:-2].replace('+', '').replace('.', '').replace('万', '000'),
            'title': item.find('.title-selling-point').text(),
            'shop': item.find('.store-stock').text(),
        }
        print(product)
        write_to_mongo(product)
        data.append(product['Sales'])
        Price_data.append(product['price'][1:-3])
        Shop_data['苏宁自营'] += int(product['shop'].count('苏宁自营'))
        Shop_data['旗舰店'] += int(product['shop'].count('旗舰店'))
        Shop_data['专卖店'] += int(product['shop'].count('专卖店'))
        name['OPPO'] += int(product['title'].count("OPPO"))
        name['苹果'] += int(product['title'].count("苹果"))
        name['华为'] += int(product['title'].count("华为"))
        name['小米'] += int(product['title'].count("小米"))
        name['中兴'] += int(product['title'].count("中兴"))


# 对数据进行处理
def update_data(Data):
    for i in range(len(Data)):
        if Data[i] == '':
            Data[i] = 0
        else:
            Data[i] = int(Data[i])
    # Data.sort(reverse=True)
    print(Data)
    print("最大值：{},最小值：{}".format(max(Data), min(Data)))


# 将数据写入mongodb数据库
def write_to_mongo(content):
    try:

        # 1 创建连接对象
        client = pymongo.MongoClient("mongodb://root:root@localhost:27017")
        # 2 获取数据库,
        # 如果这个数据库不存在，就在内存中虚拟创建
        # 当在库里创建集合的时候，就会在物理真实创建这个数据库
        db = client.BigData
        if content.get("Sales") == "":
            content["Sales"] = "0"
        db.phone2.insert(content)
        client.close()
    except Exception as e:
        print(e)


# 生成手机品牌饼图
def make_pie():
    from pyecharts import Pie
    attr = ['OPPO', '小米', '苹果', '华为', '中兴', '其他']
    iphone = [name['OPPO'], name['苹果'], name['小米'], name['华为'], name['其他'], name['中兴']]
    pie = Pie('苏宁——智能手机')
    pie.add('手机品牌', attr, iphone, is_label_show=True)
    pie.show_config()
    pie.render(path='./suNing.html')


# 生成价格/销量 柱状图
def make_price():
    from pyecharts import Bar
    bar = Bar('价格/销量 柱形图')
    attr = list(range(len(data)))
    bar.add('价格', attr, Price_data, mark_point=['min', 'max', 'average'])
    bar.add('销量', attr, data, mark_point=['min', 'max', 'average'])
    bar.show_config()
    bar.render(path='./price2.html')


def main():
    global data, Price_data, Shop_data, name
    data = []
    Price_data = []
    Shop_data = {"苏宁自营": 0, "旗舰店": 0, "专卖店": 0}
    name = {"OPPO": 0, "苹果": 0, "小米": 0, "华为": 0, "中兴": 0, "其他": 0}
    # 传入商品名
    search("智能手机")
    # 翻页
    for i in range(2, 51):
        print('开始翻页...')
        next_page(i)
    # 处理数据
    update_data(data)
    update_data(Price_data)
    print(Shop_data)
    name['其他'] = len(data) - (name['OPPO'] + name['苹果'] + name['华为'] + name['小米'] + name['中兴'])
    print(name)
    # 数据可视化
    make_pie()
    make_price()


if __name__ == '__main__':
    main()
