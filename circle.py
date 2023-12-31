import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import math as m
import time

d = 1
broker = '67.253.32.232'
topic = 'ME035'

def generateCircle(cen, rad, subPoints):
    upperPoints = []
    lowerPoints = []

    x = cen[0] - rad
    inc = (4*rad) / subPoints
    while x <= cen[0] + rad:
        print(x, rad)
        y = m.sqrt(rad**2 - (x - cen[0])**2) + cen[1]
        upperPoints.append([x, y])
        lowerPoints.append([x, -1*y])
        x += inc

    upperPoints.append([cen[0] + rad, cen[1]])
    lowerPoints.reverse()
    allPoints = upperPoints + lowerPoints
    return allPoints


# Solve x and y positions for given angles
def forwardKinematic(Ls, thetas, x0=0, y0=0):
    xs = [x0]
    ys = [y0]
    currTheta = 0
    for i in range(len(Ls)):
        currTheta += thetas[i]
        xs.append(xs[i] + Ls[i] * m.cos(currTheta))
        ys.append(ys[i] + Ls[i] * m.sin(currTheta))
    return xs, ys

# Solve angles given the end position
def solveInverse(endPos):
    x, y = endPos[0], endPos[1]
    theta2 = m.acos((x**2 + y**2 - 2*d**2) / (2*d**2))
    theta1 = m.atan2(y, x) - m.atan2((d*m.sin(theta2)), (d + d*m.cos(theta2)))
    return [theta1, theta2]

# Plot each position of the arm in order as it draws the circle
def plotArmPos(posList):
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for pos in posList:
        ax.plot(pos[0], pos[1])
        fig.canvas.draw()
        fig.canvas.flush_events()
        
# Conversion functions
def toRad(deg):
    return deg * m.pi / 180

def toDeg(rad):
    return rad * 180 / m.pi

# Initialize mqtt client based on given broker and channel
def startClient():
    client = mqtt.Client("Jordan")  # use a unique name
    client.connect(broker)
    client.loop_start()  # start the loop
    return client, topic

# Format and send the series of angles to the broker
def sendMessages(thetaList):
    client, topic = startClient()
    for thetas in thetaList:
        cut = lambda x: round(toDeg(x), 1)
        thetas2 = str(tuple(map(cut, thetas)))
        print(thetas2)
        print("Publishing message to topic", topic)
        client.publish(topic, thetas2)
        time.sleep(0.1)  # wait for a little

# Generate circle points, solve the inverse kinematics for each,
# display the arm positions on a graph, and send the messages
def main():
    increments = 101
    L = [d, d]
    circlePoints = generateCircle([d, 0], (d/2), increments)
    posList = []
    thetaList = []
    for point in circlePoints:
        thetas = solveInverse(point)
        x, y = forwardKinematic(L, thetas)
        posList.append([x, y])
        thetaList.append(thetas)

    plotArmPos(posList)
    sendMessages(thetaList)


main()












