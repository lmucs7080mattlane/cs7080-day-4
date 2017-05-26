from flask import Flask, request, abort, jsonify, render_template_string
from pymongo import MongoClient
from bson.objectid import ObjectId
app = Flask(__name__)


# http://docs.mongodb.com/getting-started/python/client/
mongo_database = None
mongo_credentials_collection = None
mongo_session_collection = None
mongo_sensor_data_collection = None
def connect_to_mongo():
    global mongo_database
    global mongo_credentials_collection
    global mongo_session_collection
    global mongo_sensor_data_collection
    client = MongoClient('mongodb://mongo:27017/devices')
    # Cheap and easy command to test the connection
    client.admin.command('ismaster')
    mongo_database = client.get_default_database()
    mongo_credentials_collection = mongo_database.credentials
    mongo_session_collection = mongo_database.session
    mongo_sensor_data_collection = mongo_database.sensor_data
connect_to_mongo()


def return_error(code):
    return ('', code)

def return_empty_success():
    return return_error(200)

def get_all_of_documents(mongo_db_collection, find_query = {}):
    db_results = [result for result in mongo_db_collection.find(find_query)]
    results = {}
    for result in db_results:
        result_id = str(result['_id'])
        del result['_id']
        results[result_id] = result
    return results


def is_valid_device_credentials(credentials):
    if 'password' not in credentials or 'device_name' not in credentials:
        return False
    return True



@app.route('/sda', methods = ['POST'])
def handle_postdata():
    data = request.getJson()
    print("TEST" + jsonify(data))
    
@app.route('/device_credentials/', methods = ['GET', 'POST'])
def handle_device_credentials():
    if request.method == 'GET':
        devices = get_all_of_documents(mongo_credentials_collection)
        return jsonify(devices)

    elif request.method == 'POST':
        new_device_credentials = request.get_json()

        if not is_valid_device_credentials(new_device_credentials):
            return return_error(400)

        # TODO how would you modify this to stop multiple versions
        # of credentials for the same 'device_name'???

        result = mongo_credentials_collection.insert_one(
            {
                'device_name': new_device_credentials['device_name'],
                'password': new_device_credentials['password']
            }
        )
        return jsonify(str(result.inserted_id))

@app.route('/device_credentials/<id>', methods = ['GET', 'PUT', 'DELETE'])
def handle_device_credentials_with_id(id):
    id = ObjectId(id)

    credentials = mongo_credentials_collection.find_one(
        {'_id': id}
    )
    if credentials is None:
        return return_error(404)

    if request.method == 'GET':
        del credentials['_id']
        return jsonify(credentials)

    elif request.method == 'PUT':
        if not is_valid_device_credentials(credentials):
            return return_error(400)
        mongo_credentials_collection.update_one(
            {'_id': id},
            {'$set':
                {
                    'device_name': credentials['device_name'],
                    'password': credentials['password']
                }
            }
        )
        return return_empty_success() # This returns the 200 Success Message

    elif request.method == 'DELETE':
        mongo_credentials_collection.remove(
            {'_id': id}
        )
        return return_empty_success()

@app.route('/connected_devices/', methods = ['GET'])
def handle_connected_devices():
    devices = get_all_of_documents(mongo_session_collection)
    return jsonify(devices)

@app.route('/connected_devices/<id>', methods = ['GET'])
def handle_connected_devices_with_id(id):
    id = ObjectId(id)

    session = mongo_session_collection.find_one(
        {'_id': id}
    )
    if session is None:
        return return_error(404)

    del session['_id']
    return jsonify(session)

@app.route('/connected_devices/<id>/sensor_data/', methods = ['GET'])
def handle_connected_devices_sensor_data(id):
    id = ObjectId(id)

    session = mongo_session_collection.find_one(
        {'_id': id}
    )
    if session is None:
        return return_error(404)

    sensor_data = get_all_of_documents(
        mongo_sensor_data_collection,
        {'device_name': session['device_name']}
    )
    return jsonify(sensor_data)

@app.route('/connected_devices/<id>/sensor_data/<data_id>', methods = ['GET'])
def handle_connected_devices_sensor_data_by_id(id, data_id):
    id = ObjectId(id)

    session = mongo_session_collection.find_one(
        {'_id': id}
    )
    if session is None:
        return return_error(404)

    sensor_data = get_all_of_documents(
        mongo_sensor_data_collection,
        {
            'device_name': session['device_name'],
            '_id': ObjectId(data_id)
        }
    )
    return jsonify(sensor_data)


