# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.utils import DocType


class TianjyOrganizationType(Document):
    DOCTYPE = 'Tianjy Organization Type'

    def on_update(self):
        if not self.no_default:
            return
        org_list = frappe.get_all('Tianjy Organization', filters=[
            ['type', '=', self.name]
        ])
        Table = DocType('Tianjy Organization Member')
        frappe.qb.update(Table).set(Table.default, 0).where(
            Table.organization.isin(list(map(lambda ol: ol.name, org_list)))
        ).run()
