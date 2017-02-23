# -*- coding: cp1250 -*-
from itertools import combinations
from time import time


def single_round(player_base, pods):
    """
    Simulates one tournament round. Players
    inside each pod encounter each other.
    """
    for pod in pods:
        for p1 in pod:
            for p2 in pod:
                if not p1 == p2 and p2 not in player_base[p1]:
                    player_base[p1].append(p2)
    return player_base

def pod_size_distribution(total_players):
    """
    Returns pod sizes for a given number of players.
    We assume:
        - total number of players is more than 5,
        - all players must participate  each round,
        - 4-man pods are prioritized.
    """
    pod_sizes = []
    pod_players = 0

    while pod_players < total_players:
        pod_players += 4
        pod_sizes.append(4)

    if pod_players == total_players:
        return pod_sizes

    while True:
        pod_players -= 4
        pod_sizes.remove(4)

        while pod_players < total_players:
            pod_players += 3
            pod_sizes.append(3)

        if pod_players == total_players:
            return pod_sizes

def grade(player_base):
    """
    Grades current player base by average number of
    encountered opponents for each player.
    """
    total_players = len(player_base.keys())
    total_score = 0

    for player in player_base.keys():
        total_score += float(len(player_base[player])) / float(total_players - 1)

    return float(total_score) / float(total_players)

def pb(total_players):
    """
    Creates player base dictionary. Keys represent players,
    while values represent opponents the player has already
    encountered.
    """
    return dict((i, []) for i in range(total_players))

def homebrew_copy(player_base):
    """
    Creates a copy of the player base. This is needed to
    avoid mutating the original player base dictionary.
    """
    player_base_copy = dict()

    for key in player_base.keys():
        player_base_copy[key] = []
        for sub_value in player_base[key]:
            player_base_copy[key].append(sub_value)

    return player_base_copy

def matchup(player_base, all_configurations, experiment=False, increase=1.3):
    """
    Offers best matchup configuration given current player base.

    Can also be used to offer "good enough" matchup configuration (experimental).
    """
    base_grade = grade(player_base)
    max_grade = -1
    best_configuration = None
    best_position = None

    for i, configuration in enumerate(all_configurations):
        current_player_base = homebrew_copy(player_base)
        current_player_base = single_round(current_player_base, configuration)
        current_grade = grade(current_player_base)

        if experiment and (current_grade > base_grade * increase):
            max_grade = current_grade
            best_configuration = configuration
            best_position = i
            break

        if current_grade > max_grade:
            max_grade = current_grade
            best_configuration = configuration
            best_position = i

    print "\t\tNajboljsa konfiguracija najdena v prvih {} %".format(
        (float(best_position) / float(len(all_configurations))) * 100)
    print "\t\tPo vrsti je: {}-ta".format(best_position)
    print "\t\tStevilo vseh konfiguracij: {}".format(len(all_configurations))
    print ""

    return best_configuration

def convert_to_list(config):
    """
    Converts given tuple configuration into a list
    for easier handling.
    """
    converted_list = []

    try:
        for tuple_i in config:
            for tuple_j in tuple_i:
                converted_list.extend(list(tuple_j))
    except TypeError:
        for tuple_i in config:
            converted_list.extend(list(tuple_i))

    return converted_list

def printp(player_base):
    """
    Prettier player_base output.
    """
    for player in player_base.keys():
        print "Igralec {} je igral proti igralcem {}".format(player, player_base[player])

def rec(player_list, config, pod_sizes):
    """
    Recursively finds all possible matchup configurations for
    a given list of players and pod size configuration.
    """
    if not pod_sizes:
        return config

    cur_pod_size = pod_sizes.pop()

    if config:
        new_config = []

        for config_element in config:
            remaining_players = list(set(player_list) - set(convert_to_list(config_element)))

            for combo in combinations(remaining_players, cur_pod_size):
                new_config_element = list(config_element)
                new_config_element.append(combo)
                new_config.append(tuple(new_config_element))

        return rec(player_list, new_config, pod_sizes)

    else:
        config = [(i, ) for i in combinations(player_list, cur_pod_size)]
        return rec(player_list, config, pod_sizes)

base_grade = input("Vpisi zeljeno oceno (v procentih) \n- 100 pomeni da mora "
                   "povprecni igralec igrati proti vsem nasprotnikom \n"
                   "- 50 pomeni da mora igrati proti polovici nasprotnikov \n"
                   "Zeljena ocena: ")
base_grade = float(base_grade) / 100.0

for i in range(6, 16):
    player_base = pb(i)
    number_of_rounds = 0

    player_list = player_base.keys()
    pod_sizes = pod_size_distribution(i)

    time_1 = time()
    all_configurations = rec(player_list, [], pod_sizes)
    print "Funkcija all_configurations(): {} sekund".format(time() - time_1)
    print

    while grade(player_base) < base_grade:

        time_1 = time()
        m = matchup(player_base, all_configurations)
        print "\tFunkcija matchup(): {} sekund".format(time() - time_1)

        player_base = single_round(player_base, m)
        number_of_rounds += 1
        print "\tTrenutna ocena: {}".format(grade(player_base))
        print ""

    print "------------------------------------------------------------------------------------------"
    print ("Ce je igralcev {}, potem povprecni igralec igra proti {}% nasprotnikov "
           "po {} rundah.").format(i, base_grade * 100, number_of_rounds)
    print "------------------------------------------------------------------------------------------"
    printp(player_base)
    print "------------------------------------------------------------------------------------------"
