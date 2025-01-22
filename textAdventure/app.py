from flask import Flask, render_template, redirect, request

app = Flask(__name__, static_folder='static')

story = [
    """Your journey begins...
    <br><br>
    You wake up suddenly to sunlight streaming through a nearby window and a mild headache. You do not recall where you are or how you got here. You think for a second--you actually can't remember anything about your life at all...
    <br><br>
    <b>Press enter to start the tutorial...</b>
    """, 
]

map = [
    ['?', '?', '?', '?', '?'], 
    ['?', '?', '?', '?', '?'], 
    ['?', '?', '?', '?', '?'], 
    ['?', '?', '?', '?', '?'], 
    ['?', '?', '?', '?', '?']
]

inventory = []

@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/play', methods=["GET", "POST"])
def play(): 
    if request.method == "GET": 
        return render_template("play.html", story=story)
    
    return redirect("/tutorial")

@app.route('/tutorial')
def tutorial(): 
    tutorial_loading="tutorial loading..."
    story.append(tutorial_loading)
    story.append("press m to see the map")
    return render_template("play.html", story=story)

# routes from key presses (will be reused throughout story)
@app.route('/display_map')
def display_map(): 
    this_row = ""
    for i in range(len(map)): 
        for j in range(len(map[i])): 
            this_row += map[i][j] + "&nbsp;&nbsp;"
        story.append(this_row)
        this_row = ""

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

if __name__ == '__main__':
    app.run(debug=True)