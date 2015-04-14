import re


class Lexer:
    def __init__(self, source):
        self.source = self._preprocess(source)
        self.idx = 0

        print(self.source)

    def get_token(self):
        if self.idx == len(self.source):
            raise RuntimeError("token expected, EOF found")


    def _preprocess(self, source):
        # Finite state machine.
        binstring = False
        string = False

        # Meta command results.
        end_meta = -1

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
                        if c in b"\r\n": break

                        comment += c

                    # Meta-command.
                    if comment.startswith("#"):
                        meta = comment[1:].strip()
                        if meta == b"end" and end_meta == -1:
                            end_meta = len(lines)

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
        lines = lines[:end_meta]

        # Strip all trailing whitespace and an even amount of spaces from the beginning.
        lines = [re.sub(b"^((  )|\t)*", b"", line.rstrip()) for line in lines]

        # Remove empty lines.
        lines = [line for line in lines if line.strip()]

        return lines

lex = Lexer("""This is a test ; this a comment
; this is a comment as well " open ." string
" ; this is not a comment
and should be on one line"""
