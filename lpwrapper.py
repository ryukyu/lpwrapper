#!/usr/bin/env python

"""LPWrapper.

Wrapper for lpass-cli that makes it easier to search for passwords.
"""

import re
import sys
import shlex
import signal
import time

from subprocess import PIPE, Popen, STDOUT

TIMEOUT = 30
PROMPT = u"Search for Password: "
NOT_FOUND = u"Sorry we couldn't find any entries that match: {}"
SELECT = u"Select the password you want: "
INVALID_CHOICE = u"Invalid choice"
ERR_CLIP = u"Error copying password to clipboard."
WAITING = u"Waiting {} for password to be used.".format(TIMEOUT)
USE_XSEL = False


class LPWrapper(object):

    def __init__(self):
        self.run()
        while True:
            more = self.wait()
            if more:
                self.run()

    def run(self):
        self.clear()
        self.start_timer()
        results = self.search()
        choices = self.render(results)
        selected = self.chooser(choices)
        self.password(selected)
        self.stop_timer()

    def wait(self):
        self.start_timer()
        print(WAITING)
        more = raw_input("Do you need more passwords? (y/n)")
        if more == 'y':
            self.stop_timer()
            return True
        time.sleep(TIMEOUT + 1)
        self.stop_timer()
        sys.exit()

    def clear(self):
        # send ESC c to clear the screen
        print("\033c")

    def timeout(self, signum, frame):
        print("\nGoodbye...\n")
        sys.exit()

    def start_timer(self, timeout=TIMEOUT):
        signal.signal(signal.SIGALRM, self.timeout)
        signal.alarm(timeout)

    def stop_timer(self):
        signal.alarm(0)

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
        cmd = "lpass show --password {}".format(password)
        if not USE_XSEL:
            cmd += " -c"
        p = Popen(shlex.split(cmd), stdout=PIPE)
        if USE_XSEL:
            out, err = p.communicate()
            return self.clipboard(out)
        p.stdout.close()
        return True

    def clipboard(self, data):
        # this is optional but lpass clears the primary buffer on exit so
        # the password isn't no longer available on the clipboard.
        # Could be what you want though.
        p = Popen(shlex.split('xsel --clipboard'), stdin=PIPE)
        out, err = p.communicate(input=data)
        if err:
            raise Exception(ERR_CLIP)
        return True


def main():
    try:
        LPWrapper()
    except KeyboardInterrupt:
        print('')
        sys.exit()


if __name__ == '__main__':
    main()
