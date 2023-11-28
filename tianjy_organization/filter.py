import frappe

filter_operators = {
	'organization': {'label': 'Organization Related', 'field': 'filter_field',},
	# 'not organization': {'label': 'Not Organization Related', 'field': 'filter_field',},
	'organizations': {'label': 'Organizations Related In', 'field': 'multi_filter_field',},
	# 'not organizations': {'label': 'Not Organizations Related In', 'field': 'multi_filter_field',},
	# "organization ancestors": {'label': 'Organizations Related Ancestors', 'field': 'filter_field',},
	# "not organization ancestors": {'label': 'Not Organizations Related Ancestors', 'field': 'filter_field',},
	"organization descendants": {'label': 'Organizations Related Descendants', 'field': 'filter_field',},
	# "not organization descendants": {'label': 'Not Organizations Related Descendants', 'field': 'filter_field',},

	'enabled organization module': {'label': 'Enabled Organization Module', 'field': 'module_filter_field',},
	# 'enabled organization modules': {'label': 'Enabled Organization Modules In', 'field': 'multi_module_filter_field',},
	# 'disabled organization module': {'label': 'Disabled Organization Module', 'field': 'module_filter_field',},
	# 'disabled organization modules': {'label': 'Disabled Organization Modules In', 'field': 'multi_module_filter_field',},
}

def get_filters_config():
	filters_config = {
		operator: {
			"label": v['label'],
			"get_field": f"tianjy_organization.filter.{v['field']}",
			"valid_for_fieldtypes": ["Link"],
			# "depends_on": "company",
		} for operator, v in filter_operators.items()
	}

	return filters_config


@frappe.whitelist()
def filter_field():
	return dict(
		fieldtype="Link",
		operator="organization",
		query_value= False,
		options='Tianjy Organization',
	)

@frappe.whitelist()
def multi_filter_field():
	return dict(
		fieldtype="MultiLink",
		operator="organization",
		query_value= False,
		options='Tianjy Organization',
	)


@frappe.whitelist()
def module_filter_field():
	return dict(
		fieldtype="Link",
		operator="organization",
		query_value= False,
		options='Tianjy Organization Module',
	)

@frappe.whitelist()
def multi_module_filter_field():
	return dict(
		fieldtype="MultiLink",
		operator="organization",
		query_value= False,
		options='Tianjy Organization Module',
	)
