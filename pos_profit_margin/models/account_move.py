from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_profit_total = fields.Monetary(
        string='Utilidad POS',
        compute='_compute_pos_profit_total',
        store=True
    )

    @api.depends('line_ids')
    def _compute_pos_profit_total(self):
        for move in self:
            profit = 0.0
            pos_orders = self.env['pos.order'].search([('account_move', '=', move.id)])
            profit = sum(pos_orders.mapped('profit_total'))
            move.pos_profit_total = profit
