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

GREEN_LETTERS = ['_', '_', '_', '_', '_']
WHITE_LETTERS = []


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


def filtered_ranker(word_list):
    new_rank_dict = { 2: [], 3: [], 4: [], 5: [] }
    for word in word_list:
        unique_letters = len(set(list(word)))
        new_rank_dict[unique_letters].append(word)
    return new_rank_dict


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


def new_filter(letter_occurrences, result, guess):
    possible_words = FILTERED_LIST if FILTERED_LIST else FULL_LIST
    new_filtered_list = []

    for word in possible_words:
        add = True

        # Check if letters are in letter_occurrences
        for char in word:
            if char in letter_occurrences.keys():
                if letter_occurrences[char] == 0:
                    WHITE_LETTERS.append(char)
                    add = False
                    break

        if not add:
            continue

        # If we have 'wwwww' for the hint, simply add all other words
        # Bad words would have been filtered out before
        if result == 'wwwww' and add:
            new_filtered_list.append(word)
            continue

        # If result contains 'g's
        elif 'g' in result:
            for i in range(5):
                if GREEN_LETTERS[i] == "_":
                    continue
                else:
                    if GREEN_LETTERS[i] != word[i]:
                        add = False
                        break
            if not add:
                continue

        # By this point, if the word is not suitable, we should be out of the iteration and onto the next word

        # If result contains y, we make sure that words must contain at least one instance of that letter
        # The letter should also not be in the position of the 'y'
        if 'y' in result:
            yellow_positions = []
            for i, c in enumerate(result):
                if c == 'y':
                    yellow_positions.append(i)

            # Look at letter occurrences for each character in a word
            letter_keys = letter_occurrences.keys()
            letter_counter = {}
            for char in word:
                if char not in letter_counter.keys():
                    letter_counter[char] = 1
                else:
                    letter_counter[char] += 1

            for i in range(5):
                if result[i] == 'y':
                    if guess[i] not in word:
                        add = False
                        break

            for char in letter_counter.keys():
                if char in letter_keys:
                    if letter_occurrences[char] == 0: # Skip word if it contains nonexistent letters
                        add = False
                        break
                    
                    if letter_counter[char] != letter_occurrences[char]:
                        add = False
                        break

            # Check positions of yellows
            for pos in yellow_positions:
                if word[pos] == guess[pos]:
                    add = False
                    break

        final_check = True
        if add:
            for char in word:
                if char in set(WHITE_LETTERS):
                    final_check = False
                    break
            if final_check:
                new_filtered_list.append(word)

    return new_filtered_list


def main():
    # Get rank of words (depending on number of unique letters)
    words_ranker()
    
    solved = False
    guess_round = 0

    while not solved:
        # Check for failure
        if guess_round > 5:
            print("\nshit sorry")
            break
        
        # First round -> pick random rank-5 word (all unique)
        # For optimal guessing, we want max number of unique letters
        if guess_round == 0:
            initial_guess_list = WORD_RANK_DICT[5]
            guess = random.choice(initial_guess_list)

            print("\nGuess 1: " + guess)

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

                if result == "ggggg":
                    solved = True

                break
        
        # Subsequent rounds
        else:
            new_ranks = filtered_ranker(FILTERED_LIST)
            print(new_ranks)
            if len(new_ranks[5]) > 0:
                guess = random.choice(new_ranks[5])
            elif len(new_ranks[4]) > 0:
                guess = random.choice(new_ranks[4])
            else:
                guess = random.choice(FILTERED_LIST)

            print(f"\nGuess {guess_round + 1}: " + guess)

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

                if result == "ggggg":
                    solved = True

                break

        # Subsequent rounds -> first find the list of possible words
        letter_occurrences = update_possibilities(result, guess)

        # Get filtered list
        new_filtered_list = new_filter(letter_occurrences, result, guess)
        FILTERED_LIST = new_filtered_list

        if solved:
            print("\nAnswer found: " + guess)
        
        guess_round += 1


if __name__ == "__main__":
    main()