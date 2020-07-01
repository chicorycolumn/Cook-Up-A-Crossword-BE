from utils import prepare_helium, test_data
import time
import eventlet
import math
from itertools import *
from flask import Flask, render_template
from flask_socketio import SocketIO

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", transports=['websocket'])

@app.route('/')
def sessions(methods=['GET', 'POST']):
    return render_template('session.html')

result_count = 0
timings = []

def gut_in_grid_not_more_times_than_it_has_dic_entries(current_guts, dic):
    for gut in current_guts:
        if len(dic[gut]) < current_guts.count(gut):
            return False
    return True

def helium(socketio, across_resource, down_resource, threshold, cw_width, cw_height, automatic_timeout_value, starting_timestamp):

    socketio.emit("started", {"time": time.time()})

    guttedwords_across = across_resource["supergut"]
    guttedmand_across = across_resource["gutted_mand"]
    dic_across = across_resource["superdict"]
    desirable_across = across_resource["desirable_words"]
    mandwords_across = across_resource["mand_words_filtered"]

    guttedwords_down = down_resource["supergut"]
    guttedmand_down = down_resource["gutted_mand"]
    dic_down = down_resource["superdict"]
    desirable_down = down_resource["desirable_words"]
    mandwords_down = down_resource["mand_words_filtered"]

    mandatory_words = list(set(mandwords_across + mandwords_down))
    desirable_combined = list(set(desirable_across + desirable_down))

    global most_recent_timestamp
    global perm_count
    global test_mode
    global result_count

    socketio.sleep(0)

    # gut_gen = product(guttedwords_across, repeat=( math.ceil(cw_height/2) ) )
    gut_gen = permutations(guttedwords_across, math.ceil(cw_height / 2))

    while starting_timestamp == most_recent_timestamp and starting_timestamp + automatic_timeout_value > time.time():

        current_guts = next(gut_gen)

        # Kick out if any across guts are in putative grid more times that they have fullwords.
        # This kickpoint can be skipped if itertools.permutations is used instead of itertools.product.
        # if not gut_in_grid_not_more_times_than_it_has_dic_entries(current_guts, dic_across):
        #     continue

        perm_count += 1
        gridguts = {"across": [], "down": []}

        for word in current_guts:
            gridguts["across"].append(word)

        for i in range( math.ceil( cw_width / 2 ) ):
            gridguts["down"].append("".join(gut[i] for gut in gridguts["across"]))

        current_guts = gridguts["across"] + gridguts["down"]
        # print(current_guts)

        #Kick out if not all mandatory words are present.
        if bool(mandatory_words) and bool(len(set(set(guttedmand_across + guttedmand_down)).difference(current_guts))):
            continue

        # Kick out if any new guts in putative grid more times that they have fullwords.
        # This also kicks out if the newly formed down guts have NO valid full words.
        if len(list(filter(lambda gut: ( len(dic_down[gut]) if gut in dic_down.keys() else 0 ) < current_guts.count(gut), gridguts["down"]))):
            continue

        bank = {}
        temporary_bank = {}
        coord_count = 1

        for gut in gridguts["down"]:
            temporary_bank[str(coord_count) + "do"] = {"gutted": gut, "ungutted": dic_down[gut] if gut in dic_down.keys() else []}
            coord_count += 1

        gut_one_across = gridguts["across"][0]
        bank["1ac"] = {"gutted": gut_one_across, "ungutted": dic_across[gut_one_across] if gut_one_across in dic_across.keys() else []}

        for gut in gridguts["across"][1:]:
            bank[str(coord_count) + "ac"] = {"gutted": gut, "ungutted": dic_across[gut] if gut in dic_across.keys() else []}
            coord_count += 1
        bank = {**bank, **temporary_bank}

        #Kick out if insufficient quantity of desirable_words in putative grid.
        if len(list(filter(lambda ungutted_list : bool(len(set(ungutted_list).intersection(desirable_combined))), [bank[coord]["ungutted"] for coord in bank.keys()]))) < threshold:
            continue

        result = {"summary": [gut.upper() for gut in gridguts["across"]], "grid": []}
        mandatory_words_copy = mandatory_words[0:]

        for coord in bank.keys():
            if bool(set(bank[coord]["ungutted"]).intersection(mandatory_words_copy)):
                mand_word = list(filter(lambda ungutted : ungutted in mandatory_words_copy, bank[coord]["ungutted"]))[0]
                mandatory_words_copy.remove(mand_word)
                newest_line = (coord, mand_word.upper())
                result["grid"].append(newest_line)
            else:
                ungutted_list = [word.upper() if word in desirable_combined else word for word in bank[coord]["ungutted"]]
                newest_line = (coord, list(filter(lambda word: word.isupper(), ungutted_list)) + list(filter(lambda word: not word.isupper(), ungutted_list)))
                result["grid"].append(newest_line)

        result_count+=1

        if test_mode:
            print(result)
            print("RESULT COUNT IS:", result_count)
        else:
            socketio.sleep(0)
            print(result)
            socketio.emit("produced grid",
                     {"mandatory_words": mandatory_words, "million_perms_processed": perm_count / 1000000,
                      "result": result})
            socketio.sleep(0)

    # We've been kicked out of the while loop.
    socketio.sleep(0)
    socketio.emit('terminated', {"time": time.time()})
    print("Successfully terminated.")

    if test_mode:
        print("RESULT COUNT SO FAR IS:", result_count)
        timings.append(result_count)
        result_count = 0
        count_timings()

