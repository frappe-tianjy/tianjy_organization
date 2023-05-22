// @ts-check
import createTree from './tree';

const { Toolbar } = frappe.ui.toolbar;

const old_make = Toolbar.prototype.make;
function addProjectSelect() {
	const ul = document.querySelector('header .navbar-nav:last-child');
	if (!ul) { return; }
	const li = document.createElement('li');
	ul.insertBefore(li, ul.firstChild);
	li.style.display = 'flex';
	li.style.alignItems = 'center';
	li.style.justifyContent = 'center';


	const btn = li.appendChild(document.createElement('a'));
	btn.className = 'nav-list text-muted';
	btn.href = '#';
	btn.title = __('Switch Organization');
	btn.appendChild(document.createTextNode(__('Organization')));
	btn.addEventListener('click', e => {
		e.preventDefault();
		const dialog = new frappe.ui.Dialog({
			title: __('Switch Organization'),
			primary_action_label: __('Close'),
		});
		console.log(dialog);
		/** @type {HTMLElement}  */
		const p = dialog.body;
		p.className = 'tianjy-organization-list';
		dialog.show();

		frappe.call({ method: 'tianjy_organization.viewable' })
			.then(data => data?.message || []).then(list => {
				const ul = createTree(list);
				p.appendChild(ul);
			});
	});
}


Toolbar.prototype.make = function () {
	old_make.call(this);
	addProjectSelect();
};

addProjectSelect();
