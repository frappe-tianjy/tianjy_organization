<template>
	<ElDialog
		v-model="dialogVisible"
		title="角色"
		destroyOnClose
		@close="cancel"
	>
		<div class="role_type_container">
			人员角色：
			<div class="role_container">
				<RoleItem v-for="role in roles.uer_doc?.roles" :role="role.role"></RoleItem>
			</div>
		</div>
		<div class="role_type_container">
			继承角色:
			<div>
				<div v-for="inherit_role in roles.inherit_roles">
					<div>继承自 {{ inherit_role.organization.label }}:</div>
					<div class="role_container">
						<RoleItem v-for="role in inherit_role.roles" :role="role.role"></RoleItem>
					</div>
				</div>
			</div>
		</div>
		<div class="role_type_container">
			本组织角色：
			<div class="role_container">
				<RoleItem v-for="role in roles.organization_role_list" :role="role.role"></RoleItem>
			</div>
		</div>
		<div class="role_type_container">
			组合之后角色：
			<div class="role_container">
				<RoleItem v-for="role in unionRoles" :role="role"></RoleItem>
			</div>
		</div>
	</ElDialog>
</template>

<script setup lang='ts'>
import { ref, watch, computed } from 'vue';
import { ElDialog } from 'element-plus';

import RoleItem from './Role.vue';
const tt = __;

interface Role{
	'uer_doc'?: {roles:{role:string}[]},
	'organization_role_list'?: {role:string}[],
	'inherit_roles'?: {
		organization:{name:string, label:string},
		roles:{role:string}[]
	}[]
}
interface Props{
	visible:boolean,
	user:string,
	organization:string
}
const props = defineProps<Props>();
interface Emit{
	(e: 'cancel'): void,
}
const emit = defineEmits<Emit>();
const dialogVisible = ref<boolean>(false);
const roles = ref<Role>({});
watch(()=>props.visible, ()=>{ dialogVisible.value = props.visible; }, {immediate:true});
watch([()=>props.user, ()=>props.organization], ()=>{
	getRoles();
}, {immediate:true});

async function getRoles(){
	if (!props.user||!props.organization){
		return;
	}
	const res = await frappe.call<{ message: Role }>({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_members.tianjy_organization_members.get_organization_roles',
		args:{
			user_name:props.user,
			organization_name:props.organization,
		},
	});
	roles.value = res?.message||{};
}

const unionRoles = computed(()=>{
	const inheritRoles = roles.value.inherit_roles?.flatMap(item=>item.roles.flatMap(each=>each.role))||[];
	const organizationRoles = roles.value.organization_role_list?.map(item=>item.role)||[];
	const userRoles = roles.value.uer_doc?.roles?.map(item=>item.role)||[];
	return Array.from(new Set([...inheritRoles, ...organizationRoles])).filter(item=>userRoles.includes(item));
});
function cancel(){
	emit('cancel');
}
</script>

<style lang='less' scoped>
.role_type_container{
	margin-bottom: 8px;
	border: 1px solid #999;
    border-radius: 4px;
    padding: 8px;
}
.role_container{
	display:flex;
    align-items: center;
	flex-wrap: wrap;
	div{
		margin: 4px 0;
		width: 33.33%;
	}
}
</style>
