from odoo import models


class CmsAbstractReport(models.AbstractModel):
    _name = "report.cms_account_reports.abstract_report"
    _description = "Abstract Report"

    def _get_domain(self, data):
        domain = [
            ("state", "=", "posted"),
            # (
            #     "move_type",
            #     "in",
            #     ["out_invoice", "out_refund", "in_invoice", "in_refund"],
            # ),
            ("amount_residual_signed", "!=", 0),
            ("date", ">=", data["start_date"]),
            ("date", "<=", data["end_date"]),
        ]
        if data["partner_ids"]:
            domain += [("partner_id", "in", data["partner_ids"])]
        if data["journal_ids"]:
            domain += [("journal_id", "in", data["journal_ids"])]
        if data["physician_ids"]:
            domain += [("physician_id", "in", data["physician_ids"])]
        if data["patient_ids"]:
            domain += [("patient_id", "in", data["patient_ids"])]
        return domain

    def get_source_orders_purchase(self, move):
        return move.line_ids.purchase_line_id.order_id

    def get_source_orders_sale(self, move):
        return move.line_ids.sale_line_ids.order_id

    def _get_ref(self, move, get_source_orders_fn):
        source_orders = get_source_orders_fn(move)
        move_ref = move.ref if move.ref is not None else ""
        if (
            source_orders is None
            or source_orders is False
            or not source_orders.exists()
        ):
            return move_ref
        if not isinstance(source_orders, list):
            orders_list = source_orders
        else:
            orders_list = source_orders
        orders_text = ", ".join(str(order.name) for order in orders_list if order.name)
        return f"{move_ref}, {orders_text}" if move_ref else orders_text
