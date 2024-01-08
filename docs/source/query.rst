Query methods
========================
The query submodule in londontube provides essential methods for interacting with web services. It fetches real-time data about the London Tube network, including station connectivity and service disruptions, which are crucial for accurate journey planning and network analysis.

Methods
-----------------------------

.. automodule:: londontube.query.query
   :members:
   :undoc-members:
   :show-inheritance:

Functionality
-------------
- **Real-Time Data Retrieval**: Methods to fetch current network status, including disruptions.
- **Network Object Creation**: Generate network objects representing the Tube network on a given day.

Usage Example
---------------

To get the Tube Network with disruptions as of "2023-01-01"

.. code-block:: python

    >>> network = get_entire_network()
    >>> disruptions = disruption_info("2023-01-01")
    >>> apply_disruptions(network, disruptions)

Similarly, this is wrapped in network_of_given_day()

.. code-block:: python

    >>> network = network_of_given_day("2023-01-01")
