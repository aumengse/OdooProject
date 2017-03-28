from openerp import api, fields, models
from datetime import datetime, timedelta
import time

class report(models.Model):
    _name ='payment_reseller.report'
    
    rfrom = fields.Date(string="From",
                       default = lambda *a: time.strftime('%Y-%m-%d'))
    rto = fields.Date(string="To",
                    default = lambda *a: time.strftime('%Y-%m-%d'))
    rselection = fields.Selection([
                 ('summary', "Summary Report"),
                 ('reseller', "Reseller Report"),
                 ('remittance', "Remittance Report"),
                 ], default='summary', string ="Reports")
    
    reseller_ids = fields.Many2one('payment_reseller.reseller', string="Reseller")
    
    @api.multi
    def action_generate(self):
        print '>>>', self.rselection

    

    