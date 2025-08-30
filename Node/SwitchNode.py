from Node.BaseNode import BaseNode

class SwitchNode(BaseNode):
    def __init__(self):
        self.compareVar = None
        self.condition = []
        self.child = [] # BaseNode list

    def add_condition(self, compareVar, cond, conetent:list):
        """
            conetent: BaseNode list
        """
        self.compareVar = compareVar
        self.condition.append(cond)
        self.child.append(conetent)

    def to_string(self, indent=0) -> str:
        pad = " " * indent
        s = f"{pad}SwitchNode(compareVar={self.compareVar})\n"
        s += f"{pad}{{\n"

        for cond, body in zip(self.condition, self.child):
            header = f"{pad}  case {cond}" if cond != "default" else f"{pad}  default"
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