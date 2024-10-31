import mysql.connector
from flask import Flask, render_template, jsonify

app = Flask(__name__)

mysql_connection = None

# Function to connect to the MySQL database using the credentials from ups_credentials
def connect_to_mysql():
    global mysql_connection

    config = {
        'host': 'localhost',            
        'user': 'root',                 
        'password': 'OcT28!2024bumFox', 
        'database': 'freedomforever'    
    }

    try:
        # Establish the connection
        mysql_connection = mysql.connector.connect(**config)
        print("MySQL connection established successfully!")
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Invalid MySQL credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist.")
        else:
            print(f"Error: {err}")

@app.route('/')
def home():
    return render_template('index.html')

# Define a route to test the connection
@app.route('/searches')
def search_leads():

    error_status = '200'
    error_message = 'success'
    iRows = 10

    search_query = request.args.get('search', '')

    connect_to_mysql();
    dbh = mysql_connection.cursor(dictionary=True)

    try:
        aLeads = []
        search_term = f"%{search_query}%"

        count_sql = """
            SELECT COUNT(*) AS total_count FROM leads
            WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
        """
        dbh.execute(count_sql, (search_term, search_term, search_term))
        total_records = dbh.fetchone()['total_count']

        # Sql = "SELECT * FROM leads LIMIT %s"
        # dbh.execute(Sql, (iRows,))

        # Use SQL LIKE for partial matching across multiple fields
        sql = """
            SELECT * FROM leads
            WHERE (name LIKE %s OR email LIKE %s OR phone LIKE %s)
            LIMIT %s
        """
        dbh.execute(sql, (search_term, search_term, search_term, iRows))
        rowleads = dbh.fetchall()

        for rowl in rowleads:
            aLeads.append({
               'id': rowl['id'],
               'name': rowl['name'],
               'email': rowl['email'],
               'phone': rowl['phone'],
               'lead_status_id': rowl['lead_status_id'],
               'created_at': rowl['created_at'],
               'updated_at': rowl['updated_at'],
            })

        # Logic for handling GET request
        return jsonify({
            'status': error_status,
            'message': error_message,
            'totalrecords': total_records,
            'page': '1',
            'totalpages': '1',
            'leads_list': aLeads
        }), 200

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        dbh.close()  # Close the cursor
        # if mysql_connection:  # Ensure connection exists before closing
        #     mysql_connection.close()  # Close the connection if it's not used elsewhere

if __name__ == '__main__':
    app.run(debug=True)