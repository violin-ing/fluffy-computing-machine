import random


FILEPATH = "./valid-wordle-words.txt"


class WordleSolver:
    def __init__(self):
        self.full_list = []
        self.filtered_list = []

        self.word_rank_dict = {
            2: [], # No possible word with only 1 letter
            3: [],
            4: [],
            5: []
        }

        self.green_letters = ['_', '_', '_', '_', '_']
        self.white_letters = []
        self.current_guess = ""

        self.load_words()


    def load_words(self):
        with open(FILEPATH) as f:
            for line in f:
                self.full_list.append(line.strip())
                unique_letters = len(set(list(line.strip())))
                self.word_rank_dict[unique_letters].append(line.strip())


    def word_ranker(self, word_list):
        new_rank_dict = { 2: [], 3: [], 4: [], 5: [] }
        for word in word_list:
            unique_letters = len(set(list(word)))
            new_rank_dict[unique_letters].append(word)
        return new_rank_dict
    

    def reset_game(self):
        self.filtered_list = []
        self.green_letters = ['_', '_', '_', '_', '_']
        self.white_letters = []
        self.current_guess = ""
        
        initial_guess_list = self.word_rank_dict.get(5, self.full_list)
        if not initial_guess_list: initial_guess_list = self.full_list
        
        self.current_guess = random.choice(initial_guess_list)
        return self.current_guess
    

    def update_possibilities(self, hint, guess):
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
                self.green_letters[index_tracker] = guess[index_tracker]
            
            index_tracker += 1

        return letters_seen


    def process_guess(self, result):
        letter_occurrences = self.update_possibilities(result, self.current_guess)

        possible_words = self.filtered_list if self.filtered_list else self.full_list
        new_filtered_list = []

        for word in possible_words:
            add = True

            # Check if letters are in letter_occurrences
            for char in word:
                if char in letter_occurrences.keys():
                    if letter_occurrences[char] == 0:
                        self.white_letters.append(char)
                        add = False
                        break

            if not add: continue

            # If we have 'wwwww' for the hint, simply add all other words
            # Bad words would have been filtered out before
            if result == 'wwwww' and add:
                new_filtered_list.append(word)
                continue

            # If result contains 'g's
            elif 'g' in result:
                for i in range(5):
                    if self.green_letters[i] == "_":
                        continue
                    else:
                        if self.green_letters[i] != word[i]:
                            add = False
                            break
                if not add: continue

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
                        if self.current_guess[i] not in word:
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
                    if word[pos] == self.current_guess[pos]:
                        add = False
                        break

            final_check = True
            if add:
                for char in word:
                    if char in set(self.white_letters):
                        final_check = False
                        break
                if final_check:
                    new_filtered_list.append(word)

        # Return new word
        self.filtered_list = new_filtered_list

        if not self.filtered_list:
            return None # Error
        
        new_ranks = self.word_ranker(self.filtered_list)

        if new_ranks[5]:
            self.current_guess = random.choice(new_ranks[5])
        elif new_ranks[4]:
            self.current_guess = random.choice(new_ranks[4])
        else:
            self.current_guess = random.choice(self.filtered_list)

        return self.current_guess