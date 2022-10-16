import config

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def fall(obj, world):
    obj.y_velocity += config.GRAVITY

    closest_other = None

    for other in world.active_objects:
        if other == obj:
            continue

        if hasattr(other, "platform") == False:
            continue

        if other.x - other.width/2 < obj.x + obj.width/2 and other.x + other.width/2 > obj.x - obj.width/2:
            if other.y - other.height/2 <= obj.y + obj.height/2 + obj.y_velocity and other.y + other.height/2 > obj.y + obj.height/2:
                if closest_other == None or other.y - other.height/2 < closest_other.y - closest_other.height/2:
                    closest_other = other

    if closest_other != None:
        obj.y = closest_other.y - closest_other.height/2 - obj.height/2
        obj.grounded = True
        obj.y_velocity = 0
    else:
        obj.y += obj.y_velocity
        obj.grounded = False

    obj.y = clamp(obj.y, 0, config.GAME_HEIGHT - obj.height/2)
