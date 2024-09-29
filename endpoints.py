from flask_pymongo import pymongo
from flask import request, jsonify
import certifi
import smtplib
from email.message import EmailMessage
from random import randint
from secrets import token_hex
from dateutil.relativedelta import relativedelta

connection_str = "mongodb+srv://sureshkumarm:OxQdM5AdpkpfZXae@cluster0.b4bhdnb.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(connection_str, tlsCAFile= certifi.where())

db = client.get_database("AccountsManager")
user_collection = db["users"]
expiry_user = db["expiry_users"]

def apiRoutes(endpoints):

    @endpoints.route('/accountsmanager',methods=['POST'])
    def accountsManager():
        resp = {}
        status = {}
        data = {}
        
        try:

            id = generate_unique_id()
            data["id"] = id
            data["name"] = request.json.get('name')
            data["phone"] = request.json.get('phone')
            data["amount"] = request.json.get('amount')
            data["tenure"] = request.json.get('tenure')
            data["amountPerMonth"] = request.json.get('amountPerMonth')
            data["date"] = request.json.get('date')
            data["pendingTenure"] = data["tenure"]

            user_collection.insert_one(data)
            
            if user_collection.find_one({'id': id}):
                status = {
                    "statusCode" : '200',
                    "statusMessage" : "User data successfully stored!"
                }
                sendMail("New Accounts Entry Added!!!", generate_add_customer_html(data))
                
            else:
                status = {
                    "statusCode" : '500',
                    "statusMessage" : "Either server or database issue. Please Try Again!!!"
                }                 
        except Exception as e:
            status = {
                "statusCode":"400",
                "statusMessage":str(e)
            }
        
        resp['status'] = status
        return jsonify(resp)
    
    return endpoints


"""Supporting Functions"""

def generate_unique_id(length=16):
    unique_id = token_hex(length)
    return unique_id

def sendMail(subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    from_email = 'salesforecastapp@gmail.com'  
    password = 'pzotbzbpdsgailla'  

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = "sureshkumar200323@gmail.com"
    msg.set_content("This is a fallback text in case the email client does not support HTML.", subtype='plain')
    msg.add_alternative(body, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def generate_notif_email_html(data_list):
    # Start HTML email template
    html_content = """
    <html>
    <head>
        <style>
            table {
                font-family: Arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            h2 {
                color: #4CAF50;
            }
        </style>
    </head>
    <body>
        <h2>Customer Payment in Due!!!</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>Amount</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add rows to the table from the data_list
    for entry in data_list:
        html_content += f"""
            <tr>
                <td>{entry['name']}</td>
                <td>{entry['phone']}</td>
                <td>{entry['amount']}</td>
                <td>{entry['date']}</td>
            </tr>
        """
    
    # Close the table and HTML tags
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html_content

def generate_add_customer_html(details):
    html = body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f8f9fa;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background: #ffffff;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }}
                h2 {{
                    color: #343a40;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }}
                th {{
                    background-color: #007bff;
                    color: white;
                }}
                tr:hover {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>New Customer!!!</h2>
                <table>
                    <tr>
                        <th>Name</th>
                        <td>{details['name']}</td>
                    </tr>
                    <tr>
                        <th>Phone</th>
                        <td>{details['phone']}</td>
                    </tr>
                    <tr>
                        <th>Amount</th>
                        <td>{details['amount']}</td>
                    </tr>
                    <tr>
                        <th>Tenure (Months)</th>
                        <td>{details['tenure']}</td>
                    </tr>
                    <tr>
                        <th>Amount per Month</th>
                        <td>{details['amountPerMonth']}</td>
                    </tr>
                    <tr>
                        <th>Date</th>
                        <td>{details['date']}</td>
                    </tr>
                </table>
            </div>
        </body>
    </html>
    """

    return html