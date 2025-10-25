import sys
import os

from Parser.CodeParser import CodeParser
from Parser.FunctionParser import FunctionParser

from Generator.FlowChartVisualizer import FlowChartVisualizer

is_debug = True

if __name__ == "__main__":
    
    file_path = ""

    if not is_debug:
        if len(sys.argv) < 2:
            print("Invalid Path, Please provide a valid file path.")
            sys.exit(1)
        file_path = sys.argv[1]
    else:
        file_path = r"D:\02_Projects\12_FlowChartGenerator\_TestFile\Test.c"
        #file_path = r"C:\Users\hkpark\Desktop\_TestFile\image\flowchart_image\functionD.dot"

    if file_path.endswith(".c"):
        parser = CodeParser(file_path)
        functions = parser.GetFunctionList()
        func_parser = FunctionParser(functions)
        parsed_func = func_parser.GetFunctions()

        # 생성
        for fname, nodes in parsed_func.items():
            visualizer = FlowChartVisualizer(fname, nodes)

    elif file_path.endswith(".dot"):
        dot_data = None
        with open(file_path, "r", encoding="utf-8") as f:
            dot_data = f.read()

        if dot_data:
            file_name = os.path.basename(file_path)
            file_name, _ = os.path.splitext(file_name)
            FlowChartVisualizer.generate(file_name, dot_data)


