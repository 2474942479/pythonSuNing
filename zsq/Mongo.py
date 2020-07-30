import re

from bson import ObjectId
from pymongo import *

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
                        '$set': {"configure": "1,"+result3.group().replace("G", "").replace("B", "").replace(" ", "")}})
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
                            "configure": result.group().replace("g", "").replace("G", "").replace("B", "").replace(" ", "").replace("+",
                                                                                                                   ",")}})
        print(result)
print(db.phone2.find({"title": {"$ne": ""}}).count())
client.close()
