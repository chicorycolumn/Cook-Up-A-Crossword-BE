from utils import print_grid, file_to_list, gut_words, ungut_words, make_dict, sum_dicts, prepare_helium, test_data
import time
import eventlet
import socketio
import threading

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
should_terminate = False

def helium(sio, starting_timestamp, guttedwords, gutted_mand, dic, desirable_words, threshold, coords, mandatory_words, cw_width, cw_height, automatic_timeout_value, number_of_for_loops, current_guts):

    global most_recent_timestamp
    global perm_count
    global test_mode
    global result_count
    global should_terminate

    sio.sleep(0)

    for one_across in guttedwords:
        current_guts = [one_across]

        #Filter out guts that are in putative grid more times that they have fullwords.
        for four_across in filter(lambda gut : len(dic[gut]) > current_guts.count(gut), guttedwords):
            current_guts = [one_across, four_across]

            # Filter out guts that are in putative grid more times that they have fullwords.
            for five_across in filter(lambda gut: len(dic[gut]) > current_guts.count(gut), guttedwords):


    # if number_of_for_loops >=1:
    #     for word in filter(lambda gut: len(dic[gut]) > current_guts.count(gut), guttedwords):
    #
    #         if should_terminate:
    #             return
    #
    #         current_guts_copy = current_guts[:]
    #         current_guts_copy.append(word)
    #
    #         helium(sio, starting_timestamp, guttedwords, gutted_mand, dic, desirable_words, threshold, coords, mandatory_words,
    #                cw_width, cw_height, automatic_timeout_value, number_of_for_loops-1, current_guts_copy)
    # else:
    #
    #     one_across = current_guts[0]
    #     four_across = current_guts[1]
    #     five_across = current_guts[2]


                perm_count += 1

                #This terminates the entire Helium fxn, and is triggered when new Post req has come in.
                if starting_timestamp != most_recent_timestamp:
                    print("The process has been terminated.")
                    sio.emit("message", {"message": "The server confirms that the process has been terminated."})
                    should_terminate = True
                    return

                # This terminates the entire Helium fxn, and is triggered after x seconds.
                if starting_timestamp + automatic_timeout_value <= time.time():
                    print("Terminated by the automatic timeout that the developer set, which was %d seconds." % automatic_timeout_value)
                    sio.emit("message", {"message": "Terminated by the automatic timeout that the developer set, which was %d seconds." % automatic_timeout_value})
                    should_terminate = True
                    return

                one_down = one_across[0] + four_across[0] + five_across[0]
                two_down = one_across[1] + four_across[1] + five_across[1]
                three_down = one_across[2] + four_across[2] + five_across[2]
                current_guts = [one_across, four_across, five_across, one_down, two_down, three_down]

                #Kick out if not all mandatory words are present.
                if bool(mandatory_words) and bool(len(set(gutted_mand).difference(current_guts))):
                    continue

                # Kick out if any new guts in putative grid more times that they have fullwords.
                # This also kicks out if the newly formed down guts have NO valid full words.
                if len(list(filter(lambda gut: ( len(dic[gut]) if gut in dic.keys() else 0 ) < current_guts.count(gut), [one_down, two_down, three_down]))):
                    continue

                bank = {
                    "1ac": {"gutted": one_across, "ungutted": dic[one_across] if one_across in dic.keys() else []},
                    "4ac": {"gutted": four_across, "ungutted": dic[four_across] if four_across in dic.keys() else []},
                    "5ac": {"gutted": five_across, "ungutted": dic[five_across] if five_across in dic.keys() else []},
                    "1do": {"gutted": one_down, "ungutted": dic[one_down] if one_down in dic.keys() else []},
                    "2do": {"gutted": two_down, "ungutted": dic[two_down] if two_down in dic.keys() else []},
                    "3do": {"gutted": three_down, "ungutted": dic[three_down] if three_down in dic.keys() else []}
                }

                #Kick out if insufficient quantity of desirable_words in putative grid.
                if len(list(filter(lambda ungutted_list : bool(len(set(ungutted_list).intersection(desirable_words))), [bank[coord]["ungutted"] for coord in bank.keys()]))) < threshold:
                    continue

                result = {"summary": [], "grid": []}
                newest_summary = [one_across.upper(), four_across.upper(), five_across.upper()]
                result["summary"] = newest_summary

                if (bool(mandatory_words)):
                    mandatory_words_copy = mandatory_words[0:]
                    for coord in coords:
                        if bool(set(bank[coord]["ungutted"]).intersection(mandatory_words_copy)):
                            mand_word = list(filter(lambda ungutted : ungutted in mandatory_words_copy, bank[coord]["ungutted"]))[0]
                            mandatory_words_copy.remove(mand_word)
                            newest_line = (coord, mand_word.upper())
                            result["grid"].append(newest_line)

                        else:
                            ungutted_list = [word.upper() if word in desirable_words else word for word in bank[coord]["ungutted"]]
                            newest_line = (coord, list(filter(lambda word: word.isupper(), ungutted_list)) + list(filter(lambda word: not word.isupper(), ungutted_list)))
                            result["grid"].append(newest_line)

                else:
                    for coord in coords:
                        ungutted_list = [word.upper() if word in desirable_words else word for word in bank[coord]["ungutted"]]
                        newest_line = (coord, list(filter(lambda word : word.isupper(), ungutted_list)) + list(filter(lambda word : not word.isupper(), ungutted_list)))
                        result["grid"].append(newest_line)

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




coords = ["1ac", "4ac", "5ac", "1do", "2do", "3do"]
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
    starting_timestamp = time.time()
    global most_recent_timestamp
    most_recent_timestamp = starting_timestamp
    perm_count = 0

    data = {
        "banned_words": [],
        "desirable_words_unfiltered": [],
        "threshold": 0
    }

    for key in data.keys():
        data[key] = incomingData[key] if key in incomingData.keys() else data[key]

    if "mandatory_words" in incomingData.keys():
        mandatory_words = incomingData["mandatory_words"]

    wordlength = 5
    automatic_timeout_value = 10

    desirable_words_unfiltered = list(set(data["desirable_words_unfiltered"]).difference(data["banned_words"]))

    (supergut, superdict, desirable_words) = prepare_helium(wordlength, data["banned_words"],
                                                            desirable_words_unfiltered)


    if bool(mandatory_words):
        gutted_mand = gut_words(mandatory_words)
        supergut = gutted_mand + [gut for gut in supergut if gut not in gutted_mand]
        mand_dic = make_dict(gutted_mand, mandatory_words)
        superdict = sum_dicts(superdict, mand_dic)

    helium(sio, starting_timestamp, supergut, gutted_mand, superdict, desirable_words, data["threshold"],
           coords, mandatory_words, grid_width, grid_height, automatic_timeout_value, 3, [])

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

if test_mode:
    receive_grid_specs(None, test_data)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)