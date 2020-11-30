# =============================================================================
# 目標: 
# 1. 縮減 LibraryFAQ 的總類別數量 (將相似的問句，賦予統一的大類類別) TF-IDF + cosine_similarity
# 2. 校正 LibraryFAQ 問句的類別

# PS. "false" ：未分類的類別
# =============================================================================
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from collections import Counter, defaultdict
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

def Get_adjusted_category(candidate_category_dict, candidate_category_list):
    max_count_category = max(candidate_category_dict, key=candidate_category_dict.get)
    
    Counter_candidate_category_list = Counter(candidate_category_list)
    max_frequency_category = max(Counter_candidate_category_list, key=Counter_candidate_category_list.get)
    #print('最多 Question 的類別: {}\n最多候選的類別: {}'.format(max_count_category, max_frequency_category))
    #print('candidate_category_list: {}\n=> Counter: {}'.format(candidate_category_list, Counter_candidate_category_list))
    
    #print('candidate_category_dict: {}'.format(candidate_category_dict))
    
    if ('false' in candidate_category_dict) == True or ('false' in candidate_category_list) == True:
        # 候選類別裡 含有'false'以及其他多個類別
        if len(Counter_candidate_category_list) > 2:
            del candidate_category_dict['false']
            second_count_category = max(candidate_category_dict, key=candidate_category_dict.get)
            
            del Counter_candidate_category_list['false']
            second_frequency_category = max(Counter_candidate_category_list, key=Counter_candidate_category_list.get)
            
            #print('第二多 Question 的類別: {}\n第二多候選的類別: {}'.format(second_count_category, second_frequency_category))
            
            return second_count_category #second_count_category second_frequency_category
        
        # 候選類別裡 含有'false'以及其他一個類別
        elif len(Counter_candidate_category_list) == 2:
            del candidate_category_dict['false']
            second_count_category = max(candidate_category_dict, key=candidate_category_dict.get)
            
            del Counter_candidate_category_list['false']
            second_frequency_category = max(Counter_candidate_category_list, key=Counter_candidate_category_list.get)
            
            return second_frequency_category #second_count_category second_frequency_category
            
        # 候選類別裡 只有 'false'
        else:
            return max_count_category
            
    else:
        # 候選類別裡 (沒有'false') 但含有其他多個類別
        if len(Counter_candidate_category_list) > 2:
            return max_frequency_category
        
        # 候選類別裡 (沒有'false') 只有一個或兩個類別
        else:
            return max_count_category



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



candidate_category_list = list()
candidate_category_dict = dict()
rawCategory_index_adjustCategory = []

count = 0
for query in docs_seg00:
    query_CategoryName = Category_list00[count]
    
    # ============ 計算相似度 ============
    print("=======================================")
    print('\n第 {} 筆\t問句: {}\t類別: {}\n'.format(count, query, query_CategoryName))
    query_count_vector = vectorizer.transform([query])
    query_tfidf = tfidf_transfomer.transform(query_count_vector)
    similarities = cosine_similarity(query_tfidf, docs_tfidf00).flatten()
    
    results = zip(id_list00, Question_list00, docs_seg00, Category_list00, similarities)
    results = sorted(results, key=lambda x: x[4], reverse=True)
    
    for i in range(50):
        if results[i][4] >= 0.75:
            doc_category = results[i][3]
            candidate_category_list.append(doc_category)
            # candidate_category_dict { 候選類別： 類別內的 Question 數量 }
            candidate_category_dict[doc_category] = doc_frequency[doc_category]
            print('Top' + str(i+1), results[i][4], '\tdoc_類別：', doc_category)
            print('doc:', results[i][1])
            print()
            """
            if Question_list00[count] == '如何才能擔任圖書館志工？':
                print('\n\n\n第 {} 筆\t問句: {}\t類別: {}\n'.format(count, query, query_CategoryName))
                print('Top' + str(i+1), results[i][4], '\tdoc_類別：', doc_category)
                print('doc:', results[i][1], candidate_category_dict, candidate_category_list)
                print()
            """
            query_id = AllFields_list00[count][3]
            row = [query_id, Question_list00[count], query, query_CategoryName, results[i][0], results[i][1], results[i][2], doc_category, results[i][4]]
            FINAL_LIST.append(row)
    
    adjusted_Category = Get_adjusted_category(candidate_category_dict, candidate_category_list)
    rawCategory_index_adjustCategory.append([query_id, query_CategoryName, adjusted_Category])
    print('>>>', [query_CategoryName, count, adjusted_Category])
    print()
    
    candidate_category_list.clear()
    candidate_category_dict.clear()
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
    'doc_category': results[i][3] or doc_category, 
    'similarities': results[i][4]
}
"""



### 更新 FINAL_LIST（加入新欄位至原本 FINAL_LIST）
rowID_adjustedCategory_dict = defaultdict(str)
for query_id, rawCat, adjCat in rawCategory_index_adjustCategory:
    temp_cat = set()
    temp_cat.add(adjCat)
    rowID_adjustedCategory_dict[query_id] = temp_cat
#print('+++', rowID_adjustedCategory_dict['5f3e14e1a9a4c23528871d34']) #Output：{'成為志工'}



for i in range(len(FINAL_LIST)):
    FINAL_LIST_query_key = FINAL_LIST[i][0]
    if FINAL_LIST_query_key in rowID_adjustedCategory_dict:
        #print(list(rowID_adjustedCategory_dict[FINAL_LIST_query_key]))
        FINAL_LIST[i].append(list(rowID_adjustedCategory_dict[FINAL_LIST_query_key])[0]) 			#adjusted_Category
        FINAL_LIST[i].append(doc_frequency[list(rowID_adjustedCategory_dict[FINAL_LIST_query_key])[0]])	#adjusted_Category_count
        FINAL_LIST[i].append(doc_frequency[FINAL_LIST[i][3]]) 				#query_CategoryName_count
        
        if FINAL_LIST[i][3] != FINAL_LIST[i][9]:
            print(FINAL_LIST[i])
        
    else:
        FINAL_LIST[i].append(FINAL_LIST[i][3]) 			#adjusted_Category == query_CategoryName
        FINAL_LIST[i].append(doc_frequency[FINAL_LIST[i][3]])	#adjusted_Category_count == query_Category_count
        FINAL_LIST[i].append(doc_frequency[FINAL_LIST[i][3]]) 	#query_CategoryName_count



with open(directory + 'Library_Adjusted_Question_Category.csv', 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['query_id', 'query', 'query_seg', 'query_category', 
                     'doc_id', 'doc', 'doc_seg', 'doc_category', 'similarities',
                     'adjusted_Category', 'adjusted_Category_count', 'query_CategoryName_count'])
    for row in FINAL_LIST:
        writer.writerow(row)
csvfile.close()
