
<template>
	<div class="sider-container" v-loading="loading">
		<div class="btn-container">
			<ElButton v-if="permissions.createPermission" type="primary" @click="createOrganization">新建组织</ElButton>
		</div>
		<div class="tree-container">
			<ElTree
				v-if="organizationTree.length>0"
				:data="organizationTree"
				@node-click="handleNodeClick"
				defaultExpandAll
				highlightCurrent
				nodeKey="name"
				:currentNodeKey="currentNodeKey"
				:expandOnClickNode="false"
				draggable
				@node-drop="handleDrop"
				:allowDrop="allowDrop"
			>
				<template #default="{ node, data }">
					<TreeItem
						:node="node"
						@reload="getOrganizations"
					></TreeItem>
				</template>
			</ElTree>
		</div>
	</div>

</template>

<script setup lang='ts'>
import { ref, onMounted, computed, toRaw} from 'vue';
import type {
	AllowDropType,
	NodeDropType,
} from 'element-plus/es/components/tree/src/tree.type';
import type { DragEvents } from 'element-plus/es/components/tree/src/model/useDragNode';
import type Node from 'element-plus/es/components/tree/src/model/node';
import { ElButton, ElTree, vLoading } from 'element-plus';

import { list2Tree } from '../helper';
import type { Organization, Permissions } from '../type';

import TreeItem from './TreeItem.vue';
interface Props{
	modelValue?:Organization
	permissions: Permissions
}
const props = defineProps<Props>();
interface Emit{
	(e:'update:modelValue', organization:any ):void
}
const emit = defineEmits<Emit>();
const organizationList = ref<Organization[]>([]);
const currentNodeKey = ref<string>('');
const loading = ref<boolean>(false);
onMounted(()=>{
	getOrganizations();
});
async function getOrganizations(){
	loading.value = true;
	const res = await frappe.call<{ message: Organization[] }>({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_config.tianjy_organization_config.get_organizations',
	});
	organizationList.value = res?.message||[];
	if (!currentNodeKey.value||!organizationList.value.some(item=>item.name===currentNodeKey.value)){
		currentNodeKey.value = organizationList.value[0]?.name;
		emit('update:modelValue', organizationList.value[0]);
	}
	loading.value = false;
}

const organizationTree = computed(()=>{
	for (const org of organizationList.value){
		org.permissions = props.permissions;
	}
	return list2Tree(toRaw(organizationList.value), 'parent_organization');
});

function handleNodeClick(data:Organization){
	currentNodeKey.value = data.name;
	emit('update:modelValue', data);
}

function createOrganization(){
	const newDoc = frappe.model.make_new_doc_and_get_name('Tianjy Organization');
	frappe.set_route(['form', 'Tianjy Organization', newDoc]);
}
async function handleDrop(
	draggingNode: Node,
	dropNode: Node,
	dropType: NodeDropType,
	ev: DragEvents,
){
	const before = dropType==='inner'?false:dropType ==='before';
	const children = dropType==='inner';
	loading.value = true;
	await frappe.call('tianjy_organization.tianjy_organization.doctype.tianjy_organization.tianjy_organization.sort', {
		target:dropNode.data.name,
		organization: draggingNode.data.name,
		before,
		children,
	});
	getOrganizations();
}

function allowDrop(
	draggingNode: Node,
	dropNode: Node,
	dropType: AllowDropType,
){
	switch (dropType){
		case 'next':
		case 'prev': return before(draggingNode, dropNode);
		case 'inner': return inner(draggingNode, dropNode);
		default: return true;
	}
}
function inner(
	draggingNode: Node,
	dropNode: Node,
){
	// 放到其他节点内
	// 判断能不能作为这个节点的子节点
	if (!dropNode.data.child_type_list.some(type=>type.name===draggingNode.data.type)){
		return false;
	}
	return true;
}
function before(
	draggingNode: Node,
	dropNode: Node,
){
	if (dropNode.parent.level===0&&draggingNode.data.type_doc.root_only!==1){
		console.log(dropNode.parent.level, draggingNode.data.type_doc.root_only, 'false');
		return false;
	}
	// 不是放到根节点，判断能不能作为其他节点的子级
	if (dropNode.parent.level!==0&&!dropNode.parent.data.child_type_list.some(type=>type.name===draggingNode.data.type)){
		console.log(dropNode.parent.level, 'false');
		return false;
	}
	return true;
}

frappe.socketio.doctype_subscribe('Tianjy Organization');
frappe.realtime.on('list_update', p => {
	if (p.doctype !== 'Tianjy Organization') { return; }
	getOrganizations();
});

</script>

<style lang='less' scoped>
.sider-container{
	display: flex;
	flex-direction: column;
	height: 100%;
	padding-top: 8px;
	.btn-container{
		margin-bottom: 8px;
	}
	.tree-container{
		overflow-y: auto;
	}
}
</style>
