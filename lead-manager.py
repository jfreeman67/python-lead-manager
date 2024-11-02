import mysql.connector
from mysql.connector import errorcode
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Function to connect to the MySQL database using the credentials from ups_credentials
def connect_to_mysql():
    config = {
        'host': 'localhost',            
        'user': 'root',                 
        'password': 'OcT28!2024bumFox', 
        'database': 'freedomforever'    
    }

    try:
        connection = mysql.connector.connect(**config)
        print("MySQL connection established successfully!")
        return connection
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Invalid MySQL credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist.")
        else:
            print(f"Error: {err}")
        return None

# Define a route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define a route to search leads
@app.route('/searches')
def search_leads():
    error_status = '200'
    error_message = 'success'
    iRows = 10

    search_query = request.args.get('search', '').strip()
    statusFilter = request.args.get('statusFilter', '').strip()
    page = request.args.get('page', default=1, type=int)  # Default to 1 if none is given
    offset = (page - 1) * iRows  # Calculate the offset for pagination

    # Establish a new MySQL connection for this request
    mysql_connection = connect_to_mysql()
    if mysql_connection is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    aLeads = []

    try:
        dbh = mysql_connection.cursor(dictionary=True)
    
        search_name = f"%{search_query}%"
        search_email = f"%{search_query}%"
        search_phone = f"%{search_query}%"

        params = [search_name, search_email, search_phone]

        # Count total records matching the search query
        count_sql = """
        SELECT 
            COUNT(*) AS total_count 
        FROM 
            leads 
        WHERE 
            (leads.name LIKE %s OR leads.email LIKE %s OR leads.phone LIKE %s)
        """
        
        if statusFilter:
            count_sql += " AND leads.lead_status_id = %s"
            params.append(statusFilter)

        dbh.execute(count_sql, params)
        total_records = dbh.fetchone()['total_count']

        # Retrieve leads matching the search query with pagination
        sql = """
            SELECT 
                leads.* 
            FROM 
                leads 
            WHERE 
                (leads.name LIKE %s OR leads.email LIKE %s OR leads.phone LIKE %s)
        """
        
        if statusFilter:
            sql += " AND leads.lead_status_id = %s"

        sql += " ORDER BY leads.name LIMIT %s OFFSET %s;"
        params.extend([iRows, offset])

        dbh.execute(sql, params)
        rowleads = dbh.fetchall()

        for rowl in rowleads:
            aLeads.append({
               'id': rowl['id'],
               'name': rowl['name'],
               'email': rowl['email'],
               'phone': rowl['phone'],
               'lead_status_id': rowl['lead_status_id'],
               'created_at': rowl['created_at'],
               'updated_at': rowl['updated_at']
            })

        # Return JSON response
        return jsonify({
            'status': error_status,
            'message': error_message,
            'totalrecords': total_records,
            'page': page,
            'totalpages': (total_records // iRows) + (1 if total_records % iRows > 0 else 0),
            'leads_list': aLeads
        }), 200

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if dbh:  # Ensure the cursor is closed
            dbh.close()
        if mysql_connection:  # Close the MySQL connection
            mysql_connection.close()

# Define a route to get lead status
@app.route('/lead_statuses', methods=['GET'])
def get_lead_statuses():
    # Establish a new MySQL connection for this request
    mysql_connection = connect_to_mysql()
    if mysql_connection is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    lead_statuses = []

    try:
        dbh = mysql_connection.cursor(dictionary=True)
        
        # Query to select all records from lead_statuses
        sql = "SELECT * FROM lead_statuses"
        dbh.execute(sql)
        
        # Fetch all records from the query
        rows = dbh.fetchall()
        
        # Loop through rows and append to lead_statuses list
        for row in rows:
            lead_statuses.append({
                'id': row['id'],
                'name': row['name']
            })
        
        # Return the JSON response
        return jsonify({
            'status': '200',
            'message': 'success',
            'lead_statuses': lead_statuses
        }), 200

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if dbh:  # Ensure the cursor is closed
            dbh.close()
        if mysql_connection:  # Close the MySQL connection
            mysql_connection.close()

@app.route('/delete_lead/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    # Establish a new MySQL connection for this request
    mysql_connection = connect_to_mysql()
    if mysql_connection is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    try:
        dbh = mysql_connection.cursor()

        # SQL query to delete the lead
        delete_sql = "DELETE FROM leads WHERE id = %s"
        dbh.execute(delete_sql, (lead_id,))

        # Commit the transaction
        mysql_connection.commit()

        # Check if a row was deleted
        if dbh.rowcount == 0:
            return jsonify({'error': 'Lead not found.'}), 404

        return jsonify({'message': 'Lead deleted successfully.'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if dbh:  # Ensure the cursor is closed
            dbh.close()
        if mysql_connection:  # Close the MySQL connection
            mysql_connection.close()

@app.route('/update_lead/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    try:
        data = request.get_json()  # Get the JSON data from the request
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        status = data.get('status')

        # Establish a new MySQL connection for this request
        mysql_connection = connect_to_mysql()
        if mysql_connection is None:
            return jsonify({'error': 'Database connection failed.'}), 500

        # Call your database function to update the lead
        dbh = mysql_connection.cursor()

        # SQL query to update the lead record
        update_sql = """
        UPDATE leads
        SET name = %s, email = %s, phone = %s, lead_status_id = %s, updated_at = NOW() 
        WHERE id = %s
        """
        dbh.execute(update_sql, (name, email, phone, status, lead_id))

        # Commit the transaction
        mysql_connection.commit()

        # Check if a row was updated
        if dbh.rowcount == 0:
            return jsonify({'error': 'Lead not found or no changes made.'}), 404

        return jsonify({'message': 'Lead updated successfully!'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if dbh:  # Ensure the cursor is closed
            dbh.close()
        if mysql_connection:  # Close the MySQL connection
            mysql_connection.close()

@app.route('/create_lead', methods=['POST'])
def create_lead():
    # Parse the incoming JSON data from the request
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    status = data.get('status')

    # Validate that all required fields are present
    if not all([name, email, phone, status]):
        return jsonify({'error': 'Please fill in all fields.'}), 400

    # Establish a new MySQL connection for this request
    mysql_connection = connect_to_mysql()
    if mysql_connection is None:
        return jsonify({'error': 'Database connection failed.'}), 500

    try:
        dbh = mysql_connection.cursor()

        # SQL query to insert a new lead record
        insert_sql = """
        INSERT INTO leads (name, email, phone, lead_status_id, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        dbh.execute(insert_sql, (name, email, phone, status))

        # Commit the transaction
        mysql_connection.commit()

        # Check if a row was inserted
        if dbh.rowcount == 0:
            return jsonify({'error': 'Failed to create lead.'}), 500

        return jsonify({'message': 'Lead created successfully!'}), 201

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if dbh:  # Ensure the cursor is closed
            dbh.close()
        if mysql_connection:  # Close the MySQL connection
            mysql_connection.close()
            
# Cleanup on exit
import atexit

def cleanup():
    print("Cleanup function called on exit.")

atexit.register(cleanup)  # Register cleanup function to run on exit

if __name__ == '__main__':
    app.run(debug=True)
