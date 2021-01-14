import requests
import bs4

def wiktionary(lang):
    '''Scrapes words in "lang" language on Wiktionary for Anki'''

    open("{0}_anki.txt".format(lang), 'w', encoding='utf8').close()

    categories = ["alternative forms", "pronunciation", "quotations", "synonyms", "derived terms", 'see also',\
                  "etymology", "antonyms", "synonyms", "usage notes", "references", "anagrams", "further reading", "related terms", "conjugation",\
                  "coordinate terms", "descendants",'proper noun', "hyponyms", "participle", "declension",'letter', 'glyph origin', 'compounds']
    word_classes = ['pronoun', 'verb', 'conjunction', 'noun', 'adverb', 'adjective', 'interjection', 'preposition', 'numeral', 'article', 'determiner', 'contraction',\
                    'particle', "classifier", 'prefix', 'ordinal number', 'postposition', 'adposition', 'suffix', 'infix', 'definitions', 'idiom',\
                    "phrase"]
    categories += word_classes
    queue = []

    in_file = open("{0}_words.txt".format(lang), 'r', encoding='utf8')
    counter = 0
    for line in in_file:

        if line.split()[0] not in queue:
            queue.append(line.strip().split()[0])

        counter += 1

        if counter > 10000:

            break

    in_file.close()

    for word in queue:

        response = requests.get("https://en.wiktionary.org/wiki/{0}#{1}".format(word, lang))
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        active = False
        meaning_state = False
        temp_active = False
        start = False
        meanings = []
        dd = []
        last = ""
        ipa = ""
        chinese_definitions = False
        trad_word = ''

        if lang == "Chinese":

            pinyin_active = False

            try:
                for ti in soup.find_all(['tr']):
                    temp_trad = ti.text
                    if "For pronunciation and definitions of " in temp_trad:
                        trad_word = temp_trad.split(" – see ")[1].split()[0]
                        response = requests.get("https://en.wiktionary.org/wiki/{0}#{1}".format(trad_word, lang))
                        soup = bs4.BeautifulSoup(response.content, 'html.parser')
            except:
                pass

            for i in soup.find_all(['a','span']):

                try:
                    if pinyin_active and i['lang'] == 'cmn':
                        ipa = ' ' + i.text + ' '
                        break
                except:
                    pass

                try:
                    if not pinyin_active and i['title'] == 'w:Pinyin':
                        pinyin_active = True
                except:
                    pass

        for i in soup.find_all(["dd","span","li","ol","p"]):

            if chinese_definitions and i.name == 'ol':
                for j in i.find_all('li'):
                    if len(j.text) > 4:
                        if meanings:
                            meanings.append('<br>' + j.text + '<br>')
                        else:
                            meanings.append(j.text + '<br>')
                        dd.append(False)
                chinese_definitions = False

            try:
                if "mw-headline" in i['class']:

                    if not active and lang == i['id'] or (temp_active and not active and i.text.lower().rstrip(" 1234567890") in word_classes):
                        start = True
                        active = True
                        temp_active = False
                        if 'definitions' in i.text.lower():
                            chinese_definitions = True
                        continue
                    elif (active or temp_active) and lang not in i['id'] and i.text.lower().rstrip(" 1234567890") not in categories:
                        if not meanings:
                            print()
                        break
                    elif active and i.text.lower().rstrip(" 1234567890") in categories and \
                            active and i.text.lower().rstrip(" 1234567890") not in word_classes:
                        start = True
                        active = False
                        temp_active = True
            except KeyError:
                pass

            if active and "title=\"Category:" in str(i):
                break

            try:
                if start and len(ipa) == 0 and "IPA" in i['class'] and i.text.lower()[0] in ['/','[']:
                    ipa = i.text.lower()
            except:
                pass

            if active:
                if not meaning_state and i.text.lower() in word_classes:
                    meaning_state = True
                    continue
                if (meaning_state and i.text.lower() in categories and i.text.lower() not in word_classes):
                    if "definitions" in i.text.lower():
                        print()
                    meaning_state = False
                    continue
                if not meaning_state and i.name == 'ol':
                    meaning_state = True
                    continue
                if meaning_state and i.name == 'p':
                    meaning_state = False
                    continue
                if i.text.lower() == '[edit]':
                    continue
                if i.text.lower() in categories:
                    continue
                if all(not x.isalpha() for x in i.text):
                    continue
                if meaning_state:
                    if len(i.text) >= 4 and all(not x.isalpha() for x in i.text[:4]):
                        continue
                    if meanings and i.text.split('\n')[0] in meanings[-1]:
                        continue
                    pure = i.text.split('\n')[0].strip()
                    if pure in last:
                        continue
                    last = pure
                    if pure in meanings or "<br>"+pure+"<br>" in meanings or pure+"<br>" in meanings:
                        continue
                    if ", trad.]" in pure and ", simp.]" in pure and "[Pinyin]" in pure:
                        exlist = pure.split(']')
                        if (len(exlist) != 4) or '[MSC, ' not in pure:
                            continue
                        pure = exlist[1][:exlist[1].find(' [')] + '<br>' + exlist[2][:exlist[2].find(' [')] + '<br>' + exlist[-1]
                        meanings.append('<br>'+pure+'<br>')
                        dd.append(False)
                        continue
                    if i.name == "dd" and "synonym" not in pure.lower() and "antonym" not in pure.lower():
                        lpure = pure[:-1].split(pure[-1])
                        if len(lpure) == 2:
                            meanings.append('<br>' + lpure[0] + pure[-1]+'<br>' + lpure[len(lpure)//2]+pure[-1]+'<br>')
                            dd.append(False)
                            dd.append(False)
                            continue
                        else:
                            dd.append(True)
                    else:
                        dd.append(False)
                    try:
                        if 'e-translation' not in i['class'] and len(meanings) > 0:
                            meanings.append('<br>' + pure + '<br>')
                        else:
                            meanings.append(pure + '<br>')
                    except KeyError:
                        if len(meanings) > 0:
                            meanings.append('<br>' + pure + '<br>')
                        else:
                            meanings.append(pure + '<br>')
        if trad_word:
            meanings.append('<br>' + trad_word + '<br>')
            dd.append(False)
        conj = ['plural', 'third-person', 'singular', 'second-person', 'first-person', 'preterite', 'indicative', 'subjunctive',\
                'inflection', 'nominative','accusative','singular','neuter','feminine','masculin','gerund','obsolete', 'participle']
        if not meanings:
            print()
        if meanings:
            if any(x in meanings[0].lower() for x in conj):
                continue
            if len(ipa) > 1:
                ipa = '['+ipa[1:-1]+']'
            for j in range(len(meanings)):
                meanings[j].replace("\"","\\\"")
                if j > 0 and dd[j] and dd[j-1] and meanings[j-1][:-4] == "<br>":
                    meanings[j] = meanings[j][4:]
            out_file = open("{0}_anki.txt".format(lang), 'a+',encoding='utf8')
            out_file.write(word+';'+ipa+';\"'+''.join(meanings)[:-4]+'\"'+'\n')
            out_file.close()