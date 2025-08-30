import re

class ForParser:
    def __init__(self, text: str):
        self.text = text
        self.startState = None
        self.condition = None
        self.action = None
        self.content = None
        self._parse()

    def _parse(self):
        code = self._remove_comments(self.text)
        i = 0
        n = len(code)

        while i < n:
            # 최상위 for 찾기
            if code.startswith("for", i) and self._is_keyword_boundary(code, i, "for"):
                # ( ... ) 추출
                open_par = code.find("(", i)
                close_par = self._match_brackets(code, open_par, "(", ")")
                inside = code[open_par+1:close_par].strip()

                parts = [p.strip() for p in inside.split(";")]
                if len(parts) == 3:
                    self.startState, self.condition, self.action = parts
                else:
                    raise ValueError("for (...) 구문 파싱 실패: 세 부분이 아님")

                # { ... } 추출
                open_curly = code.find("{", close_par)
                close_curly = self._match_brackets(code, open_curly, "{", "}")
                self.content = code[open_curly+1:close_curly].strip()

                # 첫 번째 for만 파싱
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
    for (int i = 0; i < 10; i++) {
        sum += i;
        if (i % 2 == 0) {
            continue; // 내부 for 무시
        }
    }
    """

    parser = ForParser(sample)

    print("초기화:", parser.startState)
    print("조건:", parser.condition)
    print("증감:", parser.action)
    print("본문:", parser.content)