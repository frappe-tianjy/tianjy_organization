import frappe
from json import loads


@frappe.whitelist()
def get_organizations(user_name):
    member_list = frappe.db.get_list('Tianjy Organization Member',
                                     filters=[['user', '=', user_name]],
                                     fields=['*'],
                                     limit=0)
    role_list = frappe.db.get_list('Tianjy Organization Role',
                                   filters=[['user', '=', user_name]],
                                   fields=['*'],
                                   limit=0)
    organization_names = list(map(lambda ml: ml.organization, member_list))
    organization_list = frappe.db.get_list('Tianjy Organization',
                                           filters=[
                                               ['name', 'in', organization_names]],
                                           fields=['*'],
                                           limit=0)
    for member in member_list:
        member.role_list = list(
            filter(lambda rl: rl.organization == member.organization, role_list))
        organizations = list(
            filter(lambda ol: ol.name == member.organization, organization_list))
        member.organization_doc = organizations[0] if len(
            organizations) > 0 else None
    return member_list


@frappe.whitelist()
def get_organization_roles(user_name, organization_name):
    uer_doc = frappe.get_doc('User', user_name)
    organization_role_list = frappe.db.get_list('Tianjy Organization Role',
                                                filters=[
                                                    ['user', '=', user_name],
                                                    ['organization', '=',
                                                        organization_name],
                                                ],
                                                fields=['*'],
                                                limit=0)
    inherit_members = frappe.db.get_list('Tianjy Organization Member',
                                         filters=[
                                             ['user', '=', user_name],
                                             ['organization', '=',
                                                 organization_name],
                                             ['is_inherit', '=', '1'],
                                         ],
                                         fields=['*'],
                                         limit=0)
    inherit_organization_names = list(
        map(lambda im: im.inherit_from, inherit_members))
    inherit_organization_list = frappe.db.get_list('Tianjy Organization',
                                                   filters=[
                                                       ['name', 'in',
                                                           inherit_organization_names],
                                                   ],
                                                   fields=['*'],
                                                   limit=0)
    inherit_roles = []
    for member in inherit_members:
        inherit_role_list = frappe.db.get_list('Tianjy Organization Role',
                                               filters=[
                                                   ['user', '=', user_name],
                                                   ['organization', '=',
                                                       member.inherit_from],
                                               ],
                                               fields=['*'],
                                               limit=0)
        inherit_organization = list(
            filter(lambda io: io.name == member.inherit_from, inherit_organization_list))
        if len(inherit_organization) == 0:
            continue
        inherit_roles.append({
            'organization': inherit_organization[0],
            'roles': inherit_role_list
        })
    return {
        'uer_doc': uer_doc,
        'organization_role_list': organization_role_list,
        'inherit_roles': inherit_roles}


@frappe.whitelist()
def get_organization_members(user_name, organization_name):
    organization_members = frappe.db.get_list('Tianjy Organization Member',
                                              filters=[
                                                  ['user', '=', user_name],
                                                  ['organization', '=',
                                                   organization_name],
                                                  ['is_inherit', '=', '0'],
                                              ],
                                              fields=['*'],
                                              limit=0)
    inherit_members = frappe.db.get_list('Tianjy Organization Member',
                                         filters=[
                                             ['user', '=', user_name],
                                             ['organization', '=',
                                                 organization_name],
                                             ['is_inherit', '=', '1'],
                                         ],
                                         fields=['*'],
                                         limit=0)
    inherit_organization_names = list(
        map(lambda im: im.inherit_from, inherit_members))
    inherit_organization_list = frappe.db.get_list('Tianjy Organization',
                                                   filters=[
                                                       ['name', 'in',
                                                           inherit_organization_names],
                                                   ],
                                                   fields=['*'],
                                                   limit=0)
    for member in inherit_members:
        inherit_organization = list(
            filter(lambda io: io.name == member.inherit_from, inherit_organization_list))
        if len(inherit_organization) == 0:
            continue
        member.organization_doc = inherit_organization[0]
    return {
        'organization_members': organization_members,
        'inherit_members': inherit_members
    }
