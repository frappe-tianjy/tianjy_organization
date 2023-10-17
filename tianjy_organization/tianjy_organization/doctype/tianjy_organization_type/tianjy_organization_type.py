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
			if org_list:
				Table = DocType('Tianjy Organization Member')
				frappe.qb.update(Table).set(Table.default, 0).where(
					Table.organization.isin([ol.name for ol in org_list])
				).run()
		if self.no_workspace:
			organization = frappe.get_all("Tianjy Organization", filters=[
				['type', '=', self.name]
			])
			if organization:
				workspaces = frappe.get_all('Tianjy Organization Workspace', filters={
					"organization": ('in',[on.name for on in organization])
				}, fields=['name', 'workspace'])
				if workspaces:
					frappe.db.delete('Tianjy Organization Workspace', {
						"name": ('in', [ow.name for ow in workspaces])
					})
					frappe.db.delete('Workspace', {
						"name": ('in', [ow.workspace for ow in workspaces])
					})
