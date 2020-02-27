from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time
from stl import mesh
import requests
import json
import smtplib
import mysql.connector

jumlah_printer = 1
api_printer_1 = 'E9A6E4D3B8314CE0A598C233BC612FED'
api_printer_2 = '3E99F0DBEB75478B8732569CB3B2BE97'
ip_printer_1 = '192.168.0.140'
ip_printer_2 = '192.168.0.197'
dirpath = '/home/jupyter-luddy/Luddy_Project/data/temporary_stl/'
dirupload = '/home/jupyter-luddy/Luddy_Project/data/upload/'
cnt = 0
ulang = 1;
data = []
print_1 = []
print_2 = []
print_id_ = 1
email_id = 'gcoded747@gmail.com'
email_pass = 'vekadius12'
cnt_msg1 = 0
cnt_msg2 = 0
tmp_email1 = ''
tmp_email2 = ''
resp_1 = ''
resp_2 = ''

set 3d print 1 T-Bot
set_x1 = 110
set_y1 = 120
set_z1 = 170

set 3d print 2 Ender 3 Pro
set_x2 = 220
set_y2 = 220
set_z2 = 250

sc1 = 0

def main():
    if jumlah_printer >= 1:
        resp1 = check_printer(api_printer_1,ip_printer_1)
        if resp1 == 'Closed':
            print('Printer 1 Not Connect')
            cmd_to_printer('command','connect',api_printer_1,ip_printer_1)
            print('Printer 1 Connect')
        else:
            print('Printer 1 ReConnect')
            cmd_to_printer('command','disconnect',api_printer_1,ip_printer_1)
            time.sleep(10)
            cmd_to_printer('command','connect',api_printer_1,ip_printer_1)
            print('Printer 1 Connect')
            
    if jumlah_printer >= 2:    
        resp2 = check_printer(api_printer_2,ip_printer_2)
        if resp2 == 'Closed':
            print('Printer 2 Not Connect')
            cmd_to_printer('command','connect',api_printer_2,ip_printer_2)
            print('Printer 2 Connect')
        else:
            print('Printer 2 ReConnect')
            cmd_to_printer('command','disconnect',api_printer_2,ip_printer_2)
            time.sleep(10)
            cmd_to_printer('command','connect',api_printer_2,ip_printer_2)
            print('Printer 2 Connect')
    time.sleep(10)

def upload_file(api,ip_,filename_):
    fle={'file': open(dirupload + '/' + filename_, 'rb'), 'filename': filename_}
    url= 'http://' + ip_ + ':80/api/files/local'
    header={'X-Api-Key': api}
    response = requests.post(url, files=fle,headers=header)
    print(response.status_code) #201 upload
    #print(response.text)
    return response.status_code

def cmd_to_printer(perintah,isi,api,ip_):
    url= 'http://' + ip_ + ':80/api/connection'
    payload={perintah: isi }
    header={'X-Api-Key': api}
    response = requests.post(url, json=payload,headers=header)
    print(response.text)
    print(response.status_code) #204

def check_printer(api,ip_):
    url= 'http://' + ip_ + ':80/api/connection'
    header={'X-Api-Key': api}
    response = requests.get(url, headers=header)
    print(response.status_code) #200
    status = json.loads(response.text)
    #print(status['current']['state'])
    return status['current']['state']    
         
def slice_printer(api,ip_,filename_):
    url= 'http://' + ip_ + ':80/api/files/local/' + filename_
    payload={'command': 'slice','slicer': 'curalegacy','print': 'true'}
    header={'X-Api-Key': api}
    response = requests.post(url, json=payload,headers=header)
    print(response.status_code) #202 slice
    #print(response.text)
    return response.status_code

def load_file():
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)
    entries = ((stat[ST_CTIME], path)
               for stat, path in entries if S_ISREG(stat[ST_MODE]))
    
    cnt_up = 0
     for cdate, path in sorted(entries, reverse = False):
        print(time.ctime(cdate) + ' ' + os.path.basename(path))
        data.append(os.path.basename(path))
        cnt_up = cnt_up + 1

def auto_scale(name_file,device_print):
    your_mesh = mesh.Mesh.from_file(dirpath + '/' + name_file)
    ulang_ = 1
    print(your_mesh.x.max())
    print(your_mesh.y.max())
    print(your_mesh.z.max())
    print()
    print(your_mesh.x.min())
    print(your_mesh.y.min())
    print(your_mesh.z.min())
    print("---")
    while ulang_ == 1:
        x_max = your_mesh.x.max()
        y_max = your_mesh.y.max()
        z_max = your_mesh.z.max()
        x_min = your_mesh.x.min()
        y_min = your_mesh.y.min()
        z_min = your_mesh.z.min()
        if device_print == 1:
            if (x_max-x_min) >= set_x1 or (y_max-y_min) >= set_y1 or (z_max-z_min) >= set_z1:
                your_mesh.x *= 0.95
                your_mesh.y *= 0.95
                your_mesh.z *= 0.95
            elif (x_max-x_min) <= set_x1 and (y_max-y_min) <= set_y1 and (z_max-z_min) <= set_z1:
                ulang_ = 0
        elif device_print == 2:
            if (x_max-x_min) >= set_x2 or (y_max-y_min) >= set_y2 or (z_max-z_min) >= set_z2:
                your_mesh.x *= 0.95
                your_mesh.y *= 0.95
                your_mesh.z *= 0.95
            elif (x_max-x_min) <= set_x2 and (y_max-y_min) <= set_y2 and (z_max-z_min) <= set_z2:
                ulang_ = 0
    print(your_mesh.x.max())
    print(your_mesh.y.max())
    print(your_mesh.z.max())
    print()
    print(your_mesh.x.min())
    print(your_mesh.y.min())
    print(your_mesh.z.min())
    your_mesh.save(dirupload + '/' + name_file)
    time.sleep(2)
    os.remove(dirpath + '/' + name_file)


