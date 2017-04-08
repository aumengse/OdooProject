from openerp import models, fields, api
from datetime import datetime, timedelta
import time 
    
class report_render(models.AbstractModel):
    _name = 'report.payment_reseller.sum_report_template'
 
    @api.multi
    def render_html(self, data):
        print 'printsss'
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
          
        rfrom = data['form']['rfrom']
        rto = data['form']['rto']
        rselection= data['form']['rselection']
        reseller_ids =data['form']['reseller_ids']
          
        # query = """
        # SELECT a.reseller_id,(select name from payment_reseller_reseller where id = a.reseller_id) as name,
        # (COALESCE(sum((b.qty * b.price) - ((b.qty * b.price) * (b.discount/100))))) as total_pur,
        # (COALESCE((select sum(amt_render) from payment_reseller_payment where a.reseller_id = rs_id group by rs_id),0.00)) as total_payment,
        # (COALESCE(sum((b.qty * b.price) - ((b.qty * b.price) * (b.discount/100))))) - (COALESCE((select sum(amt_render) from payment_reseller_payment where a.reseller_id = rs_id group by rs_id),0.00)) as balance
        # FROM payment_reseller_po_head a
        # INNER JOIN payment_reseller_po_det b on a.id = b.po_head_id
        # GROUP BY a.reseller_id;
        # """

        query = """
                SELECT a.reseller_id,(select name from payment_reseller_reseller where id = a.reseller_id) as name,
                (COALESCE(sum((b.qty * b.price) - ((b.qty * b.price) * (b.discount/100))))) as total_pur,
                (COALESCE((select sum(amt_render) from payment_reseller_payment where a.reseller_id = rs_id group by rs_id),0.00)) as total_payment,
                (COALESCE(sum((b.qty * b.price) - ((b.qty * b.price) * (b.discount/100))))) - (COALESCE((select sum(amt_render) from payment_reseller_payment where a.reseller_id = rs_id group by rs_id),0.00)) as balance
                FROM payment_reseller_po_head a
                INNER JOIN payment_reseller_po_det b on a.id = b.po_head_id
                GROUP BY a.reseller_id;
                """
        self.env.cr.execute(query)
        recs = self.env.cr.dictfetchall()
          
        print '>>>',recs
          
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'recs' : recs,
        }
          
        return self.env['report'].render('payment_reseller.sum_report_template', docargs)       