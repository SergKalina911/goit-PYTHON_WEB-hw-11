.. Rest API documentation master file, created by
   sphinx-quickstart on Sun Jun 14 13:01:29 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Rest API documentation
======================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.


Welcome to Contacts REST API documentation!
===========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Main Application
----------------
.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:

Database
--------
.. automodule:: src.database.db
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.database.models
   :members:
   :undoc-members:
   :show-inheritance:

Schemas
-------
.. automodule:: src.schemas
   :members:
   :undoc-members:
   :show-inheritance:

Repository
----------
.. automodule:: src.repository.users
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.repository.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Routes
------
.. automodule:: src.routes.auth
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.routes.users
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.routes.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------
.. automodule:: src.services.auth
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.services.email
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.services.cache
   :members:
   :undoc-members:
   :show-inheritance: