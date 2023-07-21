// Copyright (c) 2023, Tianjy and contributors
// For license information, please see license.txt
// @ts-check
/**
 * @typedef {object} Type
 * @property {string} name
 * @property {string[]} parent_types
 * @property {string[]} doc_types
 * @property {boolean} root_only
 */

async function getType(frm) {
	const type = frm.doc.type;
	if (!type) { return; }
	/** @type {Type | undefined} */
	const oldType = frm.__type;
	if (oldType?.name === type) { return oldType; }
	// @ts-ignore
	const t = (await frappe.call(
		'tianjy_organization.tianjy_organization.doctype.tianjy_organization.tianjy_organization.get_type',
		{ type }
	))?.message;;
	if (!t) { return; }
	frm.__type = t;
	return t;
}

function setParentOrganizationNull(frm) {
	frm.set_query('doc_type', () => ({ filters: [['name', "in", []]] }));
	frm.set_query('parent_organization', () => ({ filters: [['type', "in", []]] }));
	frm.set_df_property('parent_organization', 'hidden', true);
	frm.set_df_property('parent_organization', 'reqd', true);
	frm.set_value('parent_organization', null);
	frm.set_value('doc_type', null);
}
async function typeUpdated(frm) {
	const currentType = frm.doc.type;
	const type = await getType(frm);
	if (currentType !== frm.doc.type) { return; }
	if (!type) { return setParentOrganizationNull(frm); }

	frm.set_query('doc_type', () => ({ filters: [['name', "in", type.doc_types]] }));
	frm.set_query('parent_organization', () => ({ filters: [['type', "in", type.parent_types]] }));
	const rootOnly = !type.parent_types.length;
	frm.set_df_property('parent_organization', 'hidden', rootOnly);
	frm.set_df_property('doc_type', 'hidden', !type.doc_types?.length);
	frm.set_df_property('parent_organization', 'reqd', !rootOnly && !type.root_only);
	if (rootOnly) {
		frm.set_value('parent_organization', null);
	}
	if (!type.doc_types?.length || !type.doc_types.includes(frm.doc.doc_type)) {
		frm.set_value('doc_type', null);
	}
}


// @ts-ignore
frappe.ui.form.on('Tianjy Organization', {
	setup(frm) {
	},
	refresh: function (frm) {
		if (frm.is_new()) {
			frm.set_value('old_parent', null);
		}
		typeUpdated(frm);
	},
	type(frm) {
		typeUpdated(frm);
	},
	doc_type(frm) {
		const has = Boolean(frm.doc.doc_type);
		frm.set_df_property('docmenut', 'reqd', has);
		frm.set_df_property('docmenut', 'hidden', !has);
		if (!has) {
			frm.set_value('doc_type', null);
		}

	}
});
