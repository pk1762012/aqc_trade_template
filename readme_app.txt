# tested in postman

## Login 
 - enter http://localhost:5000/login in address bar of postman, select post 
 - select body>raw, in body there is dropdown on right end, json should be selected in that.
 - now in body, paste:
{
    "email": "test@gmail.com",
    "password": "123456789"
}
 - response there will be a access token: