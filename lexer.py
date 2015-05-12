import re
import collections


class Token:
    def __init__(self, type, data):
        self.type = type
        self.data = data

class Lexer:
    ALPHA = b"abcdefghijklmnopqrstuvwxyz"
    NUM = b"0123456789"

    def __init__(self, source):
        self.source = self._preprocess(source)
        self.idx = 0

    def has_token(self):
        # Newlines only seperate tokens, just ignore.
        while self.idx < len(self.source) and self.source[self.idx] == ord(b"\n"):
            self.idx += 1

        return self.idx < len(self.source)

    def peek_token(self, ahead=0):
        idx = self.idx
        while len(self.cache) <= ahead:
            self.cache.append(self.get_token(ignore_cache=True))
        self.idx = idx
        return self.cache[ahead]

    def get_token(self, *args, ignore_cache=False):
        if self.cache and not ignore_cache:
            return self.cache.pop(0)

        # Newlines only seperate tokens, just ignore.
        while self.idx < len(self.source) and self.source[self.idx] == ord(b"\n"):
            self.idx += 1

        if self.idx >= len(self.source):
            raise RuntimeError("expected character, found EOF")

        c = self.source[self.idx:self.idx+1]
        self.idx += 1
        if c.lower() in self.ALPHA + b" !#%&'()*+,-/:;<=>?@[]^_`{|}~":
            return Token("symb", c.decode("utf-8"))

        if c == b"\"":
            return Token("lit", "\"{}\"".format(self._tok_str().decode("utf-8")))

        elif c == b"\\":
            if self.idx < len(self.source):
                self.idx += 1
                return Token("lit", "\"{}\"".format(chr(self.source[self.idx - 1])))

            return Token("lit", "\"\"")

        elif c in self.NUM or (c == b"." and self.source[self.idx:self.idx + 1] in self.NUM):
            self.idx -= 1
            return Token("lit", self._tok_num())

        elif c == b".":
            if self.idx >= len(self.source):
                raise RuntimeError("expected character after '.', found EOF")

            c = self.source[self.idx:self.idx + 1]
            self.idx += 1

            if c == b"\"":
                return Token("lit", str(list(self._tok_str())))

            return Token("symb", (b"." + c).decode("utf-8"))

        raise RuntimeError("unexpected character while parsing tokens: {}".format(hex(c[0])))

    def _tok_str(self):
        s = b""
        while self.idx < len(self.source):
            c = self.source[self.idx:self.idx+1]
            self.idx += 1

            if c == b"\"":
                break

            # Reduce multiline strings to one line.
            if c == b"\n":
                s += b"\\n"
            else:
                s += c

            # Make sure \" doesn't count as exiting the string.
            # TODO: too sleepy to verify this - looks funky
            if c == b"\\":
                s += self.source[self.idx:self.idx + 1]
                self.idx += 1

        return s

    def _tok_num(self):
        n = b""
        # Leading zeroes are seperate tokens (in a golf language a leading zero is never useful):
        if self.source[self.idx] == b"0":
            n += b"0"
            self.idx += 1

            if self.idx < len(self.source) and self.source[self.idx] in b".":
                n += b"."
                self.idx += 1
        else:
            while self.idx < len(self.source) and self.source[self.idx] in b"." + self.NUM:
                c = self.source[self.idx:self.idx + 1]
                if c == b"." and n.count(b".") != 0: break
                n += c
                self.idx += 1

        if n.endswith(b".") and self.idx < len(self.source) and self.source[self.idx] not in b" \n":
            self.idx -= 1

        return n.decode("utf-8")

    def _preprocess(self, source):
        # Finite state machine.
        binstring = False
        string = False

        # Meta command results.
        end_meta = -1

        # Indexing bytes gives integer - we want bytes strings instead for cleaner code (no ord()
        # all over the place).
        source = [bytes([c]) for c in source]

        lines = [b""]
        i = 0
        while i < len(source):
            c = source[i]
            i += 1

            # Don't normalize anything in binary strings.
            if binstring:
                lines[-1] += c

                if c == b"\\":
                    if i < len(source): lines[-1] += source[i]
                    i += 1
                elif c == b"\"":
                    binstring = False
            
            # Normalize newline.
            elif c in b"\r\n":
                if string: lines[-1] += b"\n"
                else: lines.append(b"")

                # Greedily read \r\n.
                if c == b"\r" and i < len(source) and source[i] == b"\n":
                    i += 1

            # Handle string state.
            elif string:
                lines[-1] += c

                if c == b"\\" and i < len(source) and source[i] == b"\"":
                    lines[-1] += b"\""
                    i += 1
                elif c == b"\"":
                    string = False

            # The default state.
            else:
                # Comments.
                if c == b";" and (not lines[-1] or lines[-1][-1] in b" \t"):
                    # Read until newline.
                    comment = b""
                    while i < len(source):
                        c = source[i]
                        i += 1

                        # Greedily read \r\n, and break if found.
                        if c == b"\r" and i < len(source) and source[i] == b"\n": i += 1
                        if c in b"\r\n":
                            lines.append(b"")
                            break

                        comment += c

                    # Meta-command.
                    if comment.startswith(b"#"):
                        meta = comment[1:].strip()
                        if meta == b"end" and end_meta == -1:
                            end_meta = len(lines) - 1

                # Regular characters.
                else:
                    lines[-1] += c

                    if c == b"\"":
                        string = True
                    elif c == b"." and i < len(source) and source[i] == b"\"":
                        lines[-1] += source[i]
                        i += 1
                        binstring = True
                    elif c == b"\\":
                        if i < len(source):
                            c = source[i]
                            i += 1

                            # Greedily read \r\n.
                            if c == b"\r" and i < len(source) and source[i] == b"\n":
                                i += 1

                            lines[-1] += b"\n" if c in b"\r\n" else c

        # Handle the end metacommand.
        if end_meta != -1:
            lines = lines[:end_meta]

        # Strip all trailing whitespace and an even amount of spaces from the beginning.
        lines = [re.sub(b"^((  )|\t)*", b"", line.rstrip()) for line in lines]

        # Remove empty lines.
        lines = [line for line in lines if line.strip()]

        # Concatenate lines, unless a line ends in a number or period and the next line begins in a
        # number.
        linenr = 0
        while linenr + 1 < len(lines):
            if not (lines[linenr][-1] in b".0123456789" and lines[linenr + 1][:1].isdigit()):
                lines[linenr] += lines.pop(linenr + 1)
            else:
                linenr += 1

        return b"\n".join(lines)
