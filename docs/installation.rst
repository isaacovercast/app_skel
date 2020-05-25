.. _sec-installation:

============
Installation
============

``app_skel`` requires Python >= 3.5. Installation is facilitated by the conda package
management system.

1. Download `miniconda <https://conda.io/miniconda.html>`_ and run the installer: ``bash Miniconda*``
2. Create a separate `conda environment <https://conda.io/docs/user-guide/tasks/manage-environments.html>`_ to install app_skel into:

.. code:: bash

    conda create -n app_skel
    conda activate app_skel

3. Install:

.. code:: bash

    conda install -c conda-forge -c app_skel app_skel

4. Test:

.. code:: bash

   app_skel -v

Installation issues can be reported on the `app_skel github <https://github.com/isaacovercast/app_skel>`_.
