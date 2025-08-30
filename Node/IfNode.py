from Node.BaseNode import BaseNode

class IfNode(BaseNode):
    def __init__(self):
        self.condition = []
        self.child = [] # BaseNode list

    def add_condition(self, cond, conetent:list):
        """
            conetent: BaseNode list
        """
        self.condition.append(cond)
        self.child.append(conetent)

    def has_else_branch(self):
        return self.condition[-1] is None

    def to_string(self, indent=0) -> str:
        pad = " " * indent
        s = f"{pad}IfNode\n"
        s += f"{pad}{{\n"

        for cond, body in zip(self.condition, self.child):
            if cond is None:
                header = f"{pad}  else"
            else:
                header = f"{pad}  if ({cond})"
            s += header + " {\n"

            for sub in body:
                if hasattr(sub, "to_string"):
                    s += sub.to_string(indent + 6) + "\n"
                else:
                    s += " " * (indent + 6) + str(sub) + "\n"

            s += f"{pad}  }}\n"

        s += f"{pad}}}"
        return s

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()