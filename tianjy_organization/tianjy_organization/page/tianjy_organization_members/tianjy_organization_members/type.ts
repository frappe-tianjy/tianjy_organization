export interface User{
	name:string,
	full_name:string
}

export interface Permissions{
	deletePermission: boolean, 
	createPermission: boolean, 
	writePermission: boolean
}

export interface Organization{
	name:string,
	user:string,
	organization:string,
	roles:{role:string}[],
}
