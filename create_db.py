import sqlite3
import re
from cedict_utils.cedict import CedictParser
from chinese import ChineseAnalyzer
import pinyin

# Connect to the database (it will create a file named 'language.db' if it doesn't exist)
conn = sqlite3.connect('dictionary.db')

def create_tables(conn):
    # Create a cursor object to execute SQL commands
    c = conn.cursor()

    # Create the 'words' table with an 'id' primary key column
    c.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY,
        chinese TEXT,
        pinyin TEXT,
        english TEXT
    )
    ''')

    # Create the 'sentences' table with an 'id' primary key column
    c.execute('''
    CREATE TABLE IF NOT EXISTS sentences (
        id INTEGER PRIMARY KEY,
        chinese TEXT,
        pinyin TEXT,
        english TEXT,
        english_clean TEXT
    )
    ''')

    # Create the 'word_sentence' junction table with foreign key columns 'word_id' and 'sentence_id'
    c.execute('''
    CREATE TABLE IF NOT EXISTS word_sentence (
        word_id INTEGER,
        sentence_id INTEGER,
        PRIMARY KEY (word_id, sentence_id),
        FOREIGN KEY (word_id) REFERENCES words (id),
        FOREIGN KEY (sentence_id) REFERENCES sentences (id)
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()

def add_words(conn):
    c = conn.cursor()
    parser = CedictParser()
    entries = parser.parse()
    for entry in entries:
        chi = entry.simplified
        if "𰻝" in chi:
            continue
        english = ""
        for i, m in enumerate(entry.meanings):
            if i+1 < len(entry.meanings):
                english += m + "; "
            else:
                english += m + " "

        c.execute("INSERT OR IGNORE INTO words (chinese, pinyin, english) VALUES (?, ?, ?)", (chi, pinyin.get(chi), english))
    
    conn.commit()

def add_sentences(conn):
    c = conn.cursor()
    lines = []
    chinese_analyzer = ChineseAnalyzer()
 
    # open .tsv file
    with open("files/sentence_pairs.tsv") as f:
    
        # Read data line by line
        for line in f:
            
            # split data by tab
            # store it in list
            l=line.split('\t')
            
            # append list to ans
            lines.append(l)
    
    # print data line by line
    for i in lines:
        chinese = i[1]
        english = i[3]
        pinyin_text = ""

        # Convert characters to pinyin
        text = chinese_analyzer.parse(chinese)
        words = text.tokens()
        for w in words:
            pinyin_text += pinyin.get(w) + " "
        
        # Modify english sentence to make it easier to search for words
        # "I have a goal, it's (very) important to me!" would change to: " i have a goal it's very important to me " 
        english_clean = english.lower()
        english_clean = english_clean.rstrip('\n') # Remove endline that is added to all lines when reading text file above
        english_clean = " " + english_clean + " " # Space is added to front and end so the first and last word is also included in database query (the query checks if sentence contains " " + text + " ")
        english_clean = re.sub(r"[^\w\s']", "", english_clean) # \w: any word, \s any whitespace, ^ means match all but words, whitespace and ' character
        print(english)
        print(english_clean + "\n")

        c.execute("INSERT OR IGNORE INTO sentences (chinese, pinyin, english, english_clean) VALUES (?, ?, ?, ?)", (chinese, pinyin_text, english, english_clean))
    
    conn.commit()

def associate_sentences_to_words(conn):
    c = conn.cursor()
    
    # Query all words from the 'words' table
    c.execute("SELECT id, chinese FROM words")
    words = c.fetchall()
    
    for word_id, word_chinese in words:
        # Search for sentences containing the word in the 'sentences' table
        c.execute("SELECT id FROM sentences WHERE chinese LIKE ?", (f'%{word_chinese}%',))
        sentence_ids = c.fetchall()

        # Associate each matching sentence with the current word in the 'word_sentence' junction table
        for sentence_id, in sentence_ids:
            c.execute("INSERT OR IGNORE INTO word_sentence (word_id, sentence_id) VALUES (?, ?)", (word_id, sentence_id))
    
    # Commit the changes
    conn.commit()

create_tables(conn)
add_words(conn)
add_sentences(conn)
conn.close()
