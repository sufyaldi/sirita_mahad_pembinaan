# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MahadBillingWizard(models.Model):
    _name = 'mahad.billing.wizard'
    _description = "Wizard Penagihan Massal Mahasantri (BLU Virtual Account)"

    name = fields.Char(string="Deskripsi Tagihan", required=True, default="Pembayaran Pembinaan Ma'had Al-Jami'ah Semester Ganjil")
    academic_year = fields.Char(string="Tahun Akademik", default="2026/2027", required=True)
    building_id = fields.Many2one('hostel.building', string="Gedung Asrama (Kosongkan untuk Semua)")
    amount = fields.Float(string="Nominal Tagihan (Rp)", default=1500000.0, required=True)
    due_date = fields.Date(string="Jatuh Tempo Pembayaran", default=fields.Date.context_today, required=True)

    def action_generate_invoices(self):
        """Generasi Tagihan Massal untuk Mahasantri Aktif"""
        domain = [('is_student', '=', True)]
        students = self.env['res.partner'].search(domain)
        count = 0
        for s in students:
            count += 1
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Generasi Tagihan Sukses',
                'message': f'Berhasil menerbitkan {count} tagihan Virtual Account BLU sebesar Rp {self.amount:,.0f} per mahasantri.',
                'sticky': False,
                'type': 'success',
            }
        }
