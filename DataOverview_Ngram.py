from pymongo import MongoClient
import pandas as pd



def get_mongodb_row():
    client = MongoClient('localhost', 27017)
    db = client['Library']
    collection = db['FAQ']

    cursor = collection.find({}, {"Question":1, "Q_WS":1, "Category":1, "_id":1})

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

# tokenize text and get words list
def words(text):
    return list(text.lower())

def bigrams(text):
    unigram = words(text)
    bigram_list = []
    for i in range(1, len(unigram)):
        bigram_list.append([unigram[i - 1], unigram[i]])
    return bigram_list

def trigrams(text):
    unigram = words(text)
    trigram_list = []
    for i in range(2, len(unigram)):
        trigram_list.append([unigram[i - 2], unigram[i - 1], unigram[i]])
    return trigram_list

def fourgrams(text):
    unigram = words(text)
    fourgram_list = []
    for i in range(3, len(unigram)):
        fourgram_list.append([unigram[i - 3], unigram[i - 2], unigram[i - 1], unigram[i]])
    return fourgram_list

print(words('本校讀者預約自動化書庫的館藏，多久後可以取書？'))
print(bigrams('本校讀者預約自動化書庫的館藏，多久後可以取書？'))
print(trigrams('本校讀者預約自動化書庫的館藏，多久後可以取書？'))
print(fourgrams('本校讀者預約自動化書庫的館藏，多久後可以取書？'))

def Ngram_combine(ngram, Question_list):
    new_Ngram_list = []
    string = ''
    
    if ngram == 1:
        for row in Question_list:
            new_row = ' '.join(words(row))
            new_Ngram_list.append(new_row)
            
    elif ngram > 1:
        for row in Question_list:
            if ngram == 2:
                ngram_row = bigrams(row)
            elif ngram == 3:
                ngram_row = trigrams(row)
            elif ngram == 4:
                ngram_row = fourgrams(row)
            
            for n in ngram_row:
                w = ''.join(n)
                string += ' ' + w
            new_Ngram_list.append(string)
            string = ''
            
    return new_Ngram_list

print(Ngram_combine(3, ['本校讀者預約自動化書庫的館藏，多久後可以取書？', '多久後可以取書？']))

Question_list, Q_WS_list, Category_list, AllFields_list = get_mongodb_row()

# Save dataset into pandas dataframe
ngram = 3
list_of_tuples = list(zip(Question_list, Ngram_combine(ngram, Question_list), Category_list))
data_rawFAQ = pd.DataFrame(list_of_tuples, columns = ['Question', 'Q_Ngram', 'Category']) 
print(data_rawFAQ.Q_Ngram)



# Data Visualization - Unigram Analysis (Word)
from collections import Counter
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']
mpl.rcParams['font.size'] = '20'

def get_words(content):
    words = []
    for row in content:
        for j in row.split():
            words.append(j.strip())
    return words

counter = Counter(get_words(data_rawFAQ['Q_Ngram']))
most_common = dict(counter.most_common(20))
print(most_common)

fig1 = plt.figure(figsize=(26, 10))
sns.barplot(y=list(most_common.values()), x=list(most_common.keys()))
fig1.savefig('Top20_Unigram_test.png')
