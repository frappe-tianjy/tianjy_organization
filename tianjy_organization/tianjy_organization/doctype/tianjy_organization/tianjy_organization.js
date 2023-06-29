// Copyright (c) 2023, Tianjy and contributors
// For license information, please see license.txt
// @ts-check
/**
 * @typedef {object} Type
 * @property {string} name
 * @property {string[]} parent_types
 * @property {string[]} leader_types
 * @property {boolean} root_only
 */

/** @type {Type[]} */
let types;

async function loadTypes() {
	/** @type {Type[]} */
	// @ts-ignore
	const data = (await frappe.call(
		'tianjy_organization.tianjy_organization.doctype.tianjy_organization.tianjy_organization.get_types'
	))?.message || [];
	types = data;
	return types;
}
/** @type {Promise<Type[]>} */
const typePromise = loadTypes();



function getCurrentType(frm) {
	/** @type {Type[]?} */
	const types = frm.__types;
	if (!types) { return; }
	const type = frm.doc.type;
	return types.find((t) => t.name === type);
}
function setParentOrganization(frm) {
	frm.set_query('parent_organization', function () {
		return {
			filters: [['type', "in", getCurrentType(frm)?.parent_types || []]]
		};
	});
	const current = getCurrentType(frm);
	if (!current) {
		frm.set_df_property('parent_organization', 'hidden', true);
		frm.set_df_property('parent_organization', 'reqd', true);
		frm.set_value('parent_organization', null);
		return;
	}
	const rootOnly = !current.parent_types.length;
	frm.set_df_property('parent_organization', 'hidden', rootOnly);
	frm.set_df_property('parent_organization', 'reqd', !rootOnly && !current.root_only);
	if (rootOnly) {
		frm.set_value('parent_organization', null);
	}
}


// @ts-ignore
frappe.ui.form.on('Tianjy Organization', {
	setup(frm) {
		typePromise.then(types => {
			frm.__types = types;
			frm.trigger('refresh');
		});
		setParentOrganization(frm);
	},
	refresh: function (frm) {
		/** @type {Type[]?} */
		const types = frm.__types;
		frm.set_df_property("type", "options", types?.map(t => t.name) || '');
		frm.trigger('type');

	},
	type(frm) {
		setParentOrganization(frm);
	},
});
