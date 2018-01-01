import re, pexpect, sys, time, termios, operator
from .runner import TimeoutException
from .common import tohuman

class Interpreter(object):
    def __init__(self, verbosity, encoding, **unused):
        self.verbosity = verbosity
        self.encoding = encoding

    def get_example_match_finders(self):
        '''
        Return a list of MatchFinders, objects that will find
        examples in a given file/string.
        See the doc of MatchFinder for more information.

        If the list is empty, no example will be find (nor executed)
        unless the generic 'FencedMatchFinder' find the examples
        for this interpreter.

        In general, if your language support a prompt-like session, like
        Python or Ruby, you probably want to add a custom finder.

        If you add multiple finders, make sure that two finders will not find
        the same example. This will be considered an error.
        '''
        return []

    def __repr__(self):
        return '%s Interpreter' % tohuman(self.language)

    def run(self, example, options):
        '''
        Run the example and return the output of the execution.

        The source code is in example.source.
        You may want to add additional new lines to the source
        to ensure that the underlying interpreter accept the code

        For example, if the source (in Python) is:
           'def f()
               pass
           '

        the Python interpreter will need an extra new line to understand
        that the function definition does not continue.

        See the documentation of Example to see what other attributes it
        has.

        The parameter 'options' configure some aspects of the execution.
        For example, the option 'TIMEOUT' set for how long an execution
        should be running.
        If time out, raise an exception of type TimeoutException.

        See the code of the default interpreters of ``byexample`` like
        PythonInterpreter and RubyInterpreter to get more information.
        '''
        raise NotImplementedError() # pragma: no cover

    def interact(self, example, options):
        '''
        Connect the current interpreter session to the byexample's console
        allowing the user to manually interact with the interpreter.
        '''
        raise NotImplementedError() # pragma: no cover

    def initialize(self):
        '''
        Hook to initialize the interpreter. This method will be called
        before running any example.
        '''
        raise NotImplementedError() # pragma: no cover

    def shutdown(self):
        '''
        Hook to shutdown the interpreter. This method will be called
        after running all the examples.
        '''
        raise NotImplementedError() # pragma: no cover

class PexepctMixin(object):
    def __init__(self, cmd, PS1_re, any_PS_re):
        self.cmd = cmd
        self.PS1_re = PS1_re
        self.any_PS_re = any_PS_re

        self.last_output = []

    def _spawn_interpreter(self, delaybeforesend=0.010, wait_first_prompt=True,
                                        first_propmt_timeout=10):
        self._drop_output() # there shouldn't be any output yet but...
        self.interpreter = pexpect.spawn(self.cmd, echo=False,
                                                encoding=self.encoding)
        self.interpreter.delaybeforesend = delaybeforesend

        if wait_first_prompt:
            self._expect_prompt(timeout=first_propmt_timeout)
            self._drop_output() # discard banner and things like that

    def interact(self, send='\n', escape_character=chr(29),
                                    input_filter=None, output_filter=None):
        def ensure_cooked_mode(input_str):
            self.set_cooked_mode(True)
            if input_filter:
                return input_filter(input_str)
            return input_str

        attr = termios.tcgetattr(self.interpreter.child_fd)
        try:
            if send:
                self.interpreter.send(send)
            self.interpreter.interact(escape_character=escape_character,
                                      input_filter=ensure_cooked_mode,
                                      output_filter=output_filter)
        finally:
            termios.tcsetattr(self.interpreter.child_fd, termios.TCSANOW, attr)


    def _drop_output(self):
        self.last_output = []

    def _shutdown_interpreter(self):
        self.interpreter.sendeof()
        self.interpreter.close()
        time.sleep(0.001)
        self.interpreter.terminate(force=True)

    def _exec_and_wait(self, source, timeout=2):
        self.interpreter.send(source)
        self._expect_prompt(timeout)

        return self._get_output()

    def _expect_prompt(self, timeout):
        ''' Wait for a PS1 prompt, raises a timeout if we cannot find one.

            if we get a timeout that could mean:
                - the code executed is taking too long to finish
                - the code is malformed and the interpreter is waiting
                  more data like this:
                    prompt-1) [ 1, 2,
                    prompt-2)   3, 4,
                    prompt-2)   5, 6,

                    (the ] is missing, for example)
            if we don't get a timeout that could mean:
                - good, we got the *last* prompt line
                - good but we may didn't get the *last* prompt line
                  and we should try to find the next prompt again
        '''
        expect = [self.PS1_re, pexpect.TIMEOUT]
        PS1_found, Timeout = range(len(expect))

        what = self.interpreter.expect(expect, timeout=timeout)
        self.last_output.append(self.interpreter.before)

        if what == PS1_found:
            while what != Timeout:
                what = self.interpreter.expect(expect, timeout=0.05)
                self.last_output.append(self.interpreter.before)

            # good, we found a prompt and we couldn't find another prompt after
            # the last one so we should be on the *last* prompt
        elif what == Timeout:
            raise TimeoutException("Prompt not found: the code is taking too long to finish or there is a syntax error.\nLast 1000 bytes read:\n%s" % self.interpreter.before[-1000:])

    def _get_output(self):
        out = "".join(self.last_output)
        self._drop_output()

        # remove any other 'prompt' if any
        if self.any_PS_re:
            out = re.sub(self.any_PS_re, '', out)

        # uniform the new line endings (aka universal new lines)
        out = self._universal_new_lines(out)

        return out

    def _universal_new_lines(self, out):
        out = re.sub(r'\r\n', r'\n', out)

        # TODO: is this ok?
        if out and not out.endswith('\n'):
            out += '\n'

        return out

    def set_cooked_mode(self, state):
        # code borrowed from ptyprocess/ptyprocess.py, _setecho, and
        # adapted adding more flags to it based in stty(1)
        errmsg = 'set_cooked_mode() may not be called on this platform'

        fd = self.interpreter.child_fd

        try:
            attr = termios.tcgetattr(fd)
        except termios.error as err:
            if err.args[0] == errno.EINVAL:
                raise IOError(err.args[0], '%s: %s.' % (err.args[1], errmsg))
            raise

        input_flags = (
                       'BRKINT',
                       'IGNPAR',
                       'ISTRIP',
                       'ICRNL',
                       'IXON',
                       )

        output_flags = (
                       'OPOST',
                       )

        local_flags = (
                      'ECHO',
                      'ISIG',
                      'ICANON',
                      )

        if state:
            attr[0] |= reduce(operator.or_,
                                [getattr(termios, flag_name) for flag_name in input_flags])
            attr[1] |= reduce(operator.or_,
                                [getattr(termios, flag_name) for flag_name in output_flags])
            attr[3] |= reduce(operator.or_,
                                [getattr(termios, flag_name) for flag_name in local_flags])
        else:
            attr[0] &= reduce(operator.and_,
                                [~getattr(termios, flag_name) for flag_name in input_flags])
            attr[1] &= reduce(operator.and_,
                                [~getattr(termios, flag_name) for flag_name in output_flags])
            attr[3] &= reduce(operator.and_,
                                [~getattr(termios, flag_name) for flag_name in local_flags])


        try:
            termios.tcsetattr(fd, termios.TCSANOW, attr)
        except IOError as err:
            if err.args[0] == errno.EINVAL:
                raise IOError(err.args[0], '%s: %s.' % (err.args[1], errmsg))
            raise
