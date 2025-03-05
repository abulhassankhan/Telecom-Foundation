from odoo import fields, api, models

class HrContract(models.Model):
    _inherit = 'hr.contract'

    basic_salary = fields.Float('Basic Pay')

    adhoc_allownce_1 = fields.Float('Adhoc-Allow-22@ 25%')
    adhoc_allownce_2 = fields.Float('Adhoc-Allow-23@ 30%')
    adhoc_allownce_3 = fields.Float('Adhoc-Allow-23@ 35%')
    other_allow = fields.Float('Other Allow')

    income_tax_ded = fields.Float('Income Tax Deduction')
    house_building_loan_ded = fields.Float('HBL Deduction')
    loan_against_salary_ded = fields.Float('LAS Deduction')
    epf_loan_ded = fields.Float('EPF Loan Deduction')
    other_ded = fields.Float('Other Deduction')
    total_deductions = fields.Float('Total Deductions')

    net_salary = fields.Float('Net Salary')

    @api.onchange('basic_salary', 'officiating', 'adhoc_allownce_1', 'adhoc_allownce_2', 'head_quarter_allow', 'conveyance_allow', 'special_duty_allow', 'cashier_allow', 'performance_credit'
                  'total_without_medical', 'medical_allow')
    def onchange_basic_salary(self):
        if self.basic_salary:
            self.adhoc_allownce_1 = (self.basic_salary / 100) * 25
            self.adhoc_allownce_2 = (self.basic_salary / 100) * 30
            # self.adhoc_allownce_3 = (self.basic_salary / 100) * 35

            if self.employee_id.acting_charge_held2 or self.employee_id.additional_charge_held:
                if self.basic_salary > 100000:
                    self.officiating = 20000
                else:
                    self.officiating = (self.basic_salary / 100) * 20


    @api.onchange('basic_salary', 'officiating', 'adhoc_allownce_1', 'adhoc_allownce_2', 'adhoc_allownce_3', 'head_quarter_allow', 'conveyance_allow', 'special_duty_allow', 'cashier_allow', 'performance_credit'
                  'total_without_medical', 'medical_allow', 'adhoc_allow', 'adhoc_allow_2', 'adhoc_allow_3', 'adhoc_allow_4')
    def onchange_total_without_total(self):
        self.total_without_medical = (self.basic_salary +
                                      self.officiating +
                                      self.head_quarter_allow +
                                      self.conveyance_allow +
                                      self.special_duty_allow +
                                      self.cashier_allow +
                                      self.performance_credit +
                                      self.adhoc_allownce_1 +
                                      self.adhoc_allownce_2 +
                                      self.adhoc_allownce_3 +
                                      self.adhoc_allow +
                                      self.adhoc_allow_2 +
                                      self.adhoc_allow_3 +
                                      self.adhoc_allow_4
                                      )

    @api.onchange('medical_allow', 'total_without_medical')
    def calculate_total_with_medical(self):
        self.medical_allow = (self.total_without_medical * 2) / 12
        self.total_with_medical = self.total_without_medical + self.medical_allow


    @api.onchange('total_without_medical', 'monetization_allow', 'mobile_allow', 'other_allow')
    def onchange_total_with_medical(self):
        self.gross_salary = self.total_with_medical + self.monetization_allow + self.mobile_allow + self.other_allow


    @api.onchange('basic_salary', 'officiating')
    def onchange_basic_salary_officiating(self):
        self.pf_deduction = ((self.basic_salary + self.officiating) / 100) * 10
        self.eobi_deduction = 370


    @api.onchange('pf_deduction', 'eobi_deduction', 'hospital_deduction',
                  'income_tax_ded', 'house_building_loan_ded', 'loan_against_salary_ded'
                  , 'epf_loan_ded', 'other_ded')
    def onchange_deductions(self):
        self.total_deductions = fields.deductions = self.pf_deduction + self.eobi_deduction + self.hospital_deduction + self.income_tax_ded + self.house_building_loan_ded + self.loan_against_salary_ded + self.epf_loan_ded + self.other_ded


    @api.onchange('total_deductions', 'gross_salary')
    def calculate_net_salary(self):
        self.net_salary = self.gross_salary - self.total_deductions



