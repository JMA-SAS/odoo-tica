# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    name = fields.Char(readonly=False, copy=False, default='/')
    
    @api.onchange('posted_before', 'state', 'journal_id', 'date')
    def _onchange_journal_date(self):
        return
    
    def _get_payment_sequence_code(self):
        """Método para obtener el código de secuencia según el tipo de pago"""
        self.ensure_one()
        
        if self.payment_type == 'transfer':
            return 'account.payment.transfer'
        
        if self.partner_type == 'customer':
            if self.payment_type == 'inbound':
                return 'account.payment.customer.invoice'
            elif self.payment_type == 'outbound':
                return 'account.payment.customer.refund'
        
        if self.partner_type == 'supplier':
            if self.payment_type == 'inbound':
                return 'account.payment.supplier.refund'
            elif self.payment_type == 'outbound':
                return 'account.payment.supplier.invoice'
        
        return False
    
    def _set_payment_name(self):
        """Método para asignar el nombre/consecutivo al pago"""
        for rec in self:
            if rec.name == '/' or not rec.name or rec.name == 'Draft Payment':
                sequence_code = rec._get_payment_sequence_code()
                if sequence_code:
                    sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
                    if sequence:
                        rec.name = sequence.with_context(ir_sequence_date=rec.date).next_by_id()
                    else:
                        # Si no existe la secuencia, usar la secuencia del diario como fallback
                        if rec.journal_id and rec.journal_id.sequence_id:
                            rec.name = rec.journal_id.sequence_id.with_context(ir_sequence_date=rec.date).next_by_id()
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para asignar secuencia al crear"""
        payments = super().create(vals_list)
        for payment in payments:
            payment._set_payment_name()
        return payments
    
    def action_post(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))
            
            if any(inv.state != 'posted' for inv in rec.reconciled_invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            
            # Asignar secuencia si no la tiene
            rec._set_payment_name()
        
        res = super(AccountPayment, self).action_post()
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    @api.model
    def default_get(self, fields_list):
        """Override default_get para asegurar configuración correcta"""
        res = super().default_get(fields_list)
        
        # Asegurar que no hay un nombre predefinido que interfiera
        if 'payment_method_line_id' in res:
            # Limpiar cualquier nombre que pueda estar interfiriendo
            res.pop('name', None)
            
        return res
    
    def _create_payment_vals_from_wizard(self, batch_result):
        """Override para asegurar que el name se asigne correctamente"""
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        # Forzar que el name sea '/' para que se genere la secuencia
        payment_vals['name'] = '/'
            
        return payment_vals
    
    def _create_payment_vals_from_batch(self, batch_result):
        """Override adicional para versiones que usen este método"""
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        
        # Forzar que el name sea '/' para que se genere la secuencia
        payment_vals['name'] = '/'
            
        return payment_vals
    
    def _create_payments(self):
        """Override del método principal que crea los pagos"""
        # Llamar al método padre que crea los pagos
        payments = super()._create_payments()
        
        # Después de crear los pagos, asegurar que tengan la secuencia correcta
        for payment in payments:
            if payment.name in ('/', '', 'Draft Payment') or not payment.name:
                payment._set_payment_name()
        
        return payments


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def action_register_payment(self):
        """Override para asegurar que el contexto sea correcto"""
        res = super().action_register_payment()
        
        # Asegurar que el contexto no tenga valores que interfieran
        if 'context' in res:
            res['context'].pop('default_name', None)
            
        return res