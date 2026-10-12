# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MahadPenaltyCategory(models.Model):
    _name = 'mahad.penalty.category'
    _description = "Master Kategori Pelanggaran Kedisiplinan"

    name = fields.Char(string="Nama Pelanggaran", required=True)
    severity = fields.Selection([
        ('ringan', 'Ringan (1-10 Poin)'),
        ('sedang', 'Sedang (11-25 Poin)'),
        ('berat', 'Berat (26-50 Poin)'),
        ('sangat_berat', 'Sangat Berat (> 50 Poin)'),
    ], string="Tingkat Pelanggaran", default='ringan', required=True)
    default_points = fields.Integer(string="Bobot Poin Standard", default=5, required=True)
    default_takzir = fields.Text(string="Rekomendasi Takzir Edukatif")
    active = fields.Boolean(default=True)

class MahadPenaltyRecord(models.Model):
    _name = 'mahad.penalty.record'
    _description = "Catatan Pelanggaran & Takzir Mahasantri"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string="Kode Pelanggaran", required=True, default="NEW", copy=False, tracking=True)
    student_id = fields.Many2one('res.partner', string="Mahasantri", required=True, domain="[('is_student', '=', True)]", tracking=True)
    category_id = fields.Many2one('mahad.penalty.category', string="Kategori Pelanggaran", required=True, tracking=True)
    date = fields.Date(string="Tanggal Pelanggaran", default=fields.Date.context_today, required=True)
    points = fields.Integer(string="Poin Pelanggaran", required=True, default=5, tracking=True)
    takzir_note = fields.Text(string="Bentuk Takzir Edukatif (Tugas Perbaikan)", help="Misal: Hafalan Surah Yasin / Kebersihan Mushalla")
    state = fields.Selection([
        ('draft', 'Draft / Laporan'),
        ('confirmed', 'Dikonfirmasi (Poin Aktif)'),
        ('completed', 'Takzir Selesai Dilaksanakan'),
        ('cancelled', 'Dibatalkan'),
    ], string="Status Takzir", default='draft', tracking=True)

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            self.points = self.category_id.default_points
            self.takzir_note = self.category_id.default_takzir

    @api.model
    def create(self, vals):
        if vals.get('name', 'NEW') == 'NEW':
            vals['name'] = 'PLG/' + fields.Date.today().strftime('%Y%m') + '/' + str(fields.Date.today().day) + '/' + str(self.env['ir.sequence'].next_by_code('mahad.penalty.record') or '01')
        return super(MahadPenaltyRecord, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_complete_takzir(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_penalty_points = fields.Integer(string="Total Poin Pelanggaran Ma'had", compute='_compute_penalty_points', store=True)
    sp_status = fields.Selection([
        ('aman', 'Aman (< 25 Poin)'),
        ('sp1', 'SP-1 / Nasihat (25-49 Poin)'),
        ('sp2', 'SP-2 / Panggilan Ortu (50-99 Poin)'),
        ('sp3', 'SP-3 / Pengeluaran (>= 100 Poin)'),
    ], string="Status Peringatan Kedisiplinan", compute='_compute_penalty_points', store=True)

    @api.depends('hostel_contract_ids')
    def _compute_penalty_points(self):
        for partner in self:
            records = self.env['mahad.penalty.record'].search([
                ('student_id', '=', partner.id),
                ('state', 'in', ['confirmed', 'completed'])
            ])
            total = sum(r.points for r in records)
            partner.total_penalty_points = total
            if total >= 100:
                partner.sp_status = 'sp3'
            elif total >= 50:
                partner.sp_status = 'sp2'
            elif total >= 25:
                partner.sp_status = 'sp1'
            else:
                partner.sp_status = 'aman'
