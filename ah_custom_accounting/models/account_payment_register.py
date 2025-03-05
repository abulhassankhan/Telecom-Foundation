from odoo import fields,api,models

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string="Payee",
        readonly=False,
        store=True,
        compute='_compute_partner_bank_id',
        domain="[('id', 'in', available_partner_bank_ids)]",
    )