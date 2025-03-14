# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    # --------------Allownces-----------------

    other_allow = fields.Float()
    other_allow_type = fields.Selection([
        ('fix', 'Fix'),
        ('per', 'Percentage'),
    ], default='fix')

    # --------------Deductions---------------

    income_tax_deduction = fields.Float()
    income_tax_type = fields.Selection([
        ('fix', 'Fix'),
        ('per', 'Percentage'),
    ], default='fix')

    house_building_loan_deduction = fields.Float()
    house_building_type = fields.Selection([
        ('fix', 'Fix'),
        ('per', 'Percentage'),
    ], default='fix')

    loan_against_salary_deduction = fields.Float()
    loan_against_salary_type = fields.Selection([
        ('fix', 'Fix'),
        ('per', 'Percentage'),
    ], default='fix')

    epf_loan_deduction = fields.Float()
    epf_loan_type = fields.Selection([
        ('fix', 'Fix'),
        ('per', 'Percentage'),
    ], default='fix')

    other_deduction = fields.Float()
    other_deduction_type = fields.Selection([
        ('fix', 'Fix'),
        ('per', 'Percentage'),
    ], default='fix')
