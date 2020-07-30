import re

import numpy as np
from bson import ObjectId
from pymongo import MongoClient
from sklearn import svm, model_selection
from sklearn.cluster import KMeans


# 聚类分类分析

# 提取手机配置信息
def extract_mongo():
    client = MongoClient("mongodb://root:root@localhost:27017")
    db = client['BigData']
    # 提取手机配置信息
    for item in db.phone2.find({"title": {"$ne": ""}}):
        result = re.search(r'\d+G?B? ?\+ ?\d+G?B?', item.get("title"), re.I)
        _id = item.get("_id")
        #  判断是否为 _ + _ 形式
        if result is None:
            result2 = re.search(r'(\dG运行) (\d+G内存)', item.get("title"), re.I)

            #  判断是否为 G运行 G内存形式
            if result2 is None:
                result3 = re.search(r'\d{2,}G', item.get("title"), re.I)
                # 判断是否为 __G形式
                if result3 is None:
                    db.phone2.update({'_id': ObjectId(_id)}, {'$set': {"configure": "1,1"}})
                else:
                    result4 = re.search(r'apple', item.get("title"), re.I)
                    # 判断 _G形式的是否为Apple的手机
                    if result4 is None:
                        db.phone2.update({'_id': ObjectId(_id)}, {
                            '$set': {"configure": "1," + result3.group().replace("G", "").replace("B", "").replace(" ",
                                                                                                                   "")}})
                    else:
                        db.phone2.update({'_id': ObjectId(_id)}, {'$set': {
                            "configure": "2" + "," + result3.group().replace("G", "").replace("B", "").replace(
                                " ", "")}})

            else:
                db.phone2.update({'_id': ObjectId(_id)}, {
                    '$set': {"configure": result2.group().replace("G运行", ",").replace("G内存", "").replace(" ", "")}})

            # print("None")
        else:
            db.phone2.update({'_id': ObjectId(_id)},
                             {'$set': {
                                 "configure": result.group().replace("g", "").replace("G", "").replace("B", "").replace(
                                     " ", "").replace("+",
                                                      ",")}})
            print(result)
    print(db.phone2.find({"title": {"$ne": ""}}).count())
    client.close()


# 将数据写入文件
def write_to_file():
    client = MongoClient("mongodb://root:root@localhost:27017")
    db = client.BigData
    for item in db.phone.find({}):
        Sales = item.get("Sales")
        price = item.get("price")
        configure = item.get("configure")
        name = item.get("title")[:25]
        with open('D:/SuNing_BigData.txt', 'a', encoding='utf-8') as f:
            f.write(name + ',' + Sales + ',' + price + ',' + configure + '\n')
            f.close()


def write_to_file2(i):
    client = MongoClient("mongodb://root:root@localhost:27017")
    db = client.BigData
    for item in db.phone.find({}):
        if int(item.get("Sales")) > i:
            Sales = "1"
        else:
            Sales = '0'
        price = item.get("price")
        configure = item.get("configure")
        with open('D:/SuNing_BigData2.txt', 'a', encoding='utf-8') as f:
            f.write(Sales + ',' + price + ',' + configure + '\n')
            f.close()


# 加载数据
def loadData(filePath):
    fr = open(filePath, 'r+', encoding='UTF-8')
    lines = fr.readlines()
    data_Storage = []
    data_Memory = []
    data_Price = []
    data_Sales = []
    phone_name = []
    for line in lines:
        items = line.strip().split(',')
        phone_name.append(items[0])
        data_Storage.append([items[4]])
        data_Memory.append([items[3]])
        data_Price.append([items[2]])
        data_Sales.append([items[1]])

    return data_Storage, data_Memory, data_Price, data_Sales, phone_name


def loadData2(filePath):
    fr = open(filePath, 'r+', encoding='UTF-8')
    lines = fr.readlines()
    data = []
    data_Sales = []
    for line in lines:
        items = line.strip().split(',')
        data.append([float(items[i]) for i in range(1, len(items))])
        data_Sales.append([items[0]])
    return data, data_Sales


def show_accuracy(a, b, tip):
    acc = (a == b)
    print("%s Accuracy:%.3f" % (tip, np.mean(acc)))


# 分类模型评估
def print_accuracy(model, x_train, y_train, x_test, y_test):
    print('SVM-输出训练集的准确率为:', model.score(x_train, y_train))
    print("SVM-输出测试集的准确率为:", model.score(x_test, y_test))
    # 原始结果与预测结果进行对比
    show_accuracy(model.predict(x_train), y_train, 'traing data')
    show_accuracy(model.predict(x_test), y_test, 'testing data')


