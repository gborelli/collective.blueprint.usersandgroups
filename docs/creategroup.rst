``collective.blueprint.usersandgroups.creategroup``
===================================================

Create groups.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_groupname**: group name

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        creategroup

    ...

    [creategroup]
    blueprint = collective.blueprint.usersandgroups.creategroup

Data in pipeline::

    {
        "_groupname": "Administrators"
    }



