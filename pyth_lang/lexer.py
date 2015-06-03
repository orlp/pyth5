import re
import collections


class LexerError(Exception):
    pass

Token = collections.namedtuple('Token', ['type', 'data'])


class Lexer:
    ALPHA = b'abcdefghijklmnopqrstuvwxyz'
    NUM = b'0123456789'
    SYMB = b" !#%&'()*+,-/:;<=>?@[]^_`{|}~"

    def __init__(self, src):
        self.cache = []
        self.idx = 0
        self.src = src
        self._preprocess()

    def preprocessed_source(self):
        return self.src

    def has_token(self):
        # Newlines only seperate tokens, just ignore.
        while self._hasc() and self._peekc() == b'\n':
            self.idx += 1
        return self.cache or self._hasc()

    def peek_token(self, ahead=0):
        while len(self.cache) <= ahead:
            self.cache.append(self.get_token(ignore_cache=True))
        return self.cache[ahead]

    def get_token(self, *args, ignore_cache=False):
        if self.cache and not ignore_cache:
            return self.cache.pop(0)

        # Newlines only seperate tokens, just ignore.
        while self._hasc() and self._peekc() == b'\n':
            self.idx += 1

        if not self._hasc():
            raise LexerError('expected character, found EOF')

        c = self._getc()
        if c.lower() in self.ALPHA + self.SYMB:
            return Token('symb', c.decode('utf-8'))

        if c in b'"\\':
            data = self._getc() if c == b'\\' else self._tok_str()
            return Token('lit', repr(data.decode('utf-8')))

        if c in self.NUM or (c == b'.' and self._peekc() in self.NUM):
            self.idx -= 1  # Push back '.' on character stream.
            return Token('lit', self._tok_num())

        if c == b'.':
            return self._tok_dot()

        raise LexerError(
            'unexpected character while parsing tokens: {:x}'.format(c[0]))

    def _tok_dot(self):
        if self.idx >= len(self.src):
            raise LexerError("expected character after '.', found EOF")

        c = self._getc()
        if c == b'"':
            return Token('lit', repr(list(self._tok_str())))

        return Token('symb', (b'.' + c).decode('utf-8'))

    def _tok_str(self):
        s = b''

        while self._hasc():
            c = self._getc()
            if c == b'"':
                break

            # Handle escape sequences.
            if c == b'\\' and self._peekc() in '"\\':
                s += self._getc()
            else:
                s += c

        return s

    def _tok_num(self):
        n = b''

        # Leading zeroes are seperate tokens (in a golf language a leading zero
        # is never useful):
        if self._peekc() == b'0':
            n += self._getc()
            if self._hasc() and self._peekc() in b'.':
                n += self._getc()
        else:
            while self._hasc() and self._peekc() in b'.' + self.NUM:
                if self._peekc() == b'.' and n.count(b'.') != 0:
                    break

                n += self._getc()

        if n.endswith(b'.') and self._hasc() and self._peekc() not in b' \n':
            self.idx -= 1

        return n.decode('utf-8')

    def _hasc(self):
        return self.idx < len(self.src)

    def _peekc(self):
        return self.src[self.idx:self.idx+1]

    def _getc(self):
        self.idx += 1
        return self.src[self.idx-1:self.idx]

    def _preprocess(self):
        # Finite state machine.
        binstring = False
        string = False

        # Meta command results.
        end_meta = None

        lines = [b'']
        while self._hasc():
            c = self._getc()

            # Don't normalize anything in binary strings.
            if binstring:
                lines[-1] += c

                if c == b'\\':
                    lines[-1] += self._getc()
                elif c == b'"':
                    binstring = False

            # Normalize newline.
            elif c in b'\r\n':
                if string:
                    lines[-1] += b'\n'
                else:
                    lines.append(b'')

                # Greedily read \r\n.
                if c == b'\r' and self._peekc() == b'\n':
                    self.idx += 1

            # Handle string state.
            elif string:
                lines[-1] += c

                if c == b'\\' and self._peekc() == b'"':
                    lines[-1] += self._getc()
                elif c == b'"':
                    string = False

            # The default state.
            else:
                # Comments.
                if c == b';' and (not lines[-1] or lines[-1][-1] in b' \t'):
                    # Read until newline.
                    comment = b''
                    while self._hasc():
                        c = self._getc()

                        # Greedily read \r\n, and break if found.
                        if c == b'\r' and self._peekc() == b'\n':
                            self.idx += 1
                        if c in b'\r\n':
                            lines.append(b'')
                            break

                        comment += c

                    # Meta-command.
                    if comment.startswith(b'#'):
                        meta = comment[1:].strip()
                        if meta == b'end' and end_meta is None:
                            end_meta = len(lines) - 1

                # Regular characters.
                else:
                    lines[-1] += c

                    if c == b'"':
                        string = True
                    elif c == b'.' and self._peekc() == b'"':
                        lines[-1] += self._getc()
                        binstring = True
                    elif c == b'\\':
                        if self._hasc():
                            c = self._getc()

                            # Greedily read \r\n.
                            if c == b'\r' and self._peekc() == b'\n':
                                self.idx += 1

                            lines[-1] += b'\n' if c in b'\r\n' else c

        # Handle the end metacommand.
        if end_meta is not None:
            lines = lines[:end_meta]

        self.src = self._preprocess_whitespace(lines)
        self.idx = 0

    def _preprocess_whitespace(self, lines):
        # Strip all trailing whitespace and an even amount of spaces from the
        # beginning.
        lines = [re.sub(b'^((  )|\t)*', b'', line.rstrip()) for line in lines]

        # Remove empty lines.
        lines = [line for line in lines if line.strip()]

        # Concatenate lines, unless a line ends in a number or period and the
        # next line begins in a number (the only time a newline is necessary).
        linenr = 0
        while linenr + 1 < len(lines):
            if not (lines[linenr][-1] in b'.0123456789' and
                    lines[linenr + 1][:1].isdigit()):
                lines[linenr] += lines.pop(linenr + 1)
            else:
                linenr += 1

        return b'\n'.join(lines)
