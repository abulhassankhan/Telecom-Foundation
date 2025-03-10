from odoo import fields, api, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(PurchaseOrder, self).create(vals_list)
        rfq_code = self.env['ir.sequence'].next_by_code('request.quotation') or '/'
        res.write({'name': rfq_code})
        return res


    def button_confirm(self):
        po_code = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
        self.write({'name': po_code})
        return super(PurchaseOrder, self).button_confirm()


