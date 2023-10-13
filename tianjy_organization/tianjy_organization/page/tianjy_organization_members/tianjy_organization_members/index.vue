<template>
	<div v-loading="loading">
		<Page :siderStyle="{width:'620px'}">
			<template #title>
				<h3 class="title">组织人员</h3>
			</template>
			<template #sider>
				<Users
					v-model:loading="loading"
					v-model="user"
					:permissions="userPermissions"
				></Users>
			</template>
			<el-tabs v-model="activeName" class="user-tabs">
				<el-tab-pane class="tab-container" label="基本信息" name="info">
					<FormDetail :name="user?.name" doctype="User"></FormDetail>
				</el-tab-pane>
				<el-tab-pane class="tab-container" label="组织" name="organization">
					<Organization
						v-if="user"
						type="organization"
						:permissions="memberPermissions"
						:user="user.name"
						:allOrganizationList="organizationList"
						@refresh="getOrganizations"
					></Organization>
				</el-tab-pane>
				<el-tab-pane class="tab-container" label="继承组织" name="inherit_organization">
					<Organization
						v-if="user" type="inherit"
						:permissions="memberPermissions"
						:user="user.name"
						:allOrganizationList="organizationList"
					></Organization>
				</el-tab-pane>
			</el-tabs>
		</Page>
	</div>

</template>

<script setup lang='ts'>
import { computed, onMounted, ref, watch } from 'vue';

import Page from '../../../../../../guigu_pm/guigu_pm/public/js/components/page/index.vue';

import Users from './components/Users.vue';
import FormDetail from './components/Detail.vue';
import Organization from './components/Organization.vue';
import type { User, Organization as OrganizationType } from './type';

const user = ref<User>();
const activeName = ref<string>('info');
const userMeta = ref<locals.DocType>();
const memberMeta = ref<locals.DocType>();
const loading = ref<boolean>(true);
const organizationList = ref<OrganizationType[]>([]);

onMounted(async ()=>{
	userMeta.value = await getMeta('User');
	memberMeta.value = await getMeta('Tianjy Organization Member');
});
async function getMeta(doctype:string) {
	let local_meta = frappe.get_meta(doctype);
	if (local_meta) {
		return local_meta;
	}
	await frappe.model.with_doctype(doctype);
	local_meta = frappe.get_meta(doctype);
	return local_meta || undefined;
}

function getPermission(meta?:locals.DocType){
	if (!meta) {
		return { deletePermission: false, createPermission: false, writePermission:false };
	}
	const deletePermission = frappe.perm.has_perm(meta.name, 0, 'delete');
	const createPermission = frappe.perm.has_perm(meta.name, 0, 'create');
	const writePermission = frappe.perm.has_perm(meta.name, 0, 'write');
	return { deletePermission, createPermission, writePermission };
}
const userPermissions = computed(() => getPermission(userMeta.value));
const memberPermissions = computed(() => getPermission(memberMeta.value));

watch(user, ()=>{
	getOrganizations();
}, {immediate:true});

async function getOrganizations(){
	if (!user.value){
		return;
	}
	loading.value=true;
	const res = await frappe.call<{ message: OrganizationType[] }>({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_members.tianjy_organization_members.get_organizations',
		args:{
			user_name:user.value.name,
		},
	});
	organizationList.value = res?.message||[];
	loading.value=false;
}
</script>

<style lang='less' scoped>
.title{
	margin-bottom: 0;
}
.user-tabs{
	height: 100%;
    display: flex;
    flex-direction: column;
}
.tab-container{
	height: 100%;
	overflow: auto;
}
</style>
