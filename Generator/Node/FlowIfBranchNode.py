from __future__ import annotations

class BranchEndpoint:
    def __init__(self, endpoint_name: str, edge_label: str = ""):
        self.endpoint_name = endpoint_name
        self.edge_label = edge_label  # 오타 수정

    def __str__(self):
        return f"Endpoint(Name: {self.endpoint_name}, Edge Label: {self.edge_label})"
    
    def is_equal(self, other: BranchEndpoint) -> bool:
        return self.endpoint_name == other.endpoint_name and self.edge_label == other.edge_label


class FlowIfBranchNode:
    debug: bool = True  # ✅ 클래스 변수 (모든 인스턴스에 공통)

    def __init__(self, count_of_branch: int):
        self.true_endpoint = None
        self.false_endpoint = None
        self.normal_endpoint = [None] * count_of_branch
        self.last_endpoint = None
        self.child = []

        self.cur_normal_branch_index = 0

    @classmethod
    def log(cls, message: str):
        """클래스 단위 디버그 출력"""
        if cls.debug:
            print(message)

    def add_child(self, child_node: FlowIfBranchNode):
        self.child.append(child_node)
        self.log(f"Added Child Node: {child_node}")

    def remove_child(self, child_node: FlowIfBranchNode):
        self.child.remove(child_node)
        self.log(f"Removed Child Node: {child_node}")

    def set_normal_endpoint(self, endpoint_name: str, index: int = None):
        if index is None:
            new_index = self.cur_normal_branch_index
        else:
            self.cur_normal_branch_index = index
            new_index = index

        endpoint = BranchEndpoint(endpoint_name, "")
        self.normal_endpoint[new_index] = endpoint
        self.last_endpoint = "Normal"
        self.log(f"Set Normal Endpoint: {endpoint}, index: {index}")

    def set_true_endpoint(self, endpoint_name: str):
        endpoint = BranchEndpoint(endpoint_name, "True")
        self.true_endpoint = endpoint
        self.last_endpoint = "True"
        self.log(f"Set True Endpoint: {endpoint}")
    
    def clear_true_endpoint(self):
        self.true_endpoint = None
        self.log("Cleared True Endpoint")

    def set_false_endpoint(self, endpoint_name: str):
        endpoint = BranchEndpoint(endpoint_name, "False")
        self.false_endpoint = endpoint
        self.last_endpoint = "False"
        self.log(f"Set False Endpoint: {endpoint}")

    def clear_false_endpoint(self):
        self.false_endpoint = None
        self.log("Cleared False Endpoint")
    
    def clear_last_branch_endpoint(self):
        if self.last_endpoint == "True":
            self.clear_true_endpoint()
            self.last_endpoint = None
        elif self.last_endpoint == "False":
            self.clear_false_endpoint()        
            self.last_endpoint = None

    def get_endpoint(self) -> list[BranchEndpoint]:
        endpoints = []

        if self.true_endpoint is not None:
            endpoints.append(self.true_endpoint)

        if self.false_endpoint is not None:
            endpoints.append(self.false_endpoint)

        if self.normal_endpoint is not None:
            for endpoint in self.normal_endpoint:
                if endpoint is not None:
                    endpoints.append(endpoint)

        for child in self.child:
            endpoints.extend(child.get_endpoint())

        return endpoints
