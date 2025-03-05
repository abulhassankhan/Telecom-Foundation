from odoo import models,fields,api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_coa_installed = fields.Boolean('Is Coa Installed')