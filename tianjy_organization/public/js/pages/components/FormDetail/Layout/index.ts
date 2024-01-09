/* eslint-disable max-lines */
import type { WritableComputedRef } from 'vue';

import type Form from '../Form';

import Section from './Section';
import Tab from './Tab';
import Column from './Column';
class Layout {
	views = {};
	pages = [];
	tabs: Tab[] = [];
	sections: Section[] = [];
	page_breaks = [];
	sections_dict: Record<string, Section> = {};
	fields_list: (Section | frappe.ui.form.Control | Column)[] = [];
	fields_dict: Record<string, Section | frappe.ui.form.Control | Column> = {};
	section_count = 0;
	column_count = 0;
	with_dashboard = true;
	card_layout = true;
	currentTab: WritableComputedRef<any>;
	constructor(
		parent: HTMLElement,
		doctype: string,
		doctype_layout: unknown,
		frm: Form,
		currentTab: WritableComputedRef<any>,
	) {
		this.parent = $(parent);
		this.doctype = doctype;
		this.doctype_layout = doctype_layout;
		this.frm = frm;
		this.currentTab = currentTab;
		const wrapper = parent.querySelector('.form-layout') as HTMLElement;
		const message = parent.querySelector('.form-message') as HTMLElement;
		const page = parent.querySelector('.form-page') as HTMLElement;


		this.wrapper = $(wrapper);
		this.message = $(message);
		this.page = $(page);
		message.innerHTML = '';
		page.innerHTML = '';

		if (!this.fields) {
			this.fields = this.get_doctype_fields();
		}

		if (this.is_tabbed_layout()) {
			this.setup_tabbed_layout();
		}

		this.setup_tab_events();
		this.render();
		// 还原当前显示的 tab
		const tab = currentTab.value;
		const current = tab && this.tab_link_container?.[0]?.querySelector(`.nav-link[data-fieldname=${tab}]`);
		if (current) {
			$(current).tab('show');
		}
	}

	formTabsList = document.createElement('div');
	tabsContent = document.createElement('div');
	setup_tabbed_layout() {
		const tab_link_container = $('<ul class="nav form-tabs" id="form-tabs" role="tablist"></ul>');
		const {formTabsList} = this;
		formTabsList.className = 'form-tabs-list';
		tab_link_container.appendTo(formTabsList);
		$(formTabsList).appendTo(this.page);
		this.tab_link_container = tab_link_container;
		const {tabsContent} = this;
		tabsContent.className = 'form-tab-content tab-content';
		this.tabs_content = $(tabsContent).appendTo(
			this.page,
		);
		this.setup_events();
	}
	get_doctype_fields() {
		let fields = [this.get_new_name_field()];
		if (this.doctype_layout) {
			fields = fields.concat(this.get_fields_from_layout());
		} else {
			fields = fields.concat(
				frappe.meta.sort_docfields(frappe.meta.docfield_map[this.doctype]),
			);
		}

		return fields;
	}

	get_new_name_field() {
		return {
			parent: this.frm.doctype,
			fieldtype: 'Data',
			fieldname: '__newname',
			reqd: 1,
			hidden: 1,
			label: __('Name'),
			get_status(field) {
				if (
					field.frm &&
					field.frm.is_new() &&
					field.frm.meta.autoname &&
					['prompt', 'name'].includes(field.frm.meta.autoname.toLowerCase())
				) {
					return 'Write';
				}
				return 'None';
			},
		};
	}

	get_fields_from_layout() {
		const fields = [];
		for (let f of this.doctype_layout.fields) {
			const docfield = copy_dict(frappe.meta.docfield_map[this.doctype][f.fieldname]);
			docfield.label = f.label;
			fields.push(docfield);
		}
		return fields;
	}

