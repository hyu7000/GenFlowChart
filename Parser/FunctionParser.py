from Parser.IfParser import IfParser
from Parser.ForParser import ForParser
from Parser.SwitchParser import SwitchParser
from Parser.WhileParser import WhileParser
from Parser.DoWhileParser import DoWhileParser
from Node.IfNode import IfNode
from Node.StatementNode import StatementNode
from Node.ForNode import ForNode
from Node.SwitchNode import SwitchNode
from Node.WhileNode import WhileNode
from Node.DoWhileNode import DoWhileNode

class FunctionParser:
    CONTROL_KEYWORDS = ["for", "if", "switch", "while", "do"]

    def __init__(self, func_dict: dict):
        """
        func_dict: { 함수이름 : 함수본문("{ ... }") }
        """
        self.func_dict = func_dict
        self.parsed = self._parse_functions()

    def _parse_functions(self):
        result = {}

        for fname, body in self.func_dict.items():
            content = body.strip()[1:-1]  # {, } 제거

            tokens = self._split_by_blocks(content)
            result[fname] = tokens

        return result

    def _split_by_blocks(self, content: str):
        """
        함수 본문에서 제어문 블록 단위와 ';' 단위 구분
        """
        i = 0
        n = len(content)
        segments = []

        while i < n:
            # 공백 스킵
            if content[i].isspace():
                i += 1
                continue

            # 제어문 키워드 검사
            matched = None
            for kw in self.CONTROL_KEYWORDS:
                if content.startswith(kw, i):
                    matched = kw
                    break

            if matched:
                if matched == "do":
                    start = i
                    block, end = self._extract_do_while(content, i)

                    parser = DoWhileParser(block.strip())
                    doWhileNode = DoWhileNode()
                    doWhileNode.set_condition(parser.condition)
                    body_tokens = self._split_by_blocks(parser.content)
                    doWhileNode.add_child(body_tokens)
                    segments.append(doWhileNode)
                    i = end

                elif matched == "if":
                    start = i
                    block, end = self._extract_control_block(content, i, matched)

                    parser = IfParser(block.strip())
                    ifNode = IfNode()
                    for cond, body in zip(parser.condition, parser.conditionContent):
                        body_tokens = self._split_by_blocks(body)
                        ifNode.add_condition(cond, body_tokens)
                    segments.append(ifNode)
                    i = end

                elif matched == "for":
                    start = i
                    block, end = self._extract_control_block(content, i, matched)

                    parser = ForParser(block.strip())
                    forNode = ForNode()
                    forNode.set_state(parser.startState, parser.condition, parser.action)
                    body_tokens = self._split_by_blocks(parser.content)
                    forNode.add_child(body_tokens)
                    segments.append(forNode)
                    i = end

                elif matched == "switch":
                    start = i
                    block, end = self._extract_control_block(content, i, matched)

                    parser = SwitchParser(block.strip())
                    switchNode = SwitchNode()
                    for cond, body in zip(parser.condition, parser.conditionContent):
                        body_tokens = self._split_by_blocks(body)
                        switchNode.add_condition(parser.compareVar, cond, body_tokens)
                    segments.append(switchNode)
                    i = end

                elif matched == "while":
                    start = i
                    block, end = self._extract_control_block(content, i, matched)

                    parser = WhileParser(block.strip())
                    whileNode = WhileNode()                
                    whileNode.set_condition(parser.condition)
                    body_tokens = self._split_by_blocks(parser.content)
                    whileNode.add_child(body_tokens)
                    segments.append(whileNode)
                    i = end
            else:
                # ; 단위로 끊기
                start = i
                semi = content.find(";", start)
                if semi == -1:
                    break
                stmt = content[start:semi+1].strip() # statement
                if stmt:
                    statementNode = StatementNode(stmt)
                    segments.append(statementNode)
                i = semi + 1

        return segments

    def _skip_ws(self, text: str, i: int) -> int:
        n = len(text)
        while i < n and text[i].isspace():
            i += 1
        return i

    def _starts_with_kw(self, text: str, i: int, kw: str) -> bool:
        import string
        idch = string.ascii_letters + string.digits + '_'
        n = len(text)
        if not text.startswith(kw, i):
            return False
        before = text[i-1] if i-1 >= 0 else None
        after = text[i+len(kw)] if i+len(kw) < n else None
        if (before is not None and before in idch): 
            return False
        if (after is not None and after in idch):
            return False
        return True

    def _extract_if_chain(self, text: str, start: int) -> tuple[str, int]:
        """
        start: 'if'의 'i' 인덱스
        return: (추출된 전체 if-else 체인 문자열, 체인 다음 인덱스)
        전제: 각 분기는 { ... } 블록을 가진다. (else-if의 if도 동일)
        """
        n = len(text)
        i = start

        if not self._starts_with_kw(text, i, 'if'):
            raise ValueError("start 위치에 'if'가 없음")

        # if (...) { ... }
        open_par = text.find("(", i)
        if open_par == -1:
            raise ValueError("if 구문 오류: '(' 없음")
        close_par = self._match_brackets(text, open_par, "(", ")")

        open_curly = text.find("{", close_par)
        if open_curly == -1:
            raise ValueError("if 구문 오류: '{' 없음")
        close_curly = self._match_brackets(text, open_curly, "{", "}")
        end_pos = close_curly + 1

        # else / else if 체인 붙이기
        j = self._skip_ws(text, end_pos)
        while j < n and self._starts_with_kw(text, j, 'else'):
            j += len('else')
            j = self._skip_ws(text, j)

            if self._starts_with_kw(text, j, 'if'):
                # else if (...) { ... }
                open_par = text.find("(", j)
                if open_par == -1:
                    raise ValueError("else if 구문 오류: '(' 없음")
                close_par = self._match_brackets(text, open_par, "(", ")")

                open_curly = text.find("{", close_par)
                if open_curly == -1:
                    raise ValueError("else if 구문 오류: '{' 없음")
                close_curly = self._match_brackets(text, open_curly, "{", "}")
                end_pos = close_curly + 1
                j = self._skip_ws(text, end_pos)
            else:
                # else { ... }
                if j >= n or text[j] != '{':
                    raise ValueError("else 구문 오류: '{' 없음 (단일문은 비허용)")
                close_curly = self._match_brackets(text, j, "{", "}")
                end_pos = close_curly + 1
                j = self._skip_ws(text, end_pos)

        return text[start:end_pos], end_pos

    def _extract_control_block(self, text, start, keyword):
        if keyword == 'if':
            return self._extract_if_chain(text, start)

        # for/while/switch: 기본 한 세트만
        open_par = text.find("(", start)
        if open_par == -1:
            raise ValueError(f"{keyword} 구문 오류: '(' 없음")
        close_par = self._match_brackets(text, open_par, "(", ")")

        open_curly = text.find("{", close_par)
        if open_curly == -1:
            raise ValueError(f"{keyword} 구문 오류: '{{' 없음")
        close_curly = self._match_brackets(text, open_curly, "{", "}")
        return text[start:close_curly+1], close_curly+1

    def _extract_do_while(self, text, start):
        """
        do { ... } while(...);
        """
        if not text.startswith("do", start):
            raise ValueError("do-while 구문 아님")

        # do { ... }
        open_curly = text.find("{", start)
        if open_curly == -1:
            raise ValueError("do-while 구문 오류: '{' 없음")
        close_curly = self._match_brackets(text, open_curly, "{", "}")

        # while(...)
        while_pos = text.find("while", close_curly)
        if while_pos == -1:
            raise ValueError("do-while 구문 오류: while 없음")
        open_par = text.find("(", while_pos)
        close_par = self._match_brackets(text, open_par, "(", ")")

        end = close_par
        if text[end] == ")":
            if end+1 < len(text) and text[end+1] == ";":
                end += 1

        return text[start:end+1], end+1

    def _match_brackets(self, text, start, open_ch, close_ch):
        """
        괄호 짝 맞추기
        """
        depth = 0
        for i in range(start, len(text)):
            if text[i] == open_ch:
                depth += 1
            elif text[i] == close_ch:
                depth -= 1
                if depth == 0:
                    return i
        raise ValueError("괄호 불일치")

    def GetFunctions(self) -> dict:
        return self.parsed
