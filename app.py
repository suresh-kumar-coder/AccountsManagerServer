from flask import Flask, Blueprint
from datetime import datetime
from flask_cors import CORS 
from endpoints import apiRoutes, generate_notif_email_html, sendMail
from endpoints import user_collection, expiry_user
from apscheduler.schedulers.background import BackgroundScheduler
import pytz



def createApp():
    app = Flask(__name__)
    CORS(app)
    api_blueprint = Blueprint('api_blueprint', __name__)
    api_blueprint = apiRoutes(api_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')    
    return app

def scheduled_job():
    try:
        docs = user_collection.find()
        lst = []
        current_day = datetime.now().day
        for doc in docs:
            print(doc)
            date = int(doc["date"].split("-")[-1])

            if(date == 31):
                date -= 1
            print(date)
            if(date == current_day):
                print("curdate match")
                user_collection.update_one({'id': doc["id"]}, 
                        {'$set': 
                            {'pendingTenure': doc["pendingTenure"]-1}
                            })
                print("put")
                lst.append(doc)
                pending = doc["pendingTenure"]
                if(pending == 0):
                    expiry_user.insert_one(doc)
                    user_collection.delete_one({'id': doc["id"]})

        print(lst)
        if(len(lst) > 0):
            sendMail("Reminder!!!", generate_notif_email_html(lst))
    except Exception as e:
        print(e)

app = createApp()

timezone = pytz.timezone('Asia/Kolkata')
scheduler = BackgroundScheduler()
if not scheduler.get_job('my_scheduled_job'):
    scheduler.add_job(func=scheduled_job, trigger="cron", hour=20, minute=28, id='my_scheduled_job', timezone=timezone)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
