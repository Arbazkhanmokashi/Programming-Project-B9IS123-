from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql

app = Flask(__name__)

con = sql.connect("database.db", check_same_thread=False)
con.row_factory = sql.Row
cur = con.cursor()


def dataget(tableName, locationName, productName):
    if locationName is None and productName is None:
        queryData = cur.execute("SELECT * FROM {}".format(tableName)).fetchall()
    else:
        queryData = cur.execute(
            "SELECT * FROM {} WHERE locationName = ? AND productName = ? ".format(
                tableName
            ),
            (locationName, productName),
        ).fetchall()
    return queryData


def datainsert(tableName, newData):
    try:
        if tableName == "products":
            cur.execute(
                "INSERT INTO products (productName)VALUES (?)",
                (newData["productName"],),
            )
            con.commit()
            msg = "Added Successfully"
        if tableName == "location":
            cur.execute(
                "INSERT INTO location (locationName)VALUES (?)",
                (newData["locationName"],),
            )
            con.commit()
            msg = "Added Successfully"
        if tableName == "productmovement":
            cur.execute(
                "INSERT INTO productmovement (atTime, from_location, to_location, productName, qty)VALUES (?,?,?,?,?)",
                (
                    newData["atTime"],
                    newData["from_location"],
                    newData["to_location"],
                    newData["productName"],
                    newData["qty"],
                ),
            )
            con.commit()
            msg = "Added Successfully"
        if tableName == "balance":
            cur.execute(
                "INSERT INTO balance (locationName, productName, qty)VALUES (?,?,?)",
                (newData["locationName"], newData["productName"], 0),
            )
            con.commit()
            msg = "Entries of balance updated"
        return msg
    except:
        con.rollback()
        msg = "Error in insert operation"
        return msg


def dataupdate(tableName, newData):
    try:
        if tableName == "products":
            cur.execute(
                "UPDATE products SET productName = ? WHERE productID = ?",
                (newData["NEWProductName"], newData["ProductID"]),
            )
            con.commit()
            msg = "Edited Successfully"
        if tableName == "location":
            cur.execute(
                "UPDATE location SET locationName = ? WHERE locationID = ?",
                (newData["NEWLocationName"], newData["LocationID"]),
            )
            con.commit()
            msg = "Edited Successfully"
        if tableName == "productmovement":
            cur.execute(
                "UPDATE productmovement SET qty = ? WHERE movementID = ?",
                (newData["editedqty"], newData["movementID"]),
            )
            con.commit()
            msg = "Edited Successfully"
        if tableName == "balance":
            cur.execute(
                "UPDATE balance SET qty = ?  WHERE locationName = ? AND productName = ?",
                (newData["qty"], newData["locationName"], newData["productName"]),
            )
            con.commit()
            msg = "Edited Successfully"
        return msg

    except:
        con.rollback()
        msg = "Error in update operation"
        return msg


def datadelete(tableName, id):
    try:
        if tableName == "products":
            cur.execute("DELETE FROM products WHERE productID = ?", (id))
            con.commit()
            msg = "Deleted Successfully"
        if tableName == "location":
            cur.execute("DELETE FROM location WHERE locationID = ?", (id))
            con.commit()
            msg = "Deleted Successfully"
        if tableName == "productmovement":
            cur.execute("DELETE FROM productmovement WHERE movementID = ?", (id))
            con.commit()
            msg = "Deleted Successfully"
        return msg
    except:
        con.rollback()
        msg = "Error in delete operation"
        return msg


@app.route("/movementM")
def movementM():
    rows = dataget("productmovement", locationName=None, productName=None)
    rowsofproduct = dataget("products", locationName=None, productName=None)
    rowsoflocation = dataget("location", locationName=None, productName=None)

    for pr in rowsofproduct:
        for lr in rowsoflocation:
            data = dataget(
                "balance",
                locationName=lr["locationName"],
                productName=pr["productName"],
            )

            if len(data) == 0:
                newData = {}
                newData["locationName"] = lr["locationName"]
                newData["productName"] = pr["productName"]
                newData["qty"] = 0
                datainsert("balance", newData)

    return render_template(
        "movementM.html",
        rows=rows,
        rowsofproduct=rowsofproduct,
        rowsoflocation=rowsoflocation,
    )


@app.route("/addMovement", methods=["POST"])
def addMovement():
    if request.method == "POST":
        newData = {}

        newData["atTime"] = request.form["atTime"]
        newData["from_location"] = request.form["from_location"]
        newData["to_location"] = request.form["to_location"]
        newData["productName"] = request.form["productName"]
        newData["qty"] = int(request.form["qty"])

        status1 = movementManager(
            newData["from_location"], newData["productName"], -(newData["qty"])
        )
        status2 = movementManager(
            newData["to_location"], newData["productName"], (newData["qty"])
        )

        if (
            status1 == "Operation Successfull"
            and status2 == "Operation Successfull"
        ):
            msg = datainsert("productmovement", newData)
        else:
            msg = "Insuffecient Quantity In " + newData["from_location"]

    return redirect(url_for("movementM") + "?msg=" + msg)


