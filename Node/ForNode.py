from Node.BaseNode import BaseNode

class ForNode(BaseNode):
    def __init__(self):
        self.init = None
        self.cond = None
        self.iter = None
        self.child = [] # BaseNode list

    def set_state(self, init, cond, iter):
        self.init = init
        self.cond = cond
        self.iter = iter

    def add_child(self, content: list):
        """
            content: BaseNode list
        """
        self.child.extend(content)

    def to_string(self, indent=0) -> str:
        pad = " " * indent
        s = f"{pad}ForNode(init={self.init}, cond={self.cond}, iter={self.iter})\n"
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
