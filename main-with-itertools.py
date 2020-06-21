from utils import print_grid, file_to_list, gut_words, ungut_words, make_dict, sum_dicts, prepare_helium, test_data
import time
import eventlet
import socketio
import math
import threading
from itertools import product
eventlet.monkey_patch()
# from flask import Flask, request, render_template, jsonify
# from flask_cors import CORS
# app = Flask(__name__)
# CORS(app)

# sio = socketio.Server()
# sio = socketio.AsyncServer(cors_allowed_origins=['*'])
sio = socketio.Server(cors_allowed_origins=['*'])


app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

result_count = 0
timings = []
should_terminate = False

def gut_in_grid_not_more_times_than_it_has_dic_entries(current_guts, dic):
    for gut in current_guts:
        if len(dic[gut]) < current_guts.count(gut):
            return False
    return True

def helium(sio, starting_timestamp, across_resource, down_resource, threshold, mandatory_words, cw_width, cw_height, automatic_timeout_value, number_of_for_loops, current_guts):
    # {"supergut": supergut, "superdict": trunk_dict, "desirable_words": desirable_words, "gutted_mand": gutted_mand}

    guttedwords_across = across_resource["supergut"]
    guttedmand_across = across_resource["gutted_mand"]
    dic_across = across_resource["superdict"]
    desirable_across = across_resource["desirable_words"]
    guttedwords_down = down_resource["supergut"]
    guttedmand_down = down_resource["gutted_mand"]
    dic_down = down_resource["superdict"]
    desirable_down = down_resource["desirable_words"]

    global most_recent_timestamp
    global perm_count
    global test_mode
    global result_count
    global should_terminate

    sio.sleep(0)

    #Number of forloops to repeat is the number of connecting COLUMNS.
    gut_gen = product(guttedwords_across, repeat=( math.ceil(cw_height/2) ) )

    while starting_timestamp == most_recent_timestamp and starting_timestamp + automatic_timeout_value > time.time():
        current_guts = next(gut_gen)

        # Filter out guts that are in putative grid more times that they have fullwords.
        if gut_in_grid_not_more_times_than_it_has_dic_entries(current_guts, dic_across):

            perm_count += 1
            gridguts = {"across": [], "down": []}

            for word in current_guts:
                gridguts["across"].append(word)

            for i in range( math.ceil( grid_height / 2 ) ):
                gridguts["down"].append("".join(gut[i] for gut in gridguts["across"]))

            current_guts = gridguts["across"] + gridguts["down"]

            #Kick out if not all mandatory words are present.
            if bool(mandatory_words) and bool(len(set(set(guttedmand_across + guttedmand_down)).difference(current_guts))):
                continue

            # Kick out if any new guts in putative grid more times that they have fullwords.
            # This also kicks out if the newly formed down guts have NO valid full words.
            if len(list(filter(lambda gut: ( len(dic_down[gut]) if gut in dic_down.keys() else 0 ) < current_guts.count(gut), gridguts["down"]))):
                continue

            bank = {}
            coord_count = 1

            for gut in gridguts["down"]:
                bank[str(coord_count) + "do"] = {"gutted": gut, "ungutted": dic_down[gut] if gut in dic_down.keys() else []}
                coord_count += 1

            gut_one_across = gridguts["across"][0]
            bank["1ac"] = {"gutted": gut_one_across, "ungutted": dic_across[gut_one_across] if gut_one_across in dic_across.keys() else []}

            for gut in gridguts["across"][1:]:
                bank[str(coord_count) + "ac"] = {"gutted": gut, "ungutted": dic_across[gut] if gut in dic_across.keys() else []}
                coord_count += 1

            #Kick out if insufficient quantity of desirable_words in putative grid.
            if len(list(filter(lambda ungutted_list : bool(len(set(ungutted_list).intersection(set(desirable_across + desirable_down)))), [bank[coord]["ungutted"] for coord in bank.keys()]))) < threshold:
                continue

            result = {"summary": [gut.upper() for gut in gridguts["across"]], "grid": []}

            # if (bool(mandatory_words)):
            mandatory_words_copy = mandatory_words[0:]
            for coord in bank.keys():
                if bool(set(bank[coord]["ungutted"]).intersection(mandatory_words_copy)):
                    mand_word = list(filter(lambda ungutted : ungutted in mandatory_words_copy, bank[coord]["ungutted"]))[0]
                    mandatory_words_copy.remove(mand_word)
                    newest_line = (coord, mand_word.upper())
                    result["grid"].append(newest_line)

                else:
                    ungutted_list = [word.upper() if word in [desirable_across + desirable_down] else word for word in bank[coord]["ungutted"]]
                    newest_line = (coord, list(filter(lambda word: word.isupper(), ungutted_list)) + list(filter(lambda word: not word.isupper(), ungutted_list)))
                    result["grid"].append(newest_line)

            # else:
            #     for coord in bank.keys():
            #         ungutted_list = [word.upper() if word in desirable_words else word for word in bank[coord]["ungutted"]]
            #         newest_line = (coord, list(filter(lambda word : word.isupper(), ungutted_list)) + list(filter(lambda word : not word.isupper(), ungutted_list)))
            #         result["grid"].append(newest_line)

            result_count+=1

            if not test_mode:
                sio.sleep(0)
                print(result)
                sio.emit("produced grid",
                         {"mandatory_words": mandatory_words, "million_perms_processed": perm_count / 1000000,
                          "result": result})
                sio.sleep(0)
            else:
                print(result)
                print("***************** ", result_count)

    # We've been kicked out of the while loop.
    message = "Terminated by the client request, or by automatic timeout that the developer set, which was %d seconds, or (unlikely) by exhausting all permutations." % automatic_timeout_value
    print(message)
    sio.emit( "message", { "message": message } )
    # should_terminate = True
    if count_mode:
        print("RESULT COUNT SO FAR IS:", result_count)
        timings.append(result_count)
        result_count = 0
        count_timings()
    return

