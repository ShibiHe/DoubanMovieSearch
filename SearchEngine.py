# -*- coding: utf-8 -*-
import MySQLdb as mdb
import math
import json
import jieba
import collections
AMOUNT_OF_FINAL_RESULT = 100

ENABLE_C2RESULTS_LIMITED = True
ONLY_SHOW_TOP_RESULTS_OFb1b2b5 = True
SHOW_AT_LEAST_RESULTS_OFb1b2b5 = 500  # 1000 is OK!

def getContentDFTFromOneName(name):  # get a string
    con = mdb.connect(host="localhost", user="root", passwd="", db="douban_movie",
                      charset="utf8", use_unicode=True)
    if not isinstance(name, unicode):
        name = name.decode("utf-8")
    string = "select content,abc_dft,bc_dft,c_dft from new_index where name='" + name + "'"
    with con:
        cur = con.cursor()
        cur.execute(string)
        ver = cur.fetchone()
    if ver is None:
        print "In MySql, there is no name =", name
        return None, None, None, None
    # print ver
    abc_dft = ver[1]
    bc_dft = ver[2]
    c_dft = ver[3]
    # 25723907<info>a1:2c2:10b1:1<br>123456<info>c2:1<br>... or too many
    content = ver[0].split("<br>")  # 25723907<info>a1:2c2:10b1:1
    for i in range(len(content)):
        content_it = content[i]
        divided = content_it.split("<info>")
        content[i] = "http://movie.douban.com/subject/"+divided[0]+"/"+"<info>"+divided[1]
    print "found name =", name
    return content, abc_dft, bc_dft, c_dft
# contents, idfts = getContentIDFTFromOneName(u"科幻")
# print contents
# print idfts
def addIntoURLSet_url_tf(aimSet, url, info, category):
    pos = info.find(category)
    if pos == -1:
        return False
    number = ""
    for i in range(pos+3, len(info)):
        if info[i] in set(['a', 'b', 'c']):
            break
        number += info[i]
    url += "<tf>"+number
    aimSet.add(url)
    return True
def createPrioritySetsFromURLList(URLList):
    a1_url_set = set()
    a2_url_set = set()
    a4_url_set = set()
    a5_url_set = set()
    a6_url_set = set()
    a7_url_set = set()
    b1_url_set = set()
    b2_url_set = set()
    b5_url_set = set()
    c2_url_set = set()
    for item in URLList:  # http://movie.douban.com/subject/2082209/<info>a1:1a2:2b5:1c2:3
        alist = item.split("<info>")
        url = alist[0]
        keyInfo = alist[1]
        # a1
        addIntoURLSet_url_tf(a1_url_set, url, keyInfo, "a1")
        addIntoURLSet_url_tf(a2_url_set, url, keyInfo, "a2")
        addIntoURLSet_url_tf(a4_url_set, url, keyInfo, "a4")
        addIntoURLSet_url_tf(a5_url_set, url, keyInfo, "a5")
        addIntoURLSet_url_tf(a6_url_set, url, keyInfo, "a6")
        addIntoURLSet_url_tf(a7_url_set, url, keyInfo, "a7")
        addIntoURLSet_url_tf(b1_url_set, url, keyInfo, "b1")
        addIntoURLSet_url_tf(b2_url_set, url, keyInfo, "b2")
        addIntoURLSet_url_tf(b5_url_set, url, keyInfo, "b5")
        addIntoURLSet_url_tf(c2_url_set, url, keyInfo, "c2")
    # print "a1", a1_url_set
    # print "a2", a2_url_set
    # print "a4", a4_url_set
    # print "a5", a5_url_set
    # print "a6", a6_url_set
    # print "a7", a7_url_set
    # print "b1", b1_url_set
    # print "b2", b2_url_set
    # print "b5", b5_url_set
    # print "c2", c2_url_set
    return a1_url_set, a2_url_set, a4_url_set, a5_url_set, a6_url_set, a7_url_set, \
        b1_url_set, b2_url_set, b5_url_set, c2_url_set
