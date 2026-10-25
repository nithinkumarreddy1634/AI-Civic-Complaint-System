import urllib.request
import json

login_req = urllib.request.Request(
    'http://127.0.0.1:8000/api/auth/login',
    data=b'username=admin%40civicai.com&password=admin123',
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
token = json.loads(urllib.request.urlopen(login_req).read())['access_token']

with open('backend/sample_pothole.jpg', 'rb') as f:
    img_bytes = f.read()

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="category"\r\n\r\n'
    f'pothole\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="description"\r\n\r\n'
    f'Large dangerous pothole on MG Road near metro station\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="latitude"\r\n\r\n'
    f'12.9716\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="longitude"\r\n\r\n'
    f'77.5946\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="address"\r\n\r\n'
    f'MG Road Junction, Bangalore\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="image"; filename="pothole.jpg"\r\n'
    f'Content-Type: image/jpeg\r\n\r\n'
).encode('utf-8') + img_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/complaints/',
    data=body,
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
    }
)
try:
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode())
    print("SUCCESS:", res.status, data)
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code, e.read().decode())
except Exception as e:
    print("ERROR:", str(e))
