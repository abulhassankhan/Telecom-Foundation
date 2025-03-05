from odoo import fields,api,models

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    system_size = fields.Float('System Size')

    system_type = fields.Selection([
        ('residential', 'Residential'),
        ('corporate', 'Corporate'),
        ('government', 'Government')], default='corporate', string='System Type')

    uom_id = fields.Many2one('uom.uom')
    mobile_number = fields.Char('Mobile Number')
    pkg_qty = fields.Integer('Package Quantity')

    address = fields.Char('Address')
    region = fields.Many2one('crm.region', 'Region')

    pre_bid_meeting = fields.Boolean('Pre Bid Meeting')
    pre_bid_meeting_date = fields.Datetime('Pre Bid Meeting Date')

    tender_submission_date = fields.Datetime('Tender Submission Date')
    tender_opening_date = fields.Datetime('Tender Opening Date')
    tender_publish_date = fields.Datetime('Tender Published Date')

    tender_document_fee = fields.Boolean('Tender Document Fee')
    tender_document_amount = fields.Float('Tender Document Fee')

    bid_security_amount = fields.Float('Bid Security Amount')

    tender_no_employer = fields.Char('Tender No (Employer)')

    performance_security = fields.Float('Performance Security')
    ps_no_of_days = fields.Float('PS No of Days')

    advance_payment_guarantee = fields.Float('Advance Payment Guarantee')
    apg_no_of_days = fields.Float('APG No of Days')

    tender_payment_terms = fields.Char('Tender Payment Terms')
    project_duration = fields.Float('Project Duration')

    submission_process = fields.Selection([
        ('physical', 'Physical'),
        ('epad_online', 'Epads/Online')], string='Submission Process')

    sub_process = fields.Char('Submission Process')

    sub_stage_id = fields.Many2one('crm.sub.stage', 'Sub Stage')
