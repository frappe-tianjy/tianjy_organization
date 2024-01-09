export interface Item{
	name:string,
	[parent:string]:any
}
export interface TreeItemData extends Item {
  children?: this[];
}
export function list2Tree<T extends Item>(listData: T[], parentField:string) {
	const listDataCopy:T[]  = structuredClone(listData);
	const treeData: (T & TreeItemData)[] = [];
	const map:Record<string, any> = {};
	listDataCopy.forEach(item => {
	  map[item.name] = item;
	});
	listDataCopy.forEach(item => {
	  const parent = map[item[parentField] || 0];
	  if (parent) {
		(parent.children || (parent.children = [])).push(item);
	  } else {
		treeData.push(item);
	  }
	});
	return treeData;
  }
