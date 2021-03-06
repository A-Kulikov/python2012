__author__ = 'Pavel Moskalevich'

class Ngram:
    def __init__(self, count = 0, prob = 0, bow = 0):
        self.count = count
        self.prob  = prob
        self.bow   = bow

    def set_count(self, count):
        self.count = count

    def set_count(self, prob):
        self.prob = prob

    def set_count(self, bow):
        self.bow = bow

class NgramStorage:
    def __init__(self):
        self.n_grams = {}

    def set_n_gram(self, words_tuple, ngram):
        if not self.n_grams.has_key(len(words_tuple)):
            self.n_grams[len(words_tuple)] = {}
        self.n_grams[len(words_tuple)][words_tuple] = ngram

    def get_n_gram(self, words_tuple):
        if not self.n_grams.has_key(len(words_tuple)) or not self.n_grams[len(words_tuple)].has_key(words_tuple):
            return None
        return self.n_grams[len(words_tuple)][words_tuple]

    def total_n_grams(self, order = 0):
        ''' Returns total number of n-grams of order (sum of all counts).
        If order is zero, than summarizes across all orders.
        '''
        if order == 0:
            sum = 0
            for ord in self.n_grams.keys():
                sum = sum + reduce(lambda cum, x: cum + self.n_grams[ord][x].count, self.n_grams[ord].keys(), 0)
            return sum
        else:
            if self.n_grams.has_key(order):
                return reduce(lambda cum, x: cum + self.n_grams[order][x].count, self.n_grams[order].keys(), 0)
            else:
                return 0

    def distinct_n_grams(self, order = 0):
        ''' Returns number of distinct n-grams of order.
        If order is zero, than counts across all orders.
        '''
        if order == 0:
            return reduce(lambda cum, x: cum + len(self.n_grams[x]), self.n_grams.keys(), 0)
        else:
            if self.n_grams.has_key(order):
                return len(self.n_grams[order])
            else:
                return 0
