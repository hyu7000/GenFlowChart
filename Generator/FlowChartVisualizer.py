import os
import pydot
import re

import sys

from Node.ForNode import ForNode
from Node.SwitchNode import SwitchNode
from Node.WhileNode import WhileNode
from Node.DoWhileNode import DoWhileNode
from Node.IfNode import IfNode
from Node.StatementNode import StatementNode

from Generator.Node.FlowIfBranchNode import FlowIfBranchNode, BranchEndpoint

class FlowChartVisualizer:
    start_color = 'blue'
    start_shape = 'ellipse'
    folder_path = 'image/flowchart_image'

    def __init__(self, funcName:str, nodes:list):
        self.function_name = funcName

        # AGraph 인스턴스 생성
        self.graph = pydot.Dot(graph_type='digraph', rankdir='TB')

        # 루트 노드 추가
        self.graph.add_node(pydot.Node(self.function_name, color = FlowChartVisualizer.start_color, shape = FlowChartVisualizer.start_shape))
        
        # 현재 노드를 저장할 변수 생성
        self.cur_node = [self.function_name]
        self.if_cur_node = {} # depth_idx : is_previous_ifNode
        self.if_depth = 0        
        self.if_depth_case = 0
        self.if_true_edge = []

        # cur_node의 마지막 노드에서 시작되는 edge가 라벨이 있어야 할 경우를 저장할 변수
        self.is_need_label_at_last_node = False
        self.label_at_last_node = 'False'

        # 생생된 노드들을 저장할 변수 생성
        self.saved_node_list = {}

        # 그래프를 문자열 형태로 반환 변수 저장
        self.string_graph = None

        # 현재 반복문을 임시 저장하는 변수, 이는 break; 문 표현을 위한 변수
        self.cur_break_code_id = {}      # key : value = break id : loop node count(=loop id)
        self.cur_loop_node_count = 0

        # 리턴 코드+id를 저장하는 리스트, MISRA 적용된 코드에는 해당사항 없음
        self.return_id_list = []

        # flow 생성
        self.generate_flow(nodes)

        # End Node 모양 변경
        self.__change_end_node()

        # flow chart 새성
        self.draw_flow_chart()

        # dot 데이터 생성
        self.save_dot_data()
    
    # 노드와 엣지 생성 반복하는 함수
    def generate_flow(self, children_list, first_edge_label = '', parent_flow_node = None):
        is_previouse_loop_node = False
        edge_label = ''
        child_identifier = ''
        count = 0
        branch_node = None

        for index_children_list, child in enumerate(children_list):
            if index_children_list == 0 and first_edge_label != '':
                edge_label = first_edge_label
            else:
                edge_label = ''

            if isinstance(child, ForNode):
                # init 코드의 노드 생성
                init_code = child.init
                child_identifier, count = self.generate_edge_node_in_run_shape(init_code, edge_label)

                # 루프노드가 시작됨을 표현하기 위해 1 증가
                # init 코드 노드 생성 이후에 하는 이유는, 연속 loop 문일 경우 break 문이 다른 곳을 가리킴
                self.cur_loop_node_count += 1 

                # 조건확인 코드 노드 생성
                condition_code = child.cond
                child_identifier, count = self.generate_edge_node_in_run_shape(condition_code, shape_of_node = 'diamond')

                # loop 코드 노드 생성
                children_with_variables = child.child
                self.generate_flow(children_with_variables, first_edge_label = 'True')

                # break 는 제외시키기
                self.cur_node = [node for node in self.cur_node if 'break' not in str(node)]
                # 증감 코드 노드 생성
                increment_code = child.iter
                self.generate_edge_node_in_run_shape(increment_code)

                # condition 코드로 엣지 생성
                for node in self.cur_node:
                    if not 'break' in node:
                        self.graph.add_edge(pydot.Edge(node, child_identifier))

                # 반복문 노드중 하나가 생성이 되었음을 표시
                is_previouse_loop_node = True
                self.cur_node = [child_identifier]

                # 루프노드가 끝임을 표현하기 위해 1 감소
                self.cur_loop_node_count -= 1 

            elif isinstance(child, WhileNode):
                # 루프노드가 시작됨을 표현하기 위해 1 증가
                # init 코드 노드 생성 이후에 하는 이유는, 연속 loop 문일 경우 break 문이 다른 곳을 가리킴
                self.cur_loop_node_count += 1

                # 조건확인 코드 노드 생성
                condition_code = child.cond
                child_identifier, _ = self.generate_edge_node_in_run_shape(condition_code, edge_label=edge_label, shape_of_node = 'diamond')

                # loop 코드 노드 생성
                children_with_variables = child.child
                self.generate_flow(children_with_variables, first_edge_label = 'True')

                # init 코드로 엣지 생성
                for node in self.cur_node:
                    if not 'break' in node:
                        self.graph.add_edge(pydot.Edge(node, child_identifier))

                # 반복문 노드중 하나가 생성이 되었음을 표시, 반복문 노드 
                is_previouse_loop_node = True
                self.cur_node = [child_identifier]

                # 루프노드가 끝임을 표현하기 위해 1 감소
                self.cur_loop_node_count -= 1 

            elif isinstance(child, DoWhileNode):
                # init 코드의 노드 생성, 빈 텍스트
                init_code = ''
                init_identifier, count = self.generate_edge_node_in_run_shape(init_code, edge_label, 'point')    

                # 루프노드가 시작됨을 표현하기 위해 1 증가
                # init 코드 노드 생성 이후에 하는 이유는, 연속 loop 문일 경우 break 문이 다른 곳을 가리킴
                self.cur_loop_node_count += 1            

                # loop 코드 노드 생성
                children_with_variables = child.child
                self.generate_flow(children_with_variables, first_edge_label = 'True')

                # 조건확인 코드 노드 생성
                # condition_code = child.get_condition_code()
                condition_code = child.cond
                child_identifier, _ = self.generate_edge_node_in_run_shape(condition_code, shape_of_node = 'diamond')

                # init 코드로 엣지 생성
                for node in self.cur_node:
                    if not 'break' in node:
                        self.graph.add_edge(pydot.Edge(node, init_identifier))

                # 반복문 노드중 하나가 생성이 되었음을 표시
                is_previouse_loop_node = True
                self.cur_node = [child_identifier]

                # 루프노드가 끝임을 표현하기 위해 1 감소
                self.cur_loop_node_count -= 1 

            elif isinstance(child, IfNode):    
                children_with_variable_list = child.child
                temp_cur_node_list = []     
                temp_start_branch_list = ''

                count_of_branch = len(child.condition)
                branch_node = FlowIfBranchNode(count_of_branch)
                if parent_flow_node is not None:
                    if isinstance(parent_flow_node, FlowIfBranchNode):
                        parent_flow_node.add_child(branch_node)

                for index, child_list in enumerate(children_with_variable_list):
                    # 조건확인 코드 노드 생성
                    # 첫번째 분기                    
                    if index == 0:
                        condition_code = child.condition[index]      
                        child_identifier, count = self.generate_edge_node_in_run_shape(condition_code, edge_label, 'diamond')

                        branch_node.set_true_endpoint(child_identifier)

                    # 그외
                    else:
                        self.cur_node = [temp_start_branch_list]
                        condition_code = child.condition[index]
                        if condition_code:
                            child_identifier, count = self.generate_edge_node_in_run_shape(condition_code, edge_label='False', shape_of_node = 'diamond')                                                                           
                            branch_node.set_true_endpoint(child_identifier)
                        # else code 에 빈공간일시             
                        elif len(child_list) == 0:
                            temp_cur_node_list.append(temp_start_branch_list)
                            self.is_need_label_at_last_node = True
                            branch_node.set_false_endpoint(temp_start_branch_list)
                        # else code 에 코드가 있을 시
                        else:
                            branch_node.set_false_endpoint(temp_start_branch_list)

                    # 현 분기의 False 시작을 위해 임시 저장
                    temp_start_branch_list = child_identifier

                    # 조건 코드 노드 생성
                    child_identifier, count = self.generate_flow(child_list, first_edge_label = 'True', parent_flow_node = branch_node)

                    if len(child_list) != 0 and child_identifier:
                        branch_node.set_normal_endpoint(child_identifier, index)

                    # 마지막 분기인데 else가 없을 경우
                    if (index == len(children_with_variable_list) - 1) and not child.has_else_branch():
                        temp_cur_node_list.append(temp_start_branch_list)
                        self.is_need_label_at_last_node = True
                        branch_node.set_false_endpoint(temp_start_branch_list)
                
                # 현재 노드 값 저장
                self.cur_node = temp_cur_node_list.copy()

            elif isinstance(child, SwitchNode):
                children_with_variable_list = child.child
                temp_cur_node_list = []

                # 시작 조건 코드 저장 및 식별자 저장
                condition_code = child.compareVar
                child_identifier, count = self.generate_edge_node_in_run_shape(condition_code, edge_label, 'diamond') 
                init_code_identifier = condition_code + '__' + str(count)

                for index, child_list in enumerate(children_with_variable_list):
                    self.cur_node = [init_code_identifier]

                    if child_list is None: # default 코드일 경우
                        condition_case = ''
                    else:
                        condition_case = child.condition[index]

                    # 조건 코드 노드 생성
                    child_identifier, count = self.generate_flow(child_list, first_edge_label=str(condition_case))  

                    # 분기 마지막 노드 임시 저장
                    if child_identifier:
                        temp_cur_node_list.append(child_identifier)
                    elif child_identifier == '' and child_list is None:
                        temp_cur_node_list.append(init_code_identifier)

                # 현재 노드 값 저장                
                self.cur_node = temp_cur_node_list.copy()

            else:
                is_return_code, return_value = self.process_string(child)
                shape_of_node = None

                if is_return_code:
                    shape_of_node = 'ellipse'
                    statement = return_value
                else:
                    statement = child.statement

                if parent_flow_node is not None and isinstance(parent_flow_node, FlowIfBranchNode):
                    parent_flow_node.clear_last_branch_endpoint()
                
                if is_previouse_loop_node:
                    child_identifier, count = self.generate_edge_node_in_run_shape(statement, 'False', shape_of_node, branch_node=branch_node)
                    is_previouse_loop_node = False
                else:
                    child_identifier, count = self.generate_edge_node_in_run_shape(statement, edge_label, shape_of_node, is_return_code, branch_node=branch_node)

                    if 'break' in statement:
                        self.cur_break_code_id[child_identifier] = self.cur_loop_node_count

                if branch_node is not None:
                    branch_node = None
                    
        return child_identifier, count
    
    def __flatten_to_str_list(self, items, seen=None):
        """리스트 안의 리스트를 모두 풀어서, 중복 없는 문자열 리스트로 반환"""
        if seen is None:
            seen = set()
        result = []
        for item in items:
            if isinstance(item, list):
                result.extend(self.__flatten_to_str_list(item, seen))
            else:
                s = str(item).strip()
                if s not in seen:
                    seen.add(s)
                    result.append(s)
        return result

    # 생성된 flow를 그리기
    def draw_flow_chart(self):
        # 그래프 이미지로 저장 또는 반환
        fileName = f'{self.function_name}.png'
        file_path = os.path.join(FlowChartVisualizer.folder_path, fileName)
        
        # # 디렉토리 없으면 생성
        if not os.path.exists(FlowChartVisualizer.folder_path):
            os.makedirs(FlowChartVisualizer.folder_path)

        self.graph.write_png(file_path, encoding = 'UTF-8')

    def save_dot_data(self):
        # dot 로 저장 또는 반환
        fileName = f'{self.function_name}.dot'
        file_path = os.path.join(FlowChartVisualizer.folder_path, fileName)
        
        # # 디렉토리 없으면 생성
        if not os.path.exists(FlowChartVisualizer.folder_path):
            os.makedirs(FlowChartVisualizer.folder_path)

        self.graph.write(file_path, format="raw")

    # 수행 노드와 엣지 생성, 매개변수로 정해진 모양의 노드 생성을 의미
    def generate_edge_node_in_run_shape(self, 
                                        child, 
                                        edge_label = None, 
                                        shape_of_node = None, 
                                        is_return_code = False,
                                        branch_node = None):
        
        count = self.get_child_identifier(child)
        child_identifier = child + '__'  + str(count)

        safe_id = self.__safe_dot_string(child_identifier)
        safe_label = self.__safe_dot_string(child)
        if shape_of_node is not None:
            self.graph.add_node(pydot.Node(safe_id, label=safe_label, shape = shape_of_node))
        else:
            self.graph.add_node(pydot.Node(safe_id, label=safe_label, shape = 'rectangle'))

        if edge_label is None:
            edge_label = ''

        if is_return_code:
            self.return_id_list.append(safe_id)
        
        # 중복된 값 제거
        self.cur_node = list(dict.fromkeys(self.cur_node))

        if branch_node is not None:
            endpoints = branch_node.get_endpoint()
            unique_list = []
            for item in endpoints:  # endpoints는 BranchEndpoint 리스트
                if not any(item.is_equal(u) for u in unique_list):
                    unique_list.append(item)

            for endpoint in unique_list:
                if isinstance(endpoint, BranchEndpoint):
                    print(f"StartNode: {endpoint.endpoint_name}, EndNode: {safe_id}, label: {endpoint.edge_label}")
                    self.graph.add_edge(pydot.Edge(endpoint.endpoint_name, safe_id, label=endpoint.edge_label))

                    if endpoint.endpoint_name in self.cur_node:
                        self.cur_node.remove(endpoint.endpoint_name)

        for index, node in enumerate(self.cur_node):
            # 만약 현재 노드가 마지막 노드라면 추가 코드 실행
            if (index == len(self.cur_node) - 1) and self.is_need_label_at_last_node:
                edge_label = self.label_at_last_node
                self.is_need_label_at_last_node = False      

            # return일 경우, break일 경우 flow 방향 제어
            if (not ('break' in node)) and not (node in self.return_id_list):
                self.graph.add_edge(pydot.Edge(node, safe_id, label=edge_label))
                print(f"!StartNode: {node}, EndNode: {safe_id}, label: {edge_label}")
            elif ('break' in node):
                self.graph.add_edge(pydot.Edge(node, safe_id, label=edge_label))
                print(f"!StartNode: {node}, EndNode: {safe_id}, label: {edge_label}")

            if len(self.cur_break_code_id) > 0:
                break_id_to_delete = []
                for k_break_id, v_loop_node_count in self.cur_break_code_id.items():
                    if v_loop_node_count == (self.cur_loop_node_count + 1):
                        self.graph.add_edge(pydot.Edge(k_break_id, safe_id))
                        break_id_to_delete.append(k_break_id)

                for break_id in break_id_to_delete:
                    del self.cur_break_code_id[break_id]      

        self.cur_node = []
        self.cur_node.append(safe_id)  
        if self.if_depth == 0:
            self.if_cur_node = {}

        self.saved_node_list[child] = count

        return safe_id, count
   
    # identifier 생성 및 반환
    def get_child_identifier(self, child):
        count = 0

        if child in self.saved_node_list:
            count = self.saved_node_list[child] + 1
        else:
            self.saved_node_list[child] = 0

        return count
    
    # return 코드인지 확인하는 함수, child는 코드를 의미   
    def process_string(self, child):
        if not isinstance(child, StatementNode):
            return False, child
        
        # 문자열을 공백을 기준으로 나눈다.
        split_strings = child.statement.split()

        # 'return' 문자열이 있는지 확인하고, 있으면 제외한 나머지 문자열을 결합한다.
        if 'return' in split_strings:
            split_strings.remove('return')  # 'return'을 제거한다.
            return True, ' '.join(split_strings)

        # 'return'이 없다면 False와 원본 문자열을 반환한다.
        return False, child.statement
    
    # Out Edge가 없는 Node는 모양 변경 Filter
    def __change_end_node(self):
        end_node_list = self.__find_nodes_with_in_only()
        self.__set_node_shape(end_node_list, 'ellipse')

    def __norm_name(self, s: str) -> str:
        # pydot가 "따옴표친이름"을 돌려줄 때가 있어 정규화
        return s.strip('"')
    
    def __safe_dot_string(self, text: str) -> str:
        """pydot용 DOT 문자열로 안전하게 감싸기"""
        if text is None:
            return '""'
        s = str(text).replace('"', '\\"')  # 내부 따옴표 이스케이프
        return f'"{s}"'                    # 전체를 큰따옴표로 감싸기

    def __find_nodes_with_in_only(self) -> list[str]:
        """
        self.graph 내에서 in-degree>0 이고 out-degree==0 인 노드들(=수신만 있고 발신 없는 노드) 이름 목록 반환
        """
        from collections import defaultdict

        in_deg  = defaultdict(int)
        out_deg = defaultdict(int)
        nodes = set()

        # 명시적으로 추가된 노드
        for n in self.graph.get_nodes():
            nodes.add(self.__norm_name(n.get_name()))

        # 엣지 순회하며 in/out 계산 + 엣지로만 등장한 노드도 포함
        for e in self.graph.get_edges():
            src = self.__norm_name(e.get_source())
            dst = self.__norm_name(e.get_destination())
            out_deg[src] += 1
            in_deg[dst]  += 1
            nodes.add(src); nodes.add(dst)

        return [n for n in nodes if in_deg.get(n, 0) > 0 and out_deg.get(n, 0) == 0]

    def __set_node_shape(self, node_names: list[str], shape: str) -> None:
        """
        주어진 노드들의 모양(shape) 변경.
        - 그래프에 존재하지 않고 엣지로만 등장한 노드는 새로 add_node 하여 모양을 지정.
        - 예: shape='box'|'ellipse'|'diamond'|'circle'|'doublecircle' 등
        """
        for name in node_names:
            found = self.graph.get_node(name)
            if found:  # 이미 존재
                for n in found:
                    n.set_shape(shape)
            else:
                # 엣지로만 생성된 암시적 노드일 수 있으니 명시적으로 추가
                safe_name = self.__safe_dot_string(name)
                self.graph.add_node(pydot.Node(safe_name, shape=shape))

    @staticmethod
    def generate(fileName:str, dot_data:str):
        graphs = pydot.graph_from_dot_data(dot_data)
        graph = graphs[0]

        file_path = os.path.join(FlowChartVisualizer.folder_path, fileName)

        graph.write_png(f"{file_path}.png", encoding = 'UTF-8')

if __name__ == '__main__':
    testCase1 = False
    testCase2 = False
    testCase3 = True