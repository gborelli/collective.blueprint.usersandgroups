``collective.blueprint.usersandgroups.updategroupproperty``
===========================================================

Update group properties.

:TODO: need to review this blueprint since it was done just to solve problem. Things to fix:

    * ``_roles`` key in data pipeline should be ranamed to
      ``_group_roles`` or similar.
    * ``_properties`` key in data pipeline should be renamed to
      ``_group_properties`` or similar.
    * ``_plone_site`` shoud be removed and plone site resolved from context.
    * get rid of ``_root_group``, since this problem should be solved in the pipeline

Parameters
----------

No parameters.

Expected data in pipeline:

    * **_groupname**: group name we want to update
    * **_roles**: roles of group 
    * **_plone_site**: plone site to operate on
    * **_properties**: group properties
    * **_group_groups**: groups of group
    * **_root_group**: marking group as root group

Example
-------

Configuration::

    [tranmogrifier]
    pipeline =
        source
        updategroupproperty

    ...

    [updategroupproperty]
    blueprint = collective.blueprint.usersandgroups.updategroupproperty

Data in pipeline::

    {
        "_groupname": "Administrators",
        "_root_group": true,
        "_plone_site": "/Plone",
        "_roles": [
            "Manager",
        ],
        "_properties": {
            "email": "admins@site.tld"
            ...
        },
        "_group_groups": [
            "ContentAdministrators",
            ...
        ],
    }




