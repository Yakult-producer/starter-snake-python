import json
import os
import random

import bottle
from bottle import HTTPResponse
from collections import deque
from queue import Queue

prev_dir = random.choice([0, 1, 2, 3])

board_height = 1
board_width = 1

path=[]


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
    print("START:", json.dumps(data))

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
    # print("MOVE:", json.dumps(data))

    global board_height, board_width, prev_dir, path

    path=[]
    board_width = data["board"]["width"]
    board_height = data["board"]["height"]

    directions = ["up", "down", "left", "right"]

    myHead = {"x": data["you"]["body"][0]['x'],
              "y": data["you"]["body"][0]['y']}

    myHealth = data["you"]["health"]
    myLength = len(data["you"]["body"])
    myID=data["you"]["id"]
    my_info = {'id':myID, 'health':myHealth, 'length':myLength}
    foods = data["board"]["food"]
    snakes = data["board"]["snakes"]
    parts, li_otherSnake = parts_calculation(snakes, foods, my_info)

    print("turn :"+str(data['turn']))
    move = checker_floodfill(myHead, parts, foods, my_info, li_otherSnake)

    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"

    response = {"move": move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


def parts_calculation(snakes, foods, my_info):
    li_part = []
    li_partE = []
    li_otherSnake = []
    for snake in snakes:
        for body in snake['body']:
            li_part.append(body)
            li_partE.append(body)

    for snake in snakes:
        otherHead=snake['body'][0]
        otherPrev=snake['body'][1]
        li_other=[otherHead,otherPrev]
        li_heads=[  {"x": otherHead["x"], "y": otherHead["y"]-1},{"x": otherHead["x"], "y": otherHead["y"]+1},\
                    {"x": otherHead["x"]-1, "y": otherHead["y"]},{"x": otherHead["x"]+1, "y": otherHead["y"]}]
        if not nearFood(li_heads,foods):
            # remove actual tails
            li_part.remove(snake['body'][len(snake['body'])-1])
        if (len(snake['body'])>=my_info['length']) and (snake["id"]!=my_info["id"]) :
            # add predict heads
            li_part.append(li_heads[0])
            li_part.append(li_heads[1])
            li_part.append(li_heads[2])
            li_part.append(li_heads[3])
            li_otherSnake.append(li_other)
            # remove that food from list
            for head in li_heads:
                if head in foods:
                    foods.remove(head)
    return [li_part, li_partE], li_otherSnake

def matrix_list(row, column, parts, food):
    list=[]
    for r in range(row):
        rr=[]
        for c in range(column):
            if {"x": r, "y": c} not in parts:
                cc=["E"]
            if {"x": c, "y": r} == food:
                cc=["E"]
            if {"x": r, "y": c} in parts:
                cc=["S"]
            rr.append(cc)
        list.append(rr)
    return list

def isValid(row, col):
    return (row >= 0) and (row < board_height) and (col >= 0) and (col < board_width) 

def shortest_step(start_pt, parts, end_pt):
    global start_x, start_y, end_x, end_y
    R, C = board_height, board_width
    rowNum = [-1, 0, 0, 1] 
    colNum = [0, -1, 1, 0] 
    mat = matrix_list(R, C, parts, end_pt)
    count=0
    visted = []
    q = []
    d={}
    path=[]

    visted.append([start_pt['x'],start_pt['y']]) 
    q.append([[start_pt['x'],start_pt['y']],0])
    
    while (len(q) != 0):
        curr = q[0] 
        pt = [curr[0][0],curr[0][1]] 
  
        if ((pt[0] == end_pt['x']) and (pt[1] == end_pt['y'])):
            x = pt[0]
            y = pt[1]
            dx, dy = d[x, y]
            if (dx == start_pt['x']) and (dy == start_pt['y']):
                path.append([x,y])
                count+=1
                return count, path[0]

            while not(x == start_pt['x']) or not(y == start_pt['y']):    # stop loop when current cells == start cell
                x, y = d[x, y]
                path.append([x,y])
                count+=1

            return count, path[len(path)-2]

        q.pop(0); 

        for i in range(4):
            row = pt[0] + rowNum[i]; 
            col = pt[1] + colNum[i]; 
            if (isValid(row, col)) and (mat[row][col] == ["E"]) and ([row,col] not in visted): 
                visted.append([row,col])
                q.append([[row, col],curr[1] + 1])
                d[row,col]=[pt[0],pt[1]]

    return -1, [-1,-1]; 
 
def sorting(val):
    return val[0]

def nearFood(li_heads,foods):
    for head in li_heads:
        if head in foods:
            return True
    return False

def locateFood(foods, head_pos, otherSnake):
    x = head_pos["x"]
    y = head_pos["y"]
    lowest_index = 0
    # comparing the shortest distance to food
    for i in range(len(foods)-1):
        for j in otherSnake:
            if abs(foods[i]["x"]-x)+abs(foods[i]["y"]-y) < abs(foods[lowest_index]["x"]-x)+abs(foods[lowest_index]["y"]-y):
                lowest_index = i
    # return position of the nearest food
    return {"x": foods[lowest_index]["x"], "y": foods[lowest_index]["y"]}

def gotoFood(foods, myHead, otherSnake):
    food_pos = locateFood(foods, myHead, otherSnake)
    result=[]
    if (food_pos["x"]-myHead["x"] < 0):
        result.append('left')
    elif (food_pos["x"]-myHead["x"] > 0):
        result.append('right')
    if (food_pos["y"]-myHead["y"] < 0):
        result.append('up')
    elif (food_pos["y"]-myHead["y"] > 0):
        result.append('down')
    return result

def gotoLoc(pos, myHead):
    if (pos[0]-myHead["x"] < 0):
        return'left'
    elif (pos[0]-myHead["x"] > 0):
        return'right'
    if (pos[1]-myHead["y"] < 0):
        return'up'
    elif (pos[1]-myHead["y"] > 0):
        return'down'

def aStar_switch(mx, my_info):
    if mx<my_info['length']+5:
        return False
    return True

def floodcount(myHead, parts):
    table={'up':0, 'down':0, 'left':0, 'right':0}
    # start floodfill with position(after) and counter(0)
    up = rc_floodfill(parts.copy(), {"x": myHead["x"], "y": myHead["y"]-1})
    down = rc_floodfill(parts.copy(), {"x": myHead["x"], "y": myHead["y"]+1})
    left = rc_floodfill(parts.copy(), {"x": myHead["x"]-1, "y": myHead["y"]})
    right = rc_floodfill(parts.copy(), {"x": myHead["x"]+1, "y": myHead["y"]})
    result_mx = []
    mx = max([up, down, left, right])
    # count how many max
    for i, j in enumerate([up, down, left, right]):
        if j == mx:
            result_mx.append(i)
            if i==0:
                table['up']=mx
            if i==1:
                table['down']=mx
            if i==2:
                table['left']=mx
            if i==3:
                table['right']=mx
    # TODO: debug prints
    print([up, down, left, right])
    print(result_mx)
    return result_mx, table, mx

def prev_dirCalc(head, prev):
    if head["x"]>prev["x"]:
        return 'left'
    if head["x"]<prev["x"]:
        return 'right'
    if head["y"]>prev["y"]:
        return 'up'
    if head["y"]<prev["y"]:
        return 'down'

def nxtCalc(myHead, nxt_coord):
    if nxt_coord==0:
        return {"x": myHead["x"], "y": myHead["y"]-1}
    if nxt_coord==1:
        return {"x": myHead["x"], "y": myHead["y"]+1}
    if nxt_coord==2:
        return {"x": myHead["x"]-1, "y": myHead["y"]}
    if nxt_coord==3:
        return {"x": myHead["x"]+1, "y": myHead["y"]}

def expand_predArea(otherSnake, val, parts):
    balancer=0
    while (val>=0) and len(otherSnake)!=0:
        for otherHead, otherPrev in otherSnake:
            parts.append({"x": otherHead["x"]+val, "y": otherHead["y"]+balancer})
            parts.append({"x": otherHead["x"]-val, "y": otherHead["y"]+balancer})
            parts.append({"x": otherHead["x"]-val, "y": otherHead["y"]-balancer})
            parts.append({"x": otherHead["x"]+val, "y": otherHead["y"]-balancer})
            val-=1
            balancer+=1
            if (val==0):
                #get rid the extra spot
                prev=prev_dirCalc(otherHead,otherPrev)
                if (prev=="left") and {"x": otherHead["x"]+balancer, "y": otherHead["y"]-val} in parts:
                    parts.remove({"x": otherHead["x"]+balancer, "y": otherHead["y"]-val})
                if (prev=="right") and {"x": otherHead["x"]-balancer, "y": otherHead["y"]-val} in parts:
                    parts.remove({"x": otherHead["x"]-balancer, "y": otherHead["y"]-val})
                if (prev=="up") and {"x": otherHead["x"]+val, "y": otherHead["y"]+balancer} in parts:
                    parts.remove({"x": otherHead["x"]+val, "y": otherHead["y"]+balancer})
                if (prev=="down") and {"x": otherHead["x"]+val, "y": otherHead["y"]-balancer} in parts:
                    parts.remove({"x": otherHead["x"]+val, "y": otherHead["y"]-balancer})

def food_order(myHead, otherSnake, foods, partE):
     # Pre
    Heads=[myHead]
    for i,j in otherSnake:
        Heads.append(i)
    # heat
    li_step=[]
    for food in foods:
        step=[]
        path=[]
        for head in Heads:
            s, p = shortest_step(head, partE, food)
            step.append(s)
            path.append(p)
        li_step.append([step, path, food])
    # eat
    pathing_slot=[]
    for i in li_step:
        steps=i[0]
        nxt=i[1][0]
        food=i[2]
        if not(steps[0]==-1) and (steps[0]==min(j for j in steps if j >= 0)):
            pathing_slot.append((steps[0],nxt))
    # sort
    if not(len(pathing_slot)==0):
        pathing_slot.sort(key = sorting)
        # translate
        form=[]
        for d in pathing_slot:
            form.append(gotoLoc(d[1],myHead))
        #TODO
        return form

def checker_floodfill(myHead, li_parts, foods, my_info, otherSnake):
    parts=li_parts[0]
    partE=li_parts[1]
    # get survival path
    expand=1
    li_Spath, table, mx = floodcount(myHead, parts)

    highest = max(table.values())
    li_Spath.clear()
    for k,v in table.items():
        if v==highest:
            li_Spath.append(k)
    # print("final result")
    # print(li_Spath)
    # print(highest)
    
    # go for food path
    li_Fpath=[]
    li_Fpath.append(food_order(myHead, otherSnake, foods, partE))
    print(li_Fpath)
    if not(li_Fpath[0]==None):
        for path_set in li_Fpath:
            for path in path_set:
                if path in li_Spath:
                    print(li_Fpath)
                    print(path)
                    return path

    
    # if len(result)>1:
    #     Heads=[myHead]
    #     for i,j in otherSnake:
    #         Heads.append(i)
    #     for food in foods:
    #         shortest_step(Heads, parts, foods)
        # temp_food=[]
        
        # food_move = gotoFood(foods, myHead, otherSnake)
        # for moves in food_move:
        #     if moves in li_Spath:
        #         temp_food.append(moves)
        # # see possible to block other by results choice
        # # temp_counter=counter_move(snakes, myHead)
        # # finalize the info and pick one direaction
        # for move in li_Spath:
        #     if move in temp_food:
        #         print(move)
        #         return move
    print(li_Spath[0])
    return li_Spath[0]  # , active_AStar

def rc_floodfill(parts, position):
    count = 0
    # count how many block after 'this direaction'
    if not(check_empty(parts, position)):
        return count
    parts.append(position)
    count += 1
    up = rc_floodfill(parts, {"x": position["x"], "y": position["y"]-1})
    down = rc_floodfill(parts, {"x": position["x"], "y": position["y"]+1})
    left = rc_floodfill(parts, {"x": position["x"]-1, "y": position["y"]})
    right = rc_floodfill(parts, {"x": position["x"]+1, "y": position["y"]})

    return count + up + down + left + right

def check_empty(parts, position):
    if (position in parts) or (0 > position['x']) or (position['x'] > board_width-1) or (0 > position['y'])or(position['y'] > board_height-1):
        return False
    return True


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
