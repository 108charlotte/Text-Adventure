from flask import Flask, render_template, redirect, request

app = Flask(__name__, static_folder='static')

class Item: 
    def __init__(self, name, description, restricted, action_description=None, revealed_text=None, unlocks=None): 
        self.name = name
        self.description = description
        self.restricted = restricted
        self.revealed_text = revealed_text
        self.action_description = action_description
        self.unlocks = unlocks if unlocks else []
    
    def __repr__(self): 
        return f"{self.name}: {self.description}"

class MapLocation: 
    def __init__(self, concealed, revealed, description=None, item_description=None, items=None): 
        self.concealed = concealed
        self.revealed = revealed
        self.description = description
        self.item_description = item_description if item_description else ""
        self.items = items if items else []
    
    def __repr__(self): 
        return f"{self.concealed}, {self.revealed}"

# create items
rose = Item(name="Ageless Rose", description="A beautiful rose. Feels as though it will never wilt, no matter how long it is stuffed into your pocket", revealed_text="After the gate slowly creaks open, you are able to make out a vase resting atop the pedestal, and within it is a single rose. ", restricted=True)
note = Item(name="Mysterious Note", description="You are amazing <3 always be you, even when things get stressful! -charlotte (creator)", revealed_text="Beneath the vase, there appears to be a short note addressed to you. ", restricted=True)
key = Item(name="Rusted Key", description="An ancient, ornate key...maybe it can be used to unlock something?", action_description="unlock the garden gate. The pedestal stands before you, atop it the rose and the note", revealed_text="After carefully picking it up and brushing off a substantial amount of dirt, you are able to make out the outline of a rusted key", restricted=False, unlocks=[rose, note])

# create rooms
garden_path = MapLocation(concealed="&nbsp;", revealed="&nbsp;", description="You see in front of you a mysterious wandering garden pathway lined with all sorts of plants and flowers. ", item_description="When you look down at the mossy pathway, you can only barely make out the edges of an old, rusted item...", items=[key])
secret_garden = MapLocation(concealed="?", revealed="&nbsp;", description="", item_description="Behind an ornate gate you are able to make out the outline of what appears to be a pedestal...", items=[rose, note])
start_location = MapLocation(concealed="@", revealed="&nbsp;", description="You see a garden in front of you, and a gravel path appears to beckon you further in...")
cave_entrance = MapLocation(concealed="?", revealed="&nbsp;", description="In front of you is an ominous, looming cave. Stalactites hang from its foor and it appears to beckon you further inwards...")

story = [
    """Your journey begins...
    <br><br>
    <b>Press h for help with commands</b>
    """, 
]

key_methods = [
    "H: display quick rundown of methods", 
    "M: view map", 
    "I: view inventory", 
    "W, A, S, D: North, West, South, East", 
    "G: grab", 
    "U: use",
    "N: inspect (allows you to view the descriptions of all current items in your inventory)"
]

map = [
    ['?', '?', '?', MapLocation(concealed="?", revealed="#"), MapLocation(concealed="?", revealed="#")], 
    [MapLocation(concealed="?", revealed="#"), MapLocation(concealed="?", revealed="#"), '?', '?', MapLocation(concealed="?", revealed="#")], 
    [secret_garden, MapLocation(concealed="?", revealed="#"), '?', MapLocation(concealed="?", revealed="#"), '?'], 
    [garden_path, cave_entrance, '?', MapLocation(concealed="?", revealed="#"), '?'], 
    [start_location, MapLocation(concealed="?", revealed="#"), '?', '?', '?']
]

inventory = []

def locate_user(): 
    coords = []
    # find current location in map
    for i in range(len(map)): 
        for j in range(len(map[i])): 
            if isinstance(map[i][j], MapLocation): 
                if map[i][j].concealed == "@": 
                    coords.append(i)
                    coords.append(j)
                    return coords

# coords represent coordinates of current location
def refresh_map(coords): 
    # reveal tiles around new spot (concealed --> revealed)
    for i in (coords[0] - 2, coords[0] - 1, coords[0], coords[0] + 1): 
        for j in (coords[1] - 2, coords[1] - 1, coords[1], coords[1] + 1): 
            # ensures that the element attempting to be accessed is actually on the grid
            if i >= 0 and i < 5 and j >= 0 and j < 5: 
                if isinstance(map[i][j], MapLocation): 
                    map[i][j].concealed = map[i][j].revealed


@app.route('/')
def welcome():
    return render_template("welcome.html")


@app.route('/play')
def play(): 
    if len(story) == 1 and story[0] == """Your journey begins...
    <br><br>
    <b>Press h for help with commands</b>
    """: 
        new_room()
    return render_template("play.html", story=story)


# routes from key presses (will be reused throughout story)
@app.route('/display_map')
def display_map(): 
    this_row = ""
    for i in range(len(map)): 
        for j in range(len(map[i])): 
            if isinstance(map[i][j], MapLocation): 
                this_row += map[i][j].concealed + "&nbsp;&nbsp;"
            else: 
                this_row += map[i][j] + "&nbsp;&nbsp;"
        story.append(this_row)
        this_row = ""
    
    story.append("key: <br>@: current location<br>?: not yet discovered<br>#: wall<br>&nbsp;: open area/able to go through")

    return render_template("play.html", story=story)


@app.route('/display_inventory')
def display_inventory(): 
    if len(inventory) == 0: 
        story.append("Inventory is empty")
    else: 
        story.append("Inventory: ")
        for i in range(len(inventory)): 
            story.append(inventory[i] + "<br>")
        return render_template("play.html", story=story)


@app.route('/help')
def help(): 
    for i in range(len(key_methods)): 
        story.append(key_methods[i] + "<br>")

    return render_template("play.html", story=story)

@app.route('/north')
def north(): 
    coords = locate_user()

    if len(coords) == 0: 
        story.clear()
        story.append("I'M SO SORRY--there appears to have been an error locating your player. You are being placed back at the start space for now...")
        map[4][0].concealed = "@"
        coords = locate_user()

    # check if north is blocked or out of scope
    north_coord = coords[0]

    if north_coord == 0: 
        story.append("You cannot move north (out of map scope)")
        return render_template("play.html", story=story)

    if map[north_coord - 1][coords[1]].revealed == "#": 
        story.append("You cannot move north (blocked by wall: #)")
        return render_template("play.html", story=story)

    refresh_map(coords)

    # move @ to new concealed spot
    map[north_coord - 1][coords[1]].concealed = "@"

    new_room()

    return display_map()


@app.route('/west')
def west(): 
    coords = locate_user()

    if len(coords) == 0: 
        story.clear()
        story.append("I'M SO SORRY--there appears to have been an error locating your player. You are being placed back at the start space for now...")
        map[4][0].concealed = "@"
        coords = locate_user()

    # check if west is blocked or out of scope
    west_coord = coords[1]

    if west_coord == 0: 
        story.append("You cannot move west (out of map scope)")
        return render_template("play.html", story=story)

    if map[coords[0]][west_coord - 1].revealed == "#": 
        story.append("You cannot move west (blocked by wall: #)")
        return render_template("play.html", story=story)

    refresh_map(coords)

    # move @ to new concealed spot
    map[coords[0]][west_coord - 1].concealed = "@"

    new_room()

    return display_map()


@app.route('/south')
def south(): 
    coords = locate_user()

    if len(coords) == 0: 
        story.clear()
        story.append("I'M SO SORRY--there appears to have been an error locating your player. You are being placed back at the start space for now...")
        map[4][0].concealed = "@"
        coords = locate_user()

    # check if south is blocked or out of scope
    south_coord = coords[0]

    if south_coord == 4: 
        story.append("You cannot move south (out of map scope)")
        return render_template("play.html", story=story)

    if map[south_coord + 1][coords[1]].revealed == "#": 
        story.append("You cannot move south (blocked by wall: #)")
        return render_template("play.html", story=story)

    refresh_map(coords)

    # move @ to new concealed spot
    map[south_coord + 1][coords[1]].concealed = "@"

    new_room()

    return display_map()


@app.route('/east')
def east(): 
    coords = locate_user()

    if len(coords) == 0: 
        story.clear()
        story.append("I'M SO SORRY--there appears to have been an error locating your player. You are being placed back at the start space for now...")
        map[4][0].concealed = "@"
        coords = locate_user()

    # check if east is blocked or out of scope
    east_coord = coords[1]

    if east_coord == 4: 
        story.append("You cannot move east (out of map scope)")
        return render_template("play.html", story=story)

    if map[coords[0]][east_coord + 1].revealed == "#": 
        story.append("You cannot move east (blocked by wall: #)")
        return render_template("play.html", story=story)

    refresh_map(coords)

    # move @ to new concealed spot
    map[coords[0]][east_coord + 1].concealed = "@"

    new_room()

    return display_map()


def new_room(): 
    coords = locate_user()
    story.append(map[coords[0]][coords[1]].description)
    if map[coords[0]][coords[1]].items and any(item not in inventory for item in map[coords[0]][coords[1]].items): 
        story.append(map[coords[0]][coords[1]].item_description)


@app.route('/grab')
def grab(): 
    coords = locate_user()
    current_location = map[coords[0]][coords[1]]
    if not current_location.items: 
        story.append("There is nothing to grab here.")
        return render_template("play.html", story=story)
    
    # items detected
    nothing_added = True

    for item in current_location.items: 
        if not item.restricted and item not in inventory: 
            inventory.append(item)
            # unlock items (THIS WAS A BUG--grab should not unlock items)
            # if len(map[coords[0]][coords[1]].items[i].unlocks) != 0: 
                # for j in range(len(map[coords[0]][coords[1]].items[i].unlocks)): 
                    # map[coords[0]][coords[1]].items[i].unlocks[j].restricted = False
            story.append(item.revealed_text)
            story.append(f"Added to inventory: {item}<br>")
            nothing_added = False
        
    if nothing_added: 
        story.append("There is nothing you can grab here at the moment")
    return render_template("play.html", story=story)


@app.route('/use')
def use(): 
    coords = locate_user()
    already_used = False
    # I bet that this could be done more efficiently but I don't really want to rn :)
    for i in range(len(inventory)): 
        for j in range(len(inventory[i].unlocks)): 
            for k in range(len(map[coords[0]][coords[1]].items)): 
                if map[coords[0]][coords[1]].items[k] == inventory[i].unlocks[j]: 
                    if not already_used: 
                        story.append(f"Successfully used {inventory[i].name} to {inventory[i].action_description}")
                        already_used = True
                    inventory[i].unlocks[j].restricted = False
    return render_template("play.html", story=story)


@app.route('/inspect')
def inspect(): 
    if len(inventory) == 0: 
        story.append("You do not have any items in your inventory")
        return redirect("/play")
    story.append("Here are your items: ")
    for i in range(len(inventory)): 
        story.append(inventory[i])
    return redirect("/play")


@app.route('/clear')
def clear(): 
    story.clear()
    story.append("Workspace cleared.")
    return render_template("play.html", story=story)


if __name__ == '__main__':
    app.run(debug=True)