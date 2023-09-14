export interface User{
	name:string,
	full_name:string,
	enabled:1|0
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
