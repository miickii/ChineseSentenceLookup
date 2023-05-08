import argparse
import sqlite3
import re

def find_sentences(conn, word_id):
    c = conn.cursor()
    
    c.execute("SELECT chinese, pinyin, english FROM words WHERE id=?", (word_id,))
    word = c.fetchone()
    if word:
        # Search for sentences containing the word in the 'sentences' table
        c.execute("SELECT chinese, pinyin, english FROM sentences WHERE chinese LIKE ?", (f'%{word[0]}%',))
        sentences = c.fetchall()

        print("Sentences:")
        for sentence in sentences:
            print(sentence[0])
            print(sentence[1])
            print(sentence[2])
        
        print(f"\n{word[0]} ({word[1]}) - {word[2]}")
    else:
        print("Word not found.")

def sentences_with_english(conn, english):
    c = conn.cursor()
    c.execute("SELECT chinese, pinyin, english FROM sentences WHERE english_clean LIKE ?", (f"%{english.lower()}%",))
    sentences = c.fetchall()
    print("Sentences:")
    for sentence in sentences:
        print(sentence[0])
        print(sentence[1])
        print(sentence[2])
        print("\n")

def search_english_words(conn, english):
    c = conn.cursor()
    c.execute("SELECT id, chinese, pinyin, english FROM words WHERE english LIKE ?", (f"%{english}%",))
    words = c.fetchall()
    filtered = []
    for word in words:
        # Remove everything in brackets (including the brackets themselves)
        cleaned_text = re.sub(r'\s*\([^)]*\)', '', word[3])
        if f" {english} " in cleaned_text:
            filtered.append(word)
    
    return filtered

def main():
    parser = argparse.ArgumentParser(description='CLI to interact with the language database.')
    subparsers = parser.add_subparsers(dest='command')

    chi_parser = subparsers.add_parser('chi', help='Find the Chinese word and its related sentences.')
    chi_parser.add_argument('chinese', help='Chinese text to search.')

    eng_parser = subparsers.add_parser('eng', help='Find English words and let the user select one to display its related sentences.')
    eng_parser.add_argument('english', help='English text to search.')

    args = parser.parse_args()

    conn = sqlite3.connect('dictionary.db')

    if args.command == 'chi':
        c = conn.cursor()
        c.execute("SELECT id FROM words WHERE chinese=?", (args.chinese,))
        word_id = c.fetchone()
        if word_id:
            find_sentences(conn, word_id[0])
        else:
            print("Word not found.")
    elif args.command == 'eng':
        print(args.english)
        sentences = sentences_with_english(conn, args.english)
        
        # if words:
        #     print("Matching words:")
        #     for idx, (_, chinese, pinyin, english) in enumerate(words):
        #         print(f"{idx + 1}: {chinese} ({pinyin}) - {english}")

        #     selection = None
        #     while selection not in range(1, len(words) + 1):
        #         try:
        #             selection = int(input("Select a word by entering its number: "))
        #         except ValueError:
        #             print("Invalid input. Please enter a valid number.")
            
        #     word_id = words[selection - 1][0]
        #     find_sentences(conn, word_id)
        # else:
        #     print("No matching words found.")

    conn.close()

if __name__ == '__main__':
    main()