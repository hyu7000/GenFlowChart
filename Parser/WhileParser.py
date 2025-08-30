import re

class WhileParser:
    def __init__(self, text: str):
        self.text = text
        self.condition = None   # while(...) 안 조건
        self.content = None     # { ... } 블록
        self._parse()

    def _parse(self):
        code = self._remove_comments(self.text)

        i = 0
        n = len(code)
        while i < n:
            if code.startswith("while", i) and self._is_keyword_boundary(code, i, "while"):
                # [B] do~while 이 아닌지 확인
                before = code[:i].rstrip()
                if before.endswith("do"):
                    i += 5
                    continue  # do while 은 스킵

                # ( ... ) 조건 추출
                open_par = code.find("(", i)
                close_par = self._match_brackets(code, open_par, "(", ")")
                self.condition = code[open_par+1:close_par].strip()

                # { ... } 본문 추출
                open_curly = code.find("{", close_par)
                close_curly = self._match_brackets(code, open_curly, "{", "}")
                self.content = code[open_curly+1:close_curly].strip()

                break
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
    while (a < 10) {
        a++;
        if (a % 2 == 0) {
            continue;
        }
    }
    """

    parser = WhileParser(sample)

    print("조건:", parser.condition)
    print("본문:", parser.content)
