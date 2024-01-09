<template>
	<ElDialog
		v-model="dialogVisible"
		title="权限"
		destroyOnClose
		@close="cancel"
	>
		<div class="permission_type_container">
			<h5>继承权限:</h5>
			<div>
				<div v-for="inherit_member in members.inherit_members">
					<h6>继承自 {{ inherit_member.organization_doc.label }}:</h6>
					<div class="permission_container">
						<div v-for="p in permissions">
							<span>{{ tt(p.label) }}:</span><span>{{ inherit_member[p.value] ===1?'是':'否' }}</span>
						</div>
					</div>
				</div>
			</div>
		</div>
		<div class="permission_type_container" v-if="members.organization_members">
			<h5>本组织权限：</h5>
			<div class="permission_container">
				<div v-for="p in permissions">
					<span>{{ tt(p.label) }}:</span><span>{{ members?.organization_members?.[p.value] ===1?'是':'否' }}</span>
				</div>
			</div>
		</div>
		<div class="permission_type_container">
			<h5>组合之后权限：</h5>
			<div class="permission_container">
				<div v-for="p in permissions">
					<span>{{ tt(p.label) }}:</span><span>{{ unionPermissions[p.value] ===1?'是':'否' }}</span>
				</div>
			</div>
		</div>
	</ElDialog>
</template>

<script setup lang='ts'>
import { ref, watch, computed } from 'vue';
import { ElDialog } from 'element-plus';
const tt = __;
const permissions = [
	{value:'visible', label:'Visible'},
	{value:'viewable', label:'Viewable'},
	{value:'addible', label:'Addible'},
	{value:'editable', label:'Editable'},
	{value:'deletable', label:'Deletable'},
	{value:'manageable', label:'Manageable'},
] as const;
interface Permission{
	visible:0|1,
	viewable:0|1,
	addible:0|1,
	editable:0|1,
	deletable:0|1,
	manageable:0|1,
}
interface Member{
	'organization_members'?: Permission,
	'inherit_members'?: (Permission&{organization_doc:{name:string, label:string}})[]
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
const members = ref<Member>({});
watch(()=>props.visible, ()=>{ dialogVisible.value = props.visible; }, {immediate:true});
watch([()=>props.user, ()=>props.organization], ()=>{
	getPermissions();
}, {immediate:true});

async function getPermissions(){
	if (!props.user||!props.organization){
		return;
	}
	const res = await frappe.call<{ message: Member }>({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_members.tianjy_organization_members.get_organization_members',
		args:{
			user_name:props.user,
			organization_name:props.organization,
		},
	});
	members.value = res?.message||{};
}

const unionPermissions = computed(()=>{
	const allPermission:{[key in keyof Permission]?:0|1} = {};
	for (const p of permissions){
		const inheritPerms = members.value.inherit_members?.map(item=>item[p.value])||[];
		inheritPerms.push(members.value.organization_members?.[p.value]||0);
		allPermission[p.value] = inheritPerms.some(item=>item===1)?1:0;
	}
	return allPermission;
});
function cancel(){
	emit('cancel');
}
</script>

<style lang='less' scoped>
.permission_type_container{
	margin-bottom: 8px;
	border: 1px solid #999;
    border-radius: 4px;
    padding: 8px;
}
.permission_container{
	display:flex;
    align-items: center;
	flex-wrap: wrap;
	div{
		margin: 4px 0;
		width: 33.33%;
	}
	span{
		margin-right: 8px;
	}
}
</style>
