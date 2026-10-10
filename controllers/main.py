# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json

class MahadApiController(http.Controller):

    @http.route('/api/mahad/syahadah/status', type='http', auth='none', methods=['GET'], csrf=False)
    def verify_syahadah_status(self, nim=None, **kwargs):
        """API Endpoint untuk SIAKAD Kampus: Verifikasi Kelulusan Syahadah Mahasantri"""
        if not nim:
            return Response(json.dumps({'status': 'error', 'message': 'Parameter nim wajib diisi'}), content_type='application/json', status=400)

        syahadah = request.env['mahad.syahadah'].sudo().search([
            ('nim', '=', nim),
            ('state', '=', 'validated')
        ], limit=1)

        if syahadah:
            data = {
                'status': 'success',
                'nim': syahadah.nim,
                'student_name': syahadah.student_id.name,
                'is_unlocked_for_skripsi': True,
                'syahadah_number': syahadah.name,
                'predikat': dict(syahadah._fields['predikat'].selection).get(syahadah.predikat),
                'issue_date': str(syahadah.issue_date),
            }
        else:
            data = {
                'status': 'not_eligible',
                'nim': nim,
                'is_unlocked_for_skripsi': False,
                'message': 'Mahasantri belum memiliki Sertifikat Syahadah valid dari Ma\'had Al-Jami\'ah'
            }

        return Response(json.dumps(data), content_type='application/json', status=200)

    @http.route('/api/mahad/permit/scan_qr', type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def scan_qr_permit(self, token=None, action=None, **kwargs):
        """API Endpoint untuk Validator Pos Satpam Check-in / Check-out QR"""
        if not token:
            return Response(json.dumps({'status': 'error', 'message': 'Parameter token wajib diisi'}), content_type='application/json', status=400)

        permit = request.env['mahad.permit'].sudo().search([('qr_code_token', '=', token)], limit=1)
        if not permit:
            return Response(json.dumps({'status': 'error', 'message': 'Token perizinan tidak ditemukan'}), content_type='application/json', status=444)

        if action == 'checkout':
            if permit.state not in ('musyrif_approved', 'mudhir_approved'):
                return Response(json.dumps({'status': 'error', 'message': 'Izin belum disetujui Musyrif/Mudhir'}), content_type='application/json', status=400)
            permit.action_scan_checkout()
            msg = "Scan Keluar Berhasil"
        elif action == 'checkin':
            if permit.state != 'checked_out':
                return Response(json.dumps({'status': 'error', 'message': 'Mahasantri tidak berstatus di luar kompleks'}), content_type='application/json', status=400)
            permit.action_scan_checkin()
            msg = "Scan Kembali Berhasil"
        else:
            msg = "Token Valid"

        data = {
            'status': 'success',
            'message': msg,
            'permit_number': permit.name,
            'student_name': permit.student_id.name,
            'permit_type': permit.permit_type,
            'state': permit.state,
            'is_late': permit.is_late
        }
        return Response(json.dumps(data), content_type='application/json', status=200)

    @http.route('/syahadah/verify', type='http', auth='public', website=True, sitemap=True)
    def website_verify_syahadah(self, q=None, **kwargs):
        """Halaman Publik Verifikasi Syahadah Mahasantri"""
        syahadah = None
        searched = False
        search_query = (q or '').strip()

        if search_query:
            searched = True
            # Cari berdasarkan NIM atau Nomor Syahadah
            syahadah = request.env['mahad.syahadah'].sudo().search([
                '|',
                ('nim', '=ilike', search_query),
                ('name', '=ilike', search_query),
                ('state', '=', 'validated')
            ], limit=1)

        values = {
            'searched': searched,
            'query': search_query,
            'syahadah': syahadah,
        }
        return request.render('sirita_mahad_pembinaan.page_syahadah_verify', values)