@app.route("/editMovement", methods=["POST"])
def editMovement():

    if request.method == "POST":
        from_location = request.form["from_location"]
        to_location = request.form["to_location"]
        productName = request.form["productName"]
        qty = int(request.form["qty"])
        editedqty = int(request.form["editedqty"])

        newData = {}

        newData["movementID"] = request.form["movementID"]
        newData["editedqty"] = request.form["editedqty"]

        status1 = movementManager(from_location, productName, qty)
        status2 = movementManager(to_location, productName, -qty)

        status1 = movementManager(from_location, productName, -editedqty)
        status2 = movementManager(to_location, productName, editedqty)

        if (
            status1 == "Operation Successfull"
            and status2 == "Operation Successfull"
        ):
            msg = dataupdate("productmovement", newData)
        else:

            status1 = movementManager(from_location, productName, -editedqty)
            status2 = movementManager(to_location, productName, -editedqty)

            status1 = movementManager(from_location, productName, -qty)
            status2 = movementManager(to_location, productName, qty)

            msg = "Insuffecient Quantity In " + from_location

    return redirect(url_for("movementM") + "?msg=" + msg)


@app.route("/deleteMovement", methods=["POST"])
def deleteMovement():
    if request.method == "POST":
        movementID = request.form["movementID"]
        from_location = request.form["from_location"]
        to_location = request.form["to_location"]
        productName = request.form["productName"]
        qty = int(request.form["qty"])

        status1 = movementManager(from_location, productName, qty)

        status2 = movementManager(to_location, productName, -qty)

        if (
            status1 == "Operation Successfull"
            and status2 == "Operation Successfull"
        ):
            msg = datadelete("productmovement", movementID)
        else:
            msg = "Insuffecient Quantity In " + from_location
        return redirect(url_for("movementM") + "?msg=" + msg)


def movementManager(locationName, productName, qty):
    oldQuantity = 0
    newQuantity = 0

    if locationName != "-":
        balanceRows = dataget("balance", locationName, productName)

        if len(balanceRows) != 0:
            for br in balanceRows:
                oldQuantity = int(br["qty"])

            newQuantity = oldQuantity + qty
            if newQuantity < 0:
                status = "Insuffecient Quantity In " + locationName

            else:
                newData = {}
                newData["qty"] = newQuantity
                newData["locationName"] = locationName
                newData["productName"] = productName
                dataupdate("balance", newData)
                status = "Operation Successfull"
    else:
        status = "Operation Successfull"

    return status


@app.route("/locationM")
def locationM():
    rows = dataget("location", locationName=None, productName=None)
    return render_template("locationM.html", rows=rows)


@app.route("/addLocation", methods=["POST"])
def addLocation():
    if request.method == "POST":
        newData = {}
        newData["locationName"] = request.form["lm"]
        msg = datainsert("location", newData)
        return redirect(url_for("locationM") + "?msg=" + msg)


@app.route("/editLocation", methods=["POST"])
def editLocation():
    if request.method == "POST":
        newData = {}
        newData["LocationID"] = request.form["LocationID"]
        newData["NEWLocationName"] = request.form["NEWLocationName"]
        msg = dataupdate("location", newData)

        return redirect(url_for("locationM") + "?msg=" + msg)


@app.route("/deleteLocation/<locationID>")
def deleteLocation(locationID):
    msg = datadelete("location", locationID)
    return redirect(url_for("locationM") + "?msg=" + msg)


@app.route("/productM")
def productM():
    rows = dataget("products", locationName=None, productName=None)
    return render_template("productM.html", rows=rows)


@app.route("/addProduct", methods=["POST"])
def addProduct():
    if request.method == "POST":
        newData = {}
        newData["productName"] = request.form["pm"]
        msg = datainsert("products", newData)
        return redirect(url_for("productM") + "?msg=" + msg)


@app.route("/editProduct", methods=["POST"])
def editProduct():
    if request.method == "POST":
        newData = {}
        newData["ProductID"] = request.form["ProductID"]
        newData["NEWProductName"] = request.form["NEWProductName"]
        msg = dataupdate("products", newData)

        return redirect(url_for("productM") + "?msg=" + msg)


@app.route("/deleteProduct/<productID>")
def deleteProduct(productID):
    msg = datadelete("products", productID)
    return redirect(url_for("productM") + "?msg=" + msg)


@app.route("/")
def root():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "user" and request.form["password"] == "12345":
            return redirect(url_for("home"))
    return render_template("login.html")



@app.route("/home")
def home():
    data = []

    rowsofproduct = dataget("products", locationName=None, productName=None)
    rowsoflocation = dataget("location", locationName=None, productName=None)

    for lr in rowsoflocation:
        for pr in rowsofproduct:
            balRow = dataget("balance", lr["locationName"], pr["productName"])

            if len(balRow) != 0:
                for br in balRow:
                    qty = int(br["qty"])

                innerData = {}
                innerData["locationName"] = lr["locationName"]
                innerData["productName"] = pr["productName"]
                innerData["qty"] = qty

                data.append(innerData.copy())
    return render_template("home.html", data=data, rowsoflocation=rowsoflocation)

@app.route("/search")
def search():
    search_type = request.args.get('type', None)
    query = request.args.get('query', None)
    results = []

    if search_type and query:
        if search_type == "products":
            results = dataget("products", productName=query)
        elif search_type == "locations":
            results = dataget("location", locationName=query)
        elif search_type == "movements":
            results = dataget("productmovement", productName=query)  # Assuming you want to search movements by product name

    return render_template("search.html", results=results)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def dataget(tableName, locationName=None, productName=None):
    cur.row_factory = dict_factory  # Set the row factory to use the above function
    query = "SELECT * FROM {}".format(tableName)
    params = []
    if productName:
        query += " WHERE productName LIKE ?"
        params.append('%{}%'.format(productName))
    elif locationName:
        query += " WHERE locationName LIKE ?"
        params.append(locationName)
    return cur.execute(query, params).fetchall()




if __name__ == "__main__":
    app.run(debug=True)