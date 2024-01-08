.. londontube documentation master file, created by
   sphinx-quickstart on Mon Jan  8 17:16:21 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

londontube's documentation!
======================================

Introduction
------------
londontube is a Python package designed for analyzing and planning routes in the London Underground network. It accounts for real-time service disruptions, providing an invaluable tool for both daily commuters and transport planners.

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   londontube

User Guide
----------
Installation and Getting Started
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To install londontube, navigate to the package's root directory in your terminal and run:

.. code-block:: bash

    pip install .

This command installs londontube along with all necessary dependencies.

CLI Usage
^^^^^^^^^
The signature of the CLI is:

.. code-block:: bash

    journey-planner [--plot] start destination [setoff-date]

Which will calculate the fastest route from start to destination, printing the journey time and a list of stations to stdout.

+-------------------------+--------------------------+----------------------------------------------------------------+
|Parameter                | Format                   | Desc                                                           |
+=========================+==========================+================================================================+
| start                   | index or name of station | The station from which the journey begins                      |
+-------------------------+--------------------------+----------------------------------------------------------------+
| destination             | index or name of station | The station you want to travel to                              |
+-------------------------+--------------------------+----------------------------------------------------------------+
| seoff-date *(optional)* | YYYY-MM-DD               | The date you wish to travel on (future or past).               |
|                         |                          | If no date is provided, today's date is used.                  |
+-------------------------+--------------------------+----------------------------------------------------------------+
| plot                    | flag                     | If provided, a graph will be produced in the current directory.|
+-------------------------+--------------------------+----------------------------------------------------------------+


Example
^^^^^^^

.. code-block:: bash

    journey-planner "Northwood Hills" "Upminster" 2023-01-01

Output:

.. code-block:: none

    Journey will take 84 minutes.
    Start: Northwood Hills
    Pinner
    North Harrow
    Harrow-on-the-Hill
    Northwick Park
    Preston Road
    Wembley Park
    Finchley Road
    Baker Street
    Great Portland Street
    Euston Square
    King's Cross St. Pancras
    Angel
    Old Street
    Moorgate
    Liverpool Street
    Bethnal Green
    Mile End
    Bow Road
    Bromley-By-Bow
    West Ham
    Plaistow
    Upton Park
    East Ham
    Barking
    Upney
    Becontree
    Dagenham Heathway
    Dagenham East
    Elm Park
    Hornchurch
    Upminster Bridge
    End: Upminster


Developer Guide
---------------
Contributing to londontube
^^^^^^^^^^^^^^^^^^^^^^^^^^
We welcome contributions to the londontube package! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Develop your changes, adhering to our coding standards (detailed below).
4. Write or update tests relevant to your changes.
5. Submit a pull request with a clear description of your changes.

Testing and Development
^^^^^^^^^^^^^^^^^^^^^^^
To install optional development packages, also run:

.. code-block:: bash

    pip install .[dev]

To ensure the quality and functionality of londontube, we employ a thorough testing process:

1. Run tests using the command `pytest` in the root directory.
2. Add new tests in the `/tests` directory for any new features or bug fixes.
3. Ensure all tests pass before submitting a pull request.

Coding Style
^^^^^^^^^^^^
Our coding style follows PEP 8 standards with the following additional conventions:

- Clear and concise docstrings for every function and class.
- Meaningful variable and function names.
- Commenting on complex logic for better understanding.

For more details, refer to our Style Guide in the repository.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

