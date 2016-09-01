# -*- coding:utf8 -*-

from .models import Department, Staff, Position, Contact


def _from_xlsx_worksheet(worksheet):
    """must like $BASE_DIR/assets/SLC.xlsx"""

    # for row in list(worksheet.rows)[:10]:
    #     print ','.join([
    #                        str((cell.value, type(cell.value))) for cell in row])
    #
    # print type(worksheet.rows)

    rows = iter(worksheet.rows)
    rows.next()  # skip header

    REGIN = 0
    DEPART1 = 1
    DEPART2 = 2
    LOCAFF = 3
    OLD_EXTNUM = 4
    NEW_EXTNUM = 5
    PHONE = 6
    FAX = 7
    MOBILE = 8
    EMAIL = 9
    IM = 10
    PHONE_MAC = 11

    def rv(row, idx):
        return row[idx]

    depart_name_set = set()

    def handle_depart(depart_name, superior_depart=None):
        if not depart_name in depart_name_set:
            depart_name_set.add(depart_name)
            return Department(name=depart_name, superior=superior_depart)

    def handle_contact(row, idx, mode, locaff):
        v = rv(row, idx)
        if v:
            return Contact(staff=locaff, mode=mode, value=v)

    for row in rows:
        row = list(cell.value for cell in row)

        regin = rv(row, REGIN)
        d = handle_depart(regin)
        yield d

        depart1 = rv(row, DEPART1)
        d = handle_depart(depart1, d)
        yield d

        depart2 = rv(row, DEPART2)
        d = handle_depart(depart2, d)
        yield d

        locaff_name = rv(row, LOCAFF)
        locaff = Staff(**{
            # TODO: no save here
            # TODO: preprocess name, handle special cases
            'name': locaff_name,
        })
        yield locaff

        pos = Position(department=d, staff=locaff)
        yield pos

        yield handle_contact(row, OLD_EXTNUM, 'old_ext', locaff)
        yield handle_contact(row, NEW_EXTNUM, 'new_ext', locaff)
        yield handle_contact(row, PHONE, 'phone', locaff)
        yield handle_contact(row, FAX, 'fax', locaff)
        yield handle_contact(row, MOBILE, 'mobile', locaff)
        yield handle_contact(row, EMAIL, 'email', locaff)
        yield handle_contact(row, IM, 'im', locaff)
        yield handle_contact(row, PHONE_MAC, 'phone_mac', locaff)


def from_xlsx_worksheet(worksheet):
    return filter(None, _from_xlsx_worksheet(worksheet))
