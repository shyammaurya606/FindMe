# Deployment Guide for FindMe

Because this app uses a local **SQLite database** (`locations.db`), it requires persistent storage. If you deploy it to a platform with an "ephemeral" filesystem (like Heroku or the free tier of Render), your database will get wiped every time the app restarts.

Here are the two best options for deploying this specific app:

---

## Option 1: PythonAnywhere (Easiest & Free, Keeps SQLite Data)

PythonAnywhere is specifically designed for Python apps and provides persistent storage on their free tier, making it the perfect platform for a Flask app using SQLite.

### 1. Create an Account
- Go to [PythonAnywhere](https://www.pythonanywhere.com/) and create a "Beginner" (free) account.

### 2. Open a Bash Console
- In your PythonAnywhere dashboard, click on **Consoles** -> **Bash**.
- Clone your GitHub repository:
  ```bash
  git clone https://github.com/shyammaurya606/FindMe.git
  ```

### 3. Create a Virtual Environment
- In the bash console, run:
  ```bash
  mkvirtualenv --python=/usr/bin/python3.10 my-virtualenv
  cd FindMe
  pip install -r requirements.txt
  ```

### 4. Configure the Web App
- Go back to the PythonAnywhere dashboard and click the **Web** tab.
- Click **Add a new web app**.
- Choose **Manual configuration** (do NOT choose Flask, as choosing Flask will generate a blank template instead of using your code). Choose the Python version you used for the virtualenv (e.g., 3.10).
- Under the **Virtualenv** section, enter the name of your environment: `my-virtualenv`.

### 5. Update the WSGI Configuration File
- On the **Web** tab, look for the **WSGI configuration file** link (it looks like `/var/www/yourusername_pythonanywhere_com_wsgi.py`) and click it.
- Delete all the template code in that file and replace it with:

```python
import sys
import os

# Add your project directory to the sys.path
path = '/home/yourusername/FindMe'
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app
from app import app as application
```
*(Make sure to replace `yourusername` with your actual PythonAnywhere username)*
- Click **Save** in the top right.

### 6. Launch!
- Go back to the **Web** tab and click the big green **Reload** button.
- Your app is now live at `http://yourusername.pythonanywhere.com`!

> [!WARNING]
> Because you are using `http` instead of `https`, some browser location permissions might behave differently. PythonAnywhere provides HTTPS by default on `https://yourusername.pythonanywhere.com`.

---

## Option 2: DigitalOcean / VPS (More Professional, Highly Customizable)

If you want to use a custom domain and have full control over the server, deploying on a Linux VPS using **Gunicorn** and **Nginx** is the industry standard.

### 1. Provision a Server
- Create a basic Ubuntu Droplet on DigitalOcean (or an AWS EC2 instance).
- SSH into your server: `ssh root@your_server_ip`

### 2. Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx git
```

### 3. Clone and Setup the Project
```bash
cd /var/www
git clone https://github.com/shyammaurya606/FindMe.git
cd FindMe

# Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Gunicorn (Production WSGI Server)
pip install gunicorn
```

### 4. Create a Systemd Service (To keep the app running)
- Create a service file: `sudo nano /etc/systemd/system/findme.service`
- Add the following configuration:
```ini
[Unit]
Description=Gunicorn instance to serve FindMe
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/FindMe
Environment="PATH=/var/www/FindMe/venv/bin"
ExecStart=/var/www/FindMe/venv/bin/gunicorn --workers 3 --bind unix:findme.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```
- Start the service:
```bash
sudo systemctl start findme
sudo systemctl enable findme
```

### 5. Configure Nginx (Reverse Proxy)
- Create an Nginx config: `sudo nano /etc/nginx/sites-available/findme`
- Add the configuration:
```nginx
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://unix:/var/www/FindMe/findme.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
- Enable it and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/findme /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 6. (Optional) Setup SSL
- Install Certbot to easily get a free SSL certificate:
```bash
sudo apt install python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

Your app is now securely deployed!
