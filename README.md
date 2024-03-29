# Software Engineering Project COMP2913

```
Run test deployment by creating a flask virtual environment and executing run.py

Flask Project Structure:
run.py
cinemawebapp/
    __init__.py  
    routes.py             - route functions for site navigation - eg /home or /about
    forms.py              - user input forms
    database/
        __init__.py
        models.py           - database models
        ...
    templates/            - HTML templates
        layout.html 
        home.html
        ...
    static/
        main.css            - Style sheet
    tests/
        ...

Flask Installations

pip install flask-admin
pip install flask-babel
pip install flask-jwt
pip install pyjwt
pip install flask-login
pip install flask-mail
pip install flask-qrcode
pip install flask-sqlalchemy
pip install flask-wtf
pip install flask-migrate
pip install coverage
pip install email_validator
pip install numpy
pip install pandas
pip install matplotlib

pip install pdfkit

To get pdfkit working on Feng:
    - wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.3/wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
    - tar xvf wkhtmltox-0.12.3_linux-generic-amd64.tar.xz

    - You should have a wkhtmltox folder.
    - Add path of wkhtmltopdf executable in /wkhtmltox/bin to the file /flask/lib64/python3.6/site-packages/pdfkit/configuration.py.
    - In configuration.py, there is an __init__ function within the Configuration class - add the path of the executable inside the quotes of the 'wkhtmltopdf' parameter.

```