def send_email(penerima,nama,nama_file_):
    TO = penerima
    SUBJECT = 'Notification 3D Print'
    TEXT = 'Kepada ' + nama + ' Pesanan 3D Print Anda Dengan Nama ' + nama_file_ + ' Sudah Jadi'
    # Gmail Sign In
    gmail_sender = email_id
    gmail_passwd = email_pass
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)
    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])
    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print ('email sent')
    except:
        print ('error sending mail')
    server.quit()

def query_email(nama_file_):
    indexs = nama_file_.index('_')
    username_ = nama_file_[0:indexs]
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      passwd="LIP123!",
      database="lip-project"
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM accounts WHERE username =%s",(username_,))
    myresult = mycursor.fetchall()
    print(myresult[0][4])
    send_email(myresult[0][4],myresult[0][3],nama_file_)

if __name__ == '__main__':
    main()

while True:
    ulang = 1
    while ulang:
        pjg_file1 = len(os.listdir(dirpath))
        if jumlah_printer >= 1:
            resp_1 = check_printer(api_printer_1,ip_printer_1)
            if resp_1 == 'Operational':
                if cnt_msg1 == 2:
                    query_email(tmp_email1)
                cnt_msg1 = 1
            elif resp_1 == 'Printing':
                cnt_msg1 = 2
                print('3D Printer 1 running')
                
        if jumlah_printer >= 2:    
            resp_2 = check_printer(api_printer_2,ip_printer_2)
            if resp_2 == 'Operational':
                if cnt_msg2 == 2:
                    query_email(tmp_email2)
                cnt_msg2 = 1
            elif resp_2 == 'Printing':
                cnt_msg2 = 2
                print('3D Printer 2 running')
            
        if pjg_file1 <= 1:
            print('Null Data')
            cnt = 0
        else:
            data = []
            load_file()
            print(len(data))
            if cnt > 1:
                format_1 = 0
                if data[0].endswith('.stl') or data[0].endswith('.STL'):
                    format_1 = 1
                else:
                    print('Format File : ' + data[0] + ' Tidak Sesuai Deleted')
                    os.remove(dirpath + '/' + data[0])
                
                if resp_1 == 'Operational':
                    print_id_ = 1
                elif resp_2 == 'Operational' and jumlah_printer >= 2:
                    print_id_ = 2
                else:
                    print_id_ = 3
                if format_1 == 1:
                    if print_id_ == 1:
                        auto_scale(data[0],1)
                        print_1.append(data[0])
                    elif print_id_ == 2:
                        auto_scale(data[0],2)
                        print_2.append(data[0])
                    time.sleep(2)
                cnt = 0
                ulang = 0
            cnt = cnt + 1
        time.sleep(5)
    ulang = 1
    while ulang:
        if len(print_1) != 0:
            print('File Upload 1 not null')
            resp = check_printer(api_printer_1,ip_printer_1)
            if resp == 'Operational':
                stts = upload_file(api_printer_1,ip_printer_1,print_1[0])
                if stts == 201:
                    print('Upload Success')
                    stts_ = slice_printer(api_printer_1,ip_printer_1,print_1[0])
                    if stts_ == 202:
                        print('File1 Printing Process')
                        tmp_email1 = print_1[0]
                        os.remove(dirupload + '/' + print_1[0])
                        print_1.remove(print_1[0])
                    else:
                        print('Slicing Failed')
                else:
                    print('Upload Failed')
                time.sleep(5)
        if len(print_2) != 0:
            print('File Upload 2 not null')
            resp = check_printer(api_printer_2,ip_printer_2)
            if resp == 'Operational':
                stts = upload_file(api_printer_2,ip_printer_2,print_2[0])
                if stts == 201:
                    print('Upload Success')
                    stts_ = slice_printer(api_printer_2,ip_printer_2,print_2[0])
                    if stts_ == 202:
                        print('File1 Printing Process')
                        tmp_email2 = print_2[0]
                        os.remove(dirupload + '/' + print_2[0])
                        print_2.remove(print_2[0])
                    else:
                        print('Slicing Failed')
                else:
                    print('Upload Failed')
                time.sleep(5)
        ulang = 0
    print('OK')
    time.sleep(10)

