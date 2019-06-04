
import xlrd
from recommender import UserCF, ItemCF, ContentBased
from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_squared_error
from math import sqrt
import numpy as np
import time


# 获取用于content_based的数据
texts_wb = xlrd.open_workbook('./100_top_shops_cate.xls')
texts_ws = texts_wb.sheets()[0]
rows = texts_ws.nrows
cols = texts_ws.ncols

# 读取shop_cates数据
shop_names = list()
for row in range(rows):
    shop_names.append(texts_ws.cell(row, 0).value)

shop_cates = list()
for row in range(rows):
    shop_cates.append(texts_ws.cell(row, 1).value)


#rows = 14393
rows = 14393
cols = 98

# 获取原本的data
wb = xlrd.open_workbook('100_top_shops_rating.xls')
ws = wb.sheets()[0]

rating = {}
# 读取excel数据至dict
for row_index in range(rows):
    if row_index != 0:
        username = ws.cell(row_index, 0).value
        rating[username] = {}
        for col_index in range(cols):
            if col_index != 0:
                shop_name = ws.cell(0, col_index).value
                cell_val = ws.cell(row_index, col_index).value
                if cell_val != '':
                    rating[username][shop_name] = cell_val


# 获取用来测试的data
wb2 = xlrd.open_workbook('100_top_shops_rating-test.xls')
ws2 = wb2.sheets()[0]

rating_test = {}
for row_index in range(rows):
    if row_index != 0:
        username = ws2.cell(row_index, 0).value
        rating_test[username] = {}
        for col_index in range(cols):
            if col_index != 0:
                shop_name = ws2.cell(0, col_index).value
                cell_val = ws2.cell(row_index, col_index).value
                if cell_val != '':
                    rating_test[username][shop_name] = cell_val


all_canteen = shop_names
true_set = rating
test_set = rating_test

# 将所有true_set没有评分的用0补上
for key1 in true_set:
    temp = {}
    for m in all_canteen:
        if m in true_set[key1].keys():
            temp[m] = true_set[key1][m]
        else:
            temp[m] = 0
    true_set[key1] = temp


# 提取将dict中的评分，并存成list
def set_to_list(s):
    lst = []
    for key1 in s:
        temp = []
        for key2 in s[key1]:
            value = key2[1]
            temp.append(value)
        lst.append(temp)
    return lst


# 指定测试的用户
test_user = ['Choco814','annabelle.tinko','lamlamyuk','eating kingdom','falav','giannhui','matthew_wai','Susansyleung',
             'eat.play','蒙奇奇','占士邦oo7','kwaiying1016','bonbon妮','supersuperjengs']
             #'nc222','jackie.ip.395','foodiett','estherltt']


def predicted_by_usercf():
    # 还原数据集
   # true_set = rating
    #test_set = rating_test
    time_start = time.time()
    print("=========================== User CF ============================")
    # 对测试的用户进行predict
    for user in test_user:
        userCf = UserCF(test_set)
        for a in userCf.get_recommend(user):
            test_set[user][a[1]] = round(a[0],2)

    # 只截取测试的用户，并按顺序排序
    test_true_set = {}
    for u in test_user:
        test_true_set[u] = true_set[u]
        test_true_set[u] = sorted(test_true_set[u].items(), key=lambda d:d[0])

    # 只截取测试用户，并按顺序排序
    test_test_set = {}
    for u in test_user:
        test_test_set[u] = test_set[u]
        test_test_set[u] = sorted(test_test_set[u].items(), key=lambda d:d[0])

    test_list = set_to_list(test_test_set)
    true_list = set_to_list(test_true_set)

    # 获取rmse评分
    def rmse(prediction, ground_truth):
        prediction = np.mat(prediction)
        ground_truth = np.mat(ground_truth)
        prediction = prediction[ground_truth.nonzero()].flatten()
        ground_truth = ground_truth[ground_truth.nonzero()].flatten()
        return sqrt(mean_squared_error(prediction, ground_truth))

    print('【User-based CF RMSE】 : ' + str(rmse(test_list, true_list)))
    time_end = time.time()
    print('time cost', time_end - time_start)


def predicted_by_itemcf():
    time_start = time.time()
    # 还原数据集
    true_set = rating
    test_set = rating_test

    temp ={}
    for i,u in zip(range(150),test_set):
        temp[u] = test_set[u]
    test_set = temp

    print("=========================== Item CF ============================")
    # 对test_set进行predict
    for item in all_canteen:
        itemCf = ItemCF(test_set)
        for a in itemCf.get_recommend(item):
            test_set[a[1]][item] = a[0]

    # 因为只对比测试集的值，所以只取test的值，并按顺序排序
    test_true_set = {}
    for u in test_user:
        test_true_set[u] = true_set[u]
        test_true_set[u] = sorted(test_true_set[u].items(), key=lambda d: d[0])

    # 因为只对比测试集的值，所以只取test的值，并按顺序排序
    test_test_set = {}
    for u in test_user:
        test_test_set[u] = test_set[u]
        test_test_set[u] = sorted(test_test_set[u].items(), key=lambda d: d[0])

    test_list = set_to_list(test_test_set)
    true_list = set_to_list(test_true_set)

    # print("test matrix:")
    # for t in test_list:
    #     print(t)
    # print("\ntrue matrix:")
    # for t in true_list:
    #     print(t)

    # 获取rmse评分
    def rmse(prediction, ground_truth):
        prediction = np.array(prediction)
        ground_truth = np.array(ground_truth)
        prediction = prediction[ground_truth.nonzero()].flatten()
        ground_truth = ground_truth[ground_truth.nonzero()].flatten()
        return sqrt(mean_squared_error(prediction, ground_truth))

    print('【Item-based CF RMSE】 : ' + str(rmse(test_list, true_list)))
    time_end = time.time()
    print('time cost', time_end - time_start)


def predicted_by_contentBased():
    time_start = time.time()
    # 还原数据集
    true_set = rating
    test_set = rating_test
    print("=========================== Content Based ============================")
    for user in test_user:
        contentBased = ContentBased(test_set, shop_names, shop_cates)
        for a in contentBased.get_recommend(user):
            test_set[user][a[1]] = round(a[0],2)

    # 只截取test的值，并按顺序排序
    test_true_set = {}
    for u in test_user:
        test_true_set[u] = true_set[u]
        test_true_set[u] = sorted(test_true_set[u].items(), key=lambda d:d[0])

    # 只截取test的值，并按顺序排序
    test_test_set = {}
    for u in test_user:
        test_test_set[u] = test_set[u]
        test_test_set[u] = sorted(test_test_set[u].items(), key=lambda d:d[0])

    test_list = set_to_list(test_test_set)
    true_list = set_to_list(test_true_set)


    # get RMSE
    def rmse(prediction, ground_truth):
        prediction = np.mat(prediction)
        ground_truth = np.mat(ground_truth)
        prediction = prediction[ground_truth.nonzero()].flatten()
        ground_truth = ground_truth[ground_truth.nonzero()].flatten()
        return sqrt(mean_squared_error(prediction, ground_truth))

    print('【Content Based RMSE】: ' + str(rmse(test_list, true_list)))
    time_end = time.time()
    print('time cost', time_end - time_start)

    # print("\ntest matrix:")
    # for t in test_list:
    #     print(t)
    # print("\ntrue matrix:")
    # for t in true_list:
    #     print(t)

predicted_by_usercf()
print("\n")
predicted_by_itemcf()
print("\n")
predicted_by_contentBased()
