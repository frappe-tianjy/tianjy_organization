
### 修改指定用户在指定组织内的角色

`tianjy_organization.tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member.set_user_organization_roles`

### 获取指定用户在指定组织内的角色

`tianjy_organization.tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member.get_user_organization_roles`

### 权限判断钩子函数

`tianjy_organization.has_permission`

### 权限查询条件SQL语句片段钩子函数

`tianjy_organization.get_permission_query_conditions`

### 获取用户在拥有特定权限的组织

`tianjy_organization.get_user_organizations`

### 获取组织中拥有特定权限的用户

`tianjy_organization.get_organization_members`

### 获取用户在某组织内的角色

`tianjy_organization.get_roles`

### 获取绑定特定文档的组织列表

`tianjy_organization.get_bind_organizations`


### 获取用户拥有特定角色的组织列表

`tianjy_organization.get_user_organizations_by_role`

### 获取用户在特定 DocType 内有权限的组织列表

`tianjy_organization.get_user_organizations_by_doctype_permission`

### 获取用户在特定 DocType 内有权限的组织关联的特定类型文档名称列表

`tianjy_organization.get_user_organization_doc_names_by_doctype_permission`

### 获取可见的组织列表

`tianjy_organization.viewable`

### TODO: 前端直接查询组织的文档

### TODO: 前端仅获取可选类型的组织

### TODO: 前端获取组织时，同时获取关联文档

### TODO: 获取组织的成员
