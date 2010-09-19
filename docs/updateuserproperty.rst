``collective.blueprint.usersandgroups.updateuserproperty``
==========================================================

Update user properties.

:TODO: need to review this blueprint since it was done just to solve problem.
    Lots of things to rename and fix.

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_username**: username of user we want to update
    * **_properties**: user properties
    * **_user_groups**: groups of user
    * **_root_roles**: roles of userfolder
    * **_local_roles**: local roles for site we operate on
    * **_plone_site**: plone site to which to apply ``_local_roles``

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        updateuserproperty

    ...

    [updateuserproperty]
    blueprint = collective.blueprint.usersandgroups.updateuserproperty

Data in pipeline::

    {
        "_username": "rokgarbas",
        "_properties": {
            "email": "some@email.tld"
            ...
        },
        ...
    }





