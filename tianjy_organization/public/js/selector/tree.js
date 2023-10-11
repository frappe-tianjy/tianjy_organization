// @ts-check
/**
 * @typedef {object} TreeNode
 * @property {TreeNode[]} [children]
 * @property {string} label
 * @property {string} name
 * @property {string} [parent]
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
 * @param {TreeNode} node
 * @param {string} [organization]
 */
function create(node, organization) {
	const { name } = node;
	const title = document.createElement('a');
	title.appendChild(document.createTextNode(node.label));
	title.href = '#';
	if (name === organization) {
		title.classList.add('tianjy-organization-list-current');
	}
	title.addEventListener('click', e => {
		e.preventDefault();
		setCurrent(name);
	});
	return title;
}

/**
 *
 * @param {TreeNode} node
 * @param {string} [organization]
 */
export function createDom(node, organization) {
	const { children } = node;
	if (!children?.length) {
		const head = document.createElement('li');
		// TODO: 展开/收起 占位符
		head.appendChild(create(node, organization));

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
	head.appendChild(create(node, organization));

	const ul = root.appendChild(document.createElement('ul'));
	for (const child of children) {
		ul.appendChild(createDom(child, organization));
	}
	return root;
}
/**
 *
 * @param {TreeNode[]} list
 */
export default function createTree(list) {

	/** @type {string | undefined} */
	const organization = store.getCurrent();
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
		ul.appendChild(createDom(node, organization));
	}
	return ul;
}
