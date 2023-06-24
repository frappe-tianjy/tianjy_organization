# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder import DocType

class TianjyOrganizationWorkspace(Document):
	DOCTYPE="Tianjy Organization Workspace"

	def on_update(self):
		if not self.default: return # type: ignore
		organization = self.organization # type: ignore
		if not organization: return

		Table = DocType(self.DOCTYPE)
		frappe.qb.update(Table).set(Table.default, 0).where(
			(Table.organization == organization) & (Table.default == 1) & (Table.name != self.name)
		).run()

	pass
