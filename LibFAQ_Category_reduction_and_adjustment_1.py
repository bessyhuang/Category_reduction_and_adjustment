# =============================================================================
# 目標: 
# 1. 縮減 LibraryFAQ 的總類別數量 (將相似的問句，賦予統一的大類類別) TF-IDF + cosine_similarity
# 2. 校正 LibraryFAQ 問句的類別

# PS. "false" ：未分類的類別
# =============================================================================
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from collections import Counter
import pandas as pd
import csv
import os



directory = './LibFAQ_Category_reduction_and_adjustment/'
if not os.path.isdir(directory):
    os.mkdir(directory)
    
    
def get_mongodb_row(collection_name, myquery):
    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db[collection_name]
    cursor = collection.find(myquery, {"Question":1, "Q_WS":1, "Category":1, "_id":1})

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

def seg_CONCAT(Q_WS_list):
    docs_seg = []
    
    for doc in Q_WS_list:
        docs_seg.append('_'.join(doc))
        
    return docs_seg

def BuildVec_for_count_each_term_in_each_doc(docs_seg):
    # Step1: 建立計算每個term在doc有多少個
    text_count_vector = vectorizer.fit_transform(docs_seg)
    tf_vector = text_count_vector.toarray()
    
    # print('============全部字詞=============')
    # print(vectorizer.get_feature_names())
    
    return text_count_vector, tf_vector

def Build_TFIDF(text_count_vector):
    # Step2: 計算TFIDF
    docs_tfidf = tfidf_transfomer.fit_transform(text_count_vector)
    df = pd.DataFrame(docs_tfidf.T.toarray(), index=vectorizer.get_feature_names())
    
    return docs_tfidf, df



tfidf_transfomer = TfidfTransformer()
vectorizer = CountVectorizer(tokenizer=lambda x: x.split("_"))


id_list00, Question_list00, Q_WS_list00, Category_list00, AllFields_list00 = get_mongodb_row('FAQ', {}) 
docs_seg00 = seg_CONCAT(Q_WS_list00)
text_count_vector00, tf_vector00 = BuildVec_for_count_each_term_in_each_doc(docs_seg00)
docs_tfidf00, df00 = Build_TFIDF(text_count_vector00)



# 計算 該類別下 共有幾筆問句 (作為併入哪一個類別的標準)
doc_frequency = Counter(Category_list00)
#print(doc_frequency)



# FINAL_LIST ：最後輸出 csv 或 更新 mongodb 的資料
FINAL_LIST = [] 

count = 0
for query in docs_seg00:
    query_CategoryName = Category_list00[count]
    #print('第 {} 筆\t\t問句: {}\t類別: {}'.format(count, query, query_CategoryName))
    
    # ============ 計算相似度 ============
    print("=======================================")
    query_count_vector = vectorizer.transform([query])
    query_tfidf = tfidf_transfomer.transform(query_count_vector)
    similarities = cosine_similarity(query_tfidf, docs_tfidf00).flatten()
    
    results = zip(id_list00, Question_list00, docs_seg00, Category_list00, similarities)
    results = sorted(results, key=lambda x: x[4], reverse=True)
    
    for i in range(50):
        if results[i][4] >= 0.85:
            print('Top' + str(i+1), results[i][4], '\tdoc_類別：', results[i][3])
            print('doc:', results[i][1], results[i][2])
            print()

            query_id = AllFields_list00[count][3]
            row = [query_id, Question_list00[count], query, query_CategoryName, results[i][0], results[i][1], results[i][2], results[i][3], results[i][4]]
            FINAL_LIST.append(row)
            
    count += 1        

"""      
results:
{   
    'query_id': query_id, 
    'query': Question_list00[count], 
    'query_seg': query, 
    'query_category': query_CategoryName or Category_list00[count], 
    'doc_id': results[i][0], 
    'doc': results[i][1], 
    'doc_seg': results[i][2], 
    'doc_category': results[i][3], 
    'similarities': results[i][4]
}
"""



df = pd.DataFrame(FINAL_LIST, columns=['query_id', 'query', 'query_seg', 'query_category', 'doc_id', 'doc', 'doc_seg', 'doc_category', 'similarities'])
#print(FINAL_LIST, df['query_category'])



q_category = df.groupby("query_category")
#print(q_category.groups)
#print(q_category.get_group("圖書典藏位置"))



candidate_category_dict = dict()
rawCategory_index_adjustCategory = []

for group in q_category.groups:
    #print(q_category.get_group(group)['query'])
    #print('\n\n該 group 類別【 {} 】下（query_category_Name），有相似的問句，\n而這些相似的問句隸屬以下類別：{}'.format(group, q_category.get_group(group)['doc_category'].tolist()))
    
    #print('<< group index >>', q_category.get_group(group)['doc_category'].index)
    group_index = q_category.get_group(group)['doc_category'].index.tolist()
    
    for category in q_category.get_group(group)['doc_category'].tolist():
        if category == 'false' or category == '其他':
            pass
        else:
            # candidate_category_dict { 候選類別： 類別內的 Question 數量 }
            candidate_category_dict[category] = doc_frequency[category] 
    #print(candidate_category_dict)
    
    adjusted_Category = max(candidate_category_dict, key=candidate_category_dict.get)
    rawCategory_index_adjustCategory.append([group, group_index, adjusted_Category])
    print('>>>', [group, group_index, adjusted_Category])
    
    candidate_category_dict.clear()
    
    
    
### 更新 FINAL_LIST（加入新欄位至原本 FINAL_LIST）
rowID_adjustedCategory_dict = dict()
for rawCat, index, adjCat in rawCategory_index_adjustCategory:
    temp_cat = set()
    for i in index:
        temp_cat.add(adjCat)
    rowID_adjustedCategory_dict[i] = temp_cat
print(rowID_adjustedCategory_dict[5901]) #Output：{'關於借還書'}



for i in range(len(FINAL_LIST)):
    if i in rowID_adjustedCategory_dict:
        FINAL_LIST[i].append(list(rowID_adjustedCategory_dict[i])[0]) 			#adjusted_Category
        FINAL_LIST[i].append(doc_frequency[list(rowID_adjustedCategory_dict[i])[0]])	#adjusted_Category_count
        FINAL_LIST[i].append(doc_frequency[FINAL_LIST[i][3]]) 				#query_CategoryName
    else:
        FINAL_LIST[i].append(FINAL_LIST[i][3]) 			#adjusted_Category == query_CategoryName
        FINAL_LIST[i].append(doc_frequency[FINAL_LIST[i][3]])	#adjusted_Category_count == query_Category_count
        FINAL_LIST[i].append(doc_frequency[FINAL_LIST[i][3]]) 	#query_CategoryName
    



with open(directory + 'Library_Adjusted_Question_Category.csv', 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['query_id', 'query', 'query_seg', 'query_category', 
                     'doc_id', 'doc', 'doc_seg', 'doc_category', 'similarities',
                     'adjusted_Category', 'adjusted_Category_count', 'query_CategoryName_count'])
    for row in FINAL_LIST:
        writer.writerow(row)
csvfile.close()
