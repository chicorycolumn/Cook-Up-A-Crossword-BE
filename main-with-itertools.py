from utils import prepare_helium, test_data, is_A_not_fully_contained_by_B, gut_words, does_putative_grid_truly_meet_desithreshold
from collections import Counter
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

test_result_count = 0
timings = []

def gut_in_grid_not_more_times_than_it_has_dic_entries(current_guts, dic):
    for gut in current_guts:
        if len(dic[gut]) < current_guts.count(gut):
            return False
    return True

def helium(socketio, across_resource, down_resource, incomingData, automatic_timeout_value, starting_timestamp):

    threshold = incomingData["threshold"]
    cw_width = incomingData["grid_width"]
    cw_height = incomingData["grid_height"]
    perms_or_product = incomingData["perms_or_product"]
    results_count = incomingData["results_count"]

    shuffle_record = []

    global most_recent_timestamp
    global test_mode
    global test_result_count

    socketio.sleep(0)
    socketio.emit("started", {"time": time.time(), "perms_or_product": perms_or_product, "grand_pass_count": incomingData["grand_pass_count"]})

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

    socketio.sleep(1)

    gut_gen = []


    socketio.sleep(0)
    print("guttedwords_across[0:12]", guttedwords_across[0:12])
    send_message({"guttedwords_across[0:12]": guttedwords_across[0:12]})

    if perms_or_product == "product":
        print("PRODUCT")
        gut_gen = product(guttedwords_across, repeat=(math.ceil(cw_height/2)))
    else:
        print("PERMS")
        gut_gen = permutations(guttedwords_across, math.ceil(cw_height/2))

    while starting_timestamp == most_recent_timestamp and starting_timestamp + automatic_timeout_value > time.time():

        current_guts = next(gut_gen)

        if incomingData["perm_count"] < 20:
            shuffle_record.append(current_guts)
        elif incomingData["perm_count"] == 20:
            socketio.sleep(0)
            print("shuffle_record", shuffle_record)
            send_message({"shuffle_record": shuffle_record})

        if incomingData["perm_count"] and not incomingData["perm_count"] % 50000:
            print('incomingData["perm_count"], perms_or_product', incomingData["perm_count"], perms_or_product)
            socketio.sleep(0)
            send_message({"million_perms_processed": incomingData["perm_count"] / 1000000, "results_count": incomingData["results_count"],
                                      "grand_pass_count": incomingData["grand_pass_count"], "perms_or_product": perms_or_product})

        # Kick out if any across guts are in putative grid more times that they have fullwords.
        # This kickpoint can be skipped if itertools.permutations is used instead of itertools.product.
        if perms_or_product == "product" and not gut_in_grid_not_more_times_than_it_has_dic_entries(current_guts, dic_across):
            continue

        incomingData["perm_count"] += 1

        gridguts = {"across": [], "down": []}

        if results_count == 0 and incomingData["perm_count"] > 150000:
            if incomingData["grand_pass_count"] < 2:
                incomingData["grand_pass_count"] += 1
                receive_grid_specs(incomingData)
                return
            else:
                return

        socketio.sleep(0) #Allows reception of 'please terminate' event to stop endless crunch of difficult specs.

        for word in current_guts:
            gridguts["across"].append(word)

        for i in range( math.ceil( cw_width / 2 ) ):
            gridguts["down"].append("".join(gut[i] for gut in gridguts["across"]))

        current_guts = gridguts["across"] + gridguts["down"]

        #Kick out if not all mandatory words are present.
        if bool(mandatory_words) and is_A_not_fully_contained_by_B(guttedmand_across + guttedmand_down, current_guts):
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
        # if len(set(list(filter(lambda ungutted_list : bool(len(set(ungutted_list).intersection(desirable_combined))), [bank[coord]["ungutted"] for coord in bank.keys()])))) < threshold:
        if not does_putative_grid_truly_meet_desithreshold(threshold, bank, desirable_combined, mandatory_words):
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

        test_result_count+=1
        results_count+=1

        if test_mode:
            print(result)
            print("RESULT COUNT IS:", test_result_count)
        else:
            socketio.sleep(0)
            # print(result)
            socketio.emit("produced grid",
                     {"mandatory_words": mandatory_words, "million_perms_processed": incomingData["perm_count"] / 1000000,
                      "results_count": results_count,
                      "grand_pass_count": incomingData["grand_pass_count"],
                      "perms_or_product": perms_or_product,
                      "result": result})
            socketio.sleep(0)

    socketio.sleep(0)
    socketio.emit('terminated', {"time": time.time()})
    print("Successfully terminated.")

    if test_mode:
        print("RESULT COUNT SO FAR IS:", test_result_count)
        timings.append(test_result_count)
        test_result_count = 0
        count_timings()

global most_recent_timestamp
most_recent_timestamp = ""

global fruit
fruit = "lemon"

@socketio.on('change fruit')
def change_fruit(incomingData):
    global fruit
    fruit = incomingData["fruit"]

@socketio.on('check fruit')
def check_fruit(incomingData):
    global fruit
    send_message({"fruit": fruit})
    # emit("message", {incomingData)

# @socketio.on('my event')
# def handle_my_custom_event(json):
#     emit('my response', json)

@socketio.on('grid specs')
def receive_grid_specs(incomingData):
    print("The client sent these grid specifications: ", incomingData)

    global most_recent_timestamp
    starting_timestamp = time.time()
    most_recent_timestamp = starting_timestamp

    incomingData["perm_count"] = 0

    if "grand_pass_count" not in incomingData.keys():
        print("FIRST TIME RECEPTION")
        incomingData["grand_pass_count"] = 0
        incomingData["results_count"] = 0

        if any(key for key, tally in Counter(gut_words(incomingData["mandatory_words"], False)).items() if tally > 1):
            incomingData["perms_or_product"] = "product"
        else:
            incomingData["perms_or_product"] = "perms"

    if incomingData["grand_pass_count"] == 2:
        if incomingData["perms_or_product"] == "product":
            incomingData["perms_or_product"] = "perms"
        else:
            incomingData["perms_or_product"] = "product"

    if incomingData["threshold"] > len(incomingData["desirable_words_unfiltered"]):
        incomingData["threshold"] = len(incomingData["desirable_words_unfiltered"])

    prepared_resources_across = prepare_helium(incomingData, True, False, False)

    if incomingData["grid_height"] != incomingData["grid_width"]:
        prepared_resources_down = prepare_helium(incomingData, False, False, False)
    else:
        prepared_resources_down = {}
        for key in prepared_resources_across:
            if key not in ["gutted_mand", "mand_words_filtered"]:
                prepared_resources_down[key] = prepared_resources_across[key]
            else:
                prepared_resources_down[key] = []

    helium(socketio, prepared_resources_across, prepared_resources_down, incomingData, automatic_timeout_value, starting_timestamp)

def terminate():
    print("The process will be terminated.")
    global most_recent_timestamp
    most_recent_timestamp = time.time()

def send_message(msg):
    socketio.sleep(0)
    # print('This message is being sent to the client: ', msg)
    socketio.emit('server sent message', msg)

@socketio.on('connect')
def connect(methods=['GET', 'POST']):
    print('Client connected: ')
    socketio.emit('connection confirmed', {"time": time.time()})

@socketio.on("client sent message")
def receive_message(data, methods=['GET', 'POST']):
    send_message({"message": "Server received: " + data["message"]})
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
def client_says_terminate(data, methods=['GET', 'POST']):
    print(data)
    send_message({"message": "Hi client, I hear you want to terminate."})
    terminate()

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
    print("server running...")
    socketio.run(app, debug=False)
