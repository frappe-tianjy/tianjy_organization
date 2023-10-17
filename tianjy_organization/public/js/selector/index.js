// @ts-check
import * as store from '../store';

import createTree from './tree';

const { Toolbar } = frappe.ui.toolbar;

const old_make = Toolbar.prototype.make;


async function getOrganizationName() {
	const organization = store.getCurrent();
	if (!organization) { return; }
	try {
		const { message } = await frappe.call('frappe.desk.search.get_link_title', {
			doctype: 'Tianjy Organization',
			docname: organization,
		});
		if (message && typeof message === 'string') {
			return message;
		}
	} catch {

	}
	store.setCurrent('');
}

async function addProjectSelect() {
	const ul = document.querySelector('header .navbar-nav:last-child');
	if (!ul) { return; }
	const li = document.createElement('li');
	ul.insertBefore(li, ul.firstChild);
	li.style.display = 'flex';
	li.style.alignItems = 'center';
	li.style.justifyContent = 'center';


	const btn = li.appendChild(document.createElement('a'));
	li.classList.add('nav-item');
	btn.className = 'nav-list text-muted';

	btn.href = '#';
	btn.title = __('Switch Organization');
	const name = await getOrganizationName();
	function selectOrganization() {
		const dialog = new frappe.ui.Dialog({
			title: __('Switch Organization'),
			primary_action_label: __('Close'),
		});
		/** @type {HTMLElement}  */
		const p = dialog.body;
		p.className = 'tianjy-organization-list';
		dialog.show();

		frappe.call({ method: 'tianjy_organization.viewable' })
			.then(data => data?.message || []).then(list => {
				const ul = createTree(list);
				p.appendChild(ul);
			});

	}
	if (!name) {
		let d = new frappe.ui.Dialog({
			title: '未选择项目',
			fields: [{ label: '您当前不在任何项目中，是否现在去选择项目?', fieldtype: 'Heading' }],
			primary_action_label: __('Select Organization'),
			secondary_action_label: '取消',
			primary_action() {
				d.hide();
				selectOrganization();
			},
			secondary_action() {
				d.hide();
			},
		});
		d.show();
	}
	const organizationName = name || __('Select Organization');
	btn.appendChild(document.createTextNode(organizationName));
	btn.addEventListener('click', e => {
		e.preventDefault();
		selectOrganization();
	});
}


Toolbar.prototype.make = function () {
	old_make.call(this);
	addProjectSelect();
};

addProjectSelect();
