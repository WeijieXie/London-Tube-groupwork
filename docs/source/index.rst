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
   :maxdepth: 2
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

Example Workflow
^^^^^^^^^^^^^^^^
This section demonstrates a basic use case of londontube - planning a journey considering service disruptions. Step-by-step instructions guide users through the process.

Developer Guide
---------------
Contributing to londontube
^^^^^^^^^^^^^^^^^^^^^^^^^
We welcome contributions to the londontube package! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Develop your changes, adhering to our coding standards (detailed below).
4. Write or update tests relevant to your changes.
5. Submit a pull request with a clear description of your changes.

Testing and Development
^^^^^^^^^^^^^^^^^^^^^^^
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

