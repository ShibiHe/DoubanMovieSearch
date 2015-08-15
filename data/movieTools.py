# -*- coding: UTF-8 -*-
import json
import codecs

# Tool will get a movie JSON file and generate visited_links.json and XXX-insert-movie_information.sql

MOVIE_TOOLS_OPEN_FILE = "movieFinal2-2150"

current_line = 0;
data = []
with open(MOVIE_TOOLS_OPEN_FILE+".json") as f:
    for line in f:
        data.append(json.loads(line))
        current_line += 1
        print "current line is", current_line

visited_links = {}

def compute_visited_links():
    for item in data:
        visited_links[item['F_movieLink'][0]] = item['A_movieTitle'][0]
    linksFile = codecs.open("visited_links.json", mode="wb", encoding="utf-8")
    json.dump(dict(visited_links), linksFile, ensure_ascii=False, sort_keys=True)

def itemToUString(item):
    result = u""
    for string in item:
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
        result += s + '/<br>/'
    result = result[:-6]
    return result

def createMySql():
    file_object = codecs.open(MOVIE_TOOLS_OPEN_FILE+"-insert-movie_information.sql", "wb", "utf-8")
    for item in data:
        strings = u""
        strings += "insert ignore into movie_information(title,alias,year,director,rating,comment_amount,betterthan," \
                   "intro,link,writer,actor,info) values "
        strings += '("%s","%s","%s","%s","%s",%s,"%s","%s","%s","%s","%s","%s");\r\n' % \
                   (itemToUString(item['A_movieTitle']), itemToUString(item["A_movieAlias"]),
                    itemToUString(item['B_movieYear']), itemToUString(item['C_movieDirector']),
                    itemToUString(item['D_movieRating']), itemToUString(item["movieCommentAmount"]),
                    itemToUString(item["movieBetterThan"]), itemToUString(item['E_movieIntro']),
                    itemToUString(item['F_movieLink']), itemToUString(item['movieWriter']),
                    itemToUString(item['movieActor']), itemToUString(item['movieInfo']))
        file_object.write(strings)
        # print isinstance(strings, unicode) True
        # print strings
        # inputs = raw_input()
    file_object.close()

# main()
compute_visited_links()
createMySql()
