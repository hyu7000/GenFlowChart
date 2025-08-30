import re

class SwitchParser:
    def __init__(self, text: str):
        self.text = text
        self.compareVar = None
        self.condition = []          # case 값, default
        self.conditionContent = []   # case 블록 내용
        self._parse()

    def _parse(self):
        code = self._remove_comments(self.text)

        # 1. 최상위 switch 찾기
        i = 0
        n = len(code)
        while i < n:
            if code.startswith("switch", i) and self._is_keyword_boundary(code, i, "switch"):
                # 2. ( ... ) 안 추출
                open_par = code.find("(", i)
                close_par = self._match_brackets(code, open_par, "(", ")")
                self.compareVar = code[open_par+1:close_par].strip()

                # 3. { ... } 안 추출
                open_curly = code.find("{", close_par)
                close_curly = self._match_brackets(code, open_curly, "{", "}")
                body = code[open_curly+1:close_curly].strip()

                # 4. case, default 단위로 파싱
                self._parse_cases(body)

                break
            i += 1

    def _parse_cases(self, body: str):
        # case / default 키워드 찾기
        pattern = re.compile(r"(case\s+.*?:|default\s*:)")
        matches = list(pattern.finditer(body))

        for idx, match in enumerate(matches):
            start = match.end()
            end = matches[idx+1].start() if idx+1 < len(matches) else len(body)
            case_header = match.group()

            # 조건
            if case_header.startswith("case"):
                cond_val = case_header[len("case"):].rstrip(":").strip()
                self.condition.append(cond_val)
            else:
                self.condition.append("default")

            # 내용 (다음 case 전까지, 보통 break; 포함)
            segment = body[start:end].strip()
            self.conditionContent.append(segment)

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
    switch(mode) {
        case 0:
            x = 1;
            break;
        case 1:
            y = 2;
            break;
        default:
            z = 3;
            break;
    }
    """

    parser = SwitchParser(sample)

    print("비교 변수:", parser.compareVar)
    print("조건 리스트:", parser.condition)
    print("내용 리스트:", parser.conditionContent)
