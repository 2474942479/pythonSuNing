# 加载数据
import numpy as np
from pymongo import MongoClient
from sklearn import model_selection, svm


def write_to_file():
    client = MongoClient("mongodb://root:root@localhost:27017")
    db = client.BigData
    for item in db.phone.find({}):
        if item.get("Sales") > "10000":
            Sales = "1"
        else:
            Sales = '0'
        price = item.get("price")
        configure = item.get("configure")
        with open('D:/SuNing_BigData2.txt', 'a', encoding='utf-8') as f:
            f.write(Sales + ',' + price + ',' + configure + '\n')
            f.close()


def loadData(filePath):
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


def print_accuracy(model, x_train, y_train, x_test, y_test):
    print('SVM-输出训练集的准确率为:', model.score(x_train, y_train))
    print("SVM-输出测试集的准确率为:", model.score(x_test, y_test))
    # 原始结果与预测结果进行对比
    show_accuracy(model.predict(x_train), y_train, 'traing data')
    show_accuracy(model.predict(x_test), y_test, 'testing data')


if __name__ == '__main__':
    write_to_file()
    data, sales = loadData('D:/SuNing_BigData2.txt')
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

