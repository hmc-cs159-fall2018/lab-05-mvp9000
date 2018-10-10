#
# Spellchecker.py
#

import spacy

import string
from functools import partial

from EditDistance import EditDistanceFinder
from LanguageModel import LanguageModel, nlp_basic

class SpellChecker:
    def __init__(self, channel_model=None, language_model=None, max_distance=1):
        self.channel_model = channel_model if channel_model is not None else EditDistanceFinder()
        self.language_model = language_model if language_model is not None else LanguageModel()
        self.max_distance = max_distance
        self.char_set = list(string.ascii_lowercase)

    def load_channel_model(self, fp):
        self.channel_model.load(fp)

    def load_language_model(self, fp):
        self.language_model.load(fp)

    def bigram_score(self, prev_word, focus_word, next_word):
        sum_score = self.language_model.bigram_prob(prev_word, focus_word) + self.language_model.bigram_prob(focus_word, next_word) 
        return sum_score/2
    
    def unigram_score(self, word):
        return self.language_model.unigram_prob(word)

    def cm_score(self, error_word, corrected_word):
        return self.channel_model.prob(error_word, corrected_word)

    def inserts(self, word):
        possible_candidates = []

        for i in range(len(word)+1):
            for char in self.char_set:
                current_word = word[:i] + char + word[i:]
                possible_candidates.append(current_word)

        return possible_candidates
        
    def deletes(self, word):
        possible_candidates = []
        
        for i in range(len(word)):
            current_word = word[:i] + word[i+1:]
            possible_candidates.append(current_word)

        return possible_candidates

    def substitutions(self, word):
        possible_candidates = []

        for i in range(len(word)):
            for char in self.char_set:
                current_word = word[:i] + char + word[i+1:]
                if current_word != word:
                    possible_candidates.append(current_word)

        return possible_candidates

    def generate_candidates(self, word):
        possible_candidates = set([word])
        for _ in range(self.max_distance):
            current_candidates = set(possible_candidates)

            for word in current_candidates:
                 possible_candidates |= set(self.inserts(word))
                 possible_candidates |= set(self.deletes(word))
                 possible_candidates |= set(self.substitutions(word))
        
        return list(filter(lambda word: word in self.language_model, possible_candidates))

    def overall_score(self, observed_word, prev_word, next_word, intended_word):
        return (self.bigram_score(prev_word, intended_word, next_word) + self.unigram_score(intended_word))/2 + self.cm_score(observed_word, intended_word)

    def check_sentence(self, sentence, fallback=False):
        result = []

        for i, word in enumerate(sentence):
            if word in string.punctuation or word in string.whitespace:
                result.append([word])
            else:
                if i == 0:
                    prev_word = '<s>'
                else:
                    prev_word = sentence[i-1]

                if i == len(sentence) - 1:
                    next_word = '</s>'
                else:
                    next_word = sentence[i+1]

                possible_candidates = self.generate_candidates(word)

                if len(possible_candidates) == 0:
                    if fallback:
                        result.append([word])
                    else:
                        raise ValueError('No candidates found for a word while fallback was False!')
                else:
                    scoring_fn = partial(self.overall_score, word, prev_word, next_word)
                    candidates = sorted(possible_candidates, key=scoring_fn, reverse=True)
                    result.append(candidates)
        return result

    def check_text(self, text, fallback=False):
        return sum([self.check_sentence(list(map(lambda word: word.text, sent)), fallback) for sent in nlp_basic(text).sents], [])

    def autocorrect_sentence(self, sentence):
        return " ".join(x[0] for x in self.check_sentence(sentence, True))
    
    def autocorrect_line(self, line):
        return " ".join(x[0] for x in self.check_text(line, True))
   
    def suggest_sentence(self, sentence, max_suggestions):
        result = []
        for x in self.check_sentence(sentence, True):
            if len(x) == 1:
                result.append(x)
            else:
                result.append(x[:max_suggestions])
        return result

    def suggest_text(self, text, max_suggestions):
        result = []
        for x in self.check_text(text, True):
            if len(x) == 1:
                result.append(x)
            else:
                result.append(x[:max_suggestions])
        return result

