from pymongo import MongoClient
import pandas as pd
import string


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

def WS_combine(Q_WS_list):
    new_list = []
    for row in Q_WS_list:
        new_row = ' '.join(row)
        new_list.append(new_row)
    return new_list

def text_process(mess):
    PunctuationMark = [":" ,"：" ,":" ,".." ,"，" ,"," ,"-" ,"─" ,"－" ,"──" ,"." ,"……" ,"…" ,"..." ,"!" ,"！" ,"〕" ,"」" ,"】" ,"》" ,"【" ,"）" ,"｛" ,"｝" ,"“" ,"(" ,"「" ,"]" ,")" ,"（" ,"《" ,"[" ,"『" ,"』" ,"〔" ,"、" ,"．" ,"。" ,"." ,"‧" ,"﹖" ,"？" ,"?" ,"?" ,"；" ," 　" ,"" ,"　" ,"" ,"ㄟ" ," :" ,"？" ,"〞" ,"]" ,"／" ,"=" ,"？" ," -" ,"@" ,"." ,"～" ," ：" ,"：" ,"<", ">" ," - " ,"──" ,"~~" ,"`" ,": " ,"#" ,"/" ,"〝" ,"：" ,"'" ,"$C" ,"?" ,"?" ,"*" ,"／" ,"[" ,"." ,"?" ,"-" ,"～～" ,"\""]
    STOPWORDS = [] + PunctuationMark
    
    # Check characters to see if they are in punctuation
    nopunc = [char for char in mess if char not in string.punctuation]
    
    # Join the characters again to form the string.
    nopunc = ''.join(nopunc)
    
    # Now just remove any stopwords
    return ' '.join([word.lower() for word in nopunc.split() if word.lower() not in STOPWORDS])


Question_list, Q_WS_list, Category_list, AllFields_list = get_mongodb_row()

# Save dataset into pandas dataframe
list_of_tuples = list(zip(Question_list, WS_combine(Q_WS_list), Category_list))
data_rawFAQ = pd.DataFrame(list_of_tuples, columns = ['Question', 'Q_WS', 'Category']) 
print(data_rawFAQ.Q_WS)

# Text Pre-processing, and add new column "clean_msg"
data_rawFAQ['clean_msg'] = data_rawFAQ.Q_WS.apply(text_process)
print(data_rawFAQ.head())

# Generate descriptive statistics
data_rawFAQ.groupby('Category').describe()


# count "clean_msg" length, and add new column "length"
data_rawFAQ['length'] = data_rawFAQ['clean_msg'].apply(len)
data_rawFAQ.head()

data_rawFAQ.groupby('Category').describe()


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

counter = Counter(get_words(data_rawFAQ['clean_msg']))
most_common = dict(counter.most_common(20))
print(most_common)

fig1 = plt.figure(figsize=(20, 14))
sns.barplot(x=list(most_common.values()), y=list(most_common.keys()))
fig1.savefig('Top20_most_common_words_Unigram.png')


# Display Top80 most common words
from collections import Counter

words = data_rawFAQ.clean_msg.apply(lambda x: [word for word in x.split()])
whole_words = Counter()

for msg in words:
    whole_words.update(msg)
print(whole_words.most_common(50))


# Data Visualization - Bigram Analysis
from sklearn.feature_extraction.text import CountVectorizer

def get_top_text_ngrams(corpus, topN, n_gram):
    vec = CountVectorizer(ngram_range=(n_gram, n_gram)).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:topN]

fig2 = plt.figure(figsize=(20, 14))
most_common_bi = get_top_text_ngrams(data_rawFAQ['clean_msg'], 20, 2)
most_common_bi = dict(most_common_bi)
sns.barplot(x=list(most_common_bi.values()), y=list(most_common_bi.keys()))
fig2.savefig('Top20_most_common_words_Bigram.png')
