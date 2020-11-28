# =============================================================================
# 目標: 
# 1. 探討兩個字之間, 是否存在某種關係
#    例如：某些字比較容易一起出現, 這些字一起出現時, 可能帶有某種訊息。

# http://cpmarkchang.logdown.com/posts/195584-natural-language-processing-pointwise-mutual-information
# =============================================================================
from pymongo import MongoClient
from collections import defaultdict
import pandas as pd
import numpy as np
import vsm



START_TOKEN = '<START>'
END_TOKEN = '<END>'


def distinct_words(corpus):
    corpus_words = []
    num_corpus_words = -1
    
    word_dict = defaultdict(int)
    for doc in corpus:
        for w in doc:
            word_dict[w] += 1

    corpus_words = sorted([key for key in word_dict])
    num_corpus_words = len(word_dict)

    return corpus_words, num_corpus_words


def compute_co_occurrence_matrix(corpus, window_size=4):
    words, num_words = distinct_words(corpus)
    M = None
    word2Ind = {}
    
    #定義一個空的詞共現矩陣，這裡採用零矩陣，因爲M爲對稱陣，所以尺寸爲num_words * num_words
    M = np.zeros(shape=(num_words, num_words), dtype=np.int32)

    #建立words中詞和索引的映射關係，將其存到字典word2Int
    for i in range(num_words):
        word2Ind[words[i]] = i

    #對corpus中的每一部分分別進行處理
    for sent in corpus:
        for p in range(len(sent)):
            #找到當前sent中的詞在word2Ind中的索引
            ci = word2Ind[sent[p]]

            #前
            #因爲某些位置前面詞的個數可能會小於window_size，所以如果個數小與window_size就從頭開始
            for w in sent[max(0, p-window_size) : p]:
                wi = word2Ind[w]
                M[ci][wi] += 1 

            #後
            for w in sent[p+1 : p+1+window_size]:
                wi = word2Ind[w]
                M[ci][wi] += 1
    # ------------------
    
    numpy_data = M
    M_with_name = pd.DataFrame(data=numpy_data, index=word2Ind.keys(), columns=word2Ind.keys())
    
    return M, word2Ind, M_with_name


def get_mongodb_row(collection_name, myquery):
    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db[collection_name]
    cursor = collection.find(myquery, {"Question":1, "Q_WS":1, "Category":1, "_id":1})

    Question_list = []
    Q_WS_list = []
    Category_list = []
    AllFields_list = []
    
    for row in cursor:
        Question_list.append(row['Question'])
        Q_WS_list.append(row['Q_WS'])
        Category_list.append(row['Category'])
        AllFields_list.append((row["Question"], row["Q_WS"], row["Category"], row["_id"]))
        
    return Question_list, Q_WS_list, Category_list, AllFields_list

Q_lst00, Q_WS_lst00, Cat_lst00, All_lst00 = get_mongodb_row('FAQ', {})




# Define toy corpus1
# test_corpus1 = ["請問 如何 辦理 校友證 ？".split(" "), "如何 申請 辦理 校友證 ？".split(" ")]

for doc in Q_WS_lst00:
    doc.insert(0, START_TOKEN)
    doc.insert(len(doc), END_TOKEN)
    # print(doc)
# print(Q_WS_lst00[0])
    
test_corpus1 = Q_WS_lst00



# -------------------------------------------
test_corpus_words1, num_corpus_words1 = distinct_words(test_corpus1)
M1, word2Ind1, M1_with_name = compute_co_occurrence_matrix(test_corpus1, window_size=4)
#print('Matrix (Word X Word): \n{}'.format(M1_with_name))
"""
Matrix (Word X Word): 
     如何  校友證  申請  請問  辦理  ？
如何    0    1   1   1   2  0
校友證   1    0   1   0   2  2
申請    1    1   0   0   1  0
請問    1    0   0   0   1  0
辦理    2    2   1   1   0  2
？     0    2   0   0   2  0
"""



# -------------------------------------------
### Distributional neighbors

# The neighbors function in vsm is an investigative aide. 
# For a given word w, it ranks all the words in the vocabulary according to their distance from w, as measured by distfunc (default: vsm.cosine).

# cosine (No L2-norm)
a = vsm.neighbors('上網', M1_with_name, distfunc=vsm.cosine)
print('cosine (No L2-norm):\n{}\n\n'.format(a))
#print(a.index, a.values)
# 上網       0.000000 *** 數值小，距離近
# 網路     0.158629
# 使用     0.196703
# 內      0.199141
# 服務     0.202177
#            ...   




# euclidean + L2-norm
df_normed = M1_with_name.apply(vsm.length_norm, axis=1)
b = vsm.neighbors('上網', df_normed, distfunc=vsm.euclidean)
print('euclidean + L2-norm:\n{}\n\n'.format(b.head()))
# 上網       0.000000 *** 數值小，距離近
# 上網    0.000000
# 網路    0.563257
# 使用    0.627222
# 內     0.631095
# 服務    0.635889
#            ...   




# re-weighting => PMI + cosine (No L2-norm)
M1_pmi = vsm.pmi(M1_with_name)
c = vsm.neighbors('如何', M1_pmi, distfunc=vsm.cosine)
print('PMI + cosine (No L2-norm):\n{}\n\n'.format(c))
print(c.index.tolist()[:20], c.values.tolist()[:20])
# *** 數值小，距離近
# ['如何', '？', '<START>', '<END>', '該', '借用', '申請', '?', '查詢', '使用', '辦理', '處理', '要', '請問', '的', '圖書館', '，', '圖書', '取得', '得知'] 
# [0.0, 0.6943325635311057, 0.7051060571945668, 0.7472843590997593, 0.7961379141013549, 0.7984945372426184, 0.7992595903804213, 0.8032097604052673, 0.8215896489914758, 0.8216853668566528, 0.8301133347958569, 0.8347487349268697, 0.837620602553047, 0.8480907943828226, 0.8504429114394779, 0.8518820668884841, 0.8555783446812177, 0.8572719771295936, 0.8655600277281652, 0.8674168794518423]
