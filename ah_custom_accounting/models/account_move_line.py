from odoo import fields,api,models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    name = fields.Char(
        string='Payee Name',
        compute='_compute_name', store=True, readonly=False, precompute=True,
        tracking=True,
    )