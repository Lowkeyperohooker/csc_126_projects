from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
import os
import re

app = Flask(__name__)

def tokenize(expr):
    # Tokenize into numbers, letters, and operators
    tokens = re.findall(r'(\d+|[a-zA-Z]+|[()+*])', expr)
    return [token for token in tokens if token.strip()]

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.graph = nx.DiGraph()
        self.node_id = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected=None):
        if expected and self.current() != expected:
            return False
        self.pos += 1
        return True

    def new_node(self, label):
        self.node_id += 1
        node_name = f'n{self.node_id}'
        self.graph.add_node(node_name, label=label)
        return node_name

    def parse_E(self):
        left = self.parse_T()
        while self.current() == '+':
            op_node = self.new_node('+')
            self.graph.add_edge(op_node, left)
            self.consume()
            right = self.parse_T()
            self.graph.add_edge(op_node, right)
            left = op_node
        return left

    def parse_T(self):
        left = self.parse_F()
        while self.current() == '*':
            op_node = self.new_node('*')
            self.graph.add_edge(op_node, left)
            self.consume()
            right = self.parse_F()
            self.graph.add_edge(op_node, right)
            left = op_node
        return left

    def parse_F(self):
        current = self.current()
        if current == '(':
            self.consume()
            node = self.new_node('(E)')
            e_node = self.parse_E()
            self.graph.add_edge(node, e_node)
            if not self.consume(')'):
                raise Exception("Expected ')'")
            return node
        elif current and (current.isalnum() or current.isalpha()):
            # Accept both numbers and letters as variables
            var_node = self.new_node(current)
            self.consume()
            return var_node
        raise Exception(f"Unexpected token: {current}")

    def parse(self):
        try:
            root = self.parse_E()
            if self.pos != len(self.tokens):
                raise Exception("Extra input after parsing")
            return self.graph
        except Exception as e:
            return str(e)

def draw_tree(graph):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph, k=0.5, iterations=50)
    labels = nx.get_node_attributes(graph, 'label')
    nx.draw(graph, pos, 
            labels=labels, 
            with_labels=True, 
            node_size=2500, 
            node_color='lightblue',
            font_size=12,
            arrows=True)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf8')

@app.route('/', methods=['GET', 'POST'])
def index():
    output = None
    tree_img = None
    expr = ""

    if request.method == 'POST':
        expr = request.form.get('expr', '')
        tokens = tokenize(expr)
        parser = Parser(tokens)
        result = parser.parse()

        if isinstance(result, nx.DiGraph):
            output = f"Successfully parsed: {expr}"
            tree_img = draw_tree(result)
        else:
            output = f"Error: {result}"

    return render_template('index.html', 
                         output=output, 
                         expr=expr, 
                         tree_img=tree_img)

if __name__ == '__main__':
    app.run(debug=True)