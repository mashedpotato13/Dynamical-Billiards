"""
AbstractTable module for Dynamical Billiards Simulator
All the different tables will be a subclass of this abstract superclass
"""

import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt
from scipy import optimize as op
from PIL import Image

class Ball(object):
    """Holds the colour and state of a ball in the simulation"""
    def __init__(self, **kwargs):
        super().__init__()
        self.parameters = kwargs
        self.state = self.parameters['initstate']
        self.color = self.parameters['color']


class AbstractTable(object):
    """
    Abstract class for a table that simulates collissions
    this superclass takes care of the animating and preview genration
    subclasses will take care of detecting collissions and drawing the table

    subclasses must implement:
        drawTable
        step

    all others are optional
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.parameters = kwargs
        self.colorlist = ['r', 'g', 'b', 'y']
        self.ballList = []
        self.nBalls = self.parameters['nBalls']

    def drawTable(self,ec='none'):
        """
        Each table must implement this function
        should make a figure and axes in self and should draw the table as a
        collection of matplotlib patches

        edge colour is for the patches, when animating it can be left as none
        but must be 'k' for generatePreview
        """
        return None

    def step(self, particle, dt):
        """
        each table must implement this function
        for each check particle, check if boundaries crossed and update
        velocity (position is updated in stepall)
        """
        return None

    def stepall(self, dt):
        """
        updates position of each ball and checks boundaries using step
        """
        for particle in self.ballList:
            particle.state[0] += dt * particle.state[2]
            particle.state[1] += dt * particle.state[3]

            self.step(particle, dt)

    def generatePreview(self):
        """
        saves a preview of the figure as preview.png and returns a PIL image
        object of the preview

        must run update before using this method
        """
        # draw table with black edge color
        self.drawTable('k')
        balls=[]
        # initialize all the balls and their positions
        for i in range(self.nBalls):
            balls.append(Ball(color= self.colorlist[i],
                initstate= self.parameters['balls']['Ball ' + str(i + 1)]))
            self.ax.plot(balls[i].state[0], balls[i].state[1],
                balls[i].color + 'o', ms=6)
        # linewidth needs to be larger than animating so it will be visible in
        # the preview
        self.table.set_linewidth(6)

        self.fig.savefig('preview.png')
        f=Image.open('preview.png')
        # resize object so it will fit in tkinter canvas
        f=f.resize((300,300))
        return f

    def update(self,**kwargs):
        """saves new parameters for the Simulation"""
        self.parameters=kwargs

    def main(self):
        """
        opens the matplotlib window and starts the animation
        should run update before calling with function
        """
        # close any figures made from generatePreview
        plt.close('all')
        # make figure and axis and add the table to it
        self.drawTable()
        # define time step. this value seems to work well but can be adjusted
        dt = 1 / 30

        # initialize balls and axes objects
        particles = []
        paths = []
        self.pathx = {}
        self.pathy = {}

        for i in range(self.nBalls):
            # make ball object and add it to ball list
            self.ballList.append(Ball(color= self.colorlist[i],
                initstate=self.parameters['balls']['Ball ' + str(i + 1)]))
            # initialize particles and paths that will be plotted
            particles.append(self.ax.plot([], [], self.ballList[i].color + 'o',
                ms=6)[0])
            paths.append(self.ax.plot([], [], self.ballList[i].color + '-',
                lw=1)[0])
            self.pathx[i] = np.array([])
            self.pathy[i] = np.array([])

        def init():
            """
            initialize function for the animation.
            gets run before each frame.
            """
            # reset particles
            for ball in particles:
                ball.set_data([], [])
                ball.set_data([], [])
            # reset table
            self.table.set_edgecolor('none')

            # return proper number of objects as we can't return the whole list
            # TODO Find a way to clean this up
            if self.nBalls == 4:
                return particles[0], particles[1], particles[2], particles[3], \
                        self.table, paths[0], paths[1],paths[2],paths[3]
            elif self.nBalls == 3:
                return particles[0], particles[1], particles[2], \
                       self.table, paths[0], paths[1], paths[2]
            elif self.nBalls == 2:
                return particles[0], particles[1], \
                       self.table, paths[0], paths[1]
            else:
                return particles[0], self.table, paths[0]

        def animate(k):
            """perform animation step"""
            # trace the particle if check box is selected
            if self.parameters['trace']:
                for i in range(0, self.nBalls):
                    self.pathx[i] = np.append(self.pathx[i],
                        self.ballList[i].state[0])
                    self.pathy[i] = np.append(self.pathy[i],
                        self.ballList[i].state[1])
            # update position and check for collissions
            self.stepall(dt)
            # update table
            self.table.set_edgecolor('k')
            # set particle position and path data
            for ball in range(self.nBalls):
                particles[ball].set_data(self.ballList[ball].state[0],
                    self.ballList[ball].state[1])
                paths[ball].set_data(self.pathx[ball], self.pathy[ball])

            # return proper number of objects as we can't return the whole list
            # TODO Find a way to clean this up
            if self.nBalls == 4:
                return particles[0], particles[1], particles[2], particles[3], \
                       self.table, paths[0], paths[1], paths[2], paths[3]
            elif self.nBalls == 3:
                return particles[0], particles[1], particles[2], \
                       self.table, paths[0], paths[1], paths[2]
            elif self.nBalls == 2:
                return particles[0], particles[1], \
                       self.table, paths[0], paths[1]
            else:
                return particles[0], self.table, paths[0]

        # define animation with appropriate playbackSpeed
        ani = animation.FuncAnimation(self.fig, animate, frames=600,
            interval=np.ceil((1 / self.parameters['playbackSpeed']) * 10 ** 3),
            blit=True,init_func=init)
        # show matplotlib window
        plt.show()
