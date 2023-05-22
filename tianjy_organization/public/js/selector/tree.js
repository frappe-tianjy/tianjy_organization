// @ts-check
/**
 * @typedef {object} TreeNode
 * @property {TreeNode[]} [children]
 * @property {string} label
 * @property {string} name
 * @property {string} [parent]
 */

import setOrganization from './setOrganization';

/**
 *
 * @param {TreeNode} node
 */
export function createDom(node) {
	const { children } = node;
	if (!children?.length) {
		const head = document.createElement('li');
		// TODO: 展开/收起 占位符
		const title = head.appendChild(document.createElement('a'));
		title.appendChild(document.createTextNode(node.label));
		title.href = '#';
		title.addEventListener('click', e => {
			e.preventDefault();
			setOrganization(node.name);
		});

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
	const title = head.appendChild(document.createElement('a'));
	title.appendChild(document.createTextNode(node.label));
	title.href = '#';
	title.addEventListener('click', e => {
		e.preventDefault();
		setOrganization(node.name);
	});

	const ul = root.appendChild(document.createElement('ul'));
	for (const child of children) {
		ul.appendChild(createDom(child));
	}
	return root;
}
/**
 *
 * @param {TreeNode[]} list
 */
export default function createTree(list) {
	/** @type {Map<string, TreeNode[]>} */
	const map = new Map();
	for (const node of list) {
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