grid_width = 5
grid_height = 5

global perm_count
perm_count = 0

global mandatory_words
mandatory_words = []

global most_recent_timestamp
most_recent_timestamp = ""

@sio.event
def receive_grid_specs(sid, incomingData):

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
        "threshold": 0
    }

    for key in data.keys():
        data[key] = incomingData[key] if key in incomingData.keys() else data[key]

    if "mandatory_words" in incomingData.keys():
        mandatory_words = incomingData["mandatory_words"]

    desirable_words_unfiltered = list(set(data["desirable_words_unfiltered"]).difference(data["banned_words"]))

    if data["threshold"] > len(desirable_words_unfiltered):
        data["threshold"] = len(desirable_words_unfiltered)

    prepared_resources_across = prepare_helium(grid_width, data["banned_words"], desirable_words_unfiltered, mandatory_words)

    if grid_height != grid_width:
        prepared_resources_down = prepare_helium(grid_height, data["banned_words"], desirable_words_unfiltered, mandatory_words)
    else:
        prepared_resources_down = prepared_resources_across

    # PrepRes looks like this: {"supergut": supergut, "superdict": trunk_dict, "desirable_words": desirable_words, "gutted_mand": gutted_mand}

    helium(sio, starting_timestamp, prepared_resources_across, prepared_resources_down, data["threshold"],
           mandatory_words, grid_width, grid_height, automatic_timeout_value, 3, [])

def terminate():
    print("The process will be terminated.")
    global most_recent_timestamp
    most_recent_timestamp = time.time()

@sio.event
def connect(sid, environ):
    print('Client connected: ', sid)
    send_message(sid, {"message": "The server confirms that the client has connected."})

@sio.event
def receive_message(sid, data):
    print("The client has sent this message: ", data)

@sio.event
def send_message(sid, data):
    print('This message is being sent to the client: ', data)
    sio.emit('message', data)

@sio.event
def handle_errors(err):
    print("An error occurred: ", err)

@sio.event
def disconnect(sid):
    print("The client has disconnected.", sid)
    terminate()

@sio.event
def client_says_terminate(sid, data):
    print("The client has asked to terminate.", sid)
    terminate()

sio.on('connect', connect);
sio.on('disconnect', disconnect);
sio.on("message", receive_message)
sio.on("grid specs", receive_grid_specs)
sio.on("please terminate", client_says_terminate)
sio.on('connect_error', handle_errors);
sio.on('connect_failed', handle_errors);

test_mode = True    # A dev switch to input test data directly, rather than via socket connection.
count_mode = 20     # How many iterations to count.
automatic_timeout_value = 60
test_finished = False
wordlength = 5

def count_timings():
    if len(timings) >= count_mode:
        print("With ITERTOOLS PERMUTATIONS, the timings are: ", timings)
        print("Average results per iteration: ", sum(timings) / count_mode)
        print("Timeout: ", automatic_timeout_value)
        print("Number of iterations counted: ", count_mode)
        return
    receive_grid_specs(None, test_data)

if test_mode:
    if count_mode:
        count_timings()
    else:
        receive_grid_specs(None, test_data)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)