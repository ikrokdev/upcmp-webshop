# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe

no_cache = 1

def insertImage(item):
	item["website_image"] = frappe.get_doc("Website Item", item.website_item).website_image
	return item

def get_context(context):
	homepage = frappe.get_cached_doc("Homepage")

	for item in homepage.products:
		route = frappe.db.get_value("Website Item", {"item_code": item.item_code}, "route")
		if route:
			item.route = "/" + route

	homepage.title = homepage.title or homepage.company
	context.title = homepage.title
	context.homepage = homepage

	if homepage.hero_section_based_on == "Homepage Section" and homepage.hero_section:
		homepage.hero_section_doc = frappe.get_cached_doc("Homepage Section", homepage.hero_section)

	if homepage.slideshow:
		doc = frappe.get_cached_doc("Website Slideshow", homepage.slideshow)
		context.slideshow = homepage.slideshow
		context.slideshow_header = doc.header
		context.slides = doc.slideshow_items

	context.blogs = frappe.get_all(
		"Blog Post",
		fields=["title", "blogger", "blog_intro", "route", "published_on", "meta_image"],
		filters={"published": 1},
		order_by="modified desc",
		limit=6,
	)

	reviews = frappe.get_all(
		"Item Review",
		fields=["website_item", "user", "item", "review_title", "rating", "comment", "customer"],
		# filters={"published": 1},
		order_by="modified desc",
		
		limit=6,
	)
	context.reviews = list(map(insertImage, reviews))

	product_bundles = frappe.get_all(
		"Product Bundle",
		fields=["new_item_code", "new_item_code"],
		order_by="modified desc",
		limit=4,
	)

	validate_bundles = []
	# Loop through each Product Bundle to fetch child table items
	for bundle in product_bundles:
		# Fetch child table records
		# bundle["items"] = frappe.get_list("Product Bundle Item", filters={"parent": bundle.name}, fields=["*"])
		bundle["parent_item"] = frappe.get_all("Item", filters={"item_code": bundle.new_item_code}, fields=["item_code", "item_name", "image"])[0]
		item_price = frappe.get_all("Item Price", filters={'price_list': 'Prom Selling', 'item_code': bundle["parent_item"]["item_code"]}, fields=["price_list_rate"])
		website_item_exists = frappe.db.exists("Website Item", {"item_code": bundle.new_item_code})

		if website_item_exists:
			website_item_route = frappe.get_value("Website Item", website_item_exists, ["route"])
		else:
			website_item_route = None

		if bundle["parent_item"].get("image") and item_price:
			bundle["route"] = website_item_route
			print(website_item_route)
			bundle["price"]  = item_price[0]['price_list_rate']
			validate_bundles.append(bundle)
	
	context.bundles = validate_bundles if validate_bundles else []

	# filter out homepage section which is used as hero section
	homepage_hero_section = (
		homepage.hero_section_based_on == "Homepage Section" and homepage.hero_section
	)
	homepage_sections = frappe.get_all(
		"Homepage Section",
		filters=[["name", "!=", homepage_hero_section]] if homepage_hero_section else None,
		order_by="section_order asc",
	)
	context.homepage_sections = [
		frappe.get_cached_doc("Homepage Section", name) for name in homepage_sections
	]

	context.metatags = context.metatags or frappe._dict({})
	context.metatags.image = homepage.hero_image or None
	context.metatags.description = homepage.description or None

	context.explore_link = "/all-products"
