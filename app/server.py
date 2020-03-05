import json
import os
import random

import bottle
from bottle import HTTPResponse

#global vari
prev = 0
board_width = 1
board_height = 1


@bottle.route("/")
def index():
    return "Your Battlesnake is alive!"


@bottle.post("/ping")
def ping():
    """
    Used by the Battlesnake Engine to make sure your snake is still working.
    """
    return HTTPResponse(status=200)


@bottle.post("/start")
def start():
    """
    Called every time a new Battlesnake game starts and your snake is in it.
    Your response will control how your snake is displayed on the board.
    """
    data = bottle.request.json
    #print("START:", json.dumps(data))

    global board_width, board_height, prev
    board_width = data["board"]["width"]
    board_height = data["board"]["height"]
    directions = [0, 1, 2, 3]
    prev = random.choice(directions)

    response = {"color": "#00FF00",
                "headType": "regular", "tailType": "regular"}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/move")
def move():
    """
    Called when the Battlesnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """
    data = bottle.request.json
    print("turn"+str(data["turn"]))
    # local vari for move
    global prev
    myHead = {"x": data["you"]["body"][0]['x'],
              "y": data["you"]["body"][0]['y']}
    cur_dir=prev

    myHealth = data["you"]["health"]
    foods = data["board"]["food"]
    bodies = []
    for body in data["board"]["snakes"]:
        for parts in body:
            bodies.append(parts)

    directions = ["up", "down", "left", "right"]

    #checkers
    cur_dir=checkCollision(bodies,cur_dir,myHead)

    move = directions[cur_dir]

    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"

    response = {"move": move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )

def checkSolid(bodys, cur_dir, myHead):
    #O(n)
    if cur_dir == 0:
        if myHead["y"]-1 < 0 or {"x": myHead["x"], "y": myHead["y"]-1} in bodys:
            return True
    if cur_dir == 1:
        if myHead["y"]+1 >= board_height or {"x": myHead["x"], "y": myHead["y"]+1} in bodys:
            return True
    if cur_dir == 2:
        if myHead["x"]-1 < 0 or {"x": myHead["x"]-1, "y": myHead["y"]} in bodys:
            return True
    if cur_dir == 3:
        if myHead["x"]+1 >= board_width or {"x": myHead["x"]+1, "y": myHead["y"]} in bodys:
            return True
    return False

def checkCollision(bodys, cur_dir, myHead):
    up = 0
    down = 1
    left = 2
    right = 3
    temp = cur_dir

    """
    old checker
    """
    if checkSolid(bodys, cur_dir, myHead):
        if (temp == 0 and prev == 1) or (temp == 1 and prev == 0):
            if not(checkSolid(bodys, left, myHead) and prev != right):
                temp = left
            elif not(checkSolid(bodys, right, myHead) and prev != left):
                temp = right
        elif (temp == 2 and prev == 3) or (temp == 3 and prev == 2):
            if not(checkSolid(bodys, up, myHead) and prev != down):
                temp = up
            elif not(checkSolid(bodys, down, myHead) and prev != up):
                temp = down
    return temp


@bottle.post("/end")
def end():
    """
    Called every time a game with your snake in it ends.
    """
    data = bottle.request.json
    print("END:", json.dumps(data))
    return HTTPResponse(status=200)


def main():
    bottle.run(
        application,
        host=os.getenv("IP", "0.0.0.0"),
        port=os.getenv("PORT", "8080"),
        debug=os.getenv("DEBUG", True),
    )


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
