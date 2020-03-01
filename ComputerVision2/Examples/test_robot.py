import RobotAPI as rapi

robot = rapi.RobotAPI()
#
# robot.beep()
# robot.red()
# robot.serv(0)

# for i in range(30):
#     robot.step(-100,100, pulse_go=15)
# for i in range(30):
#         robot.step(100, -100, pulse_go=15)

robot.color_off()
#издаем звук
#robot.tone(5000, 200)

# #включаем зеленый светодиод
# robot.rgb(222,0,0)
#
# #ждем пол секунды
# robot.wait(200)
#
# #вылючаем светодиод
# robot.rgb(0,0,0)
#
# # издаем звук
# robot.tone(7000, 200)


while True:
    if robot.button()==1:
        break
    if robot.manual()==1:
        continue
    print(robot.vcc())
#
# robot.step(-250,250,800,pulse_go=10)
# robot.step(200,200,1000)
# robot.step(250,-250,900, pulse_go=10)
# robot.green()
# robot.step(200,200,1000,wait=True)
# robot.blue()
# robot.step(200,-200,1000, wait=True)
# robot.red()