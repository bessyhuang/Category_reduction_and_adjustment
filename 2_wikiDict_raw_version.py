import os.path
import gzip
import shutil
import pickle
import re



directory = './wikiDict/'
if not os.path.isdir(directory):
    os.mkdir(directory)



with gzip.open('./zhwiki-latest-all-titles.gz', 'rb') as f_in:
    with open('./wikiDict/zhwiki-latest-all-titles.txt', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)



page_list = []
with open('./wikiDict/zhwiki-latest-all-titles.txt', 'r', encoding='utf-8') as f:
    line = f.readline().strip()
    while line != '':
        page_list.append(line.split('\t'))
        line = f.readline().strip()
#print(page_list[:1000])



# 只取中文的page條目
title_list = []
regex = re.compile("(^[\u4e00-\u9fff]+$)")
for num, token in page_list:
    if regex.match(token) != None:
        title_list.append(token)
        #print('===', num, token)
#print(title_list)



page_dict = dict()
for i in range(1, len(title_list)):
	page_title = title_list[i]
	if page_title not in page_dict.keys():
		page_dict[page_title] = 1
	else:
		page_dict[page_title] += 1

"""
print(len(page_dict), set(page_dict.values())) 
#1993429 {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}

# Tips: 權重
# Ex: values > 9 -> 哲学 太阳系 恒星 沙盒 航天
for key, value in page_dict.items():
    if value > 9:
        print(key)
"""



# 物件序列化：使用Pickle
with open('./wikiDict/corpus_wikidict_PAGETITLE.pkl', 'wb') as fp:
    pickle.dump(page_dict, fp)
fp.close()
