from ckiptagger import construct_dictionary, WS, POS, NER
from pymongo import MongoClient
import pickle
import os



Q_data = []
def mongodb_Q_list(collection_name):
    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db[collection_name]
    cursor = collection.find({}, {"Question":1, "_id":0})
    for row in cursor:
        Q_data.append(row['Question'])
    return Q_data



# Load model (Use GPU)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

ws = WS("./data", disable_cuda=False)
pos = POS("./data", disable_cuda=False)
ner = NER("./data", disable_cuda=False)



# Run the WS-POS-NER pipeline
sentence_list_Q = mongodb_Q_list('FAQ')



# (Optional) Create dictionary: wikipedia
with open('./wikiDict/corpus_wikidict_PAGETITLE.pkl', 'rb') as fp:
    corpus_wikidict_PAGETITLE = pickle.load(fp)
fp.close()
dictionary1 = construct_dictionary(corpus_wikidict_PAGETITLE)

word_sentence_list = ws(sentence_list_Q[:50], 
    segment_delimiter_set = {":" ,"：" ,":" ,".." ,"，" ,"," ,"-" ,"─" ,"－" ,"──" ,"." ,"……" ,"…" ,"..." ,"!" ,"！" ,"〕" ,"」" ,"】" ,"》" ,"【" ,"）" ,"｛" ,"｝" ,"“" ,"(" ,"「" ,"]" ,")" ,"（" ,"《" ,"[" ,"『" ,"』" ,"〔" ,"、" ,"．" ,"。" ,"." ,"‧" ,"﹖" ,"？" ,"?" ,"?" ,"；" ," 　" ,"" ,"　" ,"" ,"ㄟ" ," :" ,"？" ,"〞" ,"]" ,"／" ,"=" ,"？" ," -" ,"@" ,"." ,"～" ," ：" ,"：" ,"<", ">" ," - " ,"──" ,"~~" ,"`" ,": " ,"#" ,"/" ,"〝" ,"：" ,"'" ,"$C" ,"?" ,"?" ,"*" ,"／" ,"[" ,"." ,"?" ,"-" ,"～～" ,"\""},
    recommend_dictionary = dictionary1, # 效果最好！
    #coerce_dictionary = dictionary2, # 強制字典
    )

pos_sentence_list = pos(word_sentence_list)

entity_sentence_list = ner(word_sentence_list, pos_sentence_list)


for i in range(len(word_sentence_list)):
    print(i, '\tWS:', word_sentence_list[i])
#for i in range(len(word_sentence_list)):
#    print(i, '\tPOS:', pos_sentence_list[i])
#for i in range(len(word_sentence_list)):
#    print(i, '\tNER:', entity_sentence_list[i])


""""
mydict = corpus_wikidict_PAGETITLE
myvalues = corpus_wikidict_PAGETITLE.values()
mykeys = corpus_wikidict_PAGETITLE.keys()

print('-->', [mydict[k] for k in mykeys if k == 'Coleosoma_floridanum'])    #value == [1]
print('==>', [key for key, value in mydict.items() if value == 12])         #key == ['沙盒']
"""
