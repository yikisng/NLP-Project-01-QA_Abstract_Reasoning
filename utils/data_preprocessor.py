# Data Preprocess
# 对数据做预处理，去除缺失数据、去除噪音词汇和符号；使用jieba进行中文分词处理
# @author lijun
import pandas as pd
import jieba
import datetime
import re
from jieba import posseg


# 去掉多余空格
def clean_space(text):
    match_regex = re.compile(u'[\u4e00-\u9fa5。\.,，:：《》、\(\)（）]{1} +(?<![a-zA-Z])|\d+ +| +\d+|[a-z A-Z]+')
    should_replace_list = match_regex.findall(text)
    order_replace_list = sorted(should_replace_list, key=lambda i: len(i), reverse=True)
    for i in order_replace_list:
        if i == u' ':
            continue
        new_i = i.strip()
        text = text.replace(i, new_i)
    return text


# 读取数据+简单清洗数据
def load_and_parse_data(train_csv_path, test_csv_path):
    print('[load and parse data]...{},{}'.format(train_csv_path, test_csv_path))
    train_df = pd.read_csv(train_csv_path, encoding='utf-8')
    train_df.dropna(subset=['Report'], how='any', inplace=True)
    train_x = train_df.Question.str.cat(train_df.Dialogue)
    train_y = train_df.Report
    assert len(train_x) == len(train_y)

    test_df = pd.read_csv(test_csv_path, encoding='utf-8')
    # 填充
    test_df.fillna('', inplace=True)
    test_x = test_df.Question.str.cat(test_df.Dialogue)
    test_y = []
    print(
        '[load and parse data FINISHED]:\n'
        'train_x_len:{},train_y_len:{},\n'
        'test_x_len:{},test_y_len:{}'.format(len(train_x),
                                             len(train_y),
                                             len(test_x),
                                             len(test_y)))

    return train_x, train_y, test_x, test_y


# 保存数据到文本文件
def save_data_to_file(data, file_path, cut=False, stop_words=[]):
    print('[save data to file]...file_path:{}'.format(file_path))
    start_time = datetime.datetime.now()
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in data:
            if not isinstance(line, str):
                line = str(line)
            line = clean_space(line).strip()
            if cut:
                split_words = [x for x in jieba.cut(line, HMM=True) if x not in stop_words]
                f.write('{}\n'.format(' '.join(split_words)))
            else:
                f.write('{}\n'.format(line))
    print('[save data to file FINISHED]...cost time:{}'.format(datetime.datetime.now() - start_time))


# 从文件中读取数据
def load_data_from_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = clean_space(line).strip()
            data.append(line)
    return data


# 加载停用词
def load_stopwords(file_path, add_stop_word_set):
    print('[Loading Stopwords]...')
    stop_words = set()
    stop_words_lines = load_data_from_file(file_path)
    for item in stop_words_lines:
        stop_words.add(item)
    stop_words = set.union(stop_words, add_stop_word_set)
    print('[Loading Stopwords FINISHED] stopwords cnt:{}'.format(len(stop_words)))

    return stop_words


def load_user_dic(path):
    for item in load_data_from_file(path):
        jieba.add_word(item)


# 切词 + 去掉停用词
def cut_sentences_to_vocabs(sentence_list, stop_words):
    vocab_set = set()
    for sentence in sentence_list:
        if not isinstance(sentence, str):
            sentence = str(sentence)
        sentence = sentence.strip()
        vocabs = jieba.cut(sentence, HMM=True)
        for vocab in vocabs:
            if vocab not in stop_words:
                vocab_set.add(vocab)
    return vocab_set


# 保存词典到文件（one-hot格式）
def save_vocabs_to_file_by_one_hot(file_path, vocabs):
    print('[Write vocabs to file] vocabs cnt:{} ...'.format(len(vocabs)))
    i = 1
    with open(file_path, 'w', encoding='utf-8') as f:
        for vocab in vocabs:
            f.write('{} {}\n'.format(vocab, i))
            i = i + 1
    print('[Write vocabs to file FINISHED] path:{} vocab_cnt:{}'.format(file_path, i))


# 切词
def segment(sentence, cut_type='word', pos=False):
    if pos:
        if cut_type == 'word':
            word_pos_seq = posseg.lcut(sentence)
            word_seq, pos_seq = [], []
            for w, p in word_pos_seq:
                word_seq.append(w)
                pos_seq.append(p)
            return word_seq, pos_seq
        elif cut_type == 'char':
            word_seq = list(sentence)
            pos_seq = []
            for w in word_seq:
                w_p = posseg.lcut(w)
                pos_seq.append(w_p[0].flag)
            return word_seq, pos_seq
    else:
        if cut_type == 'word':
            return jieba.lcut(sentence)
        elif cut_type == 'char':
            return list(sentence)


if __name__ == '__main__':
    # 82943 rows
    train_csv_path = '../resource/AutoMaster_TrainSet.csv'
    test_csv_path = '../resource/AutoMaster_TestSet.csv'
    stopwords_file_path = '../resource/stop_words/i_stopwords.txt'
    user_dic_file_path = '../resource/user_dic.txt'
    REMOVE_WORDS = {'|', '[', ']', '语音', '图片', '語音', '圖片'}
    # gen files:
    vocab_file_path = '../resource/gen/vocab.txt'
    train_x_file_path = '../resource/gen/train_x.txt'
    train_y_file_path = '../resource/gen/train_y.txt'
    test_x_file_path = '../resource/gen/test_x.txt'

    train_x_cut_file_path = '../resource/gen/train_x_cut.txt'
    train_y_cut_file_path = '../resource/gen/train_y_cut.txt'
    test_x_cut_file_path = '../resource/gen/test_x_cut.txt'

    train_x, train_y, test_x, test_y = load_and_parse_data(train_csv_path, test_csv_path)

    stopwords = load_stopwords(stopwords_file_path, REMOVE_WORDS)

    save_data_to_file(train_x, train_x_file_path)
    save_data_to_file(train_x, train_x_cut_file_path, cut=True, stop_words=stopwords)
    save_data_to_file(train_y, train_y_file_path)
    save_data_to_file(train_y, train_y_cut_file_path, cut=True, stop_words=stopwords)
    save_data_to_file(test_x, test_x_file_path)
    save_data_to_file(test_x, test_x_cut_file_path, cut=True, stop_words=stopwords)

    train_x_vocabs = cut_sentences_to_vocabs(train_x, stopwords)
    train_y_vocabs = cut_sentences_to_vocabs(train_y, stopwords)
    test_x_vocabs = cut_sentences_to_vocabs(test_x, stopwords)

    all_vocabs = set.union(train_x_vocabs, train_y_vocabs, test_x_vocabs)

    save_vocabs_to_file_by_one_hot(vocab_file_path, all_vocabs)