# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.utils import DocType


class TianjyOrganizationType(Document):
    DOCTYPE = 'Tianjy Organization Type'

    def on_update(self):
        if self.no_default:
            org_list = frappe.get_all('Tianjy Organization', filters=[
                ['type', '=', self.name]
            ])
            Table = DocType('Tianjy Organization Member')
            frappe.qb.update(Table).set(Table.default, 0).where(
                Table.organization.isin(
                    list(map(lambda ol: ol.name, org_list)))
            ).run()
        if self.no_workspace:
            organization = frappe.get_list("Tianjy Organization", filters=[
                ['type', '=', self.name]
            ], limit=0, ignore_permissions=True)

            organization_workspace = frappe.get_list('Tianjy Organization Workspace', filters={
                "organization": ['in', list(map(lambda on:on.name, organization))]
            }, fields=['name', 'workspace', 'organization'], limit=0, ignore_permissions=True)
            frappe.db.delete('Tianjy Organization Workspace', {
                "name": ['in', list(map(lambda ow:ow.name, organization_workspace))]
            })
            frappe.db.delete('Workspace', {
                "name": ['in', list(map(lambda ow:ow.workspace, organization_workspace))]
            })
