# -*- coding: UTF-8 -*-
import jieba
import json
import codecs
import math
import re
import jieba
from collections import OrderedDict

INDEX_NAME_MAX_LENGTH = 15

SIGN_STRING = ur""" `-=[]\;',./~!@#$%^&*()_+{}|:"<>?·【】、；‘，。、~！@#￥%……&*（）——+{}|：“《》？”’
āáǎàōóǒòêēéěèīíǐìūúǔùǖǘǚǜüˉˇ¨‘’々～‖∶”’‘｜〃〔〕《》「」『』．〖〗【【】（）〔〕｛｝
≈≡≠＝≤≥＜＞≮≯∷±＋－×÷／∫∮∝∞∧∨∑∏∪∩∈∵∴⊥‖∠⌒⊙≌∽√•
 °′〃＄￡￥‰％℃¤￠§№☆★○●◎◇◆□■△▲※→←↑↓〓＃＆＠＼＾＿…·－＝【】＼；‘，。、～！＠＃￥％……＆×（
 ）——＋｛｝｜：“《》？”’﹡	　　
 """
SIGN_SET = set(SIGN_STRING)
def isSign(s):
    for ch in s:
        if ch in SIGN_SET:
            return True
        if ch.encode("utf-8") in SIGN_SET:
            return True
    return False
def splitSign(string):
    if string == "":
        return ""
    newString = ""
    for i in range(len(string)):
        if not isSign(string[i]):
            newString += string[i]
        else:
            newString += " "
    return newString.split()
def reduceSign(string):
    if string == "":
        return ""
    newS = ""
    for c in [x for x in string if not isSign(x)]:
        newS += c
    return newS
def strQ2B(ustring):
    """全角转半角"""
    rstring = u""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:                              # 全角空格直接转换
            inside_code = 32
        elif inside_code >= 65281 and inside_code <= 65374:  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring
# print strQ2B(u"ＮＡＫＡ雅ＭＵＲＡ(脚色) 是　速度ａｂｓｄ（）｛｝【】")

# dict name:  a1:1; a4:2 ...

def addIntoDict(dictionary, key, value, tf=1):
    key = strQ2B(key)
    key = reduceSign(key)
    if key == "":
        return
    if len(key) > INDEX_NAME_MAX_LENGTH:  # some movie titles are too long!
        return
    if dictionary.get(key) is None:
        dictionary[key] = {}
        dictionary[key][value] = tf
    else:
        if dictionary[key].get(value) is None:
            dictionary[key][value] = tf
        else:
            dictionary[key][value] += tf
# "仙履奇缘(港", "台)"  "XX(台)x" 哈利波特1：神秘的魔法石(港/台) / 哈1 / Harry Potter and the Philosopher's Stone
def dealWithAlias(title):
    pos = title.find(u"(台)")
    if pos != -1:
        string = title[:pos]
        return string
    pos = title.find(u"(港)")
    if pos != -1:
        string = title[:pos]
        return string
    pos = title.find(u"(港")
    if pos != -1:
        string = title[:pos]
        return string
    pos = title.find(u"(台")
    if pos != -1:
        string = title[:pos]
        return string
    pos = title.find(u"港)")
    if pos != -1:
        return ""
    pos = title.find(u"台)")
    if pos != -1:
        return ""
    return title
# print dealWithAlias(u"台)")

def generateTitleA(dictionary, titleList, alias=False):
    for title in titleList:
        if alias:
            title = dealWithAlias(title)
        addIntoDict(dictionary, title, 'a1')
        titleSplitSign = splitSign(title)
        if len(titleSplitSign) > 1:
            for title2 in titleSplitSign:
                addIntoDict(dictionary, title2, "a2")
        titleSplit = title.split()
        for title2 in titleSplit:
            addIntoDict(dictionary, reduceSign(title2), "a2")
    # for key in dictionary:
    #     print key, dictionary[key]
# generateTitle({}, [u"你好#@啊 &我是 傻~逼 傻逼*我是 你@#好"])

def generateYearA(dictionary, yearList):
    if len(yearList) == 0:
        return
    addIntoDict(dictionary, reduceSign(yearList[0]), "a4")
    # for key in dictionary:
    #     print key, dictionary[key]
# generateYear({}, ["(2015)"])

def generateRatingA(dictionary, ratingList):
    for rating in ratingList:
        addIntoDict(dictionary, rating, "a5")

