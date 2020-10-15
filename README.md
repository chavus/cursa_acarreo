# Cursa Acarreo

An application to track and manage construction material shipping and trucks

## Application functionality

The application is divided in 2 main parts: the administration panel and the operators application.

- Adminsitration panel: Only accessed by users with admin role. Here admins can visualize all the material shippings that are in progress and finalized. Also, admins can create new users, material banks, projects, drivers and trucks.

![Admin Panel](https://github.com/chavus/cursa_acarreo/blob/master/readme_imgs/2020-10-14_18-47-12.png)

- Operators application: Can be accessed by operators and admins. Here users can create new trips or shipping of material. An receive or complete a trip when it is done.

![App](https://github.com/chavus/cursa_acarreo/blob/master/readme_imgs/2020-10-14_19-08-59.png)

## Project stack

- Framework: Python/Flask - Blueprint, flask_login, flask_wtf/wtforms, flask_mongoengine
- Frontend: Enhanced frontend with javascript(ES5/ES6), Bootstrap, Bootstrap-table, libraries: html5-qrcode.min.js
- Database: MongoDB
- App hosting: Heroku


Demo url:
https://cursa-acarreo-dev.herokuapp.com/login
Operator User: operator, Password: operator
Admin User: admin, Password: admin
