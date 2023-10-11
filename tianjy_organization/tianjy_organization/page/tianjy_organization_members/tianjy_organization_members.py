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