global perm_count
perm_count = 0

global mandatory_words
mandatory_words = []

global most_recent_timestamp
most_recent_timestamp = ""

@socketio.on('grid specs')
def receive_grid_specs(incomingData):

    print("The client sent these grid specifications: ", incomingData)
    global mandatory_words
    global perm_count
    perm_count = 0
    starting_timestamp = time.time()
    global most_recent_timestamp
    most_recent_timestamp = starting_timestamp

    data = {
        "banned_words": [],
        "desirable_words_unfiltered": [],
        "threshold": 0,
        "grid_width": 0,
        "grid_height": 0
    }

    for key in data.keys():
        data[key] = incomingData[key] if key in incomingData.keys() else data[key]

    if "mandatory_words" in incomingData.keys():
        mandatory_words = incomingData["mandatory_words"]

    desirable_words_unfiltered = list(set(data["desirable_words_unfiltered"]).difference(data["banned_words"]))

    if data["threshold"] > len(desirable_words_unfiltered):
        data["threshold"] = len(desirable_words_unfiltered)

    prepared_resources_across = prepare_helium(data["grid_width"], data["banned_words"], desirable_words_unfiltered, mandatory_words)

    if data["grid_height"] != data["grid_width"]:
        prepared_resources_down = prepare_helium(data["grid_height"], data["banned_words"], desirable_words_unfiltered, mandatory_words)
    else:
        prepared_resources_down = prepared_resources_across

    helium(socketio, prepared_resources_across, prepared_resources_down, data["threshold"],
           data["grid_width"], data["grid_height"], automatic_timeout_value, starting_timestamp)

def terminate():
    print("The process will be terminated.")
    global most_recent_timestamp
    most_recent_timestamp = time.time()

def send_message(msg):
    socketio.sleep(0)
    print('This message is being sent to the client: ', msg)
    socketio.emit('message', {"message": msg})

@socketio.on('connect')
def connect(methods=['GET', 'POST']):
    print('Client connected: ')
    send_message("The server confirms that the client has connected.")

@socketio.on("message")
def receive_message(data, methods=['GET', 'POST']):
    send_message("Server received: " + data["message"])
    print("The client has sent this message: ", data)

@socketio.on('connect_error')
def handle_connect_error(err):
    print("An error occurred: ", err)

@socketio.on('connect_failed')
def handle_connect_error(err):
    print("An error occurred, connect failed: ", err)

@socketio.on('disconnect')
def disconnect(methods=['GET', 'POST']):
    print("The client has disconnected.")
    terminate()

@socketio.on("please terminate")
def client_says_terminate(methods=['GET', 'POST']):
    print("The client has asked to terminate.")
    send_message("Hi client, I hear you want to terminate.")
    terminate()

@socketio.on("verify off")
def verify_off(methods=['GET', 'POST']):
    socketio.emit("message", {"million_perms_processed": perm_count / 1000000})

test_mode = False    # A dev switch to input test data directly, rather than via socket connection.
count_mode = 20     # How many iterations to count.
automatic_timeout_value = 30

def count_timings():
    if len(timings) >= count_mode:
        print("With ITERTOOLS, the timings are: ", timings)
        print("Average results per iteration: ", sum(timings) / count_mode)
        print("Timeout: ", automatic_timeout_value)
        print("Number of iterations counted: ", count_mode)
        return
    receive_grid_specs(test_data)

if test_mode:
    if count_mode:
        count_timings()
    else:
        receive_grid_specs(test_data)

if __name__ == '__main__':
    socketio.run(app, debug=False)