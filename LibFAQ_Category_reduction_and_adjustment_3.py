from pymongo import MongoClient
    
    

client = MongoClient('localhost', 27017)
db = client['Library']
collection = db['FAQ']



def get_mongodb_row():
    cursor = collection.find({ "adjusted_Category" : { "$exists": False } }, 
                             {"Question":1, "Category":1, "_id":1})

    id_list = []
    Question_list = []
    Category_list = []
    
    
    for row in cursor:
        id_list.append(row["_id"])
        Question_list.append(row['Question'])
        Category_list.append(row['Category'])
         
    return id_list, Question_list, Category_list



id_list, Question_list, Category_list = get_mongodb_row()

update_results = zip(id_list, Question_list, Category_list)
for raw_id, raw_Q, raw_category in update_results:
    print(raw_id, raw_Q, raw_category)
    collection.update_many({ "_id" : raw_id },
                           { "$set" : { "adjusted_Category" : raw_category } }, upsert=True)
