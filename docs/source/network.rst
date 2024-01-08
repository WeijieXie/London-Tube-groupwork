Network Class
========================
The Network class in the londontube package is a powerful tool for creating and analyzing network graphs of the London Underground. It offers a variety of methods for network manipulation and analysis, including route finding and handling service disruptions.

Network Class
-----------------------------

.. automodule:: londontube.network
   :members:
   :undoc-members:
   :show-inheritance:

Key Features
------------
- **Node and Edge Management**: Methods for nodes and edges.
- **Route Planning**: Implements Dijkstra’s algorithm for finding the shortest path between stations.
- **Disruption Handling**: Ability to update network graphs based on real-time service disruptions.

Usage Examples
--------------

Instantiate a network

.. code-block:: python

    >>> edges = [(0, 1, 10, 0), (0, 2, 30, 1), (1, 4, 20, 2)]
    >>> network = Network(5, edges)

Find the 2-distance neighbours of station 0

.. code-block:: python

    >>> network.distant_neighbours(2, 0)
    [1, 2, 4]

Find the shortest path between stations 0 and 4

.. code-block:: python

    >>> network.dijkstra(0, 4)
    ([0, 1, 4], 30)
