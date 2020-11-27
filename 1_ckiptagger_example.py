from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
import os



# 1. Download model files
#data_utils.download_data_gdown("./") # gdrive-ckip



# 2. Load model (Use GPU)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

ws = WS("./data", disable_cuda=False)
pos = POS("./data", disable_cuda=False)
ner = NER("./data", disable_cuda=False)



# 3. (Optional) Create dictionary
word_to_weight = {"土地公": 1, "土地婆": 1, "公有": 2, "啦": 1, "來亂的": 1, "緯來體育台": 1}
dictionary = construct_dictionary(word_to_weight)
print("字典：", dictionary)



# 4. Run the WS-POS-NER pipeline
sentence_list = [
    "傅達仁今將執行安樂死，卻突然爆出自己20年前遭緯來體育台封殺，他不懂自己哪裡得罪到電視台。",
    "美國參議院針對今天總統布什所提名的勞工部長趙小蘭展開認可聽證會，預料她將會很順利通過參議院支持，成為該國有史以來第一位的華裔女性內閣成員。",
    "",
    "土地公有政策?？還是土地婆有政策。.",
    "… 你確定嗎… 不要再騙了……",
    "最多容納59,000個人,或5.9萬人,再多就不行了.這是環評的結論.",
    "科長說:1,坪數對人數為1:3。2,可以再增加。",
]

word_sentence_list = ws(
    sentence_list,
    # sentence_segmentation = True, # To consider delimiters
    # segment_delimiter_set = {",", "。", ":", "?", "!", ";"}), # This is the defualt set of delimiters
    #recommend_dictionary = dictionary1, # words in this dictionary are encouraged
    coerce_dictionary = dictionary, # words in this dictionary are forced
)
print(word_sentence_list)

pos_sentence_list = pos(word_sentence_list)
#print(pos_sentence_list)

entity_sentence_list = ner(word_sentence_list, pos_sentence_list)
#print(entity_sentence_list)
