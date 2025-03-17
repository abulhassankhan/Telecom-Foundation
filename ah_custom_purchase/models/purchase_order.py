from odoo import fields, api, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[
        ('approval_1', 'Approval 1'),
        ('approval_2', 'Approval 2'),
        ('approved', 'Approved'),
        ('cancel',)
    ])

    def action_approval_1(self):
        self.write({'state': 'approval_1'})

    def action_approval_2(self):
        self.write({'state': 'approval_2'})

    def action_approved(self):
        self.write({'state': 'approved'})

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


    @api.depends('state', 'order_line.qty_to_invoice')
    def _get_invoiced(self):
        print('_get_invoiced')
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('purchase', 'done', 'approved'):
                order.invoice_status = 'no'
                continue

            if any(
                    not float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.order_line.filtered(lambda l: not l.display_type)
            ):
                order.invoice_status = 'to invoice'
            elif (
                    all(
                        float_is_zero(line.qty_to_invoice, precision_digits=precision)
                        for line in order.order_line.filtered(lambda l: not l.display_type)
                    )
                    and order.invoice_ids
            ):
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'qty_received', 'product_uom_qty', 'order_id.state')
    def _compute_qty_invoiced(self):
        print('_compute_qty_invoiced')
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line._get_invoice_lines():
                if inv_line.move_id.state not in ['cancel'] or inv_line.move_id.payment_state == 'invoicing_legacy':
                    if inv_line.move_id.move_type == 'in_invoice':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
                    elif inv_line.move_id.move_type == 'in_refund':
                        qty -= inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.qty_invoiced = qty

            # compute qty_to_invoice
            if line.order_id.state in ['purchase', 'done', 'approved']:
                if line.product_id.purchase_method == 'purchase':
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0


