<template>
	<div class="tianjy-organization-detail-header">
		<div class="col-md-4 col-sm-6 col-xs-8 page-title">
			<!-- <div class="title-image hide hidden-md hidden-lg"></div> -->
			<!-- title -->
			<span
				v-if="hasSider"
				class="sidebar-toggle-btn"
				:title="tt('Toggle Sidebar')">
				<svg class="icon icon-md sidebar-toggle-placeholder">
					<use href="#icon-menu" />
				</svg>
				<span class="sidebar-toggle-icon"
					@click="opened = !opened">
					<svg class="icon icon-md">
						<use v-if="open" href="#icon-sidebar-expand" />
						<use v-else href="#icon-sidebar-collapse" />
					</svg>
				</span>
			</span>
			<div class="flex fill-width title-area">
				<div>
					<div class="flex">
						<h3 class="ellipsis title-text"></h3>
						<span class="indicator-pill whitespace-nowrap" />
					</div>
					<div class="ellipsis sub-heading hide text-muted" />
				</div>
				<button class="btn btn-default more-button hide">
					<svg class="icon icon-sm">
						<use href="#icon-dot-horizontal" />
					</svg>
				</button>
			</div>
		</div>
		<div class="flex col page-actions justify-content-end">
			<!-- buttons -->
			<div class="custom-actions hide hidden-xs hidden-md" />
			<div class="standard-actions flex">
				<span class="page-icon-group hide hidden-xs hidden-sm" />
				<div class="menu-btn-group hide">
					<button type="button"
						class="btn btn-default icon-btn"
						data-toggle="dropdown"
						aria-expanded="false">
						<span>
							<span class="menu-btn-group-label">
								<svg class="icon icon-sm">
									<use href="#icon-dot-horizontal" />
								</svg>
							</span>
						</span>
					</button>
					<ul class="dropdown-menu dropdown-menu-right" role="menu" />
				</div>
				<button class="btn btn-secondary btn-default btn-sm hide" />
				<div class="actions-btn-group hide">
					<button type="button"
						class="btn btn-primary btn-sm"
						data-toggle="dropdown"
						aria-expanded="false">
						<span>
							<span
								class="actions-btn-group-label">{{
									tt('Actions')
								}}</span>
							<svg class="icon icon-xs">
								<use href="#icon-select" />
							</svg>
						</span>
					</button>
					<ul class="dropdown-menu dropdown-menu-right" role="menu" />
				</div>
				<button class="btn btn-primary btn-sm hide primary-action" />
				<button v-if="!isHideClose" class="btn btn-sm" @click="hide">
					{{ tt('Close') }}
				</button>
			</div>
		</div>
	</div>
</template>
<script lang="ts" setup>
import { computed } from 'vue';

const props = defineProps<{
	hasSider?: boolean;
	open?: boolean;
	isHideClose?: boolean;
}>();
const emit = defineEmits<{
	(event: 'hide'): void;
	(event: 'refresh'): void;
	(event: 'update:open', open?: boolean): void;
}>();
function hide() {
	emit('hide');
}
const opened = computed({
	get: () => props.open,
	set(v) { emit('update:open', Boolean(v)); },
});
const tt = __;

</script>
<style scoped>
.tianjy-organization-detail-header {
	display: flex;
	flex-wrap: wrap;
	justify-content: space-between;
	align-items: center;
	z-index: 6;
	position: sticky;
	top: 0;
	box-shadow: var(--shadow-sm);
	background-color: var(--card-bg);
	margin-bottom: 5px;
	height: 48px;
}
</style>
