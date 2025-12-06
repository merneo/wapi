Contributing
============

Thank you for your interest in contributing to WAPI CLI!

Getting Started
---------------

1. Fork the repository
2. Clone your fork: ``git clone https://github.com/your-username/wapi.git``
3. Create a branch: ``git checkout -b feature/your-feature-name``
4. Make your changes
5. Run tests: ``make test``
6. Commit your changes: ``git commit -m "feat: Add your feature"``
7. Push to your fork: ``git push origin feature/your-feature-name``
8. Open a pull request

Development Setup
-----------------

Install development dependencies:

.. code-block:: bash

   pip install -r requirements-dev.txt
   pre-commit install

Code Style
----------

We use:

* **black** for code formatting
* **isort** for import sorting
* **flake8** for linting
* **mypy** for type checking

Format your code:

.. code-block:: bash

   make format
   make lint

Testing
-------

Run tests:

.. code-block:: bash

   make test

Run tests with coverage:

.. code-block:: bash

   make test-cov

We maintain 100% test coverage. All new code must include tests.

Documentation
-------------

* All code must have docstrings (Google style)
* Update relevant documentation files
* Add examples for new features
* Update CHANGELOG.md

Pull Request Guidelines
-----------------------

* Write clear commit messages
* Include tests for new features
* Update documentation
* Ensure all tests pass
* Maintain 100% code coverage

Code of Conduct
---------------

Be respectful and professional in all interactions.

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.
