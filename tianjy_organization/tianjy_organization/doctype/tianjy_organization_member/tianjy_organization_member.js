// Copyright (c) 2023, 天玑 Tinajy and contributors
// For license information, please see license.txt
function showPermDialog(role, permissions) {
	const perm_dialog = new frappe.ui.Dialog({ title: __(role) });
	perm_dialog.$wrapper
		.find('.modal-dialog')
		.css('width', '1200px')
		.css('max-width', '80vw');
	perm_dialog.show();
	const $body = $(perm_dialog.body);
	if (!permissions.length) {
		$body.append(`<div class="text-muted text-center padding">
			${__('{0} role does not have permission on any doctype', [role])}
		</div>`);
		return;
	}
	const table = document.createElement('table');
	table.className = 'user-perm';
	const thead = table.appendChild(document.createElement('thead'));
	const tr = thead.appendChild(document.createElement('tr'));
	tr.appendChild(document.createElement('th'))
		.appendChild(document.createTextNode(__('Document Type')));
	tr.appendChild(document.createElement('th'))
		.appendChild(document.createTextNode(__('Level')));
	for (const p of frappe.perm.rights) {
		tr.appendChild(document.createElement('th'))
			.appendChild(document.createTextNode(frappe.unscrub(p)));
	}

	const tbody = table.appendChild(document.createElement('thead'));
	for (const perm of permissions) {
		const tr = tbody.appendChild(document.createElement('tr'));
		tr.appendChild(document.createElement('td'))
			.appendChild(document.createTextNode(perm.parent));
		tr.appendChild(document.createElement('td'))
			.appendChild(document.createTextNode(perm.permlevel));
		for (const p of frappe.perm.rights) {
			const td = tr.appendChild(document.createElement('td'));
			td.className = 'text-muted bold';
			if (perm[p]) {
				td.innerHTML = frappe.utils.icon('check', 'xs');
			} else {
				td.appendChild(document.createTextNode('-'));
			}
		}

	}
	$body.append(table);

}

let allRoles;
function getAllRoles(force) {
	if (!allRoles || force) {
		allRoles = frappe.xcall('frappe.core.doctype.user.user.get_all_roles');
	}
	return allRoles;
}
function getUserOrganizationRoles(user, organization) {
	return frappe.xcall('tianjy_organization.tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member.get_user_organization_roles', { user, organization });
}
function saveUserOrganizationRoles(user, organization, roles) {
	return frappe.xcall('tianjy_organization.tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member.set_user_organization_roles', { user, organization, roles });
}
let id = 0;
async function createEditor(user, organization) {
	id++;
	const k = id;
	const [allRoles, roles] = await Promise.all([
		getAllRoles(),
		getUserOrganizationRoles(user, organization)
	]);
	if (k !== id) { return; }

	const dialog = new frappe.ui.Dialog({
		title: __('Edit Roles'),
		fields: [
			{
				fieldname: 'roles',
				fieldtype: 'MultiCheck',
				select_all: true,
				columns: 3,
				// options: await getAllRoles(),
				get_data: () => allRoles.map(role => ({
					label: __(role),
					value: role,
					checked: roles.includes(role),
				})),
			},
		],
		primary_action() {
			this.hide();
			saveUserOrganizationRoles(user, organization, this.get_value('roles'));
		},
		primary_action_label: __('Update'),
	});


	const multicheck = dialog.fields_dict.roles;

	multicheck.$wrapper.find('.label-area').click(e => {
		const role = $(e.target).data('unit');
		e.preventDefault();
		if (!role) { return; }
		return frappe
			.xcall('frappe.core.doctype.user.user.get_perm_info', { role })
			.then(permissions => showPermDialog(role, permissions));

	});
	dialog.show();
}

frappe.ui.form.on('Tianjy Organization Member', {
	role_editor(frm) {
		const doc = frm.doc;
		createEditor(doc.user, doc.organization);
	},
	// refresh: function(frm) {

	// }
});
