from typing import Dict, List, Tuple


class Node:

    TYPE_EMPTY = 0
    TYPE_WORD = 1
    TYPE_ENDING = 2
    TYPE_GRAPH_ROOT = 3

    def __init__(self, index: int, char: str, type_: int, word: str = None):
        self.index = index
        self.char = char
        self.type_ = type_
        self.word = word
        self.epsilon_nodes = None

        self.nodes: Dict[str, Node] = {}

    def __str__(self):
        sb = "[" + self.char
        characters = [c for c in self.nodes.keys()]
        characters.sort()

        if len(self.nodes) > 0:
            sb += " children=" + ', '.join(characters)

        if self.word:
            sb += " word=" + self.word
        sb += "]"
        return sb

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, Node):
            return self.index == other.index
        else:
            return False

    def has_epsilon_connection(self) -> bool:
        return self.epsilon_nodes is not None

    def has_child(self, c: str) -> bool:
        if self.has_immediate_child(c):
            return True
        elif self.epsilon_nodes is None:
            return False
        else:
            for node in self.epsilon_nodes:
                if node.has_immediate_child(c):
                    return True

            return False

    def has_immediate_child(self, c: str) -> bool:
        return c in self.nodes.keys()

    def get_immediate_child(self, c: str) -> 'Node':
        return self.nodes.get(c)

    def get_immediate_child_nodes(self) -> Tuple['Node']:
        return tuple(self.nodes.values())

    def get_immediate_child_node_iterable(self) -> Tuple['Node']:
        return tuple(self.nodes.values())

    def get_all_child_nodes(self) -> Tuple['Node', ...]:
        if self.epsilon_nodes is None:
            return tuple(self.nodes.values())
        else:
            node_list = list(self.nodes.values())
            for empty_node in self.epsilon_nodes:
                for n in empty_node.nodes.values():
                    node_list.append(n)

            return tuple(node_list)

    def get_child_list(self, c: str = None, char_array: Tuple[str, ...] = None) -> Tuple['Node', ...]:
        children = []
        if c:
            self.add_if_child_exists(c, children)
            if self.epsilon_nodes:
                for empty_node in self.epsilon_nodes:
                    empty_node.add_if_child_exists(c, children)
        else:  # it means char_array is not None
            for c_ in char_array:
                self.add_if_child_exists(c_, children)
                if self.epsilon_nodes:
                    for empty_node in self.epsilon_nodes:
                        empty_node.add_if_child_exists(c_, children)

        return tuple(children)

    def connect_epsilon(self, node: 'Node') -> bool:
        if self.epsilon_nodes is None:
            self.epsilon_nodes = [node]
        else:
            for n in self.epsilon_nodes:
                if n == node:
                    return False
            self.epsilon_nodes.append(node)
        return True

    def add_if_child_exists(self, c: str, node_list: List['Node']):
        child = self.nodes.get(c)
        if child:
            node_list.append(child)

    def add_child(self, index: int, c: str, type_: int, word: str = None) -> 'Node':
        node = self.nodes.get(c)
        if word:
            if node is None:
                node = Node(index, c, type_, word)
                self.nodes[c] = node
            else:
                node.word = word
                node.type_ = type_
        else:
            if node is None:
                node = Node(index, c, type_)
                self.nodes[c] = node
        return node
