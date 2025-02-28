# -*- coding: utf-8 -*-
# Copyright 2020 OpenG2P (https://openg2p.org)
# @author: Salton Massally <saltonmassally@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "OpenG2P",
    "summary": "Comprehensive suite providing list management and payment routing for large scare payment programs",
    "author": "OpenG2P",
    "website": "https://openg2p.org",
    "category": "OpenG2P",
    "version": "0.1",
    "depends": [
        "base",
        "base_setup",
        "base_rest",
        "phone_validation",
        "mail",
        "base_search_fuzzy",
        "resource",
        "web",
        "queue_job",
        "mass_editing",
        "base_import_async",
        "component",
        "crnd_web_button_box_full_width",
        "storage_backend",
        "storage_backend_s3",
        "web_advanced_search",
        "web_m2x_options",
        "web_ir_actions_act_window_message",
        "web_listview_range_select",
        "remove_odoo_enterprise",
        "disable_odoo_online",
        "report_xlsx",
        "report_xlsx_helper",
        "base_currency_iso_4217",
        "module_auto_update",
        "web_notify",
        # "field_image_preview", ## XML parse issue in bitnami odoo image
        # "generic_mixin", ## Both modules causing key error while installing
        # "base_export_async",
    ],
    "data": [
        "data/base.xml",
        "views/menu.xml",
        "security/openg2p_security.xml",
        "security/ir.model.access.csv",
        "data/openg2p_data.xml",
        "wizard/beneficiary_to_batch_view.xml",
        "views/openg2p_beneficiary.xml",
        "views/openg2p_location.xml",
        "views/openg2p_templates.xml",
        "views/openg2p_beneficiary_category.xml",
        "views/openg2p_beneficiary_id_category_view.xml",
        "views/openg2p_beneficiary_id_number_view.xml",
        "views/res_config_settings_views.xml",
        "views/openg2p_beneficiary_category.xml",
        "views/openg2p_beneficiary_exception.xml",
        "views/openg2p_beneficiary_exception_type.xml",
        "views/openg2p_registration_stage.xml",
        "views/res_country_state.xml",
        "views/res_users.xml",
        "data/cron.xml",
    ],
    "demo": ["data/openg2p_demo.xml"],
    # "post_init_hook": "post_init",
    "installable": True,
    "application": True,
    "auto_install": False,
}
