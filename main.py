import sys

from Parser.CodeParser import CodeParser
from Parser.FunctionParser import FunctionParser

from Generator.FlowChartVisualizer import FlowChartVisualizer

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Invalid Path, Please provide a valid file path.")
        sys.exit(1)

    file_path = sys.argv[1]

    parser = CodeParser(file_path)
    functions = parser.GetFunctionList()
    func_parser = FunctionParser(functions)
    parsed_func = func_parser.GetFunctions()

    # 생성
    for fname, nodes in parsed_func.items():
        visualizer = FlowChartVisualizer(fname, nodes)
