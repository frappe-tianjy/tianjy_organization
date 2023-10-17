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
async function saveUserOrganizationRoles(user, organization, roles) {
	await frappe.xcall('tianjy_organization.tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member.set_user_organization_roles', { user, organization, roles });
}
let id = 0;
/**
 *
 * @param {string} user
 * @param {string} organization
 * @param {() => void} onSave
 * @returns {Promise<void>}
 */
async function createEditor(user, organization, onSave) {
	id++;
	const k = id;
	const [allRoles, roles] = await Promise.all([
		getAllRoles(),
		getUserOrganizationRoles(user, organization),
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
		async primary_action() {
			this.hide();
			await saveUserOrganizationRoles(user, organization, this.get_value('roles'));
			onSave();
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
		const {doc} = frm;
		const {user, organization } = frm.doc;
		createEditor(user, organization, async () => {
			const roles = await frappe.db.get_list('Tianjy Organization Role', {
				filters:{ user: user, organization: organization},
				fields:[ 'user', 'organization', 'role', 'name'],
				limit:0,
			});
			doc.roles = roles;
			const role_grid = frm.fields_dict.roles.grid;
			frm.refresh_field('roles');
			if (role_grid.data.length>role_grid.grid_pagination.page_length) {
				role_grid.wrapper.find('.grid-footer').toggle(true);
			}
		});
		frm.refresh_field('roles');
	},
	refresh(frm) {
		const { doc, meta } = frm;
		const disabled = !frm.is_new() && doc.organization !== doc.inherit_from;
		if (disabled) {
			frm.set_intro('此项目权限配置由系统自动生成，禁止手动修改');
			frm.disable_save();
		} else {
			frm.enable_save();
		}
		for (const field of meta.fields) {
			if (field.read_only || field.set_only_once || field.read_only_depends_on) { continue; }
			frm.set_df_property(field.fieldname, 'read_only', disabled);
		}
		if (doc.organization){
			toggle_default(frm);
		} else {
			hide_field('default');
		}
	},
	organization(frm){
		toggle_default(frm);
	},
});

async function toggle_default(frm){
	const { doc:{organization, default:isDefault} } = frm;
	const organization_doc = await frappe.db.get_doc('Tianjy Organization', organization);
	const type_doc = await frappe.db.get_doc('Tianjy Organization Type', organization_doc.type);
	if (type_doc.no_default === 1){
		hide_field('default');
		if (isDefault===1){
			frm.set_value('default', 0);
		}
	} else {
		unhide_field('default');
	}
}
