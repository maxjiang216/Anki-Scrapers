import requests
import bs4

inFile = open('words.txt','r',encoding='utf8')
outFile = open("anki.txt",'w',encoding='utf8')

done_words = set()

for i in inFile:
    if "Japanese dictionary search for " not in i:
        continue
    word = i.split("\"")[1]

    url = "https://jisho.org/search/" + word
    r = requests.get(url)
    b = bs4.BeautifulSoup(r.content, 'html.parser')

    if word in done_words:
        continue
    done_words.add(word)

    meanings = []
    word = ""
    wordsplit = []
    furisplit = []
    furigana = ""
    haveFuri = False
    counter = 0
    word_class = ''
    skipnext = False
    done_sentence = False

    for i in b.find_all("div",{"class":"clearfix"}):
        for j in i.find_all("span", {"class": "text"}):
            for k in j:
                if "<span>" in str(k).strip(): # Hiragana
                    wordsplit.append(str(k).split('>')[1].split('<')[0])
                    counter += 1
                elif len(str(k).strip()) > 0: # Kanji
                    haveFuri = True
                    for m in range(len(str(k).strip())):
                        wordsplit.append(counter)
                        counter += 1
            #print(wordsplit)
            word += j.text.strip()
            break

        if not done_sentence:
            url2 = "https://jisho.org/search/{0}%20%23sentences".format(word)
            r2 = requests.get(url)
            b2 = bs4.BeautifulSoup(r.content, 'html.parser')

            ex_sentence = ''

            for sentence in b2.find_all("li", {"class": "sentence"}):
                tempSent = ""
                tempFuri = []
                tempKanji = []
                currPos = 0
                tempSent2 = sentence.text.split('\n')
                tempSent = ''
                for part in tempSent2:
                    if not (len(part) < 3 or part == "— Tatoeba" or part == "Details ▸" \
                            or all(k.isdigit() for k in part) or all(k.isspace() for k in part)):
                        tempSent += part
                for k in sentence.find_all("ul", {"class", "japanese_sentence"}):
                    for i2 in k.find_all("li", {"class", "clearfix"}):
                        furis = i2.find_all("span", {"class": "furigana"})  # Check if it is a Kanji with Furigana
                        if not furis:
                            continue
                        tempFuri.append(i2.text)
                        for j2 in i2.find_all("span", {"class": "unlinked"}):
                            tempKanji.append(j2.text)
                for i2 in range(len(tempFuri)):  # Replace text
                    xPos = tempSent[currPos:].find(tempFuri[i2])
                    tempSent = tempSent[:currPos + xPos] + tempKanji[i2] + tempSent[currPos + xPos + len(tempFuri[i2]):]
                    currPos = xPos + len(tempKanji[i2])

                temp_eng = sentence.find("div", {"class": "english_sentence"}).text.split('\n')[1]  # Add English
                tempSent = tempSent[:-1 * len(temp_eng)]
                sentenceEnd = ['」', '。', '？', '！']
                if tempSent[-1] in sentenceEnd:
                    tempSent += '<br>' + temp_eng
                else:
                    tempSent += '。<br>' + temp_eng
                ex_sentence = tempSent + '<br><br>'
                done_sentence = True
                break

        for j in i.find_all("span",{"class":"furigana"}):
            for k in j.find_all("span"):
                furisplit.append(k.text)
        #print(furisplit)
        counter = 0
        for j in wordsplit:
            if isinstance(j,int):
                try:
                    furigana += furisplit[j]
                except IndexError:
                    try:
                        furigana = furisplit[0]
                        break
                    except IndexError:
                        furigana = i.find("rt").text
                        break
            else:
                furigana += j
        temp = ''

        for j in i.find_all("div",{"class":"meanings-wrapper"}):
            numMeaning = 0
            for k in j.find_all("div",{"class":["meaning-wrapper","meaning-tags"]}):
                if "meaning-tags" in k.get("class"):  # Class
                    if "Wikipedia" in k.text or "Place" in k.text or "Other forms" in k.text or "Notes" in k.text:
                        break
                else:  # Meaning
                    numMeaning += 1
            for k in j.find_all("div",{"class":["meaning-wrapper","meaning-tags"]}):
                if skipnext:
                    skipnext = False
                    continue
                if "meaning-tags" in k.get("class"): # Class
                    if "Wikipedia" in k.text or "Place" in k.text:
                        skipnext = True
                        continue
                    elif "Other forms" in k.text or "Notes" in k.text:
                        if ex_sentence:
                            temp += ex_sentence
                            ex_sentence = ''
                        if numMeaning == 1 and word_class:
                            temp += word_class + '<br><br>'
                            word_class = ''
                        temp += k.text + '<br>'
                    elif numMeaning == 1:
                        word_class = k.text

                else: # Meaning
                    try:
                        temp += k.find("span",{"class":"meaning-meaning"}).text
                    except:
                        temp += k.text
                    for l in k.find_all("span", {"class", "supplemental_info"}):
                        first = True
                        for m in l.text.split(', '):
                            if (not "Usually written using kana alone" in m \
                                and not "Onomatopoeic or mimetic word" in m \
                                and not "See also " in m\
                                and not "Antonym: " in m\
                                and not "Synonym: " in m\
                                and not "Yojijukugo (four character compound)" in m) or\
                               (numMeaning == 1 and not "See also " in m\
                                and not "Antonym: " in m\
                                and not "Synonym: " in m):
                                if first:
                                    if numMeaning == 1:
                                        temp += '<br>'
                                    temp += '<br>' + m
                                    first = False
                                else:
                                    temp += ', ' + m
                    temp += '<br><br>'
                    sentence = k.find("div",{"class":"sentence"})
                    if not sentence:
                        continue
                    tempSent = ""
                    tempFuri = []
                    tempKanji = []
                    currPos = 0
                    tempSent = sentence.text
                    for i in sentence.find_all("li",{"class","clearfix"}):
                        furis = i.find_all("span", {"class": "furigana"}) # Check if it is a Kanji with Furigana
                        if not furis:
                            continue
                        tempFuri.append(i.text)
                        for j in i.find_all("span", {"class": "unlinked"}):
                            tempKanji.append(j.text)
                    for i in range(len(tempFuri)): # Replace text
                        xPos = tempSent[currPos:].find(tempFuri[i])
                        tempSent = tempSent[:currPos+xPos] + tempKanji[i] + tempSent[currPos+xPos+len(tempFuri[i]):]
                        currPos = xPos + len(tempKanji[i])

                    temp_eng = sentence.find("li",{"class":"english"}).text # Add English
                    tempSent = tempSent[:-1 * len(temp_eng)]
                    sentenceEnd = ['」','。','？','！']
                    if tempSent[-1] in sentenceEnd:
                        tempSent += '<br>' + temp_eng
                    else:
                        tempSent += '。<br>' + temp_eng
                    if tempSent:
                        ex_sentence = ''
                    temp += tempSent + '<br><br>'
            break

        temp = temp.replace("\"","\"\"")
        temp = temp.split("<br>")
        while temp[-1] == '':
            temp.pop(-1)
        temp = '<br>'.join(temp)
        meanings.append(temp)
        break

    out = word+';'
    if haveFuri:
        out += furigana
    out += ';\"' + "<br>".join(meanings).strip()
    if ex_sentence:
        out += '<br><br>' + ex_sentence
    if numMeaning == 1 and word_class:
        out += '<br><br>' + word_class
    while out.find('<br><br><br>') != -1:
        out = out.replace("<br><br><br>","<br><br>")
    while out[-4:] == '<br>':
        out = out[:-4]
    out += '\"\n'
    print(out)
    outFile.write(out)

inFile.close()
outFile.close()