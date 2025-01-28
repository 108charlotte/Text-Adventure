# Python Text Adventure
## Description
A fun python-backend text adventure game set in a 5x5 world. Features include a map which gradually reveals as players explore, an updating inventory which keeps track of a player's current items, an inspect feature which allows them to see the descriptions of all items in their inventory, a clear feature allowing them to refresh the screen, WASD for moving across the map, and ability to grab and use items. 

## How to Install + Run
1. Navigate to the textAdventure directory ("cd textAdventure")
2. Install requirements.txt using "pip install requirements.txt"
3. Run project using "python app.py"

## Tech Stack
Frontent: HTML, CSS, Javascript
Backend: Python (Flask)
Hosting: Render

## Credits
Since I am not fluent in Javascript or CSS, the basis of the Javascript key input and the CSS typing animation for the welcome page were both created by chatGPT. I also used chatGPT to learn how to use sessions to store data in flask and for general debugging purposes. One example of debugging with chatGPT was when I kept getting an "Item object not JSON serializable" error, but I had already looked through my code and it looked like everything was converted. In this instance, I asked chatGPT to look through my code and find where the error was coming from since there were no hints in the error message. 