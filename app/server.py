import json
import os
import random

import bottle
from bottle import HTTPResponse

# [0=up,1=down,2=left,3=right]
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

    global board_width, board_height, prev
    board_width = data["board"]["width"]
    board_height = data["board"]["height"]
    snakes = data["board"]["snakes"]

    directions = [0, 1, 2, 3]
    prev = random.choice(directions)

    # print(checkSolid(snakes,{"x":1,"y":1}))

    print()
    print("START:", json.dumps(data))
    print()

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
    print("MOVE:", json.dumps(data))
    print()

    directions = ["up", "down", "left", "right"]
    global prev

    myHead = {"x": data["you"]["body"][0]['x'],
              "y": data["you"]["body"][0]['y']}

    myHealth = data["you"]["health"]
    foods = data["board"]["food"]
    snakes = data["board"]["snakes"]
    bodys=[{'x':3, 'y':1}]
    for snake in snakes:
        for body in snake['body']:
            bodys.append(body)

    print ({'x':3, 'y':1} in bodys)
    
    cur_dir = prev
    length = len(data["you"]["body"])
    starve=False

    if (myHealth <= 30) or length<12:
        pos = findFood(foods, myHead)
        starve=True
        if (prev == 0 or prev == 1):
            if (pos["x"]-myHead["x"] < 0):
                cur_dir = 2
            elif (pos["x"]-myHead["x"] > 0):
                cur_dir = 3
            else:
                cur_dir=prev
        else:
            if (pos["y"]-myHead["y"] < 0):
                cur_dir = 0
            elif (pos["y"]-myHead["y"] > 0):
                cur_dir = 1
            else:
                cur_dir=prev
    else:
        starve=False

    if starve:
        cur_dir = checkCollision(snakes, cur_dir, myHead)
    else:
        cur_dir = threeDirChecker(snakes,cur_dir,myHead)

    if (cur_dir == 0 and prev == 1) or (cur_dir ==1 and prev == 0):
        cur_dir= random.choice([2, 3])
    elif (cur_dir == 2 and prev == 3) or (cur_dir ==3 and prev == 2):
        cur_dir= random.choice([0, 1])

    move = directions[cur_dir]
    print(prev)
    print(move)
    prev = cur_dir
    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"

    response = {"move": move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


def findFood(foods, head_pos):
    x = head_pos["x"]
    y = head_pos["y"]

    lowest_index = 0

    for i in range(len(foods)-1):
        if abs(foods[i]["x"]-x)+abs(foods[i]["y"]-y) < abs(foods[lowest_index]["x"]-x)+abs(foods[lowest_index]["y"]-y):
            lowest_index = i

    pos = {"x": foods[lowest_index]["x"], "y": foods[lowest_index]["y"]}

    return pos


def checkSolid(snakes, cur_dir, myHead):
    #O(n)
    for snake in snakes:
        if cur_dir == 0:
            if myHead["y"]-1 < 0 or {"x": myHead["x"], "y": myHead["y"]-1} in snake["body"]:
                return True
        if cur_dir == 1:
            if myHead["y"]+1 >= board_height or {"x": myHead["x"], "y": myHead["y"]+1} in snake["body"]:
                return True
        if cur_dir == 2:
            if myHead["x"]-1 < 0 or {"x": myHead["x"]-1, "y": myHead["y"]} in snake["body"]:
                return True
        if cur_dir == 3:
            if myHead["x"]+1 >= board_width or {"x": myHead["x"]+1, "y": myHead["y"]} in snake["body"]:
                return True
    return False


def checkCollision(snakes, cur_dir, myHead):
    up = 0
    down = 1
    left = 2
    right = 3
    temp = cur_dir

    """
    old checker
    """
    if checkSolid(snakes, cur_dir, myHead):
        temp=threeDirChecker(snakes,cur_dir,myHead)
    if (temp == 0 and prev == 1) or (temp == 1 and prev == 0):
        if not(checkSolid(snakes, left, myHead) and prev != right):
            temp = left
        elif not(checkSolid(snakes, right, myHead) and prev != left):
            temp = right
    elif (temp == 2 and prev == 3) or (temp == 3 and prev == 2):
        if not(checkSolid(snakes, up, myHead) and prev != down):
            temp = up
        elif not(checkSolid(snakes, down, myHead) and prev != up):
            temp = down
    return temp


def threeDirChecker(snakes, cur_dir, myHead):
    """
    3 dir checker
    """
    first = 0
    second = 0
    third = 0
    # find the 3 dir
    if cur_dir == 0 or cur_dir == 1:
        # check possibility of left and right
        first_dir = cur_dir
        second_dir = 2
        third_dir = 3
        if cur_dir == 0:
            if not(checkSolid(snakes, cur_dir, myHead)):
                first = countEmpty(snakes, cur_dir, {"x": myHead["x"], "y": myHead["y"]-1})
        elif cur_dir == 1:
            if not(checkSolid(snakes, cur_dir, myHead)):
                first = countEmpty(snakes, cur_dir, {"x": myHead["x"], "y": myHead["y"]+1})
        if not (checkSolid(snakes, second_dir, myHead)):
            second = countEmpty(snakes, second_dir, {"x": myHead["x"]-1, "y": myHead["y"]})
            second_dict = {"x": myHead["x"]-1, "y": myHead["y"]}
        if not (checkSolid(snakes, third_dir, myHead)):
            third = countEmpty(snakes, third_dir, {"x": myHead["x"]+1, "y": myHead["y"]})
            third_dict = {"x": myHead["x"]+1, "y": myHead["y"]}

    elif cur_dir == 2 or cur_dir == 3:
        # check possiblity of up and down
        first_dir = cur_dir
        second_dir = 0
        third_dir = 1
        if cur_dir == 2:
            if not(checkSolid(snakes, cur_dir, myHead)):
                first = countEmpty(snakes, cur_dir, {"x": myHead["x"]-1, "y": myHead["y"]})
                print("first :"+str(first)+", first_dir "+str(first_dir))
        elif cur_dir == 3:
            if not(checkSolid(snakes, cur_dir, myHead)):
                first = countEmpty(snakes, cur_dir, {"x": myHead["x"]+1, "y": myHead["y"]})
                print("first :"+str(first)+", first_dir "+str(first_dir))
        if not (checkSolid(snakes, second_dir, myHead)):
            second = countEmpty(snakes, second_dir, {"x": myHead["x"], "y": myHead["y"]-1})
            second_dict = {"x": myHead["x"], "y": myHead["y"]-1}
            print("second :"+str(second)+", second_dir "+str(second_dir))
        if not (checkSolid(snakes, third_dir, myHead)):
            third = countEmpty(snakes, third_dir, {"x": myHead["x"], "y": myHead["y"]+1})
            third_dict = {"x": myHead["x"], "y": myHead["y"]+1}
            print("third :"+str(third)+", third_dir "+str(third_dir))
    #test check
    
    
    


    # compare
    if first == second == third:
        return first_dir
    elif first >= second and first >= third:
        return first_dir
    elif second > third:
        print("turn :"+str(second_dir))
        return second_dir
    elif third > second:
        print("turn:"+str(third_dir))
        return third_dir
    elif second == third:
        #do check more
        s=random.choice([second_dir, third_dir])
        print("luck :"+str(s))
        return s



def countEmpty(snakes, cur_dir, myHead):
    count = 3
    if cur_dir == 0 or cur_dir == 1:
        if checkSolid(snakes,2 , myHead):
            count-=1
            print("solid for second dir")
        if checkSolid(snakes,3,myHead):
            count-=1
            print("solid for third dir")
    if cur_dir == 2 and cur_dir == 3:
        if checkSolid(snakes,0 , myHead):
            count-=1
            print("solid for second dir")
        if checkSolid(snakes,1,myHead):
            count-=1
            print("solid for third dir")
    if checkSolid(snakes,cur_dir,myHead):
            count-=1
            print("solid ahead")
    return count


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
