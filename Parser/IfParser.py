import re

class IfParser:
    def __init__(self, text: str):
        self.text = text
        self.condition = []          # if, else if 의 조건 문자열
        self.conditionContent = []   # { ... } 블록 내용
        self._parse()

    def _parse(self):
        code = self._remove_comments(self.text)
        i = 0
        n = len(code)

        while i < n:
            # --- else if ---
            if code.startswith("else if", i) and self._is_keyword_boundary(code, i, "else if"):
                open_par = code.find("(", i)
                close_par = self._match_brackets(code, open_par, "(", ")")
                cond = code[open_par+1:close_par].strip()
                self.condition.append(cond)

                open_curly = code.find("{", close_par)
                close_curly = self._match_brackets(code, open_curly, "{", "}")
                body = code[open_curly+1:close_curly].strip()
                self.conditionContent.append(body)

                i = close_curly + 1
                continue

            # --- if ---
            if code.startswith("if", i) and self._is_keyword_boundary(code, i, "if"):
                open_par = code.find("(", i)
                close_par = self._match_brackets(code, open_par, "(", ")")
                cond = code[open_par+1:close_par].strip()
                self.condition.append(cond)

                open_curly = code.find("{", close_par)
                close_curly = self._match_brackets(code, open_curly, "{", "}")
                body = code[open_curly+1:close_curly].strip()
                self.conditionContent.append(body)

                i = close_curly + 1
                continue

            # --- else ---
            if code.startswith("else", i) and self._is_keyword_boundary(code, i, "else"):
                self.condition.append(None)

                open_curly = code.find("{", i)
                close_curly = self._match_brackets(code, open_curly, "{", "}")
                body = code[open_curly+1:close_curly].strip()
                self.conditionContent.append(body)

                i = close_curly + 1
                continue

            i += 1

    def _remove_comments(self, text: str) -> str:
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"//.*", "", text)
        return text

    def _match_brackets(self, text: str, start: int, open_ch: str, close_ch: str) -> int:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == open_ch:
                depth += 1
            elif text[i] == close_ch:
                depth -= 1
                if depth == 0:
                    return i
        raise ValueError(f"{open_ch}/{close_ch} 불일치")

    def _is_keyword_boundary(self, text: str, pos: int, keyword: str) -> bool:
        end = pos + len(keyword)
        before = text[pos-1] if pos > 0 else " "
        after = text[end] if end < len(text) else " "
        return not (before.isalnum() or before == "_") and not (after.isalnum() or after == "_")


if __name__ == "__main__":
    sample = """
    if (a > 0) {
        x = 1;
    }
    else if (b < 5) {
        y = 2;
    }
    else {
        z = 3;
    }
    """

    parser = IfParser(sample)

    print("조건 리스트:", parser.condition)
    print("내용 리스트:", parser.conditionContent)