	show_message(html, color) {
		if (this.message_color) {
			// remove previous color
			this.message.removeClass(this.message_color);
		}
		this.message_color =
			color && ['yellow', 'blue', 'red', 'green', 'orange'].includes(color) ? color : 'blue';
		if (html) {
			if (html.substr(0, 1) !== '<') {
				// wrap in a block
				html = `<div>${html}</div>`;
			}
			this.message.removeClass('hidden').addClass(this.message_color);
			$(html).appendTo(this.message);
		} else {
			this.message.empty().addClass('hidden');
		}
	}

	render(new_fields?: typeof this.fields) {
		let fields = new_fields || this.fields;

		this.section = null;
		this.column = null;

		if (this.no_opening_section() && !this.is_tabbed_layout()) {
			this.fields.unshift({ fieldtype: 'Section Break' });
		}

		if (this.is_tabbed_layout()) {
			// add a tab without `fieldname` to avoid conflicts
			let default_tab = {
				label: __('Details'),
				fieldtype: 'Tab Break',
				fieldname: '__details',
			};

			let first_field_visible = this.fields.find(element => element.hidden == false);
			let first_tab =
				first_field_visible?.fieldtype === 'Tab Break' ? first_field_visible : null;

			if (first_tab) {
				// reshuffle __newname field to accomodate under 1st Tab Break
				let newname_field = this.fields.find(df => df.fieldname === '__newname');
				if (newname_field && newname_field.get_status(this) === 'Write') {
					this.fields.splice(0, 1);
					this.fields.splice(1, 0, newname_field);
				}
			} else {
				this.fields.splice(0, 0, default_tab);
			}
		}

		for (const df of fields) {
			switch (df.fieldtype) {
				case 'Fold':
					this.make_page(df);
					break;
				case 'Page Break':
					this.make_page_break();
					this.make_section(df);
					break;
				case 'Section Break':
					this.make_section(df);
					break;
				case 'Column Break':
					this.make_column(df);
					break;
				case 'Tab Break':
					this.make_tab(df);
					break;
				default:
					this.make_field(df);
			}
		}
	}

	no_opening_section() {
		return (
			(this.fields[0] && this.fields[0].fieldtype != 'Section Break') || !this.fields.length
		);
	}

	no_opening_tab() {
		return (this.fields[1] && this.fields[1].fieldtype != 'Tab Break') || !this.fields.length;
	}

	is_tabbed_layout() {
		return this.fields.find(f => f.fieldtype === 'Tab Break');
	}

	replace_field(fieldname, df, render) {
		df.fieldname = fieldname; // change of fieldname is avoided
		if (this.fields_dict[fieldname] && this.fields_dict[fieldname].df) {
			const prev_fieldobj = this.fields_dict[fieldname];
			const fieldobj = this.init_field(df, prev_fieldobj.parent, render);
			prev_fieldobj.$wrapper.replaceWith(fieldobj.$wrapper);
			const idx = this.fields_list.findIndex(e => e == prev_fieldobj);
			this.fields_list.splice(idx, 1, fieldobj);
			this.fields_dict[fieldname] = fieldobj;
			for (const section of this.sections) { section.replace_field(fieldname, fieldobj); }
			prev_fieldobj.tab?.replace_field(fieldobj);
			this.refresh_fields([df]);
		}
	}

	make_field(df: any, colspan?: number, render?: boolean) {
		!this.section && this.make_section();
		!this.column && this.make_column();

		const parent = this.column.wrapper.get(0);
		const fieldobj = this.init_field(df, parent, render);
		this.fields_list.push(fieldobj);
		this.fields_dict[df.fieldname] = fieldobj;

		this.section!.add_field(fieldobj);
		this.column!.add_field(fieldobj);

		if (this.current_tab) {
			this.current_tab.add_field(fieldobj);
		}
	}

	init_field(df: any, parent: JQuery<HTMLElement>, render = false): frappe.ui.form.Control {
		const fieldobj = frappe.ui.form.make_control({
			df,
			doctype: this.doctype,
			parent: parent,
			frm: this.frm,
			render_input: render,
			doc: this.doc,
			layout: this,
		});

		fieldobj.layout = this;
		return fieldobj;
	}

