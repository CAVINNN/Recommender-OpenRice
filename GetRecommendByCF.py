# coding=utf8

import xlrd
from recommender import UserCF, ItemCF

wb = xlrd.open_workbook('./100_top_shops_rating.xls')
ws = wb.sheets()[0]
rows = ws.nrows
cols = ws.ncols

rating = {}

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

userCf = UserCF(rating)
print(userCf.get_recommend('Choco814'))

# itemCf = ItemCF(rating)
# print(itemCf.get_recommend('心之食堂 Love Cafe'))
