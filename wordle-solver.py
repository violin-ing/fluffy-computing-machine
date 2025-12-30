FILEPATH = "./valid-wordle-words.txt"

WORD_RANK_DICT = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: []
}

VOWEL_RANK_DICT = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
    5: []
}

COLOR_CODES = {
    "W": "\U000026aa",
    "Y": "\U0001f7e1",
    "G": "\U0001f7e2"
}


def words_ranker():
    with open(FILEPATH) as f:
        for line in f:
            unique_letters = len(set(list(line.strip())))
            WORD_RANK_DICT[unique_letters].append(line.strip())

    vowels = ['a', 'e', 'i', 'o', 'u']
    for word in WORD_RANK_DICT[5]:
        vowel_count = 0
        for char in word:
            if char in vowels:
                vowel_count += 1
        VOWEL_RANK_DICT[vowel_count].append(word)


def main():
    # Get rank of words (depending on number of unique letters)
    words_ranker()

    solved = False
    guess_round = 0
    while not solved:
        # Check for failure
        if guess_round > 5:
            print("shit sorry")
            break
        
        # First round pick random rank 5 word (all unique)
        # For optimal guessing, we want max number of vowels
        if guess_round == 0:
            pass
        
        guess_round += 1


if __name__ == "__main__":
    main()