	/** 添加分页标签 div.form-page.page-break */
	make_page_break() {
		this.page = $('<div class="form-page page-break"></div>').appendTo(this.wrapper);
	}

	make_page(df) {
		// eslint-disable-line no-unused-vars
		let me = this;
		let head = $(`
			<div class="form-clickable-section text-center">
				<a class="btn-fold h6 text-muted">
					${__('Show more details')}
				</a>
			</div>
		`).appendTo(this.wrapper);

		this.page = $('<div class="form-page second-page hide"></div>').appendTo(this.wrapper);

		this.fold_btn = head.find('.btn-fold').on('click', function () {
			let page = $(this).parent().next();
			if (page.hasClass('hide')) {
				$(this).removeClass('btn-fold').html(__('Hide details'));
				page.removeClass('hide');
				frappe.utils.scroll_to($(this), true, 30);
				me.folded = false;
			} else {
				$(this).addClass('btn-fold').html(__('Show more details'));
				page.addClass('hide');
				me.folded = true;
			}
		});

		this.section = null;
		this.folded = true;
	}

	unfold() {
		this.fold_btn.trigger('click');
	}

	/**
	 * 创建新的页面 section
	 * section 创建后，会置空 column
	 * 创建过程中，如果存在 tab ，则会创建到 tab 中，否则，会创建到 page 中
	 */
	make_section(df: {
		fieldname?: string
		fieldtype?: string
	} = {}) {
		this.section_count++;
		if (!df.fieldname) {
			df.fieldname = `__section_${this.section_count}`;
			df.fieldtype = 'Section Break';
		}

		this.section = new Section(
			this.current_tab?.wrapper || this.page,
			df,
			this.card_layout,
			this,
		);
		this.sections.push(this.section);
		this.sections_dict[df.fieldname] = this.section;

		// append to layout fields
		if (df) {
			this.fields_dict[df.fieldname] = this.section;
			this.fields_list.push(this.section);
		}

		this.column = null;
	}

	/**
	 * 创建分列
	 * 列会创建到 section 中
	 */
	make_column(df: {
		fieldname?: string
		fieldtype?: string
	} = {}) {
		this.column_count++;
		if (!df.fieldname) {
			df.fieldname = `__column_${this.section_count}`;
			df.fieldtype = 'Column Break';
		}

		this.column = new Column(this.section!, df);
		if (df && df.fieldname) {
			this.fields_list.push(this.column);
		}
	}
	/**
	 * 创建新的 tab 页面
	 * tab 创建后，会自动创建新的 section
	 */
	make_tab(df) {
		this.section = null;
		let tab = new Tab(this, df, this.frm, this.tab_link_container, this.tabs_content);
		this.current_tab = tab;
		this.make_section({ fieldtype: 'Section Break' });
		this.tabs.push(tab);
		return tab;
	}

	refresh(doc) {
		if (doc) { this.doc = doc; }

		if (this.frm) {
			this.wrapper.find('.empty-form-alert').remove();
		}

		// NOTE this might seem redundant at first, but it needs to be executed when frm.refresh_fields is called
		this.attach_doc_and_docfields(true);

		if (this.frm && this.frm.wrapper) {
			$(this.frm.wrapper).trigger('refresh-fields');
		}

		// dependent fields
		this.refresh_dependency();

		// refresh sections
		this.refresh_sections();

		if (this.frm) {
			// collapse sections
			this.refresh_section_collapse();
		}

		if (document.activeElement) {
			if (document.activeElement.tagName == 'INPUT' && this.is_numeric_field_active()) {
				document.activeElement.select();
			}
		}
	}

	is_numeric_field_active() {
		const control = $(document.activeElement).closest('.frappe-control');
		const { fieldtype } = control.data() || {};
		return frappe.model.numeric_fieldtypes.includes(fieldtype);
	}

