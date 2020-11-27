from pymongo import MongoClient
import os.path
import pickle
import re



directory = './LibraryCommonWords/'
if not os.path.isdir(directory):
    os.mkdir(directory)
    
    
    
def get_mongodb_row(collection_name):
    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db[collection_name]

    cursor = collection.find({}, {"Question":1, "Answer":1, "_id":1})

    #Question list
    Q_list = []

    #Question, Answer list
    QA_list = []

    #Question, Answer, _id list
    AllFields_list = []

    for row in cursor:
        Q_list.append(row['Question'])
        QA_list.append(row['Question'] + row['Answer'])
        AllFields_list.append((row["Question"], row["Answer"], row["_id"]))

    return Q_list, QA_list, AllFields_list



# ---------------我是分隔線-----------------
Q_list, QA_list, AllFields_list = get_mongodb_row("FAQ")

# 楊斯丞的作法：問題部分
# Q_Final = []
# for i in Q_list:
#     a = re.findall('「(.*?)」' or '『(.*?)』', i)
#     # if a == []:
#     #     a = re.findall('『(.*?)』',i)
#     Q_Final.append(a)


# 問題+答案部分
QA_Final = []
for row in QA_list:
    a = re.findall('「([a-zA-Z\s]*?)」', row)
    b = re.findall('「([\u4e00-\u9fa5]*?)」', row)

    c = re.findall('『([a-zA-Z\s]*?)』', row)
    d = re.findall('『([\u4e00-\u9fa5]*?)』', row)

    e = re.findall('《([a-zA-Z\s]*?)》', row)
    f = re.findall('《([\u4e00-\u9fa5]*?)》', row)

    g = re.findall('"([a-zA-Z\s]*?)"', row)
    h = re.findall('"([\u4e00-\u9fa5]*?)"', row)

    i = re.findall('【([a-zA-Z\s]*?)】', row)
    j = re.findall('【([\u4e00-\u9fa5]*?)】', row)

    k = re.findall('（([a-zA-Z\s]*?)）', row)
    l = re.findall('（([\u4e00-\u9fa5]*?)）', row)

    m = re.findall('〔([\u4e00-\u9fa5]*?)〕', row)

    n = re.findall('〝([\u4e00-\u9fa5]*?)〞', row)

    o = re.findall('\[([a-zA-Z\s]*?)\]', row)
    p = re.findall('\[([\u4e00-\u9fa5]*?)\]', row)

    keywords_list = a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p
    QA_Final.append((row, keywords_list))


# Row_data + keywords
with open("./LibraryCommonWords/QA_plus_keywords.txt", 'w', encoding='utf-8') as f:
    index = 0
    for i in QA_Final:
        index += 1
        row = i[0]
        keyword = i[1]
        f.write('{} : {}\n{}\n\n'.format(index, row, keyword))



# keyword 出現次數統計
keyword_dict = dict()
for qa, keywords_list in QA_Final:
    #print('===', qa, keywords_list)
    if keywords_list == []:
        pass
    else:
        for k in keywords_list:
            if len(k) == 1:
                pass
            elif k in keyword_dict:
                keyword_dict[k] += 1
            else:
                keyword_dict[k] = 1

for key in keyword_dict:
    #print(key)
    if " " in key:
        keyword_dict[key] = 0
    elif keyword_dict[key] == 1 and len(key) > 5:
        keyword_dict[key] = 0

custom_words_list = ['本校', '本館', '外校', '校外', '校友', '校內', '線上', '到館', '入館', '館內', '館外', '體外', '全國', '跨校', '跨館', '回館', '贈書', '借書', '取件', '系所', '取書', '未還', '紙本', '找不到', '借閱證', '借書證', '無線網路', '無線上網', '研究小間', '文獻傳遞', '幾片', '多長', '幾本', '幾天', '查不到', '還書箱', '為何', '未取', '進館', '多快', '未繳', '幾冊', '幾件', '商業周刊', '天下雜誌', '科學人雜誌', '新書', '每人', '最高', '幾次', '整個', '自助借書機', '各國', '每年', '全國', '還沒', '幾種', '掉了', '當月', '當週', '找書', '各類', '放在', '各系', '架上', '借的書', '非書資料', '每個', '數個']

for w in custom_words_list:
    keyword_dict[w] = 2
    


with open("./LibraryCommonWords/QA_keywords_unique.txt", 'w', encoding='utf-8') as f:
    index = 0
    for k in keyword_dict:
        index += 1
        f.write('{}\t【{}】 ： {} 次數\n'.format(index, k, keyword_dict[k]))



with open("./wikiDict/corpus_wikidict_PAGETITLE.pkl", 'rb') as fp:
    wiki_dict = pickle.load(fp)
fp.close()



wiki_dict.update(keyword_dict)
with open("./LibraryCommonWords/WikiDict_plus_QAkeywordsDict.pkl", 'wb') as fp:
    pickle.dump(wiki_dict, fp)
fp.close()
