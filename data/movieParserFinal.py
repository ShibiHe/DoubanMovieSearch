# -*- coding: UTF-8 -*-
import json
import codecs
import math
import Generate_key
import re
ENABLE_LIMITED_RESULTS_1000 = True  # one keyword at most have 1000 urls
MOVIE_PARSER_OPEN_FILES = ["movieFinal1-6930", "movieFinal2-2150", "movieFinal3-30850"]
index_dictionary = {}
data = []
for fileName in MOVIE_PARSER_OPEN_FILES:
    try:
        with open(fileName+".json") as f:
            for line in f:
                data.append(json.loads(line))
    except IOError:
        print "doesn't have "+fileName+".json"
        break
print "Number of movies:", len(data), "Press Enter to continue"
inputs = raw_input()

processed_item = 0
for item in data:
    processed_item += 1
    print "currently parsing item:", processed_item
    dictionary = {}
    print item["F_movieLink"][0]
    Generate_key.generateTitleA(dictionary, item["A_movieTitle"])
    Generate_key.generateTitleA(dictionary, item["A_movieAlias"], alias=True)
    Generate_key.generateYearA(dictionary, item["B_movieYear"])
    Generate_key.generateRatingA(dictionary, item["D_movieRating"])
    Generate_key.generatePeopleA(dictionary, item["C_movieDirector"], important=True)
    Generate_key.generatePeopleA(dictionary, item["movieActor"], important=True)
    Generate_key.generatePeopleA(dictionary, item["movieWriter"])
    Generate_key.generateTitleB(dictionary, item["A_movieTitle"])
    Generate_key.generateTitleB(dictionary, item["A_movieAlias"], alias=True)
    Generate_key.generatePeopleB(dictionary, item["C_movieDirector"]+item["movieActor"]+item["movieWriter"])
    Generate_key.generateInfoB(dictionary, item["movieInfo"])
    Generate_key.generateIntroC(dictionary, item["E_movieIntro"])
    # for key in dictionary:
    #     print key, dictionary[key]
    # inputs = raw_input()
    for key in dictionary:
        # key: http://movie.douban.com/subject/25723907/<info>a1:2c2:10b1:1<br>http://XXX/<info>c2:1<br>...
        original_url = item["F_movieLink"][0]
        pattern = re.compile(r"subject/(.*?)/")
        reIt = re.search(pattern, original_url)
        url_number = reIt.group(1)
        br_string = url_number+"<info>"
        for key2 in dictionary[key]:
            br_string += key2+":"+str(dictionary[key][key2])
        # 25723907/<info>a1:2c2:10b1:1<br>123456<info>c2:1<br>...
        # print key, br_string
        # inputs= raw_input()
        if index_dictionary.get(key) is None:
            index_dictionary[key] = br_string
        else:
            index_dictionary[key] += "<br>"+br_string


def calcDFT(stringIn):
    ABC_DFT = BC_DFT = C_DFT = 0
    urls = stringIn.split("<br>")
    for url in urls:
        s = url.split("<info>")
        ABC_DFT += 1  # this word must appear in a or b or c
        if s[1].find("c") != -1 or s[1].find("b") != - 1:
            BC_DFT += 1
        if s[1].find("c") != -1:
            C_DFT += 1
    return ABC_DFT, BC_DFT, C_DFT
    # if BC_IDFT == 0:  # this word is only in a
    #     return 50
    # return math.log((N/DFT), 2.0)  # DFT=10000 idft=1.967

def processSigns(string):
    stringSplit = string.split('\\')
    s = u""
    for littleS in stringSplit:
        s += littleS + r"\\"
    string = s[:-2]
    stringSplit = string.split('"')
    s = u""
    for littleS in stringSplit:
        s += littleS + r'\"'
    s = s[:-2]
    return s

def reduceURLsTo1000(string):  # 25723907<info>a1:2c2:10b1:1<br>123456<info>c2:1<br>...
    urls = string.split("<br>")
    urlSet = set()
    for url in urls:
        if url.find("a") != -1:
            urlSet.add(url)
    for url in urls:
        if url.find("b") != -1:
            urlSet.add(url)
    for url in urls:
        if len(urlSet) >= 1000:
            return urlSet
        urlSet.add(url)
    return urlSet

writing_count = 0
file_object = codecs.open("new_index_insert.sql", "wb", "utf-8")
for key, value in index_dictionary.iteritems():
    writing_count += 1
    print "currently writing:", writing_count
    strings = u""
    abc_dft, bc_dft, c_dft = calcDFT(value)
    if abc_dft > 1000 and ENABLE_LIMITED_RESULTS_1000:
        new_url_set = reduceURLsTo1000(value)
        new_content = ""
        for url in new_url_set:
            new_content += url+"<br>"
        new_content = new_content[:-4]
        strings += "insert ignore into new_index(name,content,abc_dft,bc_dft,c_dft) values "
        strings += '("%s","%s",%s,%s,%s);\r\n' % (processSigns(key), new_content, str(abc_dft), str(bc_dft), str(c_dft))
    else:
        strings += "insert ignore into new_index(name,content,abc_dft,bc_dft,c_dft) values "
        strings += '("%s","%s", %s, %s, %s);\r\n' % (processSigns(key), value, str(abc_dft), str(bc_dft), str(c_dft))
    file_object.write(strings)
    # print strings
    # inputs = raw_input()
file_object.close()










