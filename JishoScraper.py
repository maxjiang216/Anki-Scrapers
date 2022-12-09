import requests
import bs4


def jisho(file_name):
    """Generates an Anki deck from the vocublary words found in file_name.txt
    Writes the results in the file file_name_anki.txt"""

    inFile = open(file_name + ".txt", "r", encoding="utf8")
    outFile = open(file_name + "_anki.txt", "w", encoding="utf8")

    done_words = set()

    for i in inFile:

        word = i

        url = "https://jisho.org/search/" + word
        r = requests.get(url)
        b = bs4.BeautifulSoup(r.content, "html.parser")

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
        word_class = ""
        skipnext = False
        done_sentence = False

        for i in b.find_all("div", {"class": "clearfix"}):
            for j in i.find_all("span", {"class": "text"}):
                for k in j:
                    if "<span>" in str(k).strip():  # Hiragana
                        wordsplit.append(str(k).split(">")[1].split("<")[0])
                        counter += 1
                    elif len(str(k).strip()) > 0:  # Kanji
                        haveFuri = True
                        for m in range(len(str(k).strip())):
                            wordsplit.append(counter)
                            counter += 1
                word += j.text.strip()
                break

            if not done_sentence:
                url2 = "https://jisho.org/search/{0}%20%23sentences".format(word)
                r2 = requests.get(url2)
                b2 = bs4.BeautifulSoup(r2.content, "html.parser")

                ex_sentence = ""

                for sentence in b2.find_all("li", {"class": "sentence"}):
                    tempSent = ""
                    tempFuri = []
                    tempKanji = []
                    currPos = 0
                    tempSent2 = sentence.text.split("\n")
                    for part in tempSent2:
                        if not (
                            len(part) < 3
                            or part == "— Tatoeba"
                            or part == "Details ▸"
                            or all(k.isdigit() for k in part)
                            or all(k.isspace() for k in part)
                        ):
                            tempSent += part
                    for k in sentence.find_all("ul", {"class", "japanese_sentence"}):
                        for i2 in k.find_all("li", {"class", "clearfix"}):
                            furis = i2.find_all(
                                "span", {"class": "furigana"}
                            )  # Check if it is a Kanji with Furigana
                            if not furis:
                                continue
                            tempFuri.append(i2.text)
                            for j2 in i2.find_all("span", {"class": "unlinked"}):
                                tempKanji.append(j2.text)
                    for i2 in range(len(tempFuri)):  # Replace text
                        xPos = tempSent[currPos:].find(tempFuri[i2])
                        tempSent = (
                            tempSent[: currPos + xPos]
                            + tempKanji[i2]
                            + tempSent[currPos + xPos + len(tempFuri[i2]) :]
                        )
                        currPos = xPos + len(tempKanji[i2])

                    temp_eng = sentence.find(
                        "div", {"class": "english_sentence"}
                    ).text.split("\n")[
                        1
                    ]  # Add English
                    tempSent = tempSent[: -1 * len(temp_eng)]
                    sentenceEnd = ["」", "。", "？", "！"]
                    if tempSent[-1] in sentenceEnd:
                        tempSent += "<br>" + temp_eng
                    else:
                        tempSent += "。<br>" + temp_eng
                    ex_sentence = tempSent + "<br><br>"
                    done_sentence = True
                    break

            for j in i.find_all("span", {"class": "furigana"}):
                for k in j.find_all("span"):
                    furisplit.append(k.text)
            counter = 0
            for j in wordsplit:
                if isinstance(j, int):
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
            temp = ""

            for j in i.find_all("div", {"class": "meanings-wrapper"}):
                numMeaning = 0
                for k in j.find_all(
                    "div", {"class": ["meaning-wrapper", "meaning-tags"]}
                ):
                    if "meaning-tags" in k.get("class"):  # Class
                        if (
                            "Wikipedia" in k.text
                            or "Place" in k.text
                            or "Other forms" in k.text
                            or "Notes" in k.text
                        ):
                            break
                    else:  # Meaning
                        numMeaning += 1
                for k in j.find_all(
                    "div", {"class": ["meaning-wrapper", "meaning-tags"]}
                ):
                    if skipnext:
                        skipnext = False
                        continue
                    if "meaning-tags" in k.get("class"):  # Class
                        if "Wikipedia" in k.text or "Place" in k.text:
                            skipnext = True
                            continue
                        elif "Other forms" in k.text or "Notes" in k.text:
                            if ex_sentence:
                                temp += ex_sentence
                                ex_sentence = ""
                            if numMeaning == 1 and word_class:
                                temp += word_class + "<br><br>"
                                word_class = ""
                            temp += k.text + "<br>"
                        elif numMeaning == 1:
                            word_class = k.text

                    else:  # Meaning
                        try:
                            temp += k.find("span", {"class": "meaning-meaning"}).text
                        except:
                            temp += k.text
                        for l in k.find_all("span", {"class", "supplemental_info"}):
                            first = True
                            for m in l.text.split(", "):
                                if (
                                    not "Usually written using kana alone" in m
                                    and not "Onomatopoeic or mimetic word" in m
                                    and not "See also " in m
                                    and not "Antonym: " in m
                                    and not "Synonym: " in m
                                    and not "Yojijukugo (four character compound)" in m
                                ) or (
                                    numMeaning == 1
                                    and not "See also " in m
                                    and not "Antonym: " in m
                                    and not "Synonym: " in m
                                ):
                                    if first:
                                        if numMeaning == 1:
                                            temp += "<br>"
                                        temp += "<br>" + m
                                        first = False
                                    else:
                                        temp += ", " + m
                        temp += "<br><br>"
                        sentence = k.find("div", {"class": "sentence"})
                        if not sentence:
                            continue
                        tempSent = ""
                        tempFuri = []
                        tempKanji = []
                        currPos = 0
                        tempSent = sentence.text
                        for i in sentence.find_all("li", {"class", "clearfix"}):
                            furis = i.find_all(
                                "span", {"class": "furigana"}
                            )  # Check if it is a Kanji with Furigana
                            if not furis:
                                continue
                            tempFuri.append(i.text)
                            for j in i.find_all("span", {"class": "unlinked"}):
                                tempKanji.append(j.text)
                        for i in range(len(tempFuri)):  # Replace text
                            xPos = tempSent[currPos:].find(tempFuri[i])
                            tempSent = (
                                tempSent[: currPos + xPos]
                                + tempKanji[i]
                                + tempSent[currPos + xPos + len(tempFuri[i]) :]
                            )
                            currPos = xPos + len(tempKanji[i])

                        temp_eng = sentence.find(
                            "li", {"class": "english"}
                        ).text  # Add English
                        tempSent = tempSent[: -1 * len(temp_eng)]
                        sentenceEnd = ["」", "。", "？", "！"]
                        if tempSent[-1] in sentenceEnd:
                            tempSent += "<br>" + temp_eng
                        else:
                            tempSent += "。<br>" + temp_eng
                        if tempSent:
                            ex_sentence = ""
                        temp += tempSent + "<br><br>"
                break

            temp = temp.replace('"', '""')
            temp = temp.split("<br>")
            while temp[-1] == "":
                temp.pop(-1)
            temp = "<br>".join(temp)
            meanings.append(temp)
            break

        out = word + ";"
        if haveFuri:
            out += furigana
        out += ';"' + "<br>".join(meanings).strip()
        if ex_sentence:
            out += "<br><br>" + ex_sentence
        if numMeaning == 1 and word_class:
            out += "<br><br>" + word_class
        while out.find("<br><br><br>") != -1:
            out = out.replace("<br><br><br>", "<br><br>")
        while out[-4:] == "<br>":
            out = out[:-4]
        out += '"\n'
        outFile.write(out)

    inFile.close()
    outFile.close()