# createPrioritySetFromURLList(["http://movie.douban.com/subject/2/<info>a1:1a2:2b5:1c2:3","http://movie.douban.com/subject/1/<info>c2:3"])
def getDictionaryFromURL(url):
    con = mdb.connect(host="localhost", user="root", passwd="", db="douban_movie",
                      charset="utf8", use_unicode=True)
    string = u"select * from movie_information where link='" + url + "'"
    with con:
        cur = con.cursor()
        cur.execute(string)
        ver = cur.fetchone()
    if ver is None:
        print "In MySql, there is no url =", url
        return None
    dictionary = {}
    title = ver[1]
    if ver[2] is None:
        alias = ""
    else:
        alias = ver[2]
    if ver[3] is None:
        year = ""
    else:
        year = ver[3]
    if ver[4] is None:
        director = ""
    else:
        director = ver[4]
    if ver[5] is None:
        rating = ""
    else:
        rating = ver[5]
    if ver[6] is None:
        comment_amount = 1
    else:
        comment_amount = ver[6]
    if ver[7] is None:
        betterThan = ""
    else:
        betterThan = ver[7]
    if ver[8] is None:
        intro = ""
    else:
        intro = ver[8]
    link = ver[9]
    if ver[10] is None:
        writer = ""
    else:
        writer = ver[10]
    if ver[11] is None:
        actor = ""
    else:
        actor = ver[11]
    if ver[12] is None:
        info = ""
    else:
        info = ver[12]
    dictionary["a_title"] = title
    dictionary["b_alias"] = alias
    dictionary["c_year"] = year
    dictionary["g_director"] = director
    dictionary["d_rating"] = rating
    dictionary["e_comment_amount"] = comment_amount
    dictionary["h_betterThan"] = betterThan
    dictionary["l_intro"] = intro
    dictionary["f_link"] = link
    dictionary["j_writer"] = writer
    dictionary["i_actor"] = actor
    dictionary["k_info"] = info
    # print type(link)
    # inputs = raw_input()
    return dictionary

def ratingEvaluationSystem(url, use_tf=False, use_cf=False):
    con = mdb.connect(host="localhost", user="root", passwd="", db="douban_movie",
                      charset="utf8", use_unicode=True)
    split_ed = url.split("<tf>")
    url = split_ed[0]
    frequency = int(split_ed[1])
    string = u"select * from movie_information where link='" + url + "'"
    with con:
        cur = con.cursor()
        cur.execute(string)
        ver = cur.fetchone()
    if ver is None:
        print "In MySql, there is no url =", url
        return None
    # print ver
    rating = ver[5]  # unicode could be ""
    if rating == "":
        rating = 2.0
    else:
        rating = float(rating)
    comment_amount = ver[6]  # int  least is 1
    betterThan = ver[7]  # unicode could be ""
    if comment_amount < 100:
        coefficientOfCommentAmount = 1.0
    else:
        coefficientOfCommentAmount = math.log(comment_amount, 10)
    final_rating = rating*coefficientOfCommentAmount
    if use_tf:
        tf_coefficient = 1 + math.log(frequency, 10)
        final_rating *= tf_coefficient
    if use_cf:
        if frequency == 3:
            ctf_coefficient = 0.8
            # print "next one is cf:3"
        if frequency == 2:
            ctf_coefficient = 0.6
            # print "next one is cf:2"
        if frequency == 1:
            ctf_coefficient = 0
        final_rating = 60*ctf_coefficient - ctf_coefficient*final_rating + final_rating
    # print url, final_rating
    return final_rating
# print ratingEvaluationSystem("http://movie.douban.com/subject/1292052/")
def rankingOnlyRating(ASet, use_tf=False, use_cf=False):
    aList = list(ASet)
    aList = sorted(aList, key=lambda x: ratingEvaluationSystem(x, use_tf=use_tf, use_cf=use_cf), reverse=True)
    aList = [x.split("<tf>")[0] for x in aList]
    return aList

