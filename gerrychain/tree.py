import networkx as nx
from networkx.algorithms import tree

from .random import random
from collections import deque


def predecessors(h, root):
    return {a: b for a, b in nx.bfs_predecessors(h, root)}


def random_spanning_tree(graph):
    for edge in graph.edges:
        graph.edges[edge]["weight"] = random.random()

    spanning_tree = tree.maximum_spanning_tree(
        graph, algorithm="kruskal", weight="weight"
    )
    return spanning_tree


class PopulatedGraph:
    def __init__(self, graph, populations, ideal_pop, epsilon):
        self.graph = graph
        self.subsets = {node: {node} for node in graph}
        self.population = populations.copy()
        self.ideal_pop = ideal_pop
        self.epsilon = epsilon
        self._degrees = {node: graph.degree(node) for node in graph}

    def __iter__(self):
        return iter(self.graph)

    def degree(self, node):
        return self._degrees[node]

    def contract_node(self, node, parent):
        self.population[parent] += self.population[node]
        self.subsets[parent] |= self.subsets[node]
        self._degrees[parent] -= 1

    def has_ideal_population(self, node):
        return (
            abs(self.population[node] - self.ideal_pop) < self.epsilon * self.ideal_pop
        )


def contract_leaves_until_balanced_or_none(h, choice=random.choice):
    # this used to be greater than 2 but failed on small grids:(
    root = choice([x for x in h if h.degree(x) > 1])
    # BFS predecessors for iteratively contracting leaves
    pred = predecessors(h.graph, root)

    leaves = deque(x for x in h if h.degree(x) == 1)
    while len(leaves) > 0:
        leaf = leaves.popleft()
        if h.has_ideal_population(leaf):
            return h.subsets[leaf]
        # Contract the leaf:
        parent = pred[leaf]
        h.contract_node(leaf, parent)
        if h.degree(parent) == 1 and parent != root:
            leaves.append(parent)
    return None


def bipartition_tree(
    graph,
    pop_col,
    pop_target,
    epsilon,
    node_repeats,
    spanning_tree=None,
    choice=random.choice,
):
    """This function finds a balanced 2 partition of a graph by drawing a
    spanning tree and finding an edge to cut that leaves at most an epsilon
    imbalance between the populations of the parts. If a root fails, new roots
    are tried until node_repeats in which case a new tree is drawn.
    Builds up a connected subgraph with a connected complement whose population
    is ``epsilon * pop_target`` away from ``pop_target``.
    Returns a subset of nodes of ``graph`` (whose induced subgraph is connected).
    The other part of the partition is the complement of this subset.
    :param graph: The graph to partition
    :param pop_col: The node attribute holding the population of each node
    :param pop_target: The target population for the returned subset of nodes
    :param epsilon: The allowable deviation from  ``pop_target`` (as a percentage of
        ``pop_target``) for the subgraph's population
    :param node_repeats: A parameter for the algorithm: how many different choices
        of root to use before drawing a new spanning tree.
    :param spanning_tree: The spanning tree for the algorithm to use (used when the
        algorithm chooses a new root and for testing)
    :param choice: :func:`random.choice`. Can be substituted for testing.
    """
    populations = {node: graph.nodes[node][pop_col] for node in graph}

    balanced_subtree = None
    if spanning_tree is None:
        spanning_tree = random_spanning_tree(graph)
    restarts = 0
    while balanced_subtree is None:
        if restarts == node_repeats:
            spanning_tree = random_spanning_tree(graph)
            restarts = 0
        h = PopulatedGraph(spanning_tree, populations, pop_target, epsilon)
        balanced_subtree = contract_leaves_until_balanced_or_none(h, choice=choice)
        restarts += 1

    return balanced_subtree


def recursive_tree_part(graph, parts, pop_target, pop_col, epsilon, node_repeats=None):
    """Uses :func:`~gerrychain.tree_methods.bipartition_tree` recursively to partition a tree into
    ``len(parts)`` parts of population ``pop_target`` (within ``epsilon``). Can be used to
    generate initial seed plans or to implement ReCom-like "merge walk" proposals.
    :param graph: The graph
    :param parts: Iterable of part labels (like ``[0,1,2]`` or ``range(4)``
    :param pop_target: Target population for each part of the partition
    :param pop_col: Node attribute key holding population data
    :param epsilon: How far (as a percentage of ``pop_target``) from ``pop_target`` the parts
        of the partition can be
    :param node_repeats: Parameter for :func:`~gerrychain.tree_methods.bipartition_tree` to use.
    :return: New assignments for the nodes of ``graph``.
    :rtype: dict
    """
    flips = {}
    remaining_nodes = set(graph.nodes)

    for part in parts[:-1]:
        nodes = bipartition_tree(
            graph.subgraph(remaining_nodes),
            pop_col=pop_col,
            pop_target=pop_target,
            epsilon=epsilon,
            node_repeats=node_repeats,
        )

        for node in nodes:
            flips[node] = part
        # update pop_target?

        remaining_nodes -= nodes

    # All of the remaining nodes go in the last part
    for node in remaining_nodes:
        flips[node] = parts[-1]

    return flips
