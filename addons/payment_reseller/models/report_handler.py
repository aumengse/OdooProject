from openerp import api, fields, models
import time

class report_handler(models.Model):
    _name ='payment_reseller.report_handler'
          
#     def _get_summary_report(self):
#         
#         query = """
#             SELECT a.reseller_id,(select name from payment_reseller_reseller where id = a.reseller_id),
#                 sum((b.qty * b.price) - ((b.qty * b.price) * (b.discount/100))) as total_pur,
#                 (select sum(amt_render) from payment_reseller_payment where a.reseller_id = rs_id group by rs_id) as total_payment
#             FROM payment_reseller_po_head a
#             INNER JOIN payment_reseller_po_det b on a.id = b.po_head_id
#             GROUP BY a.reseller_id;
#                 """
#     
#         self.env.cr.execute(query)
#         recs = self.env.cr.dictfetchall()
#         
#         for x in recs:
#             print '-------',x
    
#         payment_ids = self.env['payment_reseller.payment'].search([])
#         reseller_ids = self.env['payment_reseller.reseller'].search([])
#         sum_report = []
# #         details = self.env['schoolresults.detail']
# #             details |= details.new({'subject_id': subject.id})
# #         return details
#         for r_ids in reseller_ids:
#             print '+++',r_ids.id
#             po_head_ids = self.env['payment_reseller.po_head'].search([('reseller_id','=',r_ids.id)])
#             ntotal_pur =0
#             for po_head_id in po_head_ids:
#                 po_det_ids=self.env['payment_reseller.po_det'].search([('po_head_id','=',po_head_id.id)])
#                 stotal = 0
#                 for r in po_det_ids:
#                     stotal_pur = (r.qty * r.price) - ((r.qty * r.price) * (r.discount/100))
#                     stotal = stotal +  stotal_pur
#                 ntotal_pur = ntotal_pur + stotal
#             print '+++',ntotal_pur
#             sum_report.append(r_ids.id) 
#             print '>>>',sum_report
#     
#         return payment_ids
#       
    
    
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
    
    summary_rep = fields.One2many('payment_reseller.payment','sum_rep',string="Summary Report")
    
  
    @api.multi
    def action_generate(self):
        self.ensure_one()
        data = {}
        data['form'] = self.read(['rfrom','rto','rselection','reseller_ids'])[0]
        
        return self._print_report(data)
    
    def _print_report(self, data):
        print 'print'
        return self.env['report'].sudo().get_action(self, 'payment_reseller.sum_report_template', data=data)
    
 
 
     