@app.route('/', methods = ['GET'])
def get_webpage():
    html = '''
    <!doctype html>
    <title>jQuery Example</title>
    <script type="text/javascript"
      src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.0/jquery.min.js"></script>
    <script type="text/javascript">
      var $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
    </script>
    <script type="text/javascript">
        $(function() {
            var update_device_credentials_table = function() {
                $.getJSON($SCRIPT_ROOT + '/device_credentials/', {}, function(data) {
                    $("#credentials").empty();
                    $("#credentials").append(`
                        <tr>
                            <th> ID </th>
                            <td> Device Name </td>
                            <td> Password </td>
                        </tr>
                    `);
                    for (var key in data){
                        $("#credentials").append(`
                            <tr>
                                <th> ` + key + `</th>
                                <td> ` + data[key].device_name +` </td>
                                <td> ` + data[key].password +` </td>
                            </tr>
                        `);
                    }
                    setTimeout(update_device_credentials_table, 500);
                });
            };
            setTimeout(update_device_credentials_table, 500);

            var update_connected_devices_table = function() {
                $.getJSON($SCRIPT_ROOT + '/connected_devices/', {}, function(device_data) {
                    $("#devices").empty();
                    $("#devices").append(`
                        <tr>
                            <th> Session Id </th>
                            <td> Device Name </td>
                            <td> Last Three Sensor Readings </td>
                            <td> </td>
                            <td> </td>
                        </tr>
                    `);

                    $("#sensor_data").empty();

                    for (var device_key in device_data){
                        function create_sensor_data_function(device_key, device_name){
                            return function(sensor_data) {
                                var first_sensor_data_items = ['','',''];
                                var sensor_data_items = [];
                                for (key in sensor_data) {
                                    sensor_data_items.push(sensor_data[key])
                                }
                                sensor_data_items.sort(function(a, b) {
                                    return a-b;
                                })

                                if (sensor_data_items.length > 0) {
                                    first_sensor_data_items[0] = sensor_data_items[0].sensor_data + ' at ' + sensor_data_items[0].timestamp;
                                }
                                if (sensor_data_items.length >= 2) {
                                    first_sensor_data_items[1] = sensor_data_items[1].sensor_data + ' at ' + sensor_data_items[1].timestamp;
                                }
                                if (sensor_data_items.length >= 3) {
                                    first_sensor_data_items[2] = sensor_data_items[2].sensor_data + ' at ' + sensor_data_items[2].timestamp;
                                }

                                $("#devices").append(`
                                    <tr>
                                        <th> ` + device_key + `</th>
                                        <td> ` + device_name +` </td>
                                        <td> ` + first_sensor_data_items[0] +` </td>
                                        <td> ` + first_sensor_data_items[1] +` </td>
                                        <td> ` + first_sensor_data_items[2] +` </td>
                                    </tr>
                                `);
                            };
                        }

                        $.getJSON(
                            $SCRIPT_ROOT + '/connected_devices/' + device_key + '/sensor_data/',
                            {},
                            create_sensor_data_function(device_key, device_data[device_key].device_name)
                        );
                    }
                    setTimeout(update_connected_devices_table, 500);
                });
            };
            setTimeout(update_connected_devices_table, 500);


            $( "#new_credentials_form" ).submit(function(event) {
                event.preventDefault(); // Stop the form from submitting normally

                var $form = $(this); // Get the form

                // Get the data from the form
                var device_name = $form.find( "input[name='device_name']" ).val();
                var password = $form.find( "input[name='password']" ).val();

                // The REST API address
                var url = "/device_credentials/"

                // Send the data using the /device_credentials/ POST method
                $.ajax(
                    {
                        url:url,
                        type:"POST",
                        data: JSON.stringify({
                            device_name: device_name,
                            password: password
                        }),
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function(){ return; }
                    }
                );
            });
        });
    </script>

    <h1>Add device credentials:</h1>
    <form action="/device_credentials/" id="new_credentials_form">
        device_name:<input type="text" name="device_name" placeholder="unique name of device"><br/>
        password:<input type="text" name="password" placeholder="password"><br/>
        <input type="submit" value="Add device credentials">
    </form>

    <h1>Registered Device Credentials</h1>
    <table id="credentials"> </table>
    <br/>

    <h1>Current Connected Devices</h1>
    <table id="devices"> </table>

    <script type="text/javascript">
    </script>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    app.run()
