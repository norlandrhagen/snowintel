
snowintel
=========


*snowintel* is a lightweight python package for retrieving SNOTEL data.




.. note::
  Development is in alpha and the API is unstable.



Installation
============


.. code-block:: bash

    pip install git+https://github.com/norlandrhagen/snowintel`




Basic Usage
===========

Retrieve Site Information
-------------------------

.. code-block:: python

    from snowintel.core import getSites

    gs = getSites()



Retrieve Data for a SNOTEL Site
-------------------------------

.. code-block:: python

    from snowintel.utils import get_snotel_data_by_site_id

    df = get_snotel_data_by_site_id(
        site_id="865_UT_SNTL", start_date="2023-01-01", end_date="2023-02-23", variable="SNWD_D"
    )


.. toctree::
  :maxdepth: 2
  :caption: Documentation

  User guide <user_guide>
  Advanced guide <advanced_guide>
  API reference <reference>