def get_furi(soup):

    inds = []
    counter = 0
    raw = soup.find_all("span", {"class": "text"})[0]
    haveFuri = False
    for chunk in raw:
        if "<span>" in str(chunk).strip():  # Hiragana
            inds.append(str(chunk).split(">")[1].split("<")[0])
            counter += 1
        elif len(str(chunk).strip()) > 0:  # Kanji
            haveFuri = True
            for m in range(len(str(chunk).strip())):
                inds.append(counter)
                counter += 1

    if haveFuri:
        out = ""
        pieces = []
        for chunk in soup.find_all("span", {"class": "furigana"})[0].find_all("span"):
            pieces.append(chunk.text)

        for ind in inds:
            if isinstance(ind, int):
                try:
                    out += pieces[ind]
                except IndexError:
                    try:
                        out = pieces[0]
                        break
                    except IndexError:
                        out = soup.find("rt").text
                        break
            else:
                out += ind

        return out

    return ""


def get_kanji(soup):
    """outputs Anki entry (usu. Kanji) given beautiful soup parse"""

    return soup.find_all("span", {"class": "text"})[0].text.strip()


def get_sentence(sentence):

    tempSent = ""
    tempFuri = []
    tempKanji = []
    currPos = 0
    tempSent = sentence.text
    for chunk in sentence.find_all("li", {"class", "clearfix"}):
        furis = chunk.find_all(
            "span", {"class": "furigana"}
        )  # Check if it is a Kanji with Furigana
        if not furis:
            continue
        tempFuri.append(chunk.text)
        for i in chunk.find_all("span", {"class": "unlinked"}):
            tempKanji.append(i.text)
    for i in range(len(tempFuri)):  # Replace text
        xPos = tempSent[currPos:].find(tempFuri[i])
        tempSent = (
            tempSent[: currPos + xPos]
            + tempKanji[i]
            + tempSent[currPos + xPos + len(tempFuri[i]) :]
        )
        currPos = xPos + len(tempKanji[i])

    temp_eng = sentence.find("li", {"class": "english"}).text  # Add English
    tempSent = tempSent[: -1 * len(temp_eng)]
    sentenceEnd = ["」", "。", "？", "！"]
    if tempSent[-1] in sentenceEnd:
        tempSent += "<br>" + temp_eng
    else:
        tempSent += "。<br>" + temp_eng

    return tempSent + "<br><br>"