# 聚类算法
def cluster():
    write_to_file()
    data_Storage, data_Memory, data_Price, data_Sales, phone_name = loadData('D:/SuNing_BigData.txt')
    # 指定聚类中心个数
    km_Storage = KMeans(n_clusters=7)  # 储存 2 16 32 64 128 256 512
    km_Memory = KMeans(n_clusters=5)  # 内存  1-3 4 6 8 12
    km_Price = KMeans(n_clusters=4)  # 价格 千元机 中端机 旗舰机 土豪机
    km_Sales = KMeans(n_clusters=2)  # 销量 低   中   高
    # 计算簇的中心并且预测每个样本对应的簇类别
    label_Storage = km_Storage.fit_predict(data_Storage)
    label_Memory = km_Memory.fit_predict(data_Memory)
    label_Price = km_Price.fit_predict(data_Price)
    label_Sales = km_Sales.fit_predict(data_Sales)
    # 计算簇的中心点
    meanScore_Storage = np.sum(km_Storage.cluster_centers_, axis=1)
    meanScore_Memory = np.sum(km_Memory.cluster_centers_, axis=1)
    meanScore_Price = np.sum(km_Price.cluster_centers_, axis=1)
    meanScore_Sales = np.sum(km_Sales.cluster_centers_, axis=1)

    print(meanScore_Storage)
    print(meanScore_Memory)
    print(meanScore_Price)
    print(meanScore_Sales)
    # 分类簇
    Cluster_Storage = [[], [], [], [], [], [], []]  # 储存分类簇
    CLuster_Memory = [[], [], [], [], []]
    CLuster_Price = [[], [], [], []]
    CLuster_Sales = [[], []]
    # 向标签簇中添加
    for i in range(len(phone_name)):
        Cluster_Storage[label_Storage[i]].append(phone_name[i])
        CLuster_Memory[label_Memory[i]].append(phone_name[i])
        CLuster_Price[label_Price[i]].append(phone_name[i])
        CLuster_Sales[label_Sales[i]].append(phone_name[i])
    # print(nameCluster)
    # 智能手机存储占比
    phone_Storage = {'2G': 0, '16G': 0, '32G': 0, '64G': 0, '128G': 0, '256G': 0, '512G': 0}
    # 内存占比
    phone_Memory = {'2G': 0, '4G': 0, '6G': 0, '8G': 0, '12': 0}
    phone_Price = {'千元机': 0, '中端机': 0, '旗舰机': 0, '机皇': 0}
    for i in range(len(Cluster_Storage)):
        print("存储大小:{}G".format(int(round(meanScore_Storage[i]))))
        print(Cluster_Storage[i])
        phone_Storage[int(round(meanScore_Storage[i])).__str__() + 'G'] = len(Cluster_Storage[i])
    for i in range(len(CLuster_Memory)):
        print("内存大小:{}G".format(int(round(meanScore_Memory[i]))))
        print(CLuster_Memory[i])
        phone_Memory[int(round(meanScore_Memory[i])).__str__() + 'G'] = len(CLuster_Memory[i])
    for i in range(len(CLuster_Price)):
        print("价格:{}".format(int(round(meanScore_Price[i]))))
        print(CLuster_Price[i])
        if int(round(meanScore_Price[i])) < 1500:
            phone_Price["千元机"] = len(CLuster_Price[i])
        elif int(round(meanScore_Price[i])) < 4000:
            phone_Price["中端机"] = len(CLuster_Price[i])
        elif int(round(meanScore_Price[i])) < 6000:
            phone_Price["旗舰机"] = len(CLuster_Price[i])
        elif int(round(meanScore_Price[i])) > 6000:
            phone_Price["机皇"] = len(CLuster_Price[i])
    for i in range(len(CLuster_Sales)):
        print("销量:{}".format(int(round(meanScore_Sales[i]))))
        print(CLuster_Sales[i])

        #     可视化
        # 生成手机储存饼图
        from pyecharts import Pie

        attr_Storage = ['2G', '16G', '32G', '64G', '128G', '256G', '512G']
        attr_Memory = ['2G', '4G', '6G', '8G', '12G']
        attr_Price = ['千元机', '中端机', '旗舰机', '土豪机']
        iphone_Storage = [phone_Storage['2G'], phone_Storage['16G'], phone_Storage['32G'], phone_Storage['64G'],
                          phone_Storage['128G'], phone_Storage['256G'], phone_Storage['512G']]
        iphone_Memory = [phone_Memory['2G'], phone_Memory['4G'], phone_Memory['6G'], phone_Memory['8G'],
                         phone_Memory['12G']]
        iphone_Price = [phone_Price['千元机'], phone_Price['中端机'], phone_Price['旗舰机'], phone_Price['机皇']]
        pie = Pie(title_pos='center', width=900)
        pie.add('手机存储分类', attr_Storage, iphone_Storage, center=[25, 40], radius=[0, 25], is_label_show=True)
        pie.add('手机内存分类', attr_Memory, iphone_Memory, center=[75, 40], radius=[0, 25], is_label_show=True)
        pie.add('手机价格分类', attr_Price, iphone_Price, center=[25, 80], radius=[0, 25], is_label_show=True)

        # pie.show_config()
        pie.render(path='./phone_storage.html')

        return int(round(meanScore_Sales[i]))


#    分类算法
def svc(i):
    write_to_file2(i)
    data, sales = loadData2('D:/SuNing_BigData2.txt')
    x, y = data, sales
    x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, random_state=1, test_size=0.3)
    # 模型训练
    # sc  数据标准化 clf
    clf = svm.SVC(kernel='rbf',  # 核函数
                  gamma=0.1,
                  decision_function_shape='ovo',  # one vs one 分类问题
                  C=0.8)
    clf.fit(x_train, y_train)  # 训练

    print_accuracy(clf, x_train, y_train, x_test, y_test)


if __name__ == '__main__':
    # 数据清洗
    extract_mongo()
    # 聚类算法
    i = cluster()
    # 分类算法
    svc(i)