def getResultDictionaryListFromOneSingleWord(name, return_dictionaryList=True):
    urlList, abc_dft, bc_dft, c_dft = getContentDFTFromOneName(name)
    if urlList is None:
        return []
    print abc_dft, bc_dft, c_dft
    a1_url_set, a2_url_set, a4_url_set, a5_url_set, a6_url_set, a7_url_set, b1_url_set, b2_url_set, b5_url_set, \
        c2_url_set = createPrioritySetsFromURLList(urlList)

    result1 = rankingOnlyRating(a1_url_set)
    for x in result1:
        print "result1:", x

    result2 = rankingOnlyRating(a2_url_set)
    for x in result2:
        print "result2:", x

    # a4 a5 a7
    setA457 = a4_url_set.copy()
    setA457.update(a5_url_set)
    setA457.update(a7_url_set)
    result3 = rankingOnlyRating(setA457)
    for x in result3:
        print "result3:", x

    result4 = rankingOnlyRating(a6_url_set)
    for x in result4:
        print "result4:", x

    # b1 b2 b5
    setB125 = b1_url_set.copy()
    setB125.update(b2_url_set)
    setB125.update(b5_url_set)
    cf_set = set()
    for item in setB125:
        split_item = item.split("<tf>")
        url = split_item[0]
        cf = 0
        if item in b1_url_set:
            cf += 1
        if item in b2_url_set:
            cf += 1
        if item in b5_url_set:
            cf += 1
        url += "<tf>"+str(cf)
        cf_set.add(url)
    result5 = rankingOnlyRating(cf_set, use_cf=True)
    for x in result5:
        print "result5:", x

    if ENABLE_C2RESULTS_LIMITED and len(result1)+len(result2)+len(result3)+len(result4)+len(result5) < 500:
        result6 = rankingOnlyRating(c2_url_set.copy(), use_tf=True)
        for x in result6:
            print "result6:", x
    else:
        print "no c2 results because of ENABLE_C2RESULTS_LIMITED"
        result6 = []

    # 记得去掉result之间的重复
    already_output = set()
    urlResultFinal = []
    for x in result1:
        urlResultFinal.append(x)
        already_output.add(x)
    for x in result2:
        if x in already_output:
            continue
        urlResultFinal.append(x)
        already_output.add(x)
    for x in result3:
        if x in already_output:
            continue
        urlResultFinal.append(x)
        already_output.add(x)
    for x in result4:
        if x in already_output:
            continue
        urlResultFinal.append(x)
        already_output.add(x)
    for x in result5:
        if ONLY_SHOW_TOP_RESULTS_OFb1b2b5 and len(already_output) >= SHOW_AT_LEAST_RESULTS_OFb1b2b5:
            break
        if x in already_output:
            continue
        urlResultFinal.append(x)
        already_output.add(x)
    for x in result6:
        if ONLY_SHOW_TOP_RESULTS_OFb1b2b5 and len(already_output) >= SHOW_AT_LEAST_RESULTS_OFb1b2b5:
            break
        if x in already_output:
            continue
        urlResultFinal.append(x)
        already_output.add(x)

    if not return_dictionaryList:  # return a url list
        return urlResultFinal

    # output a dictionary list
    output_list = []
    for x in urlResultFinal:
        output_list.append(getDictionaryFromURL(x))
        line = json.dumps(dict(output_list[-1]), ensure_ascii=False, sort_keys=True)
        print line
    # print output_list
    return output_list
# getResultDictionaryListFromOneSingleWord(u"科幻")

def getResultDictionaryListFromSentence(sentence):
    words = sentence.split("+")
    words_results = []
    longest_result_length = 0
    some_new_jieba_words = []
    for word in words:
        one_result = getResultDictionaryListFromOneSingleWord(word, return_dictionaryList=False)
        if len(one_result) == 0:
            some_new_jieba_words += jieba.lcut_for_search(word)
            continue
        words_results.append(one_result)
        if len(one_result) > longest_result_length:
            longest_result_length = len(one_result)
    if len(some_new_jieba_words) > 0:
        for word in some_new_jieba_words:
            one_result = getResultDictionaryListFromOneSingleWord(word, return_dictionaryList=False)
            words_results.append(one_result)
            if len(one_result) > longest_result_length:
                longest_result_length = len(one_result)

    URLOrderDict = collections.OrderedDict()
    for movie_pos in range(longest_result_length):
        for word_pos in range(len(words_results)):
            if movie_pos >= len(words_results[word_pos]):
                continue
            if URLOrderDict.get(words_results[word_pos][movie_pos]) is None:
                URLOrderDict[words_results[word_pos][movie_pos]] = 1
            else:
                URLOrderDict[words_results[word_pos][movie_pos]] += 1
    final_dictionaryList = []
    for appearance in reversed(range(len(words_results))):
        for url in URLOrderDict:
            if len(final_dictionaryList) > AMOUNT_OF_FINAL_RESULT:
                break
            if URLOrderDict[url] == appearance+1:
                print url, URLOrderDict[url]
                final_dictionaryList.append(getDictionaryFromURL(url))
                line = json.dumps(dict(final_dictionaryList[-1]), ensure_ascii=False, sort_keys=True)
                print line
    return final_dictionaryList
# getResultDictionaryListFromSentence(u"霍金")
# getResultDictionaryListFromSentence(u"魔法 传说")
# getResultDictionaryListFromSentence(u"科幻")
# getResultDictionaryListFromSentence(u"科幻电影与未来时代")
# getResultDictionaryListFromSentence(u"科幻+爱情")
getResultDictionaryListFromSentence(u"身手敏捷")
# getResultDictionaryListFromSentence(u"悬疑")
# getResultDictionaryListFromSentence(u"冒险+英雄")
# getResultDictionaryListFromSentence(u"诺兰")

