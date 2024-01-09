// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

import type Form from './Form';

class Footer {
	constructor(opts: {
		frm: Form;
		parent: JQuery;
	}) {
		$.extend(this, opts);
		this.make();
		this.make_comment_box();
		this.make_timeline();
		// render-complete
		$(this.frm.wrapper).on('render_complete', () => {
			this.refresh();
		});
	}
	make() {
		const wrapper = $(`<div class="form-footer">
	<div class="after-save">
		<div class="comment-box"></div>
		<div class="timeline"></div>
	</div>
</div>`).appendTo(this.parent);
		const toTop = document.createElement('button');
		toTop.className = 'scroll-to-top btn btn-default icon-btn';
		toTop.innerHTML = '<svg class="icon icon-xs"><use href="#icon-up-line"></use></svg>';
		toTop.addEventListener('click', () => {
			let e: HTMLElement | null = toTop;
			// eslint-disable-next-line no-cond-assign
			while (e = e.parentElement) {
				if (e.scrollTop) {
					break;
				}
			}
			if (e) {
				frappe.utils.scroll_to(0, true, 0, $(e));
			}
		});
		wrapper.append(toTop);
		this.wrapper = wrapper;
		wrapper.find('.btn-save').on('click', () => {
			this.frm.save('Save', null, this);
		});
	}
	make_comment_box() {
		frappe.ui.form.Footer.prototype.make_comment_box.call(this);

	}
	make_timeline() {
		frappe.ui.form.Footer.prototype.make_timeline.call(this);
	}
	refresh() {
		frappe.ui.form.Footer.prototype.refresh.call(this);
	}
}
interface Footer {
	frm: Form;
	parent: JQuery;
	wrapper: JQuery;
}
export default Footer;
