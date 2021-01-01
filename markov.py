# -*- coding: utf-8 -*-
import MeCab
import re
import random
import pickle
import time


class Word:
    def __init__(self, deep, maxi):
        self.deep = deep
        self.count = 0
        self.nexts = {}
        self.MAXI_CHAIN = maxi

    def add(self, words):
        self.count += 1
        if len(words) < 1:
            return
        if len(words) < self.MAXI_CHAIN - self.deep - 1:
            return
        w = words.pop(0)
        if self.deep < self.MAXI_CHAIN - 1:
            if w not in self.nexts:
                self.nexts[w] = Word(self.deep+1, self.MAXI_CHAIN)
            self.nexts[w].add(words)

    def show(self):
        text = ""
        for w in self.nexts:
            blank = ""
            for _ in range(self.deep):
                blank += "  "
            text += blank + w + "[" + str(self.nexts[w].deep) + \
                " / " + str(self.nexts[w].count) + "]"
            if self.deep < self.MAXI_CHAIN - 1:
                text += " -> " + self.nexts[w].show() + "\n"
        return text

    def pick(self):
        r = random.randrange(self.count)
        cnt = 0
        for k, n in self.nexts.items():
            cnt += n.count
            # print(f"{cnt} -> {r}/{self.count}")
            if r < cnt:
                # print(f"HIT")
                return k
        raise Exception("Tree Counter is broken.")

    def write(self, cnt=0):
        for key, val in self.nexts.items():
            cnt = val.write(cnt+1)
        return cnt

    def dic_format(self):
        dic = {}
        dic["count"] = self.count
        dic["children"] = {}
        for k, v in self.nexts.items():
            dic[k] = self.nexts[k].dic_format()
        return dic


class MarkovTree:
    def __init__(self, maxi=3):
        self.root = Word(-1, maxi)
        self.MAXI_CHAIN = maxi

    def add_tree(self, data):
        words = ["[START]"]
        words.extend(self.separate(data))
        # words[-1] = "[END]"
        words.append("[END]")
        self.make_chain(words)

    def make_chain(self, words_list):
        for i in range(len(words_list)):
            self.root.add(words_list[i:])

    def separate(self, data):
        # mecab = MeCab.Tagger("-d /opt/mecab/lib/mecab/dic/neologd")
        mecab = MeCab.Tagger()
        mecab.parse("")
        m = mecab.parse(data)
        lines = m.split("\n")
        words = []
        for line in lines:
            words.append((re.split('[\t,]', line)[0]))
        for _ in range(2):
            words.pop()  # 最後の謎の空白2こを削除
        return words

    def create(self, sentencelist):
        for s in sentencelist:
            # s = f.read()
            # s = self.cut_unneccesarry(s)
            # s = self.replace_spletters(s)
            self.add_tree(s)

    def write(self):
        self.root.write(0)

    def dic_format(self):
        return self.root.dic_format()


def pickle_markov_tree(data):
    """Create and pickle markov tree

    Parameters
    ----------
    data: string
        Data file path

    Returns
    -------
    bool
        Is pickling success
    """

    try:
        tree = MarkovTree()
        with open(data) as f:
            sentencelist = f.read().split("\n")
        tree.create(sentencelist)

        with open(data+".pickle", "wb") as buf:
            pickle.dump(tree, buf)
        return True
    except Exception:
        return False


def get_from_pickle(data, num=1):
    """Make sentences from pickle file

    Parameters
    ----------
    data: string
        Pickle file path
    num: int
        Number of returned sentences


    Returns
    -------
    string
        Line Separated Generation Results
    """

    with open(data, "rb") as buf:
        tree = pickle.load(buf)

    results = []
    for _ in range(num):
        lis = []

        fst = "[START]"
        # tree.root.nexts[fst].show()
        snd = tree.root.nexts[fst].pick()
        lis.append(snd)

        while snd != "[END]":
            newsnd = tree.root.nexts[fst].nexts[snd].pick()
            lis.append(newsnd)
            fst = snd
            snd = newsnd
        lis.pop()

        results.append("".join(lis))
    return "\n".join(results)


def get_markov(data, num=1):
    """[Legacy] Make sentences from data file

    Parameters
    ----------
    data: string
        Data file path
    num: int
        Number of returned sentences


    Returns
    -------
    string
        Line Separated Generation Results
    """
    tree = MarkovTree()
    with open(data) as f:
        sentencelist = f.read().split("\n")
    tree.create(sentencelist)
    # tree.write()

    results = []
    for _ in range(num):
        lis = []

        fst = "[START]"
        # tree.root.nexts[fst].show()
        snd = tree.root.nexts[fst].pick()
        lis.append(snd)

        while snd != "[END]":
            newsnd = tree.root.nexts[fst].nexts[snd].pick()
            lis.append(newsnd)
            fst = snd
            snd = newsnd
        lis.pop()

        results.append("".join(lis))
    return "\n".join(results)


if __name__ == "__main__":
    start = time.time()
    print(get_markov("sing.tb", 20))
    print(f"Legacy Time: {time.time()-start}")
    start = time.time()
    pickle_markov_tree("sing.tb")
    print(f"Pickle time: {time.time()-start}")
    start = time.time()
    print(get_from_pickle("sing.tb.pickle", 20))
    print(f"Alt. Time: {time.time()-start}")
