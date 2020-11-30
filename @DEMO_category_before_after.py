from collections import defaultdict
from pymongo import MongoClient
import pandas as pd



def get_mongodb_row(collection_name, myquery):
    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db[collection_name]
    cursor = collection.find(myquery, {"Question":1, "Q_WS":1, "Category":1, "adjusted_Category":1, "_id":1})

    Question_list = []
    Q_WS_list = []
    Category_list = []
    adjusted_Category_list = []
    AllFields_list = []
    
    for row in cursor:
        Question_list.append(row['Question'])
        Q_WS_list.append(row['Q_WS'])
        Category_list.append(row['Category'])
        adjusted_Category_list.append(row['adjusted_Category'])
        AllFields_list.append((row["Question"], row["Q_WS"], row["Category"], row['adjusted_Category'], row["_id"]))
    return Question_list, Q_WS_list, Category_list, adjusted_Category_list, AllFields_list

Question_list00, Q_WS_list00, Category_list00, adjusted_Category_list00, AllFields_list00 = get_mongodb_row('FAQ', {})



### {Category_name: index} ###
Category_dict = defaultdict(str)
index = 0
for cat_name in Category_list00:
    if cat_name in Category_dict:
        pass
    else:
        Category_dict[cat_name] = index
        index += 1
        
        
        
Q_Cat_combime = pd.DataFrame({'Q_seg': Q_WS_list00, 'Category': Category_list00, 'adjusted_Category' : adjusted_Category_list00})
CATEGORY_groupby_raw = Q_Cat_combime.groupby("Category")
raw = CATEGORY_groupby_raw.groups
# print(CATEGORY_groupby_raw.get_group("續借"))
print('\n\nCATEGORY_groupby_raw:\n', CATEGORY_groupby_raw.size())
#CATEGORY_groupby_raw: Length: 490, dtype: int64



CATEGORY_groupby_adj = Q_Cat_combime.groupby("adjusted_Category")
adj = CATEGORY_groupby_adj.groups
print('\n\nCATEGORY_groupby_adj:\n', CATEGORY_groupby_adj.size())
#CATEGORY_groupby_adj: Length: 473, dtype: int64



count = 0
for i in range(len(Category_list00)):
    if Category_list00[i] != adjusted_Category_list00[i]:
        count += 1
        #print()
        #print('Q: {}\nraw_cat: {}\t\tadj_cat: {}'.format(Question_list00[i], Category_list00[i], adjusted_Category_list00[i]))
        
print('總計調整 {} 筆 Question'.format(count))
# 總計調整 715 筆 Question

print(raw.keys() - adj.keys())
"""
{'圖書薦購', '贈送資料', '圖書推薦服務及贈書相關問題 - 贈書', '逾期/罰款', '畢業紀念冊', 
'電腦設備相關問題', ' 館藏利用', '無線網路服務', '報紙', '資料庫問題', '尋書/急編', 
'如何查詢學位論文', '學位論文問題', '贈送圖書', '遺失與賠償', '如何向圖書館推薦圖書', '閱報服務'}
"""
