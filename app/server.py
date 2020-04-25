import json
import os
import random

import bottle
from bottle import HTTPResponse
import operator
import copy


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
    myPrev = {"x": data["you"]["body"][1]['x'],
              "y": data["you"]["body"][1]['y']}
    prev_dir = inverse_dir(prev_dirCalc(myHead, myPrev))


    myHealth = data["you"]["health"]
    myLength = len(data["you"]["body"])
    myID=data["you"]["id"]
    my_info = {'id':myID, 'health':myHealth, 'length':myLength, 'prev':prev_dir}
    foods = data["board"]["food"]
    snakes = data["board"]["snakes"]
    parts, li_otherSnake, li_HLSnake = parts_calculation(snakes, foods, my_info)
    #partz = stupid_list(parts[1], snakes)

    print("turn :"+str(data['turn']))
    move = checker_floodfill(myHead, parts, foods, my_info, li_otherSnake, li_HLSnake)

    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"

    response = {"move": move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


def inverse_dir(dir):
    if dir=='up':
        return 'down'
    if dir=='down':
        return 'up'
    if dir=='left':
        return 'right'
    if dir=='right':
        return 'left'

def stupid_list(snakes):   
    list = snakes
    cpy_list = []
    for li in list:
        d2 = copy.deepcopy(li)
        cpy_list.append(d2)
    for i in cpy_list:
        i['step']=1
    return cpy_list

def parts_calculation(snakes, foods, my_info):
    li_part = []
    li_partE = []
    li_partA =[]
    li_otherSnake = []
    li_HLSnake = []
    for snake in snakes:
        i=0
        for body in snake['body']:
            li_part.append(body)
            li_partE.append(body)
        for body in stupid_list(snake['body']):
            body['step']=(len(snake['body'])-i)
            li_partA.append(body)
            i+=1

    

    for snake in snakes:
        otherHead=snake['body'][0]
        otherPrev=snake['body'][1]
        otherTail=snake['body'][len(snake['body'])-1]

        li_other=[otherHead,otherPrev,otherTail]
        li_heads=[  {"x": otherHead["x"], "y": otherHead["y"]-1},{"x": otherHead["x"], "y": otherHead["y"]+1},\
                    {"x": otherHead["x"]-1, "y": otherHead["y"]},{"x": otherHead["x"]+1, "y": otherHead["y"]}]
        # if not nearFood(li_heads,foods):
        #     # remove actual tails
        li_part.remove(snake['body'][len(snake['body'])-1])
        li_partE.remove(snake['body'][len(snake['body'])-1])

        if (len(snake['body'])>=(my_info['length'])) and (snake["id"]!=my_info["id"]) :
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
        if ((len(snake['body'])<my_info['length']) and (snake["id"]!=my_info["id"])):
            li_HLSnake.append([otherHead, otherPrev])
    return [li_part, li_partE, li_partA], li_otherSnake, li_HLSnake

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

def sorting1(val):
    return val[1]

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
    # print([up, down, left, right])
    # print(result_mx)
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
    if nxt_coord=="up":
        return {"x": myHead["x"], "y": myHead["y"]-1}
    if nxt_coord=="down":
        return {"x": myHead["x"], "y": myHead["y"]+1}
    if nxt_coord=="left":
        return {"x": myHead["x"]-1, "y": myHead["y"]}
    if nxt_coord=="right":
        return {"x": myHead["x"]+1, "y": myHead["y"]}

def expand_predArea(otherSnake, val, parts):
    balancer=0
    while (val>=0) and len(otherSnake)!=0:
        for otherHead, otherPrev, otherTail in otherSnake:
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
    for i,j,k in otherSnake:
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
        if not(steps[0]==-1) and (steps[0]==min(j for j in steps if j >= 0)) and not(steps[0]==(j for j in range(1, len(i)))):
            pathing_slot.append((steps[0],nxt,food))
    # sort
    if not(len(pathing_slot)==0):
        pathing_slot.sort(key = sorting)
        # translate
        form=[]
        for d in pathing_slot:
            form.append([gotoLoc(d[1],myHead),d[0],d[2]])
        #TODO
        return form

def checker_floodfill(myHead, li_parts, foods, my_info, otherSnake, HLSnake):
    parts=li_parts[0]
    partE=li_parts[1]
    partA=li_parts[2]
    # get survival path
    li_SpathE, tableE, mxE = floodcount(myHead, partE)
    expand=1
    li_Spath, table, mx = floodcount(myHead, parts)

    highest = max(table.values())
    # if highest<=my_info['length']:
    #     for A in partA:
    #         if A['step']<=highest:
    #             temp_dic={'x':A['x'], 'y':A['y']}
    #             if temp_dic in parts:
    #                 parts.remove(temp_dic)
    #     li_Spath, table, mx = floodcount(myHead, parts)
    #     highest = max(table.values())
    li_Spath.clear()
    for k,v in table.items():
        if v==highest:
            li_Spath.append(k)

    TEMPo_Spath=[]
    for i in tableE:
        TEMPo_Spath.append((table[i],i))
    TEMPo_Spath.sort(key = operator.itemgetter(0, 1),  reverse=True)

    # decision for more than one max
    if len(li_Spath) > 0 and mx!=0:
        expand_predArea(otherSnake, expand, parts)
        expand+=1
        print("second checker")
        expand_predArea(otherSnake, expand, parts)
        expand+=1
        for direaction in li_Spath:
            virtualHead = nxtCalc(myHead,direaction)
            if not(virtualHead==None):
                print("VH")
                temp_result, temp_table, temp_mx = floodcount(virtualHead, parts)
                i = max(temp_table.items(), key=operator.itemgetter(1))[0]
                if direaction=='up':
                    table['up']+=temp_table[i]
                if direaction=='down':
                    table['down']+=temp_table[i]
                if direaction=='left':
                        table['left']+=temp_table[i]
                if direaction=='right':
                    table['right']+=temp_table[i]
        print(table)                
    
    print('table: ', table)
    # go for food path
    li_Fpath=[]
    li_Fpath.append(food_order(myHead, otherSnake, foods, partE))

    o_Spath=[]
    for i in table:
        if not(li_Fpath==[None]):
            if i in li_Fpath[0][0]:
                indexing=len(li_Fpath[0][0])-li_Fpath[0][0].index(i)
                o_Spath.append((table[i],indexing,i))
            else:
                o_Spath.append((table[i],0,i))
    o_Spath.sort(key = operator.itemgetter(0, 1),  reverse=True)
    # TODO
    print(o_Spath)
    if myHead['x']==0 or myHead['x']==board_width-1:   
        if 'right' in(j[2] for j in o_Spath if j[0] > 0) :
            print('failure')
            return 'right'
        if 'left' in (j[2] for j in o_Spath if j[0] > 0):
            print('failure')
            return 'left'
    if myHead['y']==0 or myHead['y']==board_height-1:
        #print('failure')
        if 'down' in (j[2] for j in o_Spath if j[0] > 0):
            print('failure')
            return 'down'
        if 'up' in (j[2] for j in o_Spath if j[0] > 0):
            print('failure')
            return 'up'

    print(o_Spath)
    if not(li_Fpath[0]==None):
        for path_set in li_Fpath:

            for path in o_Spath:
                print("path",path[2]," pathset", path_set[0][0])
                if path[0]>=my_info['length'] and path[2] in path_set[0][0] :
                    if not(path_set[0][2]['x']==0 or path_set[0][2]['x']==board_width-1 or path_set[0][2]['y']==0 or path_set[0][2]['y']==board_height-1):
                        print(o_Spath)
                        print(li_Fpath)
                        print(path)                    
                        return path[2]
                    else:
                        if path_set[0][1]<=3:
                            return path[2]

    li_path=[]
    for i in otherSnake:
        count, path = shortest_step(myHead, parts, i[2])
        if count>0:
            li_path.append([count, path])
    li_path.sort()
    if len(li_path)>0:
        print("chase tail ", li_path)
        for i in TEMPo_Spath:
            if i in li_path:
                return i
    
    if len(li_Spath)==4 and len(TEMPo_Spath)>0:
        for path_set in li_Fpath:
            for path in o_Spath:
                if path[0]>=my_info['length'] and path[2] in path_set[0][0]:                
                    return path[2]
        if prev_dir in (j[1] for j in TEMPo_Spath):
            print('sad')
            return prev_dir
        else:
            print('super sad')
            return TEMPo_Spath[0][1]

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
