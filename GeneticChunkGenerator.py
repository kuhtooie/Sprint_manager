import random
import string
from collections import Counter

class GeneticChunkGenerator:
    def __init__(
        self,
        min_length=6,
        max_length=20,
        digit_bias=(0.2, 0.6),
        entropy=1.0
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.digit_bias = digit_bias
        self.entropy = entropy

        self.digits = list(string.digits)
        self.letters = list(string.ascii_lowercase)
        self.code = ""
        
        
    def scramble_list(self, list):
        b = len(list) - 1
        self.list = []
        while b >= 0:
            c = randint(0, randint(0, b))
            self.list.append(list[c])
            list.pop(c)
            b -= 1
            
    def scramble(self, phrase):
        phrase = phrase.split(" ")
        b = len(phrase) - 1
        d = []
        while b >= 0:
            c = randint(0, randint(0, b))
            d.append(phrase[c])
            phrase.pop(c)
            b -= 1
        self.code = ''
        for i in range(len(d)):
            if i == len(d) - 1:
                self.code += d[i]
            else:
                self.code += d[i] + " "

    def make_sha(self):

        l1 = ['a', 'b', 'c', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
              't', 'u', 'v', 'w', 'x', 'y', 'z']
        l2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        l3 = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=']
        b = len(l1) - 1
        d = []
        for i in range(3):

            if i < 1:
                a = l1
            elif i < 2:
                a = l2
                b = len(l2) - 1
            else:
                a = l3
                b = len(l3) - 1

            while b >= 0:
                c = randint(0, randint(0, b))
                d.append(str(a[c]))
                a.pop(c)
                b -= randint(1,4)

        self.scramble_list(d)
        self.code = ''
        for i in self.list:
            self.code += i

        self.scramble(self.code)

    def get_shas(self):
        self.make_sha()
        code = self.code[round((len(self.code) - 1) / 2)::] + self.code
        self.make_sha()
        self.code = self.code + code

    # -------- Layer 1: structural length --------
    def _random_length(self):
        base = random.randint(self.min_length, self.max_length)
        jitter = int(random.gauss(0, self.entropy))
        return max(self.min_length, base + jitter)

    # -------- Layer 2: numeric genome --------
    def _numeric_prefix(self, total_length):
        min_frac, max_frac = self.digit_bias
        digit_len = max(
            1,
            int(total_length * random.uniform(min_frac, max_frac))
        )
        return ''.join(random.choices(self.digits, k=digit_len))

    # -------- Layer 3: alphabetic mutation --------
    def _alphabetic_tail(self, remaining_length):
        weights = [
            random.random() ** self.entropy
            for _ in self.letters
        ]
        return ''.join(
            random.choices(self.letters, weights=weights, k=remaining_length)
        )

    def generate_chunk(self):
        total_length = self._random_length()
        numeric = self._numeric_prefix(total_length)
        letters = self._alphabetic_tail(total_length - len(numeric))
        return numeric + letters

    def generate_population(self, size=10):
        population = []
        for _ in range(size):
            genome = self.generate_chunk()
            population.append({
                "genome": genome,
                "length": len(genome),
                "alleles": Counter(genome)
            })
        return population
