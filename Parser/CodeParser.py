import re
import os

class CodeParser:
    def __init__(self, filepath: str):
        if not os.path.isabs(filepath):
            raise ValueError("절대 경로를 입력해야 합니다.")
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")

        self.filepath = filepath
        self.source = self._read_file()
        self.functions = self._parse_functions()

    def _read_file(self) -> str:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _remove_comments(self, text: str) -> str:
        # /* ... */ 주석 제거
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        # // ... 주석 제거
        text = re.sub(r"//.*", "", text)
        return text

    def _parse_functions(self) -> dict:
        code = self._remove_comments(self.source)
        functions = {}

        i = 0
        n = len(code)
        while i < n:
            ch = code[i]

            if ch == "{":
                # --- [2] 최상단 블록 찾기 ---
                block, end = self._extract_block(code, i)

                # --- [3] { 앞이 ')' 인가? ---
                before = code[:i].rstrip()
                if not before.endswith(")"):
                    i += 1
                    continue

                # --- [4] } 뒤에 ';' 없는가? ---
                after = code[end:].lstrip()
                if after.startswith(";"):
                    i = end + 1
                    continue

                # --- [5] 함수명 추출 ---
                func_name = self._extract_func_name(before)
                if func_name is None:
                    i = end + 1
                    continue

                # 함수 저장
                functions[func_name] = block

                i = end + 1
            else:
                i += 1

        return functions

    def _extract_block(self, code: str, start_index: int):
        """ '{' ~ 대응되는 '}' 까지 추출 """
        depth = 0
        for i in range(start_index, len(code)):
            if code[i] == "{":
                depth += 1
            elif code[i] == "}":
                depth -= 1
                if depth == 0:
                    return code[start_index:i+1], i
        raise ValueError("블록 추출 실패: 괄호 불일치")

    def _extract_func_name(self, before: str):
        """
        ')' 직전의 identifier를 함수명으로 추출
        예: int foo(int a) → foo
        """
        # 공백/개행 제거
        temp = before.rstrip()
        # 마지막 '(' 찾기
        pos = temp.rfind("(")
        if pos == -1:
            return None
        # '(' 앞 토큰이 함수명
        token_part = temp[:pos].strip().split()
        if not token_part:
            return None
        candidate = token_part[-1]
        # 함수명 유효성 체크 (선택)
        if re.match(r"^[A-Za-z_]\w*$", candidate):
            return candidate
        return None

    def GetFunctionList(self) -> dict:
        return self.functions

if __name__ == "__main__":
    parser = CodeParser(r"D:\02_Projects\12_FlowChartGenerator\_TestFile\SmuIf.c")
    functions = parser.GetFunctionList()
    for name, body in functions.items():
        print(f"Function: {name}\nBody:\n{body}\n")