# Cursa Acarreo

An application to track and manage construction materials shipping.

*Application UI is in Spanish since it is developed for a client in México. Code is all in English.*

## Application functionality

The application is divided in 2 main parts: the administration panel and the operators' application.

- Adminsitration panel: Only accessed by users with admin role. Here admins can visualize all the shippings that are in progress and finalized. Also, admins can create new users, material banks, projects, drivers and trucks.

![Admin Panel](/readme_imgs/2020-10-14_18-47-12.png)

- Operators application: Can be accessed by operators and admins. Here users can create new shipping of material. And complete a shipping when it is done.

![App](/readme_imgs/2020-10-14_19-08-59.png)

## Project stack

- Framework: Python/Flask using Blueprint, flask_login, flask_wtf/wtforms, flask_mongoengine.
- Frontend: Enhanced frontend with javascript(ES5/ES6), Bootstrap, Bootstrap-table, Bootstrap Admin Template Coreui.io, libraries: SweetAlert, Html5-QRCode
- Database: MongoDB with Mongoengine ODM
- App hosting: Heroku

## Platform/Support

- Web: Chrome(fully tested), Safari and Firefox(not fully tested)
- Mobile: Fully responsive

## Demo access 
URL: https://cursa-acarreo-dev.herokuapp.com/login 
(might take 30 secs to respond the first time since demo server sleeps when not in use)
- Operator User: operator, Password: operator
- Admin User: admin, Password: admin
