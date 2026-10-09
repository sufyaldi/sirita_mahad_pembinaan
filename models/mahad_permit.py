# -*- coding: utf-8 -*-
from odoo import models, fields, api
import uuid

class MahadPermit(models.Model):
    _name = 'mahad.permit'
    _description = "Perizinan Pesiar & Bermalam Mahasantri"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'departure_time desc, id desc'

    name = fields.Char(string="Kode Perizinan", required=True, default="NEW", copy=False, tracking=True)
    student_id = fields.Many2one('res.partner', string="Mahasantri", required=True, domain="[('is_student', '=', True)]", tracking=True)
    permit_type = fields.Selection([
        ('pesiar', 'Izin Pesiar (Siang / Sore)'),
        ('bermalam', 'Izin Bermalam / Pulang Kampung'),
    ], string="Jenis Izin", default='pesiar', required=True, tracking=True)
    reason = fields.Text(string="Alasan Perizinan", required=True)
    destination = fields.Char(string="Tujuan / Alamat", required=True)

    departure_time = fields.Datetime(string="Waktu Rencana Keberangkatan", required=True, default=fields.Datetime.now)
    expected_return_time = fields.Datetime(string="Waktu Rencana Kembali", required=True)
    actual_checkout_time = fields.Datetime(string="Waktu Scan Keluar Pos Satpam")
    actual_checkin_time = fields.Datetime(string="Waktu Scan Kembali Pos Satpam")

    qr_code_token = fields.Char(string="QR Code Token", copy=False, default=lambda self: str(uuid.uuid4())[:8].upper())
    is_late = fields.Boolean(string="Keterlambatan Kembali", compute='_compute_is_late', store=True)

    state = fields.Selection([
        ('draft', 'Pengajuan Mahasantri'),
        ('musyrif_approved', 'Disetujui Musyrif'),
        ('mudhir_approved', 'Disetujui Pengasuh/Mudhir'),
        ('checked_out', 'Di Luar Kompleks (Scan Satpam)'),
        ('checked_in', 'Selesai (Kembali ke Asrama)'),
        ('cancelled', 'Ditolak / Dibatalkan'),
    ], string="Status Approval", default='draft', tracking=True)

    @api.depends('actual_checkin_time', 'expected_return_time')
    def _compute_is_late(self):
        for rec in self:
            if rec.actual_checkin_time and rec.expected_return_time:
                rec.is_late = (rec.actual_checkin_time > rec.expected_return_time)
            else:
                rec.is_late = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'NEW') == 'NEW':
            prefix = 'IZN-PSR/' if vals.get('permit_type') == 'pesiar' else 'IZN-BML/'
            vals['name'] = prefix + fields.Date.today().strftime('%Y%m%d') + '/' + str(uuid.uuid4())[:4].upper()
        return super(MahadPermit, self).create(vals)

    def action_approve_musyrif(self):
        for rec in self:
            if rec.permit_type == 'pesiar':
                rec.state = 'musyrif_approved'
            else:
                rec.state = 'musyrif_approved'

    def action_approve_mudhir(self):
        self.write({'state': 'mudhir_approved'})

    def action_scan_checkout(self):
        self.write({
            'state': 'checked_out',
            'actual_checkout_time': fields.Datetime.now()
        })

    def action_scan_checkin(self):
        self.write({
            'state': 'checked_in',
            'actual_checkin_time': fields.Datetime.now()
        })

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.model
    def cron_check_late_permits(self):
        """Cron Job: Deteksi Perizinan Kedaluwarsa & Generasi Poin Pelanggaran Otomatis"""
        now = fields.Datetime.now()
        late_permits = self.search([
            ('state', '=', 'checked_out'),
            ('expected_return_time', '<', now)
        ])
        cat_late = self.env['mahad.penalty.category'].search([('name', 'ilike', 'Keterlambatan')], limit=1)
        if not cat_late:
            cat_late = self.env['mahad.penalty.category'].create({
                'name': 'Keterlambatan Jam Malam / Pesiar',
                'severity': 'sedang',
                'default_points': 15,
                'default_takzir': 'Tugas Kebersihan Kompleks & Setoran Surah Yasin'
            })

        for permit in late_permits:
            permit.is_late = True
            existing = self.env['mahad.penalty.record'].search([
                ('student_id', '=', permit.student_id.id),
                ('date', '=', fields.Date.today()),
                ('category_id', '=', cat_late.id)
            ], limit=1)
            if not existing:
                self.env['mahad.penalty.record'].create({
                    'student_id': permit.student_id.id,
                    'category_id': cat_late.id,
                    'date': fields.Date.today(),
                    'points': cat_late.default_points,
                    'takzir_note': f"Otomatis dari Sistem: Keterlambatan perizinan {permit.name}",
                    'state': 'confirmed'
                })
