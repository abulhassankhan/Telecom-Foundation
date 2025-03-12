from odoo.exceptions import UserError
from odoo import models,fields,api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', ' RFQ Sent'),
        ('comparative', 'Comparative'),
        ('email', 'Email'),
        ('received', 'Received'),
        ('approval_1', 'Approval 1'),
        ('approval_2', 'Approval 2'),
        ('purchase', 'Purchase Order'),
        ('cancel', 'Cancel'),
        ('done','Lock'),
    ], default='draft', tracking=True, copy=False)

    comparative_line_ids = fields.One2many(
        'purchase.comparative.line', 'comparative_id', string="Vendors"
    )

    received_line_ids = fields.One2many(
        'received.comparative.line', 'received_id', string="Received"
    )

    @api.model_create_multi
    def create(self, vals):
        order = super(PurchaseOrder, self).create(vals)

        if order.partner_id:
            self._update_comparative_lines(order)

        return order

    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)

        if 'partner_id' in vals:
            for order in self:
                self._update_comparative_lines(order)

        return result

    def _update_comparative_lines(self, order):
        order.comparative_line_ids.unlink()

        if order.partner_id:
            self.env['purchase.comparative.line'].create({
                'comparative_id': order.id,
                'vendor_id': order.partner_id.id,
                'product_id': False,
                # 'quantity': 1.0,
            })

    def action_approval_1(self):
        self.write({'state': 'approval_1'})

    def action_approval_2(self):
        self.write({'state': 'approval_2'})

    def button_confirm(self):
        for order in self:
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            if order._approval_allowed():
                order.button_approve()
                order.write({'state': 'purchase'})
            else:
                order.write({'state': 'purchase'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])

            # for line in order.order_line:
            #     self.env['stock.quality.check'].create({
            #         'product_id': line.product_id.id,
            #         'quality_check': 'default',
            #         'stock_picking_id': order.picking_ids.id if order.picking_ids else False
            #     })
        return True

    def action_comparative(self):
        for order in self:
            if len(order.comparative_line_ids) != 3:
                raise UserError("You must add exactly 3 vendors.")

            vendor_ids = [line.vendor_id.id for line in order.comparative_line_ids]
            if len(vendor_ids) != len(set(vendor_ids)):
                raise UserError("You cannot select the same vendor multiple times.")

            selected_lines = order.comparative_line_ids.filtered(lambda l: l.is_selected)
            if not selected_lines:
                raise UserError("Please select at least one vendor to proceed.")

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

            order.state = 'comparative'

    def action_received(self):
        for order in self:
            selected_lines = order.comparative_line_ids.filtered(lambda l: l.is_selected and l.po_id)

            if not selected_lines:
                raise UserError("No selected vendors with generated POs found.")

            received_lines = [(0, 0, {
                'vendor_id': line.vendor_id.id,
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                # 'price_unit': line.price_unit,
                'is_selected': line.is_selected,
                'po_id': line.po_id.id,
            }) for line in selected_lines]

            order.write({'received_line_ids': received_lines})

            order.state = 'received'


class ReceivedComparative(models.Model):
    _name = 'received.comparative.line'

    received_id = fields.Many2one(comodel_name='purchase.order', string="Comparative")
    vendor_id = fields.Many2one(comodel_name='res.partner', string="Vendor", domain=[('supplier_rank', '>', 0)])
    product_id = fields.Many2one(comodel_name='product.product', string="Product")
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    price_unit = fields.Float(string="Unit Price",)
    is_selected = fields.Boolean(string="Select for PO")
    po_id = fields.Many2one(comodel_name='purchase.order', string="Generated PO", readonly=True)


class PurchaseComparative(models.Model):
    _name = 'purchase.comparative.line'

    comparative_id = fields.Many2one(comodel_name='purchase.order', string="Comparative")
    vendor_id = fields.Many2one(comodel_name='res.partner', string="Vendor", domain=[('supplier_rank', '>', 0)])
    product_id = fields.Many2one(comodel_name='product.product', string="Product", compute='_compute_product_quantity')
    quantity = fields.Float(string="Quantity", default=1.0, compute='_compute_product_quantity')
    price_unit = fields.Float(string="Unit Price")
    is_selected = fields.Boolean(string="Select for PO")
    po_id = fields.Many2one(comodel_name='purchase.order', string="Generated PO", readonly=True)

    @api.depends('comparative_id.order_line')
    def _compute_product_quantity(self):
        for record in self:
            if record.comparative_id and record.comparative_id.order_line:
                first_line = record.comparative_id.order_line[0]
                record.product_id = first_line.product_id.id
                record.quantity = first_line.product_qty
                # record.price_unit = first_line.price_unit
            else:
                record.product_id = False
                record.quantity = 1

    # _sql_constraints = [
    #     ('vendor_id_uniq', 'unique (vendor_id)',
    #      'The name of the vendor must be unique!')
    # ]
