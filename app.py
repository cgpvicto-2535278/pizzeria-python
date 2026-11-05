from flask import Flask, render_template
import mysql.connector
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_name = os.getenv('DB_NAME')

connexion = mysql.connector.connect(
    host=db_host,
    user=db_user,
    database=db_name
)

