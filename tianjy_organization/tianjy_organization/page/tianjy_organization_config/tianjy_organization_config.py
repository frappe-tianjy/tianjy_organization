import frappe
from json import loads, dumps

from pypika import Order
import frappe
from frappe import _
from frappe.desk.desktop import Workspace
from frappe.query_builder.utils import DocType
from frappe.desk.doctype.workspace.workspace import last_sequence_id


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
                                      ['organization', '=',
                                       organization_name],
                                      ['inherit_from', '=',
                                       organization_name],
                                  ],
                                  fields=['*'],
                                  limit=0
                                  )
    user_names = list(map(lambda ml: ml.user, member_list))
    user_list = frappe.get_list('User',
                                filters=[
                                    ['name', 'in',
                                     user_names]
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


@frappe.whitelist()
def get_inherit(organization_name):
    inherit_list = frappe.get_list('Tianjy Organization Inheritable',
                                   filters=[
                                       ['organization', '=',
                                        organization_name]
                                   ],
                                   fields=['*'],
                                   limit=0
                                   )
    organization_names = list(map(lambda il: il.organization, inherit_list)) + \
        list(map(lambda il: il.inherit_from, inherit_list))
    organization_list = frappe.get_list('Tianjy Organization',
                                        filters=[
                                            ['name', 'in',
                                             organization_names]
                                        ],
                                        fields=['*'],
                                        limit=0
                                        )
    for inherit in inherit_list:
        organizations = list(
            filter(lambda ol: ol.name == inherit.organization, organization_list))
        inherit_from_organizations = list(
            filter(lambda ol: ol.name == inherit.inherit_from, organization_list))
        if len(organizations) == 0 or len(inherit_from_organizations) == 0:
            continue
        organization = organizations[0]
        inherit_from_organization = inherit_from_organizations[0]
        inherit.organization_doc = organization
        inherit.inherit_from_organization_doc = inherit_from_organization
    return inherit_list


def get_pages(organization_name):
    # don't get domain restricted pages

    Workspace = DocType('Workspace')
    OrganizationWorkspace = DocType('Tianjy Organization Workspace')

    query = frappe.qb.from_(Workspace).select(
        Workspace.name.as_("name"),
        Workspace.title.as_("title"),
        Workspace.for_user.as_("for_user"),
        Workspace.parent_page.as_("parent_page"),
        Workspace.content.as_("content"),
        Workspace.public.as_("public"),
        Workspace.module.as_("module"),
        Workspace.icon.as_("icon"),
        Workspace.is_hidden.as_("is_hidden"),
        OrganizationWorkspace.default.as_("default"),
        OrganizationWorkspace.organization.as_('organization'),
    ).left_join(OrganizationWorkspace).on(Workspace.name == OrganizationWorkspace.workspace)
    where = OrganizationWorkspace.organization == organization_name
    query = query.where(where)
    query = query.orderby(Workspace.sequence_id, order=Order.asc)
    return query.run(as_dict=True)


@frappe.whitelist()
def get_workspace_sidebar_items(organization_name):
    """Get list of sidebar items for desk"""
    user: str = frappe.session.user
    is_admin = "System Manager" in frappe.get_roles()
    has_access = "Workspace Manager" in frappe.get_roles()

    all_pages = get_pages(organization_name)
    pages = []
    private_pages = []

    # Filter Page based on Permission
    for page in all_pages:
        try:
            workspace = Workspace(page, True)
            if has_access or workspace.is_permitted():
                if page.public and (has_access or not page.is_hidden):
                    pages.append(page)
                elif page.for_user == user:
                    private_pages.append(page)
                page["label"] = _(page.get("name"))
        except frappe.PermissionError:
            pass
    if private_pages:
        pages.extend(private_pages)

    if len(pages) == 0:
        organization = frappe.get_doc('Tianjy Organization', organization_name)
        workspace = frappe.new_doc("Workspace")
        workspace.title = label = organization.label
        workspace.content = dumps([{
            "type": "header",
            "data": {"text": organization.label}
        }])
        workspace.label = organization.label
        workspace.public = 1
        workspace.for_user = ''
        workspace.sequence_id = last_sequence_id(workspace) + 1
        workspace.save(ignore_permissions=True)

        organization_workspace = frappe.new_doc(
            'Tianjy Organization Workspace')
        organization_workspace.workspace = workspace.name
        organization_workspace.organization = organization_name
        organization_workspace.default = 1
        organization_workspace.save()
        pages = [{
            "name": workspace.name,
            "title": workspace.title,
            "for_user": workspace.for_user,
            "parent_page": workspace.parent_page,
            "content": workspace.content,
            "public": workspace.public,
            "module": workspace.module,
            "icon": workspace.icon,
            "is_hidden": workspace.is_hidden,
            'organization': organization_name
        }]
    return {"pages": pages, "has_access": has_access}