	refresh_sections() {
		// hide invisible sections
		this.wrapper.find('.form-section:not(.hide-control)').each(function () {
			const section = $(this).removeClass('empty-section visible-section');
			if (section.find('.frappe-control:not(.hide-control)').length) {
				section.addClass('visible-section');
			} else {
				// nothing visible, hide the section
				section.addClass('empty-section');
			}
		});

		// refresh tabs
		this.is_tabbed_layout() && this.refresh_tabs();
	}

	refresh_tabs() {
		for (let tab of this.tabs) {
			tab.refresh();
		}

		const visible_tabs = this.tabs.filter(tab => !tab.hidden);
		if (visible_tabs && visible_tabs.length == 1) {
			visible_tabs[0].tab_link.toggleClass('hide show');
		}
		this.set_tab_as_active();
	}

	set_tab_as_active() {
		let frm_active_tab = this?.frm.get_active_tab?.();
		if (frm_active_tab) {
			frm_active_tab.set_active();
		} else if (this.tabs.length) {
			// set first tab as active when opening for first time, or new doc
			let first_visible_tab = this.tabs.find(tab => !tab.is_hidden());
			first_visible_tab && first_visible_tab.set_active();
		}
	}

	refresh_fields(fields) {
		let fieldnames = fields.map(field => {
			if (field.fieldname) { return field.fieldname; }
		});

		this.fields_list.map(fieldobj => {
			if (fieldnames.includes(fieldobj.df.fieldname)) {
				fieldobj.refresh();
				if (fieldobj.df.default) {
					fieldobj.set_input(fieldobj.df.default);
				}
			}
		});
	}

	add_fields(fields) {
		this.render(fields);
		this.refresh_fields(fields);
	}

	refresh_section_collapse() {
		if (!(this.sections && this.sections.length)) { return; }

		for (let i = 0; i < this.sections.length; i++) {
			let section = this.sections[i];
			let { df } = section;
			if (df && df.collapsible) {
				let collapse = true;

				if (df.collapsible_depends_on) {
					collapse = !this.evaluate_depends_on_value(df.collapsible_depends_on);
				}

				if (collapse && section.has_missing_mandatory()) {
					collapse = false;
				}

				section.collapse(collapse);
			}
		}
	}

	attach_doc_and_docfields(refresh) {
		let me = this;
		for (let i = 0, l = this.fields_list.length; i < l; i++) {
			let fieldobj = this.fields_list[i];
			if (me.doc) {
				fieldobj.doc = me.doc;
				fieldobj.doctype = me.doc.doctype;
				fieldobj.docname = me.doc.name;
				fieldobj.df =
					frappe.meta.get_docfield(me.doc.doctype, fieldobj.df.fieldname, me.doc.name) ||
					fieldobj.df;
			}
			refresh && fieldobj.df && fieldobj.refresh && fieldobj.refresh();
		}
	}

	refresh_section_count() {
		this.wrapper.find('.section-count-label:visible').each(function (i) {
			$(this).html(i + 1);
		});
	}

	setup_events() {

		let last_scroll = 0;
		const {formTabsList} = this;
		let {tabsContent} = this;

		const eventListener = frappe.utils.throttle(() => {
			let current_scroll = document.documentElement.scrollTop;
			if (current_scroll > 0 && last_scroll <= current_scroll) {
				formTabsList.classList.remove('form-tabs-sticky-down');
				formTabsList.classList.add('form-tabs-sticky-up');
			} else {
				formTabsList.classList.remove('form-tabs-sticky-up');
				formTabsList.classList.add('form-tabs-sticky-down');
			}
			last_scroll = current_scroll;
		}, 500);
		window.addEventListener('scroll', eventListener);
		// TODO: 增加移除逻辑


		this.tab_link_container.off('click').on('click', '.nav-link', e => {
			e.preventDefault();
			e.stopImmediatePropagation();
			const el = e.currentTarget as HTMLAnchorElement;
			$(el).tab('show');
			// 记住当前显示的 tab
			const { fieldname } = el.dataset;
			if (fieldname) {
				this.currentTab.value = fieldname;
			}
			if (tabsContent.getBoundingClientRect().top < 100) {
				tabsContent.scrollIntoView();
				setTimeout(() => {
					$('.page-head').css('top', '-15px');
					formTabsList.classList.remove('form-tabs-sticky-down');
					formTabsList.classList.add('form-tabs-sticky-up');
				}, 3);
			}
		});
	}

