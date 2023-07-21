# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TianjyOrganizationInheritable(Document):
	DOCTYPE="Tianjy Organization Inheritable"
	def validate(self):
		if self.organization == self.inherit_from:
			frappe.throw('不能从自身继承')
