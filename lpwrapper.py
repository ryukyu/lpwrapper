#!/usr/bin/env python

"""LPWrapper.

Wrapper for lpass-cli that makes it easier to search for passwords.
"""

import re
import sys
import shlex

from subprocess import PIPE, Popen, STDOUT

PROMPT = u"Search for Password: "
NOT_FOUND = u"Sorry we couldn't find any entries that match: {}"
SELECT = u"Select the password you want: "
INVALID_CHOICE = u"Invalid choice"
ERR_CLIP = u"Error copying password to clipboard."


class LPWrapper(object):

    def __init__(self):
        self.clear()
        results = self.search()
        choices = self.render(results)
        selected = self.chooser(choices)
        password = self.password(selected)
        self.clipboard(password)

    def clear(self):
        # send ESC c to clear the screen
        print("\033c")

    def search(self):
        p_input = raw_input(PROMPT)
        if not p_input:
            return self.search()
        p1 = Popen(shlex.split('lpass ls'), stdout=PIPE)
        p2 = Popen(shlex.split('grep -i {}'.format(p_input)), stdin=p1.stdout,
                   stdout=PIPE, stderr=STDOUT)
        p1.stdout.close()
        output, err = p2.communicate()
        if err:
            raise Exception(err)
        elif output == '':
            print(NOT_FOUND.format(p_input))
            return self.search()

        return output

    def render(self, results):
        self.clear()
        cnt = 1
        choices = {}
        for item in results.split('\n'):
            m = re.search(r'(.+) \[id: (\d+)\]', item)
            if m:
                choices[cnt] = m.group(2)
                print("{0}: {1}".format(cnt, m.group(1)))
                cnt += 1
        return choices

    def chooser(self, choices):
        num = int(raw_input(SELECT))
        if num in choices:
            return choices[num]
        else:
            print(INVALID_CHOICE)
            return self.chooser(choices)

    def password(self, password):
        cmd = 'lpass show --password {}'.format(password)
        p = Popen(shlex.split(cmd), stdout=PIPE)
        return p.stdout.read()

    def clipboard(self, data):
        p = Popen(shlex.split('xsel --clipboard'), stdin=PIPE)
        out, err = p.communicate(input=data)
        if err:
            raise Exception(ERR_CLIP)
        return True


if __name__ == '__main__':
    try:
        LPWrapper()
    except KeyboardInterrupt:
        print('')
        sys.exit()
