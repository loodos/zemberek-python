from typing import Set
from threading import Lock

from zemberek.normalization.node import Node


class AtomicCounter:
    def __init__(self):
        self.count = 0
        self._lock = Lock()

    def get_and_increment(self):
        value = self.count
        with self._lock:
            self.count += 1
        return value


class CharacterGraph:

    node_index_counter = AtomicCounter()

    def __init__(self):
        self.root = Node(self.node_index_counter.get_and_increment(), '\u0000', 3)

    def add_word(self, word: str, type_: int) -> Node:
        return self.add_(self.root, index=0, word=word, type_=type_)

    def add_(self, current_node: Node, index: int, word: str, type_: int) -> Node:

        c = word[index]
        if index == len(word) - 1:
            return current_node.add_child(self.node_index_counter.get_and_increment(), c, type_, word=word)
        else:
            child = current_node.add_child(self.node_index_counter.get_and_increment(), c, 0)
            index += 1
            return self.add_(child, index, word, type_)

    def get_all_nodes(self) -> Set[Node]:
        nodes: Set[Node] = set()
        self.walk(self.root, nodes)
        return nodes

    @staticmethod
    def walk(current: Node, nodes: Set[Node]):
        if current in nodes:
            return
        if current.word:  # using hard coded if statement instead of predicate
            nodes.add(current)

        for node in current.get_immediate_child_nodes():
            CharacterGraph.walk(node, nodes)
