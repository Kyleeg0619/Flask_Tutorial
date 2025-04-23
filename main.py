from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
conn_str = "mysql+pymysql://root:Ky31ik3$m0s$;@localhost/boatdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


# render a file
@app.route('/')
def index():
    return render_template('index.html')


# remember how to take user inputs?
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# get all boats
# this is done to handle requests for two routes -
@app.route('/boats/')
@app.route('/boats/<page>')
def get_boats(page=1):
    page = int(page)  # request params always come as strings. So type conversion is necessary.
    per_page = 10  # records to show per page
    boats = conn.execute(text(f"SELECT * FROM boats LIMIT {per_page} OFFSET {(page - 1) * per_page}")).all()
    print(boats)
    return render_template('boats.html', boats=boats, page=page, per_page=per_page)


@app.route('/create', methods=['GET'])
def create_get_request():
    return render_template('boats_create.html')


@app.route('/create', methods=['POST'])
def create_boat():
    # you can access the values with request.from.name
    # this name is the value of the name attribute in HTML form's input element
    # ex: print(request.form['id'])
    try:
        conn.execute(
            text("INSERT INTO boats values (:id, :name, :type, :owner_id, :rental_price)"),
            request.form
        )
        conn.commit()
        return render_template('boats_create.html', error=None, success="Data inserted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_create.html', error=error, success=None)

@app.route('/search', methods=["POST"])
def search():
    search_query = request.form.get("query", "").strip()
    
    if not search_query:
        return render_template('boats.html', boats=[], page=1, error="Please enter a search term.")

    try:
        query = text("SELECT * FROM boats WHERE id LIKE :search_query OR name LIKE :search_query OR type LIKE :search_query")
        boats = conn.execute(query, {"search_query": f"%{search_query}%"}).all()

        return render_template('boats.html', boats=boats, page=1, search_query=search_query)

    except Exception as e:
        return render_template('boats.html', boats=[], page=1, error=str(e))

@app.route('/boat/<int:boat_id>')
def boat_details(boat_id):
    query = text("SELECT * FROM boats WHERE id = :boat_id")
    boat = conn.execute(query, {"boat_id": boat_id}).fetchone()

    if boat is None:
        return "Boat not found", 404

    return render_template('boat_details.html', boat=boat)

@app.route('/delete', methods=['GET'])
def create_get_request_for_delete():
    return render_template('boats_delete.html')

@app.route('/delete', methods=['POST'])
def delete_boat():
    try:
        conn.execute(
            text("DELETE FROM boats WHERE id = (:id)"),
            request.form
        )
        conn.commit()
        return render_template('boats_create.html', error=None, success="Data Deleted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_delete.html', error=error, success=None)

@app.route('/update', methods=['GET'])
def create_get_request_for_update():
    return render_template('boats_update.html')


@app.route('/update', methods=['POST'])
def update_boat():
    try:
        conn.execute(
            text("UPDATE boats SET name = :name, type = :type, owner_id = :owner_id, rental_price = :rental_price WHERE id = :id"),
            request.form
        )
        conn.commit()
        return render_template('boats_update.html', error=None, success="Data Updated successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_update.html', error=error, success=None)

if __name__ == '__main__':
    app.run(debug=True)