	setup_tab_events() {
		this.wrapper.on('keydown', ev => {
			if (ev.which == 9) {
				let current = $(ev.target);
				let doctype = current.attr('data-doctype');
				let fieldname = current.attr('data-fieldname');
				if (doctype) {
					return this.handle_tab(doctype, fieldname, ev.shiftKey);
				}
			}
		});
	}

	handle_tab(doctype: string, fieldname: string, shift: boolean) {
		let grid_row = null,
			prev = null,
			fields = this.fields_list,
			focused = false;

		// in grid
		if (doctype != this.doctype) {
			grid_row = this.get_open_grid_row();
			if (!grid_row || !grid_row.layout) {
				return;
			}
			fields = grid_row.layout.fields_list;
		}

		for (let i = 0, len = fields.length; i < len; i++) {
			if (fields[i].df.fieldname == fieldname) {
				if (shift) {
					if (prev) {
						this.set_focus(prev);
					} else {
						$(this.primary_button).focus();
					}
					break;
				}
				if (i < len - 1) {
					focused = this.focus_on_next_field(i, fields);
				}

				if (focused) {
					break;
				}
			}
			if (this.is_visible(fields[i])) { prev = fields[i]; }
		}

		if (!focused) {
			// last field in this group
			if (grid_row) {
				// in grid
				if (grid_row.doc.idx == grid_row.grid.grid_rows.length) {
					// last row, close it and find next field
					grid_row.toggle_view(false, function () {
						grid_row.grid.frm.layout.handle_tab(
							grid_row.grid.df.parent,
							grid_row.grid.df.fieldname,
						);
					});
				} else {
					// next row
					grid_row.grid.grid_rows[grid_row.doc.idx].toggle_view(true);
				}
			} else if (!shift) {
				// End of tab navigation
				$(this.primary_button).focus();
			}
		}

		return false;
	}

	focus_on_next_field(start_idx, fields) {
		// loop to find next eligible fields
		for (let i = start_idx + 1, len = fields.length; i < len; i++) {
			let field = fields[i];
			if (this.is_visible(field)) {
				if (field.df.fieldtype === 'Table') {
					// open table grid
					if (!(field.grid.grid_rows && field.grid.grid_rows.length)) {
						// empty grid, add a new row
						field.grid.add_new_row();
					}
					// show grid row (if exists)
					field.grid.grid_rows[0].show_form();
					return true;
				} else if (!in_list(frappe.model.no_value_type, field.df.fieldtype)) {
					this.set_focus(field);
					return true;
				}
			}
		}
	}

	is_visible(field) {
		return (
			field.disp_status === 'Write' && field.df && 'hidden' in field.df && !field.df.hidden
		);
	}

	set_focus(field) {
		if (field.tab) {
			field.tab.set_active();
		}
		// next is table, show the table
		if (field.df.fieldtype == 'Table') {
			if (field.grid.grid_rows.length) {
				field.grid.grid_rows[0].toggle_view(true);
			} else {
				field.grid.add_new_row(1);
			}
		} else if (field.editor) {
			field.editor.set_focus();
		} else if (field.$input) {
			field.$input.focus();
		}
	}

	get_open_grid_row() {
		return $('.grid-row-open').data('grid_row');
	}