def get_example(word):

    out = ""
    url = "https://jisho.org/search/{0}%20%23sentences".format(word)
    r = requests.get(url)
    b = bs4.BeautifulSoup(r.content, "html.parser")

    furi = []
    kanji = []
    pos = 0
    if not b.find_all("li", {"class": "sentence"}):
        return ""
    sentence = b.find_all("li", {"class": "sentence"})[0]
    parts = sentence.text.split("\n")

    for part in parts:
        if not (
            len(part) < 3
            or part == "— Tatoeba"
            or part == "Details ▸"
            or all(i.isdigit() for i in part)
            or all(i.isspace() for i in part)
        ):
            out += part

    for jPart in sentence.find_all("ul", {"class", "japanese_sentence"}):
        for kPart in jPart.find_all("li", {"class", "clearfix"}):
            if not kPart.find_all(
                "span", {"class": "furigana"}
            ):  # Check if it is a Kanji with Furigana
                continue
            furi.append(kPart.text)
            for k in kPart.find_all("span", {"class": "unlinked"}):
                kanji.append(k.text)

    for i in range(len(furi)):  # Replace text
        xPos = out[pos:].find(furi[i])
        try:
            out = out[: pos + xPos] + kanji[i] + out[pos + xPos + len(furi[i]) :]
        except IndexError:
            return
        pos = xPos + len(kanji[i])

    eng = sentence.find("div", {"class": "english_sentence"}).text.split("\n")[
        1
    ]  # Add English
    out = out[: -1 * len(eng)]
    end = ["」", "。", "？", "！"]
    if out[-1] in end:
        out += "<br>" + eng
    else:
        out += "。<br>" + eng

    return out + "<br><br>"


