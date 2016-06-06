from flask import request
from flask.ext.security import login_required
from . import interfaces
from iggybase.interfaces.connections import spinal_db_session
from . import models
import datetime
import logging

MODULE_NAME = 'interfaces'


@interfaces.route('/check_harvard_code', methods=['POST', 'GET'])
@login_required
def check_harvard_code(facility_name):
    spinal_code = request.args.get('spinal_code')

    spinal_session = spinal_db_session()
    spinal_rec = spinal_session.query(models.ExpenseCodesExpensecode).filter_by(fullcode = spinal_code).first()

    if not spinal_rec:
        resp = 'NOT_FOUND'
    elif spinal_rec.active != 1:
        resp = 'INACTIVE'
    elif spinal_rec.expiration_date < datetime.date.today():
        resp = 'EXPIRED'
    elif spinal_rec.start_date > datetime.date.today():
        resp = 'PREMATURE'
    else:
        resp = 'VALID'

    spinal_session.commit()

    return resp
