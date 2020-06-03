from utils import print_grid, file_to_list, gut_words, ungut_words, make_dict, sum_dicts, prepare_helium
import time
from threading import Timer

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def helium(specific_timestamp, results, currently_working, guttedwords, dic, desirable_words, threshold, coords, mandatory_words, cw_width, cw_height):

    global most_recent_timestamp
    global perm_count

    if bool(mandatory_words):
        gutted_mand = gut_words(mandatory_words)
        guttedwords = gutted_mand + [gut for gut in guttedwords if gut not in gutted_mand]
        mand_dic = make_dict(gutted_mand, mandatory_words)
        dic = sum_dicts(dic, mand_dic)

    for one_across in guttedwords:
        current_guts = [one_across]

        #Filter out guts that are in putative grid more times that they have fullwords.
        for four_across in filter(lambda gut : len(dic[gut]) > current_guts.count(gut), guttedwords):
            current_guts = [one_across, four_across]

            # Filter out guts that are in putative grid more times that they have fullwords.
            for five_across in filter(lambda gut: len(dic[gut]) > current_guts.count(gut), guttedwords):
                perm_count += 1

                #This terminates the entire Helium fxn, and is triggered when new Post req has come in.
                if specific_timestamp != most_recent_timestamp:
                    print("I'mma terminating the process!")
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

                # print("***")
                # print([bank[coord]["ungutted"] for coord in bank.keys()])
                # print(list(filter(lambda ungutted_list : bool(len(set(ungutted_list).intersection(desirable_words))), [bank[coord]["ungutted"] for coord in bank.keys()])))
                # print(len(list(filter(lambda ungutted_list : bool(len(set(ungutted_list).intersection(desirable_words))), [bank[coord]["ungutted"] for coord in bank.keys()]))))
                # print("***")

                #Kick out if insufficient quantity of desirable_words in putative grid.
                if len(list(filter(lambda ungutted_list : bool(len(set(ungutted_list).intersection(desirable_words))), [bank[coord]["ungutted"] for coord in bank.keys()]))) < threshold:
                    continue

                result = {"summary": [], "grid": []}

                newest_summary = [one_across.upper(), four_across.upper(), five_across.upper()]

                result["summary"] = newest_summary
                print_grid(newest_summary)

                if (bool(mandatory_words)):
                    mandatory_words_copy = mandatory_words[0:]
                    for coord in coords:
                        if bool(set(bank[coord]["ungutted"]).intersection(mandatory_words_copy)):
                            mand_word = list(filter(lambda ungutted : ungutted in mandatory_words_copy, bank[coord]["ungutted"]))[0]
                            mandatory_words_copy.remove(mand_word)

                            newest_line = (coord, mand_word.upper())
                            result["grid"].append(newest_line)
                            print(newest_line)

                        else:
                            ungutted_list = [word.upper() if word in desirable_words else word for word in bank[coord]["ungutted"]]

                            newest_line = (coord, list(filter(lambda word: word.isupper(), ungutted_list)) + list(filter(lambda word: not word.isupper(), ungutted_list)))
                            result["grid"].append(newest_line)
                            print(newest_line)

                else:
                    for coord in coords:
                        ungutted_list = [word.upper() if word in desirable_words else word for word in bank[coord]["ungutted"]]

                        newest_line = (coord, list(filter(lambda word : word.isupper(), ungutted_list)) + list(filter(lambda word : not word.isupper(), ungutted_list)))
                        result["grid"].append(newest_line)
                        print(newest_line)

                results.append(result)


    print("GONNA CHANGE CURRENTLY WORKING BACK TO FALSE")
    currently_working = False

coords = ["1ac", "4ac", "5ac", "1do", "2do", "3do"]
grid_width = 5
grid_height = 5

global currently_working
currently_working = False

global results
results = []

global perm_count
perm_count = 0

global mandatory_words
mandatory_words = []

global most_recent_timestamp
most_recent_timestamp = ""

@app.route('/', methods= ['GET', 'POST'])
def get_message():

    global currently_working
    global results
    global mandatory_words
    global perm_count

    if request.method == "GET":
        return jsonify({"mandatory_words": mandatory_words, "million_perms_processed": perm_count/1000000, "ought_you_continue_get_requests": currently_working, "results": results, "resultcount": len(results)})

    elif request.method == "POST":

        specific_timestamp = time.time()

        global most_recent_timestamp
        most_recent_timestamp = specific_timestamp
        perm_count = 0

        currently_working = True
        results = []

        incomingData = request.get_json()

        data = {
            "banned_words": [],
            "desirable_words_unfiltered": [],
            "threshold": 0
        }

        for key in data.keys():
            data[key] = incomingData[key] if key in incomingData.keys() else data[key]

        if "mandatory_words" in incomingData.keys():
            mandatory_words = incomingData["mandatory_words"]

        def begin_crosswordwizard():
            desirable_words_unfiltered = list(set(data["desirable_words_unfiltered"]).difference(data["banned_words"]))
            (supergut, superdict, desirable_words) = prepare_helium(wordlength, data["banned_words"], desirable_words_unfiltered)
            helium(specific_timestamp, results, currently_working, supergut, superdict, desirable_words, data["threshold"], coords, mandatory_words, grid_width, grid_height)

        wordlength = 5
        # begin_crosswordwizard()
        t = Timer(1.0, begin_crosswordwizard)
        t.start()

        return jsonify({"a message": "Alright, I'm on it!", "million_perms_processed": perm_count/1000000, "mandatory_words": mandatory_words, "ought_you_continue_get_requests": currently_working, "results": results, "resultcount": len(results)})

if __name__ == '__main__':
    app.run(debug=False)

