# Anki-Scrapers
Scrapes online dictionaries to create multilingual Anki flashcards

Both programs require requests and bs4 to run.

`JishoScraper.py` contains the function `jisho` that takes `file_name` (string) as an argument. The function reads from the file `XXX.txt`, where `XXX` is the string `file_name`, which should contain a list of Jisho queries, and then creates an Japanese-English Anki flashcard from the first result on Jisho of that query.
The flashcards created will have 3 fields separated by semicolons: Kanji (Kanji form of first result), Furigana (Hiragana reading), and Meaning (the English meanings of the word on Jisho, including example sentences).
The Anki flashcards will be written into the file `XXX_anki.txt`, where `XXX` is the string `file_name`, which can then be used to import the cards into Anki.

`WiktionaryScraper.py` contains the function wiktionary that takes `lang` (string) as an argument. The function reads from the file `XXX_words.txt`, where `XXX` is the string `lang`, which should contain a list of vocabulary terms in the language lang.
The program will search each word on Wiktionary and create a Foreign Language-English Anki flashcard if an entry of the word in the language lang appears on Wiktionary.
The Anki flashcards will have 3 fields separated by semicolons: Word (word in the foreign language), IPA reading, and Meaning (the English meanings of the word).
The Anki flashcards will be written into the file `XXX_anki.txt`, where `XXX` is the string lang, which can then be used to import the cards into Anki.
