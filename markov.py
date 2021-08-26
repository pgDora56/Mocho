# -*- coding: utf-8 -*-
import MeCab
import re
import random
import json


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

    def json_format(self):
        dic = {}
        dic["count"] = self.count
        dic["children"] = {}
        for k, v in self.nexts.items():
            dic[k] = self.nexts[k].json_format()
        return dic


class MarkovTree:
    def __init__(self, dic, maxi=3):
        self.root = Word(-1, maxi)
        self.MAXI_CHAIN = maxi
        self.dic = dic

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
        mecab = MeCab.Tagger(self.dic)
        # mecab = MeCab.Tagger()
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

    def json_format(self):
        return self.root.json_format()


def get_markov(dic, data, num=1):
    tree = MarkovTree(dic)
    with open(data) as f:
        sentencelist = f.read().split("\n")
    tree.create(sentencelist)
    tree.write()
    print(json.dumps(tree.json_format(), ensure_ascii=False))

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
    print(get_markov("sing.tb", 20))
