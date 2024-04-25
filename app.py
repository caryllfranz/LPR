from flask import Flask, render_template, request, jsonify, redirect
import subprocess
import sqlite3

app = Flask(__name__)


def connect_to_database():
    try:
        conn = sqlite3.connect("database.db")
        print("Connected to database successfully!")
        return conn
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
        return None


def insert_vehicle(conn, license_plate):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vehicle (licenseplate) VALUES (?)", (license_plate,)
        )
        conn.commit()
        print("Record inserted successfully!")
    except sqlite3.Error as e:
        print("Error inserting record:", e)


def delete_vehicle(conn, license_plate):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehicle WHERE licenseplate = ?", (license_plate,))
        conn.commit()
        print("Record deleted successfully!")
    except sqlite3.Error as e:
        print("Error deleting record:", e)


def run_command(command):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = process.communicate()
    if process.returncode != 0:
        return "Error: " + error.decode("utf-8")
    else:
        return "Output: " + output.decode("utf-8")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/database")
def database():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicle")
    rows = cursor.fetchall()
    vehicle_data = [{"license_plate": row[0]} for row in rows]
    print(vehicle_data)
    return render_template("database.html", vehicles=vehicle_data)


@app.route("/process", methods=["POST"])
def process():
    api_key = "59db79c4062b1ed23fbe9ef9e26c20b16664028c"
    image_path = request.files["image"]
    image_path.save("uploaded_image.jpg")
    command = f'python plate_recognition.py -a {api_key} "uploaded_image.jpg"'
    result = run_command(command)
    print(result)
    return jsonify({"result": result})


@app.route("/vehicle", methods=["POST"])
def manage_vehicle():
    action = request.form.get("action")
    license_plate = request.form.get("license_plate").strip().upper()

    conn = connect_to_database()
    if conn is None:
        return jsonify({"result": "Error connecting to database"})

    if action == "insert":
        insert_vehicle(conn, license_plate)

    elif action == "delete":
        delete_vehicle(conn, license_plate)

    return redirect("/database")


if __name__ == "__main__":
    app.run(debug=True)
