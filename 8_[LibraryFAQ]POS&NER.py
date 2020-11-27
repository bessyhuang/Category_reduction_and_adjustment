from pymongo import MongoClient
from ckiptagger import POS, NER
import pickle
import os



os.environ["CUDA_VISIBLE_DEVICES"] = "0"

directory = './[LibraryFAQ]CkipTagger_WS_POS_NER/'
if not os.path.isdir(directory):
    os.mkdir(directory)
    
    
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



def POS_NER_and_write2file(Q_WS_list, A_WS_list, QA_WS_list):
    pos = POS("./data", disable_cuda=False)

    count = 0
    for sent in [Q_WS_list, A_WS_list, QA_WS_list]:
        pos_sentence_list = pos(sent)
        
        # Q_WS_list POS
        if count == 0:
            zipped_Q_POS = []

            with open(directory + 'zipped_Q_POS.txt', 'a', encoding='utf-8') as f:
                for ws_and_pos in zip(Q_WS_list, pos_sentence_list):
                    #print('ws_and_pos:', ws, pos)

                    row = [ws.strip() + "_" + pos for ws, pos in zip(ws_and_pos[0], ws_and_pos[1])]
                    f.write('{}\n'.format(row))
                    zipped_Q_POS.append(row)
            f.close()

            with open(directory + 'zipped_Q_POS.pkl', 'wb') as fp:
                pickle.dump(zipped_Q_POS, fp)
            fp.close()

            NER_and_write2file('Q', Q_WS_list, pos_sentence_list)       #function
            POS_write2file('Q', pos_sentence_list)

            count += 1
            del pos_sentence_list

        # A_WS_list POS
        elif count == 1:
            zipped_A_POS = []

            with open(directory + 'zipped_A_POS.txt', 'a', encoding='utf-8') as f:
                for ws_and_pos in zip(A_WS_list, pos_sentence_list):
                    # print('ws_and_pos:', ws, pos)

                    row = [ws.strip() + "_" + pos for ws, pos in zip(ws_and_pos[0], ws_and_pos[1])]
                    f.write('{}\n'.format(row))
                    zipped_A_POS.append(row)
            f.close()

            with open(directory + 'zipped_A_POS.pkl', 'wb') as fp:
                pickle.dump(zipped_A_POS, fp)
            fp.close()

            NER_and_write2file('A', A_WS_list, pos_sentence_list)       #function
            POS_write2file('A', pos_sentence_list)

            count += 1
            del pos_sentence_list

        # QA_WS_list POS
        elif count == 2:
            zipped_QA_POS = []

            with open(directory + 'zipped_QA_POS.txt', 'a', encoding='utf-8') as f:
                for ws_and_pos in zip(QA_WS_list, pos_sentence_list):
                    # print('ws_and_pos:', ws, pos)

                    row = [ws.strip() + "_" + pos for ws, pos in zip(ws_and_pos[0], ws_and_pos[1])]
                    f.write('{}\n'.format(row))
                    zipped_QA_POS.append(row)
            f.close()

            with open(directory + 'zipped_QA_POS.pkl', 'wb') as fp:
                pickle.dump(zipped_QA_POS, fp)
            fp.close()

            NER_and_write2file('QA', QA_WS_list, pos_sentence_list)       #function
            POS_write2file('QA', zipped_QA_POS)



def NER_and_write2file(name, word_sentence_list, pos_sentence_list):
    if name != 'QA':
        ner = NER("./data")

        entity_sentence_list = ner(word_sentence_list, pos_sentence_list)

        new_ner_list = []
        with open(directory + '{}_NER_list.txt'.format(name), 'a', encoding='utf-8') as f:
            
            for ners_sent in entity_sentence_list:
                # print('ners_sent', ners_sent)

                ner_len = len(ners_sent)
                
                if ner_len == 0:
                    f.write('{}\n'.format('NULL'))
                    new_ner_list.append(['NULL'])
                else:
                    OneSent_ners = []
                    for ners in ners_sent:
                        string = '{}_{}'.format(ners[2], ners[3])
                        OneSent_ners.append(string)
                    f.write('{}\n'.format(OneSent_ners))
                    new_ner_list.append(OneSent_ners)
                    del OneSent_ners 
        f.close()

        with open(directory + '{}_NER_list.pkl'.format(name), 'wb') as fp:
            pickle.dump(new_ner_list, fp)
        fp.close()

    else:
        with open(directory + 'A_NER_list.pkl', 'rb') as fp:
            A_ner_list = pickle.load(fp)
        fp.close()
        with open(directory + 'Q_NER_list.pkl', 'rb') as fp:
            Q_ner_list = pickle.load(fp)
        fp.close()

        QA_ner_list = []
        with open(directory + '{}_NER_list.txt'.format(name), 'a', encoding='utf-8') as f:
            for i in range(len(Q_ner_list)):
                f.write('{}\n'.format(Q_ner_list[i] + A_ner_list[i]))
                QA_ner_list.append(Q_ner_list[i] + A_ner_list[i])
        f.close()

        with open(directory + '{}_NER_list.pkl'.format(name), 'wb') as fp:
            pickle.dump(QA_ner_list, fp)
        fp.close()



def POS_write2file(name, pos_sentence_list):
    # print(name, "==>", pos_sentence_list)
    with open(directory + '{}_pos_sentence_list.pkl'.format(name), 'wb') as fp:
        pickle.dump(pos_sentence_list, fp)
    fp.close()



POS_NER_and_write2file(Q_WS_list, A_WS_list, QA_WS_list)
