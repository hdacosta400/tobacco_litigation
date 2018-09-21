import os
import pickle
from pathlib import Path

import nltk
from IPython import embed

from tobacco_litigation.configuration import CONTRACTIONS, WORD_SPLIT_REGEX, \
    STOP_WORDS_LITIGATION


class Closing:

    def __init__(self, case, side, phase, trial_date, doc_date, outcome, defendants,
                 defendant_counsel, compensatory_damages, punitive_damages, filename, tid):
        self.case = case
        self.side = side
        self.phase = phase
        self.trial_date = trial_date
        self.doc_date = doc_date
        self.outcome = outcome
        self.defendants = defendants
        self.defendant_counsel = defendant_counsel
        self.compensatory_damages = compensatory_damages
        self.punitive_damages = punitive_damages
        self.filename = filename
        self.tid = tid

        self.text_raw = self._load_text()
        self.text_clean = self._clean_text()
        self.part_of_speech = self._load_part_of_speech()

    def _load_text(self):
        """
        Loads the text of the closing and expands all contractions

        >>> from tobacco_litigation.corpus import Closing
        >>> c = Closing('ahrens', 'plaintiff', 1, 2006, 2006, 'w', 'PM', 'Kaczynski', 9000000,
        ...             5000000, 'ahrens1_1_c_p.txt', 'kglw0225')
        >>> c.text_raw.split()[:6] # split because of leading white space
        ['closing', 'statement', 'mr.', 'paige:', 'good', 'morning.']

        :rtype: str
        """

        base_path = Path(os.path.abspath(os.path.dirname(__file__)))
        full_path = base_path.joinpath(Path('data', 'closings', self.filename))

        text = open(full_path, encoding='utf8').read()
        text = text.lower()
        for contraction in CONTRACTIONS:
            text = text.replace(contraction, CONTRACTIONS[contraction])

        return text

    def _clean_text(self):
        """
        Returns a cleaned version of the text without punctuation and numbers (except years).
        The clean version is then used for tokenization

        >>> from tobacco_litigation.corpus import Closing
        >>> c = Closing('ahrens', 'plaintiff', 1, 2006, 2006, 'w', 'PM', 'Kaczynski', 9000000,
        ...             5000000, 'ahrens1_1_c_p.txt', 'kglw0225')
        >>> c.text_raw.split()[:6] # split because of leading white space
        ['closing', 'statement', 'mr.', 'paige:', 'good', 'morning.']
        >>> c.text_clean[:39]
        'closing statement mr paige good morning'

        :rtype: str
        """

        text = WORD_SPLIT_REGEX.findall(self.text_raw)
        text_clean = []
        for word in text:
            if not word in STOP_WORDS_LITIGATION:
                text_clean.append(word)
        text_clean = " ".join(text_clean)
        return text_clean

    def _load_part_of_speech(self):
        """
        Returns part of speech tags for the closing text as a list

        Note: this takes about 5 seconds per closing.

        >>> from tobacco_litigation.corpus import Closing
        >>> c = Closing('ahrens', 'plaintiff', 1, 2006, 2006, 'w', 'PM', 'Kaczynski', 9000000,
        ...             5000000, 'ahrens1_1_c_p.txt', 'kglw0225')
        >>> c.text_raw.split()[:7]
        ['closing', 'statement', 'mr.', 'paige:', 'good', 'morning.', 'so']
        >>> c.part_of_speech[:6]
        ['VBG', 'NN', 'NN', 'NN', ':', 'JJ']

        Returns a list of all POS tags.
        :rtype: list
        """
        pos_filename = self.filename[:-4] + '.pickle'
        base_path = Path(os.path.abspath(os.path.dirname(__file__)))
        full_path = base_path.joinpath(Path('data', 'part_of_speech', pos_filename))

        try:
            pos_tags = pickle.load(open(full_path, 'rb'))
        except FileNotFoundError:

            pos_tags = []
            text_tokenized = nltk.word_tokenize(self.text_raw)
            for pos_tag in nltk.pos_tag(text_tokenized):
                pos_tags.append(pos_tag[1])

            pickle.dump(pos_tags, open(full_path, 'wb'))

        return pos_tags


if __name__ == '__main__':

    c = Closing('c', 'plaintiff', 1, '1998', '1987', 'w', 'RJR', 'test', 100, 100,
                'ahrens1_1_c_d.txt', 'otehu')

    corpus = Corpus()
    ex = corpus.get_search_term_extracts('plaintiff', 'Proctor')
    embed()