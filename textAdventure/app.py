from flask import Flask, render_template, redirect, request, session

app = Flask(__name__, static_folder='static')

import secrets
import os
import uuid

app.secret_key = secrets.token_hex()

class Item: 
    def __init__(self, name, description, restricted, action=None, when_used=None, when_grabbed=None, when_revealed=None, hidden_description=None, environment_effect=None, unlocks=None, used=False): 
        self.name = name
        self.description = description
        self.restricted = restricted
        self.when_grabbed = when_grabbed
        # text to be displayed when the item is grabbed
        self.when_revealed = when_revealed
        # text to be displayed only for unlocked items
        self.environment_effect = environment_effect
        # used {item} to _______
        self.action = action
        # how used tells what to unlock when a certain item is used
        self.unlocks = unlocks if unlocks else []
        self.hidden_description = hidden_description
        # makes sure an item cannot be used to unlock already unlocked items
        self._used = used
        self.when_used = when_used
    
    @property
    def is_used(self): 
        return self._used
    
    @is_used.setter
    def is_used(self, value): 
        if value and not self._used and self.when_used: 
            if self.when_used == 'driftwood_to_torch': 
                driftwood_to_torch()
        self._used = value

    def to_dict(self): 
        unlocks = [item.to_dict() for item in self.unlocks]
        return {'name': self.name, 
                'description': self.description, 
                'restricted': self.restricted, 
                'when_revealed': self.when_revealed, 
                'action': self.action, 
                'environment_effect': self.environment_effect, 
                'hidden_description': self.hidden_description, 
                'unlocks': unlocks, 
                'when_grabbed': self.when_grabbed, 
                '_used': self._used, 
                'when_used': self.when_used}

    @staticmethod
    def from_dict(data): 
        unlocks_dicts = data['unlocks']
        unlocks = [Item.from_dict(unlock) for unlock in unlocks_dicts]
        return Item(name=data['name'], 
                    description=data['description'], 
                    restricted=data['restricted'], 
                    when_revealed=data['when_revealed'], 
                    environment_effect=data['environment_effect'], 
                    action=data['action'], 
                    when_grabbed=data['when_grabbed'], 
                    hidden_description=data['hidden_description'], 
                    unlocks=unlocks, used=data['_used'], 
                    when_used=data['when_used'])

class MapLocation: 
    def __init__(self, concealed, revealed, description=None, items=None): 
        self.concealed = concealed
        self.revealed = revealed
        self.items = items if items else []
        self.description = description
    
    def to_dict(self): 
        items = [item.to_dict() for item in self.items if isinstance(item, Item)]
        return {'concealed': self.concealed, 
                'revealed': self.revealed, 
                'description': self.description, 
                'items': items}

    @staticmethod
    def from_dict(data): 
        item_dicts = data['items']
        items = [Item.from_dict(item) for item in item_dicts]
        return MapLocation(concealed=data['concealed'], 
                           revealed=data['revealed'], 
                           description=data['description'], 
                           items=items)


key_methods = [
    "H: display quick rundown of methods", 
    "M: view map", 
    "I: view inventory", 
    "W, A, S, D: North, West, South, East", 
    "G: grab", 
    "U: use",
    "N: inspect (allows you to view the descriptions of all current items in your inventory)"
]
                    
# coords represent coordinates of current location
def refresh_map(coords): 
    world_map = session.get('world_map')

    # reveal tiles around new spot (concealed --> revealed)
    for i in range(coords[0] - 1, coords[0] + 2): 
        for j in range(coords[1] - 1, coords[1] + 2): 
            # ensures that the element attempting to be accessed is actually on the grid
            if i >= 0 and i < 5 and j >= 0 and j < 5: 
                if isinstance(world_map[i][j], dict): 
                    world_map[i][j]['concealed'] = world_map[i][j]['revealed']
    
    if isinstance(world_map[coords[0]][coords[1]], dict): 
        world_map[coords[0]][coords[1]]['concealed'] = "@"
    
    session['world_map'] = world_map
    session.modified = True


def reset_variables(): 
    story = ["""Your journey begins...
    <br><br>
    <b>Press h for help with commands</b>
    """]

    items = create_items()

    rooms = create_rooms(items[0], items[1], items[2], items[3], items[4])

    world_map = create_map(rooms[0], rooms[1], rooms[2], rooms[3], rooms[4])

    with app.app_context(): 
        session['items'] = [items[0].to_dict(), items[1].to_dict(), items[2].to_dict(), items[3].to_dict(), items[4].to_dict()]

        session['inventory'] = []

        story.append(rooms[2]['description'])

        session['story'] = story

        session['rooms'] = rooms

        session['coords'] = [4, 0]

        session['world_map'] = world_map

        session.modified = True

        session['variables_reset'] = True

        return render_template("play.html", story=story)


def driftwood_to_torch(): 
        items = session.get('items')
        if items: 
            driftwood=items[4]
            driftwood['name']="Torch"
            driftwood['when_grabbed']="You have now created a small torch. "
            driftwood['description']="A makeshift torch consisting of a small piece of driftwood, lit using a matchbox. "
            inventory = session.get('inventory')
            inventory.append(driftwood)
            session['items'][4] = driftwood
            first_room_cave=session.get('rooms')[4]
            first_room_cave['description']="With light from the torch you are able to make out your surroundings. On the opposite end of the cave is a strange altar with an engraving of a flower on top of it. "
            first_room_cave['items'] = []
            session['rooms'][4] = first_room_cave
            session['inventory'] = inventory
            session['world_map'][3][2] = first_room_cave
            session.modified = True
            room_description()

def create_items(): 
    rose = Item(name="Ageless Rose", 
                description="A beautiful rose. Feels as though it will never wilt, no matter how long it is stuffed into your pocket", 
                when_revealed="After entering the gate, the pedestal stands before you. Atop it sits a singular rose in a vase. ", 
                environment_effect="The rose remains in the vase on the pedestal. ", 
                hidden_description="Behind the locked gate you are vaguely able to make out the edges of a pedestal with a strange vase resting atop it. ", 
                when_grabbed="You reach out and gently pick up the rose. Since you don't have a backpack, you pocket it.", 
                restricted=True)
    note = Item(name="Mysterious Note", 
                description="You are amazing <3 ! Thank you so much for playing my game -charlotte (creator)", 
                when_revealed="Tucked carefully beneath the vase, there appears to be a short note addressed to you.<br>Although the overgrowth around you appears ancient, this note and the rose both appear quite fresh...<br>", 
                environment_effect="The note addressed to you peeks out from beneath the vase", 
                when_grabbed="You pick up the letter and gently open it, reading it before pocketing it. ", 
                restricted=True)
    key = Item(name="Rusted Key", 
               description="An ancient, ornate key...maybe it can be used to unlock something?", 
               action="unlock the garden gate. ", 
               when_grabbed="After carefully picking it up and brushing off a substantial amount of dirt, you are able to make out the outline of a rusted key", 
               environment_effect="When you look down at the mossy pathway, you can only barely make out the edges of an old, rusted item. ", 
               restricted=False, 
               unlocks=[rose, note])

    driftwood = Item(name="Driftwood", 
                     description="After lighting the driftwood, you are now mysteriously able to lift it", 
                     hidden_description="Although you are barely able to make out anything in the pitch-black of the cave, you can see the edge of what appears to be a piece of wood...<br>Mysteriously, you are unable to lift it", 
                     restricted=True
                     )
    
    matchbox = Item(name="Matchbox", 
                 description="A mysterious matchbox you found at the cave entrance. I wonder how it got here...", 
                 action ="light the driftwood. ", 
                 when_grabbed="After checking around to make sure its owner isn't nearby, you pocket the matchbox. ", 
                 environment_effect="There appears to be a small matchbox resting atop a small outcropping of boulders. ", 
                 restricted=False, 
                 unlocks=[driftwood], 
                 when_used="driftwood_to_torch", 
                 )

    return [rose, note, key, matchbox, driftwood]


def create_rooms(rose, note, key, matchbox, driftwood): 
    garden_path = MapLocation(concealed="&nbsp;", 
                              revealed="&nbsp;", 
                              description="You see in front of you a mysterious wandering garden pathway lined with all sorts of plants and flowers. ", 
                              items=[key])
    secret_garden = MapLocation(concealed="?", 
                                revealed="&nbsp;", 
                                description="You find yourself at the center of an ancient, magical garden. Strange palm trees seem to lean towards you as you approach the center. ", 
                                items=[rose, note])
    start_location = MapLocation(concealed="@", 
                                 revealed="&nbsp;", 
                                 description="You see a garden in front of you, and a gravel path appears to beckon you further in...")
    cave_entrance = MapLocation(concealed="?", 
                                revealed="&nbsp;", 
                                description="In front of you is an ominous, looming cave. Stalactites hang from its foor and it appears to beckon you further inwards...", 
                                items=[matchbox])
    first_room_cave = MapLocation(concealed="?", 
                                  revealed="&nbsp;", 
                                  description="After entering the cave you are barely able to make out your surroundings. ", 
                                  items=[driftwood])
    return [garden_path.to_dict(), secret_garden.to_dict(), start_location.to_dict(), cave_entrance.to_dict(), first_room_cave.to_dict()]


def create_map(garden_path, secret_garden, start_location, cave_entrance, first_room_cave): 
    return [
            ['?', '?', '?', MapLocation.to_dict(MapLocation(concealed="?", revealed="#")), MapLocation.to_dict(MapLocation(concealed="?", revealed="#"))], 
            [MapLocation.to_dict(MapLocation(concealed="?", revealed="#")), MapLocation.to_dict(MapLocation(concealed="?", revealed="#")), '?', '?', MapLocation.to_dict(MapLocation(concealed="?", revealed="#"))], 
            [secret_garden, MapLocation.to_dict(MapLocation(concealed="?", revealed="#")), '?', MapLocation.to_dict(MapLocation(concealed="?", revealed="#")), '?'], 
            [garden_path, cave_entrance, first_room_cave, MapLocation.to_dict(MapLocation(concealed="?", revealed="#")), '?'], 
            [start_location, MapLocation.to_dict(MapLocation(concealed="#", revealed="#")), '?', '?', '?']
        ]

def room_description(): 
    world_map = session.get('world_map')
    
    coords = session.get('coords', [4,0])
    story = session.get('story', ["""Your journey begins...
    <br><br>
    <b>Press h for help with commands</b>
    """])

    current_room = MapLocation.from_dict(world_map[coords[0]][coords[1]])

    story.append(current_room.description)

    if current_room.items: 
        for item in current_room.items: 
            if not item.restricted and item.environment_effect: 
                story.append(item.environment_effect)
            elif item.restricted and item.hidden_description: 
                story.append(item.hidden_description)

    session['story'] = story

@app.before_request
def assign_user_id(): 
    if 'user_id' not in session: 
        session['user_id'] = str(uuid.uuid4())

@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/play')
def play(): 
    while not session.get('variables_reset'): 
        reset_variables()
    story = session.get('story')
    return render_template("play.html", story=story)


# routes from key presses (will be reused throughout story)
@app.route('/display_map')
def display_map(): 
    story = session.get('story')
    world_map = session.get('world_map')
    this_row = ""

    map_display = ""

    for row in world_map: 
        for cell in row: 
            if isinstance(cell, dict): 
                this_row += cell['concealed'] + "&nbsp;&nbsp;"
            else: 
                this_row += cell + "&nbsp;&nbsp;"
        map_display += this_row + "<br>"
        this_row = ""
    
    map_display += "key: <br>@: current location<br>?: not yet discovered<br>#: wall<br>&nbsp;: open area/able to go through"

    story.append(map_display)

    session['story'] = story

    session.modified = True

    return render_template("play.html", story=story)


@app.route('/display_inventory')
def display_inventory(): 
    inventory = session.get('inventory', [])
    story = session.get('story')

    if len(inventory) == 0: 
        story.append("Inventory is empty")
    else: 
        inventory_display = "Inventory: <br><ul>"
        for item in inventory: 
            if isinstance(item, dict): 
                this_item = Item.from_dict(item)
                inventory_display += f"<li>{this_item.name}</li>"
        inventory_display += "</ul>"
        story.append(inventory_display)
    
    session['story'] = story

    session.modified = True

    return render_template("play.html", story=story)


@app.route('/help')
def help(): 
    story = session.get('story')

    for method in key_methods: 
        story.append(method + "<br>")

    session['story'] = story

    session.modified = True

    return render_template("play.html", story=story)


