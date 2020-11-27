from pymongo import MongoClient
import numpy as np
import pickle
import os



directory = './[LibraryFAQ]CkipTagger_WS_POS_NER/'
if not os.path.isdir(directory):
    os.mkdir(directory)
    
    
#====================================================
All_list = []
with open(directory + 'All_list.pkl', 'rb') as fp:
    All_list = pickle.load(fp)
fp.close()

Q_WS_list = []
with open(directory + 'Q_WS_list.pkl', 'rb') as fp:
    Q_WS_list = pickle.load(fp)
fp.close()

A_WS_list = []
with open(directory + 'A_WS_list.pkl', 'rb') as fp:
    A_WS_list = pickle.load(fp)
fp.close()

QA_WS_list = []
with open(directory + 'QA_WS_list.pkl', 'rb') as fp:
    QA_WS_list = pickle.load(fp)
fp.close()

#====================================================
zipped_Q_POS = []
with open(directory + 'zipped_Q_POS.pkl', 'rb') as fp:
    zipped_Q_POS = pickle.load(fp)
fp.close()

zipped_A_POS = []
with open(directory + 'zipped_A_POS.pkl', 'rb') as fp:
    zipped_A_POS = pickle.load(fp)
fp.close()

zipped_QA_POS = []
with open(directory + 'zipped_QA_POS.pkl', 'rb') as fp:
    zipped_QA_POS = pickle.load(fp)
fp.close()

#====================================================
Q_NER_list = []
with open(directory + 'Q_NER_list.pkl', 'rb') as fp:
    Q_NER_list = pickle.load(fp)
fp.close()

A_NER_list = []
with open(directory + 'A_NER_list.pkl', 'rb') as fp:
    A_NER_list = pickle.load(fp)
fp.close()

QA_NER_list = []
with open(directory + 'QA_NER_list.pkl', 'rb') as fp:
    QA_NER_list = pickle.load(fp)
fp.close()

#====================================================
Q_pos_sentence_list = []
with open(directory + 'Q_pos_sentence_list.pkl', 'rb') as fp:
    Q_pos_sentence_list = pickle.load(fp)
fp.close()

A_pos_sentence_list = []
with open(directory + 'A_pos_sentence_list.pkl', 'rb') as fp:
    A_pos_sentence_list = pickle.load(fp)
fp.close()

QA_pos_sentence_list = []
with open(directory + 'QA_pos_sentence_list.pkl', 'rb') as fp:
    QA_pos_sentence_list = pickle.load(fp)
fp.close()

#====================================================



def add_field_to_mongodb(collection_name, All_list, 
        zipped_Q_POS, zipped_A_POS, zipped_QA_POS, 
        Q_NER_list, A_NER_list, QA_NER_list, 
        Q_pos_sentence_list, A_pos_sentence_list, QA_pos_sentence_list):

    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db[collection_name]

    AllFields_array = np.array(All_list)
    # print(AllFields_list[0][2], AllFields_list[1][2])
    # print('===', AllFields_array[:, 2])

    for i, _id in enumerate(AllFields_array[:, 2]):
        #print(_id, zipped_Q_POS[i])

        collection.update_many({"_id": _id}, 
            {"$set": {
                "Q_WS | POS": zipped_Q_POS[i], 
                "A_WS | POS": zipped_A_POS[i], 
                "QA_WS | POS": zipped_QA_POS[i],
                "Q_NER": Q_NER_list[i],
                "A_NER": A_NER_list[i],
                "QA_NER": QA_NER_list[i],
                "Q_POS": Q_pos_sentence_list[i],
                "A_POS": A_pos_sentence_list[i],
                "QA_POS": QA_pos_sentence_list[i],
                }
            })



# Word Segment and POS tagging (WS|POS) write to mongdb
add_field_to_mongodb('FAQ', All_list, 
    zipped_Q_POS, zipped_A_POS, zipped_QA_POS, 
    Q_NER_list, A_NER_list, QA_NER_list, 
    Q_pos_sentence_list, A_pos_sentence_list, QA_pos_sentence_list)
