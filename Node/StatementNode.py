from Node.BaseNode import BaseNode

class StatementNode(BaseNode):
    def __init__(self, statement):
        self.statement = statement
        self.child = None

        if self.statement in 'return':
            self.isReturnStatement = True
        else:
            self.isReturnStatement = False

    def to_string(self, indent=0) -> str:
        pad = " " * indent
        return f"{pad}StatementNode({self.statement})"

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()