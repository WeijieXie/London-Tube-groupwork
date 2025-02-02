londontube package
==================

The londontube package is a comprehensive tool designed for the analysis and journey planning in the London Underground network. It incorporates real-time data handling for service disruptions, making it an essential tool for both regular commuters and transport network analysts.

Components
----------
The package consists of three main components:

1. **Network Class**: For creating and analyzing network graphs. It includes functionalities like route finding and disruption handling.
2. **Query Submodule**: For fetching real-time data about the London Tube network from web services.
3. **Command-Line Interface (CLI)**: Provides the `journey-planner` tool for planning journeys directly from the terminal, considering real-time data and disruptions.


.. toctree::
   :maxdepth: 4

   network
   query
   command
