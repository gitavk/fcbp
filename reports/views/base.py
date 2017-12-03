# -*- coding: utf-8 -*-
import os
import xlwt
from xlutils.copy import copy
from xlrd import open_workbook
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.utils.dateparse import parse_date

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

import reports.styles as styles

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class Report(ViewSet):

    file_name = 'base_report'
    sheet_name = 'base_sheet_name'
    # list of columns
    table_headers = []
    # list of the columns with not default style
    table_styles = {}

    def initial(self, request, *args, **kwargs):
        self.request = request
        self.title = self.get_title(**kwargs)
        self.response = HttpResponse(content_type='application/ms-excel')
        disposition = 'attachment; filename={file_name}.xls'.format(
            file_name=self.file_name)
        self.response['Content-Disposition'] = disposition
        self.row_heiht = None
        self.wb = xlwt.Workbook(encoding='utf-8')
        self.ws = self.wb.add_sheet(self.sheet_name)
        self.write_title()
        return super(Report, self).initial(request, *args, **kwargs)

    def write_title(self):
        self.ws.write_merge(0, 0, 0, len(self.table_headers) - 1,
                            self.title, styles.styleh)

    def get_title(self, **kwargs):
        return u'String need to replace by report.'

    def get_fdate(self):
        fdate = self.request.query_params.get('fdate')
        if fdate:
            return datetime.strptime(fdate, '%d.%m.%Y')
        else:
            return datetime.now()

    def get_tdate(self):
        tdate = self.request.query_params.get('tdate')
        if tdate:
            return datetime.strptime(tdate, '%d.%m.%Y')
        else:
            return datetime.now()

    def get_data(self):
        raise ('Need update by child')

    def write_data(self):
        for row in self.get_data():
            row_step = 0
            for i, cell in enumerate(row):
                style = self.table_styles.get(i, styles.style)
                if not isinstance(cell, (list, set, tuple)):
                    self.ws.write(self.row_num, i, cell, style)
                    if self.row_heiht:
                        self.ws.row(self.row_num).height = self.row_heiht
                else:
                    style.borders = styles.borders_cmb
                    row_step = self.write_multi_data(i, cell, style)
            self.row_num += (1 + row_step)

    def write_multi_data(self, coll, cell, style):
        row_step = 0
        for j, subcell in enumerate(cell[:-1]):
            self.ws.write(self.row_num + j, coll, subcell, style)
        # write bottom sub cell row
        old_bord = style.borders
        style.borders = styles.borders_cmb
        j += 1
        self.ws.write(self.row_num + j, coll, cell[-1], style)
        style.borders = old_bord
        row_step = row_step if j < row_step else j
        return row_step

    def write_bottom(self):
        raise ('Need update by child')

    def write_heads(self):
        self.ws.row(self.row_num).height_mismatch = True
        self.ws.row(self.row_num).height = 35*20
        col_num = 0
        for header in self.table_headers:
            if len(header) > 2:
                merge_column = col_num + header[2]
                self.ws.write_merge(
                    self.row_num, self.row_num,
                    col_num, merge_column, header[0], styles.styleth)
                for x in range(col_num, merge_column + 1):
                    self.ws.col(x).width = header[1]
                col_num = merge_column + 1
            else:
                self.ws.write(
                    self.row_num, col_num, header[0], styles.styleth)
                self.ws.col(col_num).width = header[1]
                col_num += 1

    def write_sheet(self):
        self.row_num = 2
        self.write_heads()
        self.row_num += 1
        self.write_data()
        self.row_num += 2
        self.write_bottom()

    def list(self, request, **kwargs):
        """
        Return a list of all users.
        """
        self.write_sheet()
        self.wb.save(self.response)
        return self.response


class ReportTemplate(Report):
    """create report from xls template"""

    tpl_path = ''
    tpl_start_row = 0

    def write_title(self):
        tpl_file = os.path.join(BASE_DIR, self.tpl_path)
        rb = open_workbook(tpl_file, formatting_info=True)
        r_sheet = rb.sheet_by_index(0)
        self.wb = copy(rb)
        self.ws = self.wb.get_sheet(0)
        super(ReportTemplate, self).write_title()

    def write_heads(self):
        self.row_num = self.tpl_start_row
        for col_num, header in enumerate(self.table_headers):
            self.ws.col(col_num).width = header[1]

    def get_data(self):
        return []

    def write_bottom(self):
        pass
