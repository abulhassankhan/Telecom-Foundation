from odoo import api,fields,models

class ProjectDefaultUsers(models.Model):
    _name = 'project.default.users'

    user_id = fields.Many2one('res.users', 'User')
