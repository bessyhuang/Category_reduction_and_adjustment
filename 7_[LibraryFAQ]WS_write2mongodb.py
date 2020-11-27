from pymongo import MongoClient
import numpy as np
import pickle
import os



directory = './[LibraryFAQ]CkipTagger_WS_POS_NER/'
if not os.path.isdir(directory):
    os.mkdir(directory)
    
    

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



def add_field_to_mongodb(collection_name, All_list, Q_WS_list, A_WS_list, QA_WS_list):
    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db[collection_name]

    AllFields_array = np.array(All_list)
    # print(AllFields_list[0][2], AllFields_list[1][2])
    # print('===', AllFields_array[:, 2])

    for i, _id in enumerate(AllFields_array[:, 2]):
        # print(_id, zipped_Q_segment_POS[i])

        collection.update_many({"_id": _id}, 
            {"$set": {
                "Q_WS": Q_WS_list[i], 
                "A_WS": A_WS_list[i], 
                "QA_WS": QA_WS_list[i]
                }
            })



# Word Segment (WS) write to mongdb
add_field_to_mongodb('FAQ', All_list, Q_WS_list, A_WS_list, QA_WS_list)
