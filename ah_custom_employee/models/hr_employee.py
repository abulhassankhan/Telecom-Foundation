from odoo import fields, api, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    acting_charge_held2 = fields.Many2one('hr.job', relation='acting_charge_held2', string='Acting Charge Held')
    additional_charge_held = fields.Many2one('hr.job',  relation='additional_charge_held', string='Additional Charge Held')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups='base.group_user', tracking=True)

    address_home_id = fields.Many2one(
        'res.partner', 'Address',
        help='Enter here the private address of the employee, not the one linked to your company.',
        groups="base.group_user", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="base.group_user", copy=False)

    birthday = fields.Date('Date of Birth', groups="base.group_user", tracking=True)

    certificate = fields.Selection([
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Certificate Level', default='other', groups="base.group_user", tracking=True)

    children = fields.Integer(string='Number of Dependent Children',groups="base.group_user", tracking=True)
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", groups="base.group_user" , tracking=True)
    emergency_contact = fields.Char("Contact Name",groups="base.group_user", tracking=True)
    emergency_phone = fields.Char("Contact Phone", groups="base.group_user", tracking=True)
    km_home_work = fields.Integer(string="Home-Work Distance", groups="base.group_user", tracking=True)

    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        domain="[('partner_id', '=', address_home_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        groups="base.group_user",
        tracking=True,
        help='Employee bank account to pay salaries')

    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', groups="base.group_user", tracking=True)

    phone = fields.Char(related='address_home_id.phone', related_sudo=False, readonly=False, string="Private Phone", groups='base.group_user')


    identification_id = fields.Char(string='Identification No', groups='base.group_user', tracking=True)

    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups='base.group_user', default='single', tracking=True)

    passport_id = fields.Char('Passport No', groups='base.group_user', tracking=True)

    permit_no = fields.Char('Work Permit No', groups='base.group_user', tracking=True)

    pin = fields.Char(string="PIN", groups='base.group_user', copy=False,
                      help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.")

    place_of_birth = fields.Char('Place of Birth', groups='base.group_user', tracking=True)

    spouse_birthdate = fields.Date(string="Spouse Birthdate", groups='base.group_user', tracking=True)
    spouse_complete_name = fields.Char(string="Spouse Complete Name", groups='base.group_user', tracking=True)

    study_field = fields.Char("Field of Study", groups='base.group_user', tracking=True)
    study_school = fields.Char("School", groups='base.group_user', tracking=True)

    visa_expire = fields.Date('Visa Expiration Date', groups='base.group_user', tracking=True)
    visa_no = fields.Char('Visa No', groups='base.group_user', tracking=True)

    total_overtime = fields.Float(
        compute='_compute_total_overtime', compute_sudo=True,
        groups="base.group_user")

    hours_last_month_display = fields.Char(
        compute='_compute_hours_last_month', groups="base.group_user")

