def generatePeopleA(dictionary, nameList, important=False):  # importance means some people are playing important role
    if important:  # director or first five actors
        if len(nameList) <= 5:
            for name in nameList:
                addIntoDict(dictionary, name, "a7")
                nameSplitSign = splitSign(name)  # 克里斯托弗·诺兰
                if len(nameSplitSign) > 1:
                    for name2 in nameSplitSign:
                        addIntoDict(dictionary, name2, "a7")
        else:
            for i in range(5):
                name = nameList[i]
                addIntoDict(dictionary, name, "a7")
                nameSplitSign = splitSign(name)  # 克里斯托弗·诺兰
                if len(nameSplitSign) > 1:
                    for name2 in nameSplitSign:
                        addIntoDict(dictionary, name2, "a7")
            for i in range(5, len(nameList)):
                name = nameList[i]
                addIntoDict(dictionary, name, "a6")
                nameSplitSign = splitSign(name)  # 克里斯托弗·诺兰
                if len(nameSplitSign) > 1:
                    for name2 in nameSplitSign:
                        addIntoDict(dictionary, name2, "a6")
    else:
        for name in nameList:
            addIntoDict(dictionary, name, "a6")
            nameSplitSign = splitSign(name)  # 克里斯托弗·诺兰
            if len(nameSplitSign) > 1:
                for name2 in nameSplitSign:
                    addIntoDict(dictionary, name2, "a6")
    # for key in dictionary:
    #     print key, dictionary[key]
# generatePeople({}, [u"你·好", u"我", u"OK", u"OKOK**OK", u"啊哈哈", u"你好啊", u"我#是猪", u"订单", u"匹配"], True)

def generateTitleB(dictionary, titleList, alias=False):
    for title in titleList:
        if alias:
            title = dealWithAlias(title)
        titleSplitSign = splitSign(title)  # has been added in a2
        for title2 in titleSplitSign:
            jieba_cut_title_list = jieba.lcut_for_search(title2)
            if len(jieba_cut_title_list) > 1:
                for title3 in jieba_cut_title_list:
                    if title3 == title2:  # 克里斯 cut出 克里斯 和 克里  克里斯不用再添加了
                        continue
                    addIntoDict(dictionary, title3, "b1")
    # for key in dictionary:
    #     print key, dictionary[key]
# generateTitleB({}, [u"超级无敌羊咩咩大电影之咩最劲(港)"], alias=True)
def generatePeopleB(dictionary, nameList):
    for name in nameList:
        nameSplitSign = splitSign(name)  # has been added in a6 a7
        for name2 in nameSplitSign:
            jieba_cut_name_list = jieba.lcut_for_search(name2)
            if len(jieba_cut_name_list) > 1:
                for name3 in jieba_cut_name_list:
                    if name3 == name2:  # 克里斯 cut出 克里斯 和 克里  克里斯不用再添加了
                        continue
                    addIntoDict(dictionary, name3, "b2")
    # for key in dictionary:
    #     print key, dictionary[key]
# generatePeopleB({}, [u"克里斯托弗-诺兰", u"克里斯"])
def generateInfoB(dictionary, infoList):
    for info in infoList:
        # 2015-07-24(中国大陆)
        infoSplitSign = splitSign(info)
        for info2 in infoSplitSign:
            addIntoDict(dictionary, info2, "b5")
            jieba_cut_info_list = jieba.lcut_for_search(info2)
            if len(jieba_cut_info_list) > 1:
                for info3 in jieba_cut_info_list:
                    if info3 == info2:  # 中国大陆 有 中国大陆 和 中国 和 大陆
                        continue
                    addIntoDict(dictionary, info3, "b5")
#     for key in dictionary:
#         print key, dictionary[key]
# generateInfoB({}, [u"2015-07-12（中国大陆）",u"爱情"])
def generateIntroC(dictionary, introList):
    jieba_cut_intro_list = []
    longIntro = u""
    for intro in introList:
        jieba_cut_intro_list += jieba.lcut_for_search(intro)
        longIntro += intro
    jieba_cut_intro_list = [y for y in jieba_cut_intro_list if not isSign(y)]
    jieba_cut_intro_set = set(jieba_cut_intro_list)
    for word in jieba_cut_intro_set:  # for every word, search its term frequency
        pattern = re.compile(word)
        tf = len(re.findall(pattern, longIntro))
        # print word, tf
        addIntoDict(dictionary, word, "c2", tf)
    # for key in dictionary:
    #     print key, dictionary[key]
# generateIntroC({}, [u"民国时期，外敌入侵，军阀混战，乱世中各类江湖人物纷纷登场。不谙世事的小道士何安下（王宝强 饰），外敌的入侵"])







