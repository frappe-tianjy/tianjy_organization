import frappe

filter_operators = {
		'organization': {'label': 'Organization Related', 'multi': False},
		# 'not organization': {'label': 'Not Organization Related', 'multi': False},
		'organizations': {'label': 'Organizations Related In', 'multi': True},
		# 'not organizations': {'label': 'Not Organizations Related In', 'multi': True},
		# "organization ancestors": {'label': 'Organizations Related Ancestors', 'multi': False},
		# "not organization ancestors": {'label': 'Not Organizations Related Ancestors', 'multi': False},
		"organization descendants": {'label': 'Organizations Related Descendants', 'multi': False},
		# "not organization descendants": {'label': 'Not Organizations Related Descendants', 'multi': False},
}

def get_filters_config():
	filters_config = {
		operator: {
			"label": v['label'],
			"get_field": "tianjy_organization.filter.multi_filter_field" if  v['multi'] else "tianjy_organization.filter.filter_field",
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
