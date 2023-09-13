import frappe
from json import loads


@frappe.whitelist()
def get_organizations():
    organization_list = frappe.db.get_list('Tianjy Organization',
                                           fields=['*'],
                                           limit=0,
                                           order_by='lft asc')
    organization_types = frappe.db.get_list('Tianjy Organization Type',
                                            fields=['*'],
                                            limit=0,)
    organization_parent_type_list = frappe.db.get_list('Tianjy Organization Type List',
                                                       fields=["*"],
                                                       limit=0,)
    for org in organization_list:
        types = list(filter(lambda ot: org.type ==
                            ot.name, organization_types))
        if types is None or len(types) == 0:
            continue
        org_type = types[0]
        org.type_doc = org_type
        parent_types = list(filter(lambda optl: org_type.name ==
                                   optl.parent, organization_parent_type_list))
        org.parent_type_list = parent_types
        child_type_names = list(map(lambda pt: pt.parent, filter(
            lambda optl: org_type.name == optl.type, organization_parent_type_list)))
        child_type_list = list(filter(
            lambda ol: ol.name in child_type_names, organization_types))
        org.child_type_list = child_type_list
    return organization_list


@frappe.whitelist()
def save_organization_workspace(workspace_name, organization_name, default):
    organization_workspace = frappe.new_doc('Tianjy Organization Workspace')
    organization_workspace.workspace = workspace_name
    organization_workspace.organization = organization_name
    organization_workspace.default = default
    organization_workspace.save()


@frappe.whitelist()
def set_organization_workspace(workspace_name, organization_name, default):
    organization_workspace = frappe.get_list('Tianjy Organization Workspace',
                                             filters=[
                                                 ['workspace', '=',
                                                     workspace_name],
                                                 ['organization', '=',
                                                     organization_name],
                                             ])
    for ow in organization_workspace:
        wo_doc = frappe.get_doc('Tianjy Organization Workspace', ow.name)
        wo_doc.default = default
        wo_doc.save()


def is_workspace_manager():
    return "Workspace Manager" in frappe.get_roles()


@frappe.whitelist()
def delete_page(page):
    if not loads(page):
        return
    page = loads(page)
    if page.get("public") and not is_workspace_manager():
        return

    frappe.db.delete("Tianjy Organization Workspace", {
        "workspace": ("=", page.get("name")),
    })
    if frappe.db.exists("Workspace", page.get("name")):
        frappe.get_doc("Workspace", page.get("name")
                       ).delete(ignore_permissions=True)

    return {"name": page.get("name"), "public": page.get("public"), "title": page.get("title")}


@frappe.whitelist()
def get_members(organization_name):
    member_list = frappe.get_list('Tianjy Organization Member',
                                  filters=[
                                      ['organization', '=', organization_name]
                                  ],
                                  fields=['*'],
                                  limit=0
                                  )
    user_names = list(map(lambda ml: ml.user, member_list))
    user_list = frappe.get_list('User',
                                filters=[
                                    ['name', 'in', user_names]
                                ],
                                fields=['*'],
                                limit=0
                                )

    organization_role_list = frappe.get_list('Tianjy Organization Role',
                                             filters=[
                                                 ['organization', '=',
                                                     organization_name]
                                             ],
                                             fields=['*'],
                                             limit=0
                                             )
    for member in member_list:
        users = list(filter(lambda ul: ul.name == member.user, user_list))
        if len(users) == 0:
            continue
        user = users[0]
        member.user_doc = user
        member.roles = list(filter(
            lambda organization_role: organization_role.user == user.name, organization_role_list))
    return member_list
