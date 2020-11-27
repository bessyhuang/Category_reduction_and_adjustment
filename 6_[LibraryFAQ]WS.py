from ckiptagger import construct_dictionary, WS
from pymongo import MongoClient
import pickle
import os


os.environ["CUDA_VISIBLE_DEVICES"] = "0"



directory = './[LibraryFAQ]CkipTagger_WS_POS_NER/'
if not os.path.isdir(directory):
    os.mkdir(directory)
    
    
    
# Get Data Row from Mongodb (Answer, Question, Q&A)
def get_mongodb_row(collection_name):
    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db[collection_name]

    cursor = collection.find({}, {"Question":1, "Answer":1, "_id":1})

    #Question list
    Q_list = []

    #Answer list
    A_list = []

    #Question, Answer list
    QA_list = []

    #Question, Answer, _id list
    All_list = []

    for row in cursor:
        Q_list.append(row['Question'])
        A_list.append(row['Answer'])
        QA_list.append(row['Question'] + row['Answer'])
        All_list.append((row['Question'], row['Answer'], row['_id']))

    return Q_list, A_list, QA_list, All_list



# Word Segment and save to XXX_WS_list.pkl
def WordSegment_and_write2file(Q_list, A_list, QA_list):
    ws = WS("./data", disable_cuda=False)

    # (Optional) Create dictionary: wikipedia
    with open('./LibraryCommonWords/WikiDict_plus_QAkeywordsDict.pkl', 'rb') as fp:
        WikiDict_plus_QAkeywordsDict = pickle.load(fp)
    fp.close()

    dictionary1 = construct_dictionary(WikiDict_plus_QAkeywordsDict)

    count = 0
    for sent in [Q_list, A_list, QA_list]:
        word_sentence_list = ws(sent,
            segment_delimiter_set = {":" ,"：" ,":" ,".." ,"，" ,"," ,"-" ,"─" ,"－" ,"──" ,"." ,"……" ,"…" ,"..." ,"!" ,"！" ,"〕" ,"」" ,"】" ,"》" ,"【" ,"）" ,"｛" ,"｝" ,"“" ,"(" ,"「" ,"]" ,")" ,"（" ,"《" ,"[" ,"『" ,"』" ,"〔" ,"、" ,"．" ,"。" ,"." ,"‧" ,"﹖" ,"？" ,"?" ,"?" ,"；" ," 　" ,"" ,"　" ,"" ,"ㄟ" ," :" ,"？" ,"〞" ,"]" ,"／" ,"=" ,"？" ," -" ,"@" ,"." ,"～" ," ：" ,"：" ,"<", ">" ," - " ,"──" ,"~~" ,"`" ,": " ,"#" ,"/" ,"〝" ,"：" ,"'" ,"$C" ,"?" ,"?" ,"*" ,"／" ,"[" ,"." ,"?" ,"-" ,"～～" ,"\""},
            recommend_dictionary = dictionary1, # 效果最好！
            coerce_dictionary = construct_dictionary({'OPAC':2, 'OK':2, '滯還金':2, '浮水印':2, '索書號':2, '圖書館':2}), # 強制字典
    )
        
        # Q_list 斷詞
        if count == 0:
            with open('./[LibraryFAQ]CkipTagger_WS_POS_NER/Q_WS_list.pkl', 'wb') as fp:
                pickle.dump(word_sentence_list, fp)
            fp.close()
            count += 1
            del word_sentence_list

        # A_list 斷詞
        elif count == 1:
            with open('./[LibraryFAQ]CkipTagger_WS_POS_NER/A_WS_list.pkl', 'wb') as fp:
                pickle.dump(word_sentence_list, fp)
            fp.close()
            count += 1
            del word_sentence_list

        # QA_list 斷詞
        elif count == 2:
            with open('./[LibraryFAQ]CkipTagger_WS_POS_NER/QA_WS_list.pkl', 'wb') as fp:
                pickle.dump(word_sentence_list, fp)
            fp.close()



Q_list, A_list, QA_list, All_list = get_mongodb_row('FAQ')
WordSegment_and_write2file(Q_list, A_list, QA_list)



with open('./[LibraryFAQ]CkipTagger_WS_POS_NER/All_list.pkl', 'wb') as fp:
    pickle.dump(All_list, fp)
fp.close()
