from gerrychain.graph import Graph
from gerrychain.partition import Partition
from gerrychain.updaters import (
    Tally,
    boundary_nodes,
    cut_edges,
    cut_edges_by_part,
    exterior_boundaries,
    interior_boundaries,
    perimeter,
    polsby_popper,
)
from gerrychain.updaters.compactness import compactness_score


class GeographicPartition(Partition):
    """A :class:`Partition` with areas, perimeters, and boundary information included.
    These additional data allow you to compute compactness scores like
    `Polsby-Popper <https://en.wikipedia.org/wiki/Polsby-Popper_Test>`_.
    """

    default_updaters = {
        "perimeter": perimeter,
        "exterior_boundaries": exterior_boundaries,
        "interior_boundaries": interior_boundaries,
        "boundary_nodes": boundary_nodes,
        "cut_edges": cut_edges,
        "area": Tally("ALAND10", alias="area"),
        "cut_edges_by_part": cut_edges_by_part,
        "polsby_popper": polsby_popper,
        "compactness_score": compactness_score,
    }

    @classmethod
    def from_file(cls, filename, assignment, updaters, columns=None):
        """Create a :class:`GeographicPartition` from an ESRI Shapefile, a GeoPackage,
        a GeoJSON file, or any other file that the `fiona` library can handle.
        """
        graph = Graph.from_file(filename, columns)
        cls(graph, assignment, updaters)
