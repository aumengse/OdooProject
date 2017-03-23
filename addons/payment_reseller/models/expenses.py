from openerp import api, fields, models
from datetime import datetime, timedelta
import time

class Expenses(models.Model):
    _name = "payment_reseller.expenses"
    _order = 'trans_date desc'
    
    name = fields.Char(string="Name", related = "expense_num")
    trans_date =fields.Date(string="Date", default = lambda *a: time.strftime('%Y-%m-%d'))
    expense_num =fields.Char(string="Document No.",readonly=True)
    reseller_id = fields.Many2one('payment_reseller.reseller',string="Reseller")
    expenses_ids = fields.One2many('payment_reseller.expense_det','exp_id_head',string="Expenses")
    
    
    @api.model
    def create(self, vals):
        vals['expense_num'] = self.env['ir.sequence'].get('exp_code')
        
        return super(Expenses, self).create(vals)
    
class Expenses_Det(models.Model):
    _name = "payment_reseller.expense_det"
   
    exp_id_head = fields.Many2one('payment_reseller.expenses', ondelete = "cascade")
    desc = fields.Char(string="Description", size=100)
    amt = fields.Float(string="Amount", digits=(16,2))