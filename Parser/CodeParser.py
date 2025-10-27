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

                # --- [6] 함수 바디 평탄화
                flat_block = self._flatten_blocks(block)

                # 함수 저장
                functions[func_name] = flat_block

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
        temp = before.rstrip()

        # 내부 괄호들 제거 (P2VAR(...) 같은 매크로 오탐 방지)
        # 괄호 깊이를 추적하면서 완전한 (...) 블록을 제거
        result = []
        depth = 0
        for ch in temp:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth < 0:  # 불균형 시 안전장치
                    depth = 0
                continue
            elif depth == 0:
                result.append(ch)
        cleaned = ''.join(result)

        # 이제 매개변수 목록이 제거된 상태
        token_part = cleaned.strip().split()
        if not token_part:
            return None

        candidate = token_part[-1].strip('*(')
        if re.match(r"^[A-Za-z_]\w*$", candidate):
            return candidate
        return None

    def _flatten_blocks(self, block: str, is_top_level: bool = True) -> str:
        """
        중첩된 의미 없는 { ... } 블록을 재귀적으로 제거
        """
        block = block.strip()
        if not block.startswith("{") or not block.endswith("}"):
            return block

        # 내부 내용만 추출
        inner = block[1:-1].strip()

        # --- 내부 블록들 재귀적으로 탐색 ---
        i = 0
        result = ""
        while i < len(inner):
            ch = inner[i]
            if ch == "{":
                sub_block, end = self._extract_block(inner, i)
                flattened = self._flatten_blocks(sub_block, is_top_level=False)
                result += flattened
                i = end + 1
            else:
                result += ch
                i += 1

        # --- 최상위 블록은 유지, 내부는 판단 후 제거 ---
        cleaned = result.strip()
        if not is_top_level:
            # 의미 있는 코드가 있는지 판단
            if not re.search(r"\b(if|for|while|switch|do|return|int|char|float|double|struct)\b", cleaned):
                # 내부 코드만 반환 (즉, 중괄호 제거)
                return cleaned

        return "{\n" + cleaned + "\n}"



    def GetFunctionList(self) -> dict:
        return self.functions

if __name__ == "__main__":
    parser = CodeParser(r"D:\02_Projects\12_FlowChartGenerator\_TestFile\Test.c")
    functions = parser.GetFunctionList()
    for name, body in functions.items():
        print(f"Function: {name}\nBody:\n{body}\n")