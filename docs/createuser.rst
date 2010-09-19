``collective.blueprint.usersandgroups.createuser``
==================================================

Create users.

:TODO: since in plone2.0 are passwords stored in plain text I didn't even try
    to migrate already encripted passwords. This might happen when I do
    migration from plone2.5 site (or somebody else does it).

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_username**: username
    * **_password**: plain password

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        createuser

    ...

    [createuser]
    blueprint = collective.blueprint.usersandgroups.createuser

Data in pipeline::

    {
        "_username": "rokgarbas",
        "_password": "rok-garbas-password"
    }


