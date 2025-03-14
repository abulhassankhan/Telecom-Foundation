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
    total_deductions = fields.Float(compute='_compute_total_deductions', store=True)

    net_salary = fields.Float(compute='_compute_net_salary', store=True)

    total_without_medical = fields.Float(compute='_compute_total_without_medical', store=True)
    total_with_medical = fields.Float(compute='_compute_total_with_medical', store=True)
    gross_salary = fields.Float(compute='_compute_gross_salary', store=True)

    @api.depends('wage', 'officiating', 'head_quarter_allow', 'conveyance_allow', 'adhoc_allownce_1', 'adhoc_allownce_2', 'adhoc_allownce_3',
                 'adhoc_allow', 'adhoc_allow_2', 'adhoc_allow_3', 'adhoc_allow_4', 'special_duty_allow', 'cashier_allow', 'performance_credit')
    def _compute_total_without_medical(self):
        self.total_without_medical = (self.wage +
                                      self.officiating +
                                      self.head_quarter_allow +
                                      self.conveyance_allow +
                                      self.adhoc_allownce_1 +
                                      self.adhoc_allownce_2 +
                                      self.adhoc_allownce_3 +
                                      self.adhoc_allow +
                                      self.adhoc_allow_2 +
                                      self.adhoc_allow_3 +
                                      self.adhoc_allow_4 +
                                      self.special_duty_allow +
                                      self.cashier_allow +
                                      self.performance_credit
                                      )

    @api.depends('total_without_medical', 'medical_allow')
    def _compute_total_with_medical(self):
        self.total_with_medical = (self.total_without_medical + self.medical_allow)


    @api.depends('total_with_medical', 'monetization_allow', 'mobile_allow', 'other_allow')
    def _compute_gross_salary(self):
        self.gross_salary = (self.total_with_medical + self.monetization_allow + self.mobile_allow + self.other_allow)

    @api.depends('pf_deduction', 'eobi_deduction', 'hospital_deduction', 'income_tax_ded', 'house_building_loan_ded',
                 'loan_against_salary_ded', 'epf_loan_ded', 'other_ded')
    def _compute_total_deductions(self):
        self.total_deductions = (self.pf_deduction +
                                 self.eobi_deduction +
                                 self.hospital_deduction +
                                 self.income_tax_ded +
                                 self.house_building_loan_ded +
                                 self.loan_against_salary_ded +
                                 self.epf_loan_ded +
                                 self.other_ded
                                 )

    @api.depends('gross_salary', 'total_deductions')
    def _compute_net_salary(self):
        self.net_salary = (self.gross_salary - self.total_deductions)


    @api.onchange('struct_id', 'wage')
    def onchange_allowances_deduction(self):
        res = super(HrContract, self).onchange_allowances_deduction()

        # --------------------------

        self.medical_allow = (self.total_without_medical * 2) / 12

        # --------------------------

        if self.struct_id.pf_type == 'fix':
            self.pf_deduction = self.struct_id.pf_deduction
        else:
            self.pf_deduction = self.struct_id.pf_deduction * (self.wage + self.officiating) / 100

        # --------------------------

        if self.struct_id.house_building_type == 'fix':
            self.house_building_loan_ded = self.struct_id.house_building_loan_deduction
        else:
            self.house_building_loan_ded = self.struct_id.house_building_loan_deduction * self.wage / 100

        # --------------------------

        if self.struct_id.loan_against_salary_type == 'fix':
            self.loan_against_salary_ded = self.struct_id.loan_against_salary_deduction
        else:
            self.loan_against_salary_ded = self.struct_id.loan_against_salary_deduction * self.wage / 100

        # --------------------------

        if self.struct_id.epf_loan_type == 'fix':
            self.epf_loan_ded = self.struct_id.epf_loan_deduction
        else:
            self.epf_loan_ded = self.struct_id.epf_loan_deduction * self.wage / 100

        # --------------------------

        if self.struct_id.other_deduction_type == 'fix':
            self.other_ded = self.struct_id.other_deduction
        else:
            self.other_ded = self.struct_id.other_deduction * self.wage / 100

        return res


    @api.onchange('gross_salary')
    def compute_income_tax(self):
        gross_salary = self.gross_salary
        annual_salary = gross_salary * 12

        tax_config_line = self.env['tax.calculator.config'].search([], limit=1).config_line
        for line in tax_config_line:
            if line.from_value <= annual_salary and annual_salary <= line.to_value:
                fixed_amount = line.fixed_amount
                annual_exceed_amount = annual_salary - line.applicable_after_amount
                percentance_tax = (annual_exceed_amount / 100) * line.tax_rate
                total_tax = percentance_tax + fixed_amount
                self.income_tax_ded = total_tax / 12

    @api.onchange('total_without_medical')
    def onchange_total_without_medical(self):
        self.medical_allow = (self.total_without_medical * 2) / 12