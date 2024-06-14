# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

no_cache = 1

from webshop.webshop.shopping_cart.cart import get_cart_quotation
from frappe.translate import get_all_translations
import frappe


def get_context(context):
	context.body_class = "product-page"
	context.update(get_cart_quotation())
	language = get_all_translations(frappe.local.lang)
	context.translated_messages = language
