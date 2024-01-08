Command-Line Interface
======================
The `journey-planner` is a command-line interface tool in the londontube package. It allows users to plan journeys in the London Underground network, considering real-time disruptions.

Usage
-----
To use the journey-planner tool, execute the following command in your terminal:

.. code-block:: bash

    journey-planner [--plot] start destination [setoff-date]

- **start**: Station index or name where the journey begins.
- **destination**: Station index or name where the journey ends.
- **setoff-date**: Optional. Date of journey in YYYY-MM-DD format. Defaults to the current date if not provided.

Examples
--------------
1. Planning a Journey:
   To plan a journey from "Northwood Hills" to "Upminster" on January 1, 2023:

   .. code-block:: bash

       journey-planner "Northwood Hills" Upminster 2023-01-01

2. Planning a Journey with Plotting:
   To generate a visual map for a journey on January 1, 2023, from "Northwood Hills" to "Upminster" and plot it:

   .. code-block:: bash

       journey-planner --plot "Northwood Hills" Upminster 2023-01-01

   This will create a file named `journey_from_northwood_hills_to_upminster.png`, depicting the route taken.
