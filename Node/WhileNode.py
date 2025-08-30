from Node.BaseNode import BaseNode

class WhileNode(BaseNode):
    def __init__(self):
        self.cond = None
        self.child = [] # BaseNode list

    def set_condition(self, cond):
        self.cond = cond

    def add_child(self, content: list):
        """
            content: BaseNode list
        """
        self.child.extend(content)

    def to_string(self, indent=0) -> str:
        pad = " " * indent
        s = f"{pad}WhileNode(condition={self.cond})\n"
        s += f"{pad}{{\n"

        for c in self.child:
            if isinstance(c, list):  # add_child()에서 list로 추가된 경우
                for sub in c:
                    if hasattr(sub, "to_string"):
                        s += sub.to_string(indent + 4) + "\n"
                    else:
                        s += " " * (indent + 4) + str(sub) + "\n"
            else:
                if hasattr(c, "to_string"):
                    s += c.to_string(indent + 4) + "\n"
                else:
                    s += " " * (indent + 4) + str(c) + "\n"

        s += f"{pad}}}"
        return s

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
