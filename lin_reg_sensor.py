from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from math import *
import matrix

hub = PrimeHub()
ports = ['A', 'B', 'C', 'D', 'E', 'F']

# Not idempotent. Removes port from ports when it finds a thing
def find_thing(thing):
    ret = None
    remove = None
    for port in ports:
        try:
            ret = thing(port)
            remove = port
            break
        except:
            pass
    if remove:
        ports.remove(remove)
    return ret

motor = find_thing(Motor)
color = find_thing(ColorSensor)
motor2 = find_thing(Motor)

def clear_buttons():
    hub.left_button.was_pressed()
    hub.right_button.was_pressed()

def setup_get_sensor_data(color_sensor):
    #return lambda : (color_sensor.get_rgb_intensity()[0]*1024/(color_sensor.get_rgb_intensity()[3]+1),color_sensor.get_rgb_intensity()[1]*1024/(color_sensor.get_rgb_intensity()[3]+1))
    return lambda : list(color_sensor.get_rgb_intensity()[0:3])


def train_menu():
    train = False
    hub.light_matrix.show_image('GO_RIGHT')
    clear_buttons()
    while True:
        if hub.motion_sensor.was_gesture('tapped'):
            return train
        if hub.left_button.was_pressed() or hub.right_button.was_pressed():
            train = not train
            if train:
                hub.light_matrix.write('T')
            else:
                hub.light_matrix.show_image('GO_RIGHT')


def train(get_sensor_data, motor, motor2 = None):
    xs = []
    y1s = []
    y2s = []
    choices = ['CHESSBOARD', 'GO_RIGHT']
    choice = 0
    hub.light_matrix.show_image(choices[choice])
    while True:
        if hub.left_button.was_pressed():
            choice = (choice - 1) % 2
            hub.light_matrix.show_image(choices[choice])
        if hub.right_button.was_pressed():
            choice = (choice + 1 ) % 2
            hub.light_matrix.show_image(choices[choice])
        if hub.motion_sensor.was_gesture('tapped'):
            if choice == 1:
                hub.light_matrix.off()
                hub.speaker.beep(90, 0.15)
                hub.speaker.beep(94, 0.15)
                hub.speaker.beep(98, 0.15)
                return xs, y1s, y2s
            xs.append(get_sensor_data())
            y1s.append(motor.get_position())
            if motor2:
                y2s.append(get_position())

            hub.light_matrix.show_image('YES')
            hub.speaker.beep(90, 0.15)
            hub.speaker.beep(94, 0.15)
            choice = 0
            hub.light_matrix.show_image(choices[choice])

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

def proportional_adjust(target_angle, motor):
    error = target_angle - motor.get_position()
    power = floor(error*.2)
    power = clamp(power,-100,100)
    motor.start_at_power(power)


motor.run_to_position(180)
if motor2:
    motor2.run_to_position(180)
get_sensor_data = setup_get_sensor_data(color)

hub.motion_sensor.was_gesture('tapped')

train_flag = train_menu()
if train_flag:
    xs, y1s, y2s = train(get_sensor_data, motor, motor2)

print(xs)
print(y1s)
xs = matrix.Matrix(xs)
ys = matrix.Matrix(y1s)
m1eq = matrix.lin_regression(xs, ys)

hub.light_matrix.off()
hub.light_matrix.show_image('DIAMOND')
rounds = 0

status = ["azure","blue","cyan","green","orange","pink","red","violet","yellow","white"]
while True:
    hub.status_light.on(status[rounds])
    raw = get_sensor_data()
    raw.insert(0,1)
    current = matrix.Matrix(raw).T()
    print(current)
    target_angle1 = int((current * m1eq).get(0,0)) % 360
    print(target_angle1)
    if motor2:
        target_angle2 = (current * m2eq).get(0,0)
        proportional_adjust(target_angle2, motor2)
    else:
        motor.run_to_position(target_angle1)
#    motor.run_to_position(target_angle)
    rounds = (rounds + 1) % 10
    wait_for_seconds(.05)
