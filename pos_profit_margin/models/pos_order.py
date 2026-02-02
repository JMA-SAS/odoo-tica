from odoo import models, fields, api
import logging

class PosOrder(models.Model):
    _inherit = 'pos.order'

    cost_total = fields.Monetary(
        string='Costo Total',
        compute='_compute_cost_total',
        store=True
    )

    profit_total = fields.Monetary(
        string='Utilidad',
        compute='_compute_profit_total',
        store=True
    )

    @api.depends('lines.qty', 'lines.product_id.standard_price')
    def _compute_cost_total(self):
        for order in self:
            cost = 0.0
            for line in order.lines:
                cost += (line.product_id.standard_price or 0.0) * line.qty
            order.cost_total = cost

    @api.depends('amount_total', 'cost_total')
    def _compute_profit_total(self):
        for order in self:
            order.profit_total = order.amount_total - order.cost_total