	refresh_dependency() {
		/**
			Resolve "depends_on" and show / hide accordingly
			build dependants' dictionary
		*/

		let has_dep = false;

		const fields = this.fields_list.concat(this.tabs);

		for (let fkey in fields) {
			let f = fields[fkey];
			if (f.df.depends_on || f.df.mandatory_depends_on || f.df.read_only_depends_on) {
				has_dep = true;
				break;
			}
		}

		if (!has_dep) { return; }

		// show / hide based on values
		for (let i = fields.length - 1; i >= 0; i--) {
			let f = fields[i];
			f.guardian_has_value = true;
			if (f.df.depends_on) {
				// evaluate guardian

				f.guardian_has_value = this.evaluate_depends_on_value(f.df.depends_on);

				// show / hide
				if (f.guardian_has_value) {
					if (f.df.hidden_due_to_dependency) {
						f.df.hidden_due_to_dependency = false;
						f.refresh();
					}
				} else if (!f.df.hidden_due_to_dependency) {
					f.df.hidden_due_to_dependency = true;
					f.refresh();
				}
			}

			if (f.df.mandatory_depends_on) {
				this.set_dependant_property(f.df.mandatory_depends_on, f.df.fieldname, 'reqd');
			}

			if (f.df.read_only_depends_on) {
				this.set_dependant_property(
					f.df.read_only_depends_on,
					f.df.fieldname,
					'read_only',
				);
			}
		}

		this.refresh_section_count();
	}

	set_dependant_property(condition, fieldname, property) {
		let set_property = this.evaluate_depends_on_value(condition);
		let value = set_property ? 1 : 0;
		let form_obj;

		if (this.frm) {
			form_obj = this.frm;
		} else if (this.is_dialog || this.doctype === 'Web Form') {
			form_obj = this;
		}
		if (form_obj) {
			if (this.doc && this.doc.parent && this.doc.parentfield) {
				form_obj.setting_dependency = true;
				form_obj.set_df_property(
					this.doc.parentfield,
					property,
					value,
					this.doc.parent,
					fieldname,
					this.doc.name,
				);
				form_obj.setting_dependency = false;
				// refresh child fields
				this.fields_dict[fieldname] && this.fields_dict[fieldname].refresh();
			} else {
				form_obj.set_df_property(fieldname, property, value);
			}
		}
	}

	evaluate_depends_on_value(expression) {
		let out = null;
		let {doc} = this;

		if (!doc && this.get_values) {
			doc = this.get_values(true);
		}

		if (!doc) {
			return;
		}

		let parent = this.frm ? this.frm.doc : this.doc || null;

		if (typeof expression === 'boolean') {
			out = expression;
		} else if (typeof expression === 'function') {
			out = expression(doc);
		} else if (expression.substr(0, 5) == 'eval:') {
			try {
				out = frappe.utils.eval(expression.substr(5), { doc, parent });
				if (parent && parent.istable && expression.includes('is_submittable')) {
					out = true;
				}
			} catch (e) {
				frappe.throw(__('Invalid "depends_on" expression'));
			}
		} else if (expression.substr(0, 3) == 'fn:' && this.frm) {
			out = this.frm.script_manager.trigger(
				expression.substr(3),
				this.doctype,
				this.docname,
			);
		} else {
			let value = doc[expression];
			if ($.isArray(value)) {
				out = Boolean(value.length);
			} else {
				out = Boolean(value);
			}
		}

		return out;
	}
}
interface Layout {

	doc: any;
	parent: JQuery;
	doctype: string;
	doctype_layout: unknown;
	frm: Form;

	wrapper: JQuery;
	message: JQuery;
	page: JQuery;
	fields: any[];
	tab_link_container: JQuery;
	tabs_content: JQuery;
	current_tab?: Tab
	section?: Section | null
	column?: Column | null
	active_tab?: Tab;
}
export default Layout;
