import json
import os
import sys
import random

from workflow import Workflow3


class PwBlock:
    def pwgen(self):
        return ''


class RandomWord(PwBlock):
    words_file = './words{}-{}.txt'

    def __init__(self, capital='first', min_len=3, max_len=6):
        if capital not in ('none', 'first', 'random'):
            raise ValueError("capital not in ('none', 'first', 'random')")
        self.capital = capital
        self.min_len = min_len
        self.max_len = max_len
        self.words_file = RandomWord.words_file.format(self.min_len, self.max_len)

    def generate_dictionary(self):
        if not os.path.isfile(self.words_file.format(self.min_len, self.max_len)):
            if os.path.isfile('/usr/dict/words'):
                with open('/usr/dict/words', 'r') as file:
                    words = [word.strip() for word in file]
            elif os.path.isfile('/usr/share/dict/words'):
                with open('/usr/share/dict/words', 'r') as file:
                    words = [word.strip() for word in file]
            else:
                words = requests.get('https://gist.githubusercontent.com/wchargin/8927565/raw/'
                                     'd9783627c731268fb2935a731a618aa8e95cf465/words').content
                words = str(words[2:-1]).split('\\n')

            words = [word for word in words
                     if self.min_len <= len(word) <= self.max_len
                     and not word.__contains__('\\n')
                     and not word.__contains__("'")]
            content = '\n'.join(words)
            with open(self.words_file, 'w') as file:
                file.write(content)

    def pwgen(self):
        self.generate_dictionary()
        word = random.choice(list(open(self.words_file)))
        word = word.strip().lower()
        if self.capital == 'first':
            word = word.capitalize()
        elif self.capital == 'random':
            word = ''.join(random.choice([c.upper(), c]) for c in word)
        return word


class Deliminator(PwBlock):
    def __init__(self, c='-'):
        self.c = c

    def pwgen(self):
        return self.c


class RandomNumber(PwBlock):
    def __init__(self, num_digits):
        self.num_digits = num_digits

    def pwgen(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(self.num_digits)])


class Password:
    block_types = ['RandomWord', 'RandomNumber', 'Deliminator']

    def __init__(self, config_file='./config.json'):
        with open(config_file) as file:
            lst = json.loads(file.read())

        assert len(lst) > 0, "Empty config file"

        self.blocks = []
        for d in lst:
            assert len(d) == 1, "Invalid config file"
            try:
                for class_name, args in d.items():
                    self.blocks.append(globals()[class_name](**args))
            except ValueError:
                assert False, "Invalid config arguments"

    def pwgen(self):
        return ''.join([block.pwgen() for block in self.blocks])


def main(wf):
    import requests

    pwgen = Password()
    for _ in range(5):
        pw = pwgen.pwgen()
        wf.add_item(title=pw, arg=pw, subtitle='Copy to clipboard', valid=True)
    wf.add_item(title='Edit config',
                arg="REVEALCONFIGFILE",
                subtitle='Reveal "config.json" in Finder',
                valid=True)
    wf.send_feedback()


if __name__ == '__main__':
    workflow = Workflow3(libraries=['./libs'])
    sys.exit(workflow.run(main))
