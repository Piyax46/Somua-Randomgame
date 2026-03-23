import json
import os
import random
from flask import Blueprint, jsonify

heroes_bp = Blueprint('heroes', __name__)

# Load hero data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def load_dota2():
    with open(os.path.join(DATA_DIR, 'dota2.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def load_lol():
    with open(os.path.join(DATA_DIR, 'lol.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


from flask import render_template

@heroes_bp.route('/heroes')
def heroes_page():
    dota2 = load_dota2()
    lol = load_lol()
    return render_template('heroes.html',
                           dota2_heroes=dota2['heroes'],
                           dota2_roles=dota2['roles'],
                           lol_champions=lol['champions'],
                           lol_lanes=lol['lanes'])


@heroes_bp.route('/heroes/dota2/random', methods=['POST'])
def dota2_random():
    data = load_dota2()
    hero = random.choice(data['heroes'])
    return jsonify({'hero': hero})


@heroes_bp.route('/heroes/dota2/role', methods=['POST'])
def dota2_role():
    data = load_dota2()
    role = random.choice(data['roles'])
    return jsonify({'role': role})


@heroes_bp.route('/heroes/lol/random', methods=['POST'])
def lol_random():
    data = load_lol()
    champ = random.choice(data['champions'])
    return jsonify({'champion': champ})
