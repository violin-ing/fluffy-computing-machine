import random


FILEPATH = "./valid-wordle-words.txt"

FULL_LIST = []
FILTERED_LIST = []

WORD_RANK_DICT = {
    2: [], # No possible word with only 1 letter
    3: [],
    4: [],
    5: []
}

VOWEL_RANK_DICT = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [] # No possible word with all vowels
}

# COLOR_CODES = {
#     "W": "\U000026aa",
#     "Y": "\U0001f7e1",
#     "G": "\U0001f7e2"
# }

GREEN_LETTERS = ['_', '_', '_', '_', '_']


def words_ranker():
    with open(FILEPATH) as f:
        for line in f:
            FULL_LIST.append(line.strip())
            unique_letters = len(set(list(line.strip())))
            WORD_RANK_DICT[unique_letters].append(line.strip())

    vowels = ['a', 'e', 'i', 'o', 'u']
    for word in WORD_RANK_DICT[5]:
        vowel_count = 0
        for char in word:
            if char in vowels:
                vowel_count += 1
        VOWEL_RANK_DICT[vowel_count].append(word)


def update_possibilities(hint, guess):
    # E.g. guess = crack, hint = ygwwy
    # Stores the occurrences of letters for that guess
    letters_seen = {}
    index_tracker = 0
    while index_tracker < 5:
        if hint[index_tracker] == 'w':
            letters_seen[guess[index_tracker]] = 0
        elif hint[index_tracker] == 'y':
            if guess[index_tracker] not in letters_seen.keys():
                letters_seen[guess[index_tracker]] = 1
            else:
                letters_seen[guess[index_tracker]] += 1
        else:
            if guess[index_tracker] not in letters_seen.keys():
                letters_seen[guess[index_tracker]] = 1
            else:
                letters_seen[guess[index_tracker]] += 1
            GREEN_LETTERS[index_tracker] = guess[index_tracker]
        
        index_tracker += 1

    return letters_seen


def main():
    # Get rank of words (depending on number of unique letters)
    words_ranker()
    
    solved = False
    guess_round = 0
    guess= ""
    while not solved:
        # Check for failure
        if guess_round > 5:
            print("shit sorry")
            break
        
        # First round -> pick random rank-5 word (all unique)
        # For optimal guessing, we want max number of vowels
        if guess_round == 0:
            initial_guess_list = VOWEL_RANK_DICT[4]
            initial_guess = random.choice(initial_guess_list)
            guess = initial_guess

            print("Guess 1:")
            print(initial_guess)

            result = ""
            while True:
                result_input = input("Enter guess result:\n").lower().strip()
                if len(result_input) != 5:
                    print("Invalid result.")
                    continue
                for char in result_input:
                    if char not in ['w', 'y', 'g']:
                        print("Invalid result.")
                        continue
                result = result_input
                break

        # Subsequent rounds -> first find the list of possible words
        letter_occurrences = update_possibilities(result, guess)

        # Get filtered list
        possible_words = FILTERED_LIST if FILTERED_LIST else FULL_LIST
        new_filtered_list = []
        for word in possible_words:
            # Check if letters are in letter_occurrences
            for char in word:
                if char in letter_occurrences.keys():
                    if letter_occurrences[char] == 0:
                        break
                        
        
        guess_round += 1


if __name__ == "__main__":
    main()