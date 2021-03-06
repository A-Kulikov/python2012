# coding=utf-8
import re
from nltk.tokenize import wordpunct_tokenize
import time

def read_stop_list(stop_list_file):
    input = open(stop_list_file, "r")
    stop_list = set()

    for line in input:
        stop_list.add(line.lower().rstrip())
    input.close()

    return stop_list

def parse_line(line):
    return map(lambda x: x.lower(), wordpunct_tokenize(line))

def filter_bag_of_words(bag, stop_list):
    return set(filter(lambda x: x not in stop_list, bag))

def normalize_bag_of_words_with_index(bag, norm_index):
    new_bag = set()
    for word in bag:
        if norm_index.exists(word):
            norm_word = norm_index.get(word)
            if norm_word != "":
                new_bag.add(norm_word)
        else: pass
    return new_bag

def parse_data(data):
    word_bag = set()
    for rec in data:
        for text in rec[1:]:
            #print text
            word_bag |= set(parse_line(text)) #filter_bag_of_words(parse_line(text), stop_list)
    return word_bag

def contain_only_ascii(word):
    if re.match("^[A-Za-z0-9]+$", word):
        return word

def filter_cyrillic(bag_of_words):
    return filter(lambda x: contain_only_ascii(x), bag_of_words)

def count_one_symbol_words(bag_of_words):
    return len(filter(is_one_symbol_word, bag_of_words))

def is_one_symbol_word(word):
    return len(word) == 1

"""сделано на основе http://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator"""
def print_time(func):
    def wrapper(*arg,**kw):
        t1 = time.time()
        res = func(*arg,**kw)
        t2 = time.time()
        print "Time: %.2f seconds" % (t2-t1)
        return res
    return wrapper