def get_meanings(soup, example=True):

    numMeaning = 0
    # find number of meanings
    for meaning in soup.find_all("div", {"class": "meanings-wrapper"})[0].find_all(
        "div", {"class": ["meaning-wrapper", "meaning-tags"]}
    ):
        if "meaning-tags" in meaning.get("class"):  # Class
            if (
                "Wikipedia" in meaning.text
                or "Place" in meaning.text
                or "Other forms" in meaning.text
                or "Notes" in meaning.text
            ):
                break  # no more useful meanings
        else:  # Meaning
            numMeaning += 1

    out = ""
    word_class = ""
    skipNext = False
    counter = 0
    for chunk in soup.find_all("div", {"class": "meanings-wrapper"})[0].find_all(
        "div", {"class": ["meaning-wrapper", "meaning-tags"]}
    ):
        if "Notes" in chunk.text:
            break  # no more useful meanings
        if skipNext:
            skipNext = False
            continue
        if "meaning-tags" in chunk.get("class"):  # Class
            if "Wikipedia" in chunk.text or "Place" in chunk.text:
                skipNext = True
                continue
            elif "Other forms" in chunk.text or "Notes" in chunk.text:
                if not example:
                    skipNext = True
                    continue
                if numMeaning == 1 and word_class:
                    out += word_class + "<br><br>"
                    word_class = ""
                out += chunk.text + "<br>"
            elif numMeaning == 1:
                word_class = chunk.text
        else:  # Meaning
            try:
                out += chunk.find("span", {"class": "meaning-meaning"}).text
            except:
                out += chunk.text
            for extra in chunk.find_all("span", {"class", "supplemental_info"}):
                first = True
                for note in extra.text.split(", "):
                    if (
                        example
                        and (
                            (
                                not "Onomatopoeic or mimetic word" in note
                                and not "See also " in note
                                and not "Antonym: " in note
                                and not "Synonym: " in note
                                and not "Yojijukugo (four character compound)" in note
                            )
                            or (
                                numMeaning == 1
                                and not "See also " in note
                                and not "Antonym: " in note
                                and not "Synonym: " in note
                            )
                        )
                    ) or (
                        not example
                        and (
                            (
                                not "Onomatopoeic or mimetic word" in note
                                and not "See also " in note
                                and not "Antonym: " in note
                                and not "Synonym: " in note
                                and not "Yojijukugo (four character compound)" in note
                                and not "often " in note
                            )
                            or (
                                numMeaning == 1
                                and not "See also " in note
                                and not "Antonym: " in note
                                and not "Synonym: " in note
                                and not "often " in note
                            )
                        )
                    ):
                        temp = note
                        if "Usually written using kana alone" in note:
                            temp = "Usu. kana"
                        if first:
                            if numMeaning == 1:
                                out += "<br>"
                            out += "<br>" + temp
                            first = False
                        else:
                            out += ", " + temp
            sentence = chunk.find("div", {"class": "sentence"})
            out += "<br><br>"
            if not sentence:
                continue
            else:
                if example:
                    out += get_sentence(sentence)

        if not (
            "Wikipedia" in chunk.text
            or "Place" in chunk.text
            or "Other forms" in chunk.text
            or "Notes" in chunk.text
        ):
            counter += 1
        if counter > min(3, numMeaning):
            break

    return out


def compile_entry(word, done_words):
    """Returns string
    Anki card for word"""

    url = "https://jisho.org/search/" + word
    r = requests.get(url)
    b = bs4.BeautifulSoup(r.content, "html.parser")

    entry = b.find_all("div", {"class": "clearfix"})[0]
    kanji = get_kanji(entry)

    if kanji in done_words:
        return ""
    else:
        done_words.add(kanji)

    furi = get_furi(entry)
    meanings = get_meanings(entry)
    meanings_no_ex = get_meanings(entry, False)
    example = get_example(kanji)

    out = kanji + ";"
    out += furi
    out += ';;"' + meanings
    if example:
        out += "<br><br>" + example
    while out[-4:] == "<br>":
        out = out[:-4]
    out += '";"' + meanings_no_ex
    while out.find("<br><br><br>") != -1:
        out = out.replace("<br><br><br>", "<br><br>")
    while out[-4:] == "<br>":
        out = out[:-4]
    out += '"\n'

    return out


def compile_results(file_name):
    """Generates an Anki deck from the vocublary words found in file_name.txt
    Writes the results in the file file_name_anki.txt"""

    inFile = open(file_name + ".txt", "r", encoding="utf8")
    outFile = open(file_name + "_anki.txt", "w", encoding="utf8")

    done_words = set()

    for line in inFile:

        word = line
        if word in done_words:
            continue

        outFile.write(compile_entry(word, done_words))

    inFile.close()
    outFile.close()


def clean_file(file_name):

    inFile = open(file_name + ".txt", "r", encoding="utf8")
    outFile = open("clean.txt", "w", encoding="utf8")

    done_words = set()

    for line in inFile:

        if "Japanese dictionary search for " in line:
            word = line.split('"')[1]
        else:
            continue
        if word in done_words:
            continue
        done_words.add(word)

        outFile.write(word + "\n")

    inFile.close()
    outFile.close()


clean_file("opera")
compile_results("clean")
