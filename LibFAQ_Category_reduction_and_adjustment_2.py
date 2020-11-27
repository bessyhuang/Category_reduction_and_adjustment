# =============================================================================
# 目標: 
# 1. 將 LibFAQ_Category_reduction_and_adjustment_1.py 的結果 (.csv) update to MongoDB

# PS. "false" ：未分類的類別
# =============================================================================
from pymongo import MongoClient
import csv
import os



directory = './LibFAQ_Category_reduction_and_adjustment/'
if not os.path.isdir(directory):
    os.mkdir(directory)
    


doc_list = []
with open(directory + 'Library_Adjusted_Question_Category.csv', newline='', encoding='utf-8') as csvfile:
    rows = csv.reader(csvfile)
    for row in rows:
        doc_list.append(row)
    
    
    
client = MongoClient('localhost', 27017)
db = client['Library']
collection = db['FAQ']



def get_mongodb_row():
    cursor = collection.find({}, {"Question":1, "Q_WS":1, "Category":1, "_id":1})

    id_list = []
    Question_list = []
    Q_WS_list = []
    Category_list = []
    AllFields_list = []
    
    
    for row in cursor:
        id_list.append(row["_id"])
        Question_list.append(row['Question'])
        Q_WS_list.append(row['Q_WS'])
        Category_list.append(row['Category'])
        AllFields_list.append((row["Question"], row["Q_WS"], row["Category"], row["_id"]))
         
    return id_list, Question_list, Q_WS_list, Category_list, AllFields_list



id_list, Question_list, Q_WS_list, Category_list, AllFields_list = get_mongodb_row()


col_name = doc_list[0]
print(col_name)



for ID in id_list:
    for query_id, query, query_seg, query_category, doc_id, doc, doc_seg, doc_category, similarities, adjusted_Category, adjusted_Category_count, query_CategoryName_count in doc_list:
        if query_id == ID:
            collection.update_many({ "_id" : ID },
                                   { "$set" : { "adjusted_Category" : adjusted_Category } }, upsert=True)