def move(hv): 
    coords = session.get('coords', [4, 0])
    story = session.get('story')
    world_map = session.get('world_map')
    
    new_coords = [coords[0], coords[1]]

    if hv == "N": 
        new_coords[0] -= 1
    elif hv == "S": 
        new_coords[0] += 1
    elif hv == "W": 
        new_coords[1] -= 1
    elif hv == "E": 
        new_coords[1] += 1
    
    if not (0 <= new_coords[0] < 5 and 0 <= new_coords[1] < 5): 
        story.append(f'You cannot move {hv} (out of map scope)')
        session['story'] = story
        session.modified = True
        return render_template("play.html", story=story)
    
    new_location = world_map[new_coords[0]][new_coords[1]]

    if not isinstance(new_location, dict): 
        story.append("This part of the map has not yet been developed...wait for future releases to explore here!")
        session['story'] = story
        session.modified = True
        return render_template("play.html", story=story)

    if new_location['revealed'] == "#": 
        story.append(f"You cannot move {hv} (blocked by wall: #)")
        session['story'] = story
        session.modified = True
        return render_template("play.html", story=story)
    
    session['coords'] = new_coords
    session.modified = True
    world_map[new_coords[0]][new_coords[1]]['concealed'] = "@"
    session['world_map'] = world_map
    session['story'] = story
    
    session.modified = True

    room_description()

    refresh_map(new_coords)

    return render_template("play.html", story=story)


@app.route('/north')
def north(): 
    return move("N")


@app.route('/west')
def west(): 
    return move("W")


@app.route('/south')
def south(): 
    return move("S")


@app.route('/east')
def east(): 
    return move("E")


@app.route('/grab')
def grab(): 
    coords = session.get('coords')
    world_map = session.get('world_map')
    story = session.get('story')
    inventory = session.get('inventory')

    current_location = MapLocation.from_dict(world_map[coords[0]][coords[1]])

    if not current_location.items: 
        story.append("There is nothing to grab here.")
        session['story'] = story
        return render_template("play.html", story=story)
    
    # items detected
    nothing_added = True

    for item in current_location.items: 
        if not item.restricted and item.to_dict() not in inventory: 
            if isinstance(item, Item): 
                inventory.append(item.to_dict())
                current_location.items.remove(item)
            if item.when_grabbed: 
                story.append(item.when_grabbed)
            story.append(f"Added to inventory: {item.name}: {item.description}<br>")
            nothing_added = False
    

    if nothing_added: 
        story.append("There is nothing you can grab here at the moment")
    
    world_map[coords[0]][coords[1]] = current_location.to_dict()

    session['world_map'] = world_map
    session['story'] = story
    session['inventory'] = inventory

    session.modified = True

    return render_template("play.html", story=story)


@app.route('/use')
def use(): 
    coords = session.get('coords')
    inventory = session.get('inventory')
    story = session.get('story')
    world_map = session.get('world_map')

    current_location = MapLocation.from_dict(world_map[coords[0]][coords[1]])

    # I bet that this could be done more efficiently but I don't really want to rn :)
    already_used = False

    for item in inventory: 

        for unlock in item['unlocks']: 

            for i in range(len(current_location.items)): 

                if current_location.items[i].to_dict() == unlock: 
                    if not already_used and not item['_used']: 
                        story.append(f"Successfully used {item['name']} to {item['action']}")
                        already_used = True
                    item = Item.from_dict(item)
                    item.is_used = True
                    if item.when_used: 
                        inventory=session.get('inventory')
                        story=session.get('story')
                        world_map=session.get('world_map')
                        current_location = MapLocation.from_dict(world_map[coords[0]][coords[1]])
                    if current_location.items and i < len(current_location.items): 
                        if isinstance(current_location.items[i], Item): 
                            current_location.items[i].restricted = False
                            if current_location.items[i].when_revealed: 
                                story.append(current_location.items[i].when_revealed)
                    world_map[coords[0]][coords[1]] = current_location.to_dict()

    if not already_used: 
        story.append("You cannot use that item here")
    
    session['world_map'] = world_map
    session['story'] = story

    session.modified = True

    return render_template("play.html", story=story)


@app.route('/inspect')
def inspect(): 
    inventory = session.get('inventory')
    story = session.get('story')

    if len(inventory) == 0: 
        story.append("You do not have any items in your inventory")
        session['story'] = story
        session.modified = True
        return render_template("play.html", story=story)
    
    text = ""
    text += "Here are your items: <br>"
    for item in inventory: 
        text += f"&nbsp;&nbsp;{item['name']}: {item['description']}<br>"
    
    story.append(text)

    session['story'] = story

    session.modified = True

    return render_template("play.html", story=story)


@app.route('/clear')
def clear(): 
    story = session['story']
    story.clear()
    story.append("Workspace cleared.")
    session['story'] = story

    session.modified = True

    return render_template("play.html", story=story)


if __name__ == '__main__':
    # chatgpt code to get render (web application publishing service) to display my webpage by fixing the port number
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)