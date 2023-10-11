export interface Organization{
	name:string,
	label:string,
	parent_organization?:string,
	type:string,
	doc_type?:string,
	document?:string,
	work_space:OrganizationWorkspace[],
	child_type_list?:OrganizationType[],
	parent_type_list?:OrganizationType[],
	permissions?:Permissions
}

export interface OrganizationWorkspace{
	name:string,
	workspace:string,
	organization:string,
	default: 0|1,
}

export interface OrganizationType{
	name:string,
	root_only:1|0,
	parent_types:ParentType[],
	doc_types:any[]
}
export interface ParentType{
	name:string,
	type:string
}

export interface Permissions{
	deletePermission: boolean, 
	createPermission: boolean, 
	writePermission: boolean
}

export interface Member{
	name:string,
	user:string,
	organization:string,
	roles:{role:string}[],
}

export interface InheritOrganization{
	name:string,
	organization:string,
	inherit_from:string,
	visible:0|1,
	viewable:0|1,
	addible:0|1,
	editable:0|1,
	deletable:0|1,
	manageable:0|1,
}
