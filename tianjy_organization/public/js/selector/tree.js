// @ts-check
/**
 * @typedef {object} TreeNode
 * @property {TreeNode[]} [children]
 * @property {string} label
 * @property {string} name
 * @property {string} [parent]
 * @property {1} [default]
 */

import * as store from '../store';

/**
 *
 * @param {string} organization
 */
async function setCurrent(organization) {
	store.setCurrent(organization);
	try {
		const method = 'tianjy_organization.lib.get_default_workspace';
		const v = await frappe.call(method, { organization });
		const workspace = v?.message;
		if (workspace) {
			location.href = `/app/${encodeURIComponent(workspace)}`;
			return;
		}
	} catch {}
	location.reload();
}
/**
 *
 * @param {string} organization
 */
async function setDefault(organization) {
	try {
		const method = 'tianjy_organization.lib.set_default';
		const s = await frappe.call(method, { organization });
		return s?.message || false;
	} catch {}
}


/**
 *
 * @param {TreeNode[]} list
 */
export default function createTree(list) {
	/** @type {string | undefined} */
	let organization = store.getCurrent();
	/** @type {HTMLElement} */
	let defaultLine;
	/**
	 * @param {TreeNode} node
	 * @param {HTMLElement} head
	 */
	function create(node, head) {
		const { name } = node;
		const title = head.appendChild(document.createElement('a'));
		title.appendChild(document.createTextNode(node.label));
		title.href = '#';
		if (name === organization) {
			title.classList.add('tianjy-organization-list-current');
		}
		title.addEventListener('click', e => {
			e.preventDefault();
			setCurrent(name);
		});
		const button = head.appendChild(document.createElement('button'));
		button.addEventListener('click', async e => {
			e.preventDefault();
			if (await setDefault(name)) {
				defaultLine?.classList.remove('tianjy-organization-list-default');
				defaultLine = head;
				defaultLine.classList.add('tianjy-organization-list-default');
			}
		});
		if (node.default) {
			defaultLine = head;
			defaultLine.classList.add('tianjy-organization-list-default');
		}
		return head;
	}
	/**
	 *
	 * @param {TreeNode} node
	 */
	function createDom(node) {
		const { children } = node;
		if (!children?.length) {
			const head = document.createElement('li');
			// TODO: 展开/收起 占位符
			create(node, head);

			return head;
		}
		const root = document.createElement('li');
		const head = root.appendChild(document.createElement('div'));
		const folder = root.appendChild(document.createElement('span'));
		folder.className = 'tianjy-organization-list-tree-folder';
		folder.addEventListener('click', e => {
			e.preventDefault();
			root.classList.toggle('tianjy-organization-list-tree-folded');
		});
		// TODO: 展开/收起
		create(node, head);

		const ul = root.appendChild(document.createElement('ul'));
		for (const child of children) {
			ul.appendChild(createDom(child));
		}
		return root;
	}

	/** @type {Map<string, TreeNode[]>} */
	const map = new Map();
	for (const node of list) {
		/** @type {TreeNode[]} */
		const children = [];
		node.children = children;
		map.set(node.name, children);
	}
	/** @type {TreeNode[]} */
	const root = [];
	for (const node of list) {
		const { parent } = node;
		const list = parent && map.get(parent) || root;
		list.push(node);
	}

	const ul = document.createElement('ul');
	for (const node of root) {
		ul.appendChild(createDom(node));
	}
	return ul;
}
