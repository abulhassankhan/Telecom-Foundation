from odoo import fields, api, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    comparative_line_ids = fields.One2many(
        'purchase.comparative.line', 'comparative_id', string="Vendors"
    )

    @api.constrains('comparative_line_ids', 'comparative_line_ids.vendor_id')
    def same_vendor(self):
        vendor_ids = []
        for rec in self.comparative_line_ids:
            vendor_ids.append(rec.vendor_id.id)
            print(vendor_ids)
        if len(vendor_ids) != len(set(vendor_ids)):
            raise UserError("You cannot select the same vendor multiple times.")


    @api.constrains('comparative_line_ids')
    def _check_vendor_count(self):
        for order in self:
            if len(order.comparative_line_ids) != 3:
                raise UserError("You must add exactly 3 vendors.")

    def button_confirm(self):
        for order in self:
            selected_lines = order.comparative_line_ids.filtered(lambda l: l.is_selected)
            if not selected_lines:
                raise UserError("Please select at least one vendor to confirm the purchase order.")

            purchase_orders = {}

            for line in selected_lines:
                if line.vendor_id.id not in purchase_orders:
                    new_po = self.env['purchase.order'].create({
                        'partner_id': line.vendor_id.id,
                        'order_line': []
                    })
                    purchase_orders[line.vendor_id.id] = new_po

                self.env['purchase.order.line'].create({
                    'order_id': purchase_orders[line.vendor_id.id].id,
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'price_unit': line.price_unit,
                })

                line.po_id = purchase_orders[line.vendor_id.id].id

        return super(PurchaseOrder, self).button_confirm()



class PurchaseComparative(models.Model):
    _name = 'purchase.comparative.line'

    comparative_id = fields.Many2one(comodel_name='purchase.order', string="Comparative")
    vendor_id = fields.Many2one(comodel_name='res.partner', string="Vendor", domain=[('supplier_rank', '>', 0)])
    product_id = fields.Many2one(comodel_name='product.product', string="Product")
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    price_unit = fields.Float(string="Unit Price")
    is_selected = fields.Boolean(string="Select for PO")
    po_id = fields.Many2one(comodel_name='purchase.order', string="Generated PO", readonly=True)

    # _sql_constraints = [
    #     ('vendor_id_uniq', 'unique (vendor_id)',
    #      'The name of the vendor must be unique!')
    # ]