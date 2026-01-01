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
        letters_seen = {}
        
        # PASS 1: Handle 'g' and 'w'
        # We do this first so we know which letters are definitely in the word
        for i in range(5):
            char = guess[i]
            color = hint[i]
            
            if color != 'w': # If Green or Yellow
                if char not in letters_seen:
                    letters_seen[char] = 1
                else:
                    letters_seen[char] += 1
                
                if color == 'g':
                    self.green_letters[i] = char

        # PASS 2: Handle 'w'
        for i in range(5):
            char = guess[i]
            color = hint[i]
            
            if color == 'w':
                # Only mark as 0 (forbidden) if not 'y' or 'g'
                if char not in letters_seen:
                    letters_seen[char] = 0
                    if char not in self.white_letters:
                        self.white_letters.append(char)
        
        return letters_seen


    def process_guess(self, result):
        letters_seen = self.update_possibilities(result, self.current_guess)

        possible_words = self.filtered_list if self.filtered_list else self.full_list
        new_filtered_list = []

        # --- YOUR ORIGINAL FILTER LOGIC (Adapted & Fixed) ---
        for word in possible_words:
            add = True
            
            # Check letters seen (Counts)
            for char in letters_seen:
                count_needed = letters_seen[char]
                
                if count_needed == 0:
                    if char in word:
                        add = False; break
                else:
                    if word.count(char) < count_needed:
                        add = False; break
            
            if not add: continue

            # Check for 'g's
            # Candidates must have same letter at positions of 'g'
            if 'g' in result:
                for i in range(5):
                    if self.green_letters[i] != "_":
                        if self.green_letters[i] != word[i]:
                            add = False
                            break
                if not add: continue

            # Check for 'y's
            # Filtered words cannot have same letter as position of 'y'
            if 'y' in result:
                for i in range(5):
                    if result[i] == 'y':
                        if word[i] == self.current_guess[i]:
                            add = False
                            break
                if not add: continue

            # Check for 'w's
            # Filtered words should not contain gray letters
            if add:
                for char in self.white_letters:
                    if char in word:
                         if char not in letters_seen or letters_seen[char] == 0:
                             add = False
                             break
            
            if add:
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