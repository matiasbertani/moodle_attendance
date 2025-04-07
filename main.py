import os

import bs4
import requests

MOODLE_URL = os.getenv("MOODLE_URL")
MOODLE_USERNAME = os.getenv("MOODLE_USERNAME")
MOODLE_PASSWORD = os.getenv("MOODLE_PASSWORD")
MOODLE_ATTENDANCE_ID = os.getenv("MOODLE_ATTENDANCE_ID")


def check_env_vars():
    if not MOODLE_URL:
        raise ValueError("MOODLE_URL is not set")
    if not MOODLE_USERNAME:
        raise ValueError("MOODLE_USERNAME is not set")
    if not MOODLE_PASSWORD:
        raise ValueError("MOODLE_PASSWORD is not set")
    if not MOODLE_ATTENDANCE_ID:
        raise ValueError("MOODLE_ATTENDANCE_ID is not set")


def send_attendance():

    with requests.Session() as s:

        login_url = MOODLE_URL + "/login/index.php"
        r = s.get(login_url)
        login_token = bs4.BeautifulSoup(r.text).find('input', {'name': 'logintoken'}).get('value')
        login_payload = {
            'username': MOODLE_USERNAME,
            'password': MOODLE_PASSWORD,
            'logintoken': login_token
        }
        s.post(login_url, data=login_payload)

        r = s.get(MOODLE_URL + f"/mod/attendance/view.php?id={MOODLE_ATTENDANCE_ID}&view=5")

        attendance_item = bs4.BeautifulSoup(r.text).find('a', string='Enviar asistencia')

        if not attendance_item:
            print("No attendance to send")
            raise SystemExit

        attendance_url = attendance_item.attrs['href']
        r = s.get(attendance_url)

        # Get payload data
        soup = bs4.BeautifulSoup(r.text)
        sessid = soup.find_all('input', {'name': 'sessid'})[0].attrs['value']
        sesskey = soup.find_all('input', {'name': 'sesskey'})[0].attrs['value']
        _qf__mod_attendance_form_studentattendance = soup.find_all(
            'input', {'name': '_qf__mod_attendance_form_studentattendance'}
        )[0].attrs['value']
        mform_isexpanded_id_session = soup.find_all('input', {'name': 'mform_isexpanded_id_session'})[0].attrs['value']
        status = soup.find_all('span', {'class': 'statusdesc'}, string="Present")[0].parent.find('input').attrs['value']
        submitbutton = soup.find_all('input', {'name': 'submitbutton'})[0].attrs['value']

        attendance_payload = {
            'sessid': sessid,
            'sesskey': sesskey,
            '_qf__mod_attendance_form_studentattendance': _qf__mod_attendance_form_studentattendance,
            'mform_isexpanded_id_session': mform_isexpanded_id_session,
            'status': status,
            'submitbutton': submitbutton
        }
        url_submition = f"{MOODLE_URL}/mod/attendance/attendance.php"
        s.post(url_submition, data=attendance_payload)


if __name__ == "__main__":
    check_env_vars()
    send_attendance()
