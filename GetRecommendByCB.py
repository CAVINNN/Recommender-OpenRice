import xlrd
from recommender import ContentBased

texts_wb = xlrd.open_workbook('./100_top_shops_cate.xls')
texts_ws = texts_wb.sheets()[0]
rows = texts_ws.nrows
cols = texts_ws.ncols

# import shop_cates data
shop_names = list()
for row in range(rows):
    shop_names.append(texts_ws.cell(row, 0).value)

shop_cates = list()
for row in range(rows):
    shop_cates.append(texts_ws.cell(row, 1).value)

# import rating data
wb = xlrd.open_workbook('./100_top_shops_rating.xls')
ws = wb.sheets()[0]
rows = ws.nrows
cols = ws.ncols

rating = {}

# import excel rating to dict
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

contentBased = ContentBased(rating, shop_names, shop_cates)
print(contentBased.get_recommend('sindymelody'))
