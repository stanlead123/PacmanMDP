
from game import Agent
import api

# MDP agent which uses Value Iteration to guide pacman through the maze

class MDPAgent(Agent):


    def __init__(self):
        print "Running init!"

    # This is what gets run when the game ends.
    def final(self, state):
        # Reset the reward map
        self.Reward = {}


    # Functions to get the height and the width of the map. Taken from mapAgents.py
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1


    # Returns map width. [Ref: mapAgents.py]
    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1


    # Simple function which takes directional input and returns its unit vector equivalent
    def directiontoVector(self,direction):

        if direction == api.Directions.NORTH:
            return (0, 1)
        if direction == api.Directions.SOUTH:
            return (0, -1)
        if direction == api.Directions.EAST:
            return (1, 0)
        if direction == api.Directions.WEST:
            return (-1, 0)


    # Function which returns a list of all possible coordinates within 1 step of (x,y)
    def getSuccessor(self, state, x, y):
        successors = []
        walls = api.walls(state)
        for action in [api.Directions.NORTH, api.Directions.SOUTH, api.Directions.EAST, api.Directions.WEST]:
            self.x = x
            self.y = y
            dx, dy = self.directiontoVector(action)
            nextx, nexty = int(self.x + dx), int(self.y + dy)
            if (nextx, nexty) not in walls:
                nextState = (nextx, nexty)
                successors.append(nextState)

        return successors

    # The following 4 ghostRegion functions are all just used to create a region around
    # the ghosts of negative reward.

    # Creates a list of all coordinates within 1 move of any ghosts
    # i.e. all the successors of the ghosts coordinates
    def ghostRegion1(self,state):
        ghosts = api.ghosts(state)

        region1 = []
        # for loop creates a list of lists
        for k in range(len(ghosts)):
            region1.append(self.getSuccessor(state, ghosts[k][0], ghosts[k][1]))

        # Create a list containing every element in the previously created list of lists
        flat_list = [item for sublist in region1 for item in sublist]

        # Remove any duplicates in the list
        flat_list = list(set(flat_list))

        return flat_list


    # Creates a list of all coordinates within exactly 2 moves of any ghosts
    # Similar to ghostRegion1() method
    def ghostRegion2(self, state, lst_1):
        ghosts = api.ghosts(state)

        region2 = []
        for i in range(len(lst_1)):
            region2.append(self.getSuccessor(state, lst_1[i][0], lst_1[i][1]))


        flat_list2 = [item for sublist in region2 for item in sublist]

        region2 = list(set(flat_list2))

        # Remove ghost coordinates as they're already explored in ghostRegion1()
        for k in range(len(ghosts)):
            if ghosts[k] in region2:
                region2.remove(ghosts[k])

        return region2


    # Creates a list of all coordinates within exactly 3 moves of any ghosts
    def ghostRegion3(self, state, lst_2):

        region3 = []

        for i in range(len(lst_2)):
            region3.append(self.getSuccessor(state, lst_2[i][0], lst_2[i][1]))

        flat_list3 = [item for sublist in region3 for item in sublist]

        region3 = list(set(flat_list3))

        # Remove any coordinates which were already explore in lst_2
        for j in range(len(lst_2)):
            if (lst_2[j][0],lst_2[j][1]) in region3:
                region3.remove((lst_2[j][0],lst_2[j][1]))

        return region3


    # Creates a list of all coordinates within exactly 4 moves of any ghosts
    def ghostRegion4(self, state, lst_3):

        region4 = []

        for i in range(len(lst_3)):
            region4.append(self.getSuccessor(state, lst_3[i][0], lst_3[i][1]))

        flat_list4 = [item for sublist in region4 for item in sublist]

        region4 = list(set(flat_list4))

        # Remove any coordinates which were already explore in lst_3
        for j in range(len(lst_3)):
            if (lst_3[j][0],lst_3[j][1]) in region4:
                region4.remove((lst_3[j][0],lst_3[j][1]))

        return region4


    # Function which calculates the expected utility of move 'action' when in state (x,y)
    # given utility map M
    def expectedUtility(self, x, y, action, M):

        self.M = M
        dx, dy = self.directiontoVector(action)

        # The desired target coordinate (Probability = 0.8)
        target = (x + dx, y + dy)

        # Setting the corresponding perpendicular target coordinates
        # Which each have an associated probability of 0.1
        if dx != 0:
            p1 = (x, y + 1)
            p2 = (x, y - 1)
        else:
            p1 = (x + 1, y)
            p2 = (x - 1, y)

        # target, p1 & p2 are all the possible resulting coordinates from applying 'action'

        # Now calculate the expected utility of the move 'action'
        self.utility = 0.0

        # If main target coordinate is not a wall, update utility accordingly,
        # else, calculate utility of remaining in current position.
        if self.M[target] != '#':
            self.utility = 0.8 * self.M[target]
        else:
            self.utility = 0.8 * self.M[(x, y)]

        # Likewise for the first perpendicular coordinate p1
        if self.M[p1] != '#':
            self.utility += 0.1 * self.M[p1]
        else:
            self.utility += 0.1 * self.M[(x, y)]

        # Second perpendicular coordinate p2
        if self.M[p2] != '#':
            self.utility += 0.1 * self.M[p2]
        else:
            self.utility += 0.1 * self.M[(x, y)]

        # Return the expected utility
        return self.utility






    # Function which calculates the expected utility of every possible move
    # for coordinate (x,y) given utility map M and returns the Maximum Expected Utility of (x,y).
    def MEU(self, x, y, M):

        self.x = x
        self.y = y
        self.M = M

        # Initialise list of utilities
        NSEW_utils = []

        # Calculate expected utility of NSEW
        for a in [api.Directions.NORTH, api.Directions.SOUTH, api.Directions.EAST, api.Directions.WEST]:
            NSEW_utils.append(self.expectedUtility(self.x, self.y, a, self.M))

        # Return MEU
        return max(NSEW_utils)


    # Create a reward map for mediumClassic layout in the form of a dictionary
    def rewardmap(self, state):
        pacman = api.whereAmI(state)
        food = api.food(state)
        ghosts = api.ghosts(state)
        capsules = api.capsules(state)
        corners = api.corners(state)
        walls = api.walls(state)

        width = self.getLayoutWidth(corners)
        height = self.getLayoutHeight(corners)

        # Initialise map
        self.Rmap = {}

        # Set all rewards to 0 to initialize dictionary
        for i in range(width):
            for j in range(height):
                self.Rmap[(i, j)] = 0

        # Set all walls to '#' symbol
        wall_dict = dict.fromkeys(walls, '#')

        # Update the coordinates which are walls with '#' value
        self.Rmap.update(wall_dict)


        # If there is less than 10 food pieces left, increase food reward by multiple of 5.
        # If 10 < food < 20 : increase reward by multiple of 2
        # Otherwise assign food as a reward of 50
        if len(food) < 10:
            self.r_food_dict = dict.fromkeys(food, 5*50)
        elif len(food) < 20:
            self.r_food_dict = dict.fromkeys(food, 2*50)
        else:
            self.r_food_dict = dict.fromkeys(food, 50)


        # Assign capsules reward 50 and ghosts -150
        self.r_capsule_dict = dict.fromkeys(capsules, 50)
        self.r_ghosts_dict = dict.fromkeys(ghosts, -150)

        # Updating the reward map dictionary
        self.Rmap.update(self.r_food_dict)
        self.Rmap.update(self.r_capsule_dict)

        self.Rmap.update(self.r_ghosts_dict)

        # Set 0 reward for pacman's current location
        self.Rmap[pacman] = 0

        # Create region of 4 steps around ghosts of decreasing rewards: 90%, 70%, 50%, 20%
        GR1 = self.ghostRegion1(state)
        GR2 = self.ghostRegion2(state, GR1)
        GR3 = self.ghostRegion3(state, GR2)
        GR4 = self.ghostRegion4(state, GR3)

        for i in range(width):
            for j in range(height):
                if (i, j) not in ghosts:
                    if (i, j) in GR1:
                        self.Rmap[(i, j)] = 0.9*(-150)
                    elif (i, j) in GR2:
                        self.Rmap[(i, j)] = 0.7*(-150)
                    elif (i, j) in GR3:
                        self.Rmap[(i, j)] = 0.5*(-150)
                    elif (i, j) in GR4:
                        self.Rmap[(i, j)] = 0.2*(-150)

        return self.Rmap

    # Creates reward map for smallGrid layout in the form of a dictionary
    def smallrewardmap(self,state):
        corners = api.corners(state)
        food = api.food(state)
        ghosts = api.ghosts(state)
        walls = api.walls(state)

        width = self.getLayoutWidth(corners)
        height = self.getLayoutHeight(corners)

        # Initialize map
        self.smallRmap = {}

        # Set all rewards to 0 to initialize dictionary
        for i in range(width):
            for j in range(height):
                self.smallRmap[(i, j)] = 0

        # Set all walls to '#' symbol
        wall_dict = dict.fromkeys(walls, '#')

        # Update the coordinates which are walls with '#'
        self.smallRmap.update(wall_dict)

        # Create dictionary assigning food reward 20 and ghosts -10
        self.small_r_fooddict = dict.fromkeys(food,20)
        self.small_r_ghostsdict = dict.fromkeys(ghosts, -10)

        # Update smallRmap with these rewards
        self.smallRmap.update(self.small_r_fooddict)
        self.smallRmap.update(self.small_r_ghostsdict)

        # Create ghost region of only two steps with decreasing rewards: 90%, 70%
        GR1 = self.ghostRegion1(state)
        GR2 = self.ghostRegion2(state, GR1)

        for i in range(width):
            for j in range(height):
                if (i, j) not in ghosts:
                    if (i, j) in GR1:
                        self.smallRmap[(i, j)] = 0.9*(-10)
                    elif (i, j) in GR2:
                        self.smallRmap[(i, j)] = 0.7*(-10)

        return self.smallRmap



    # Value iteration algorithm which updates the inputted initial utility map M
    def ValueIteration(self, state, M):

        corners = api.corners(state)
        walls = api.walls(state)

        height = self.getLayoutHeight(corners)
        width = self.getLayoutWidth(corners)

        # Setting the reward map according to map size
        if height < 10 or width < 10:
            self.Reward = self.smallrewardmap(state)
        else:
            self.Reward = self.rewardmap(state)


        # This algorithm is based inspired from pseudo-code provided in lecture slides along with
        # Russell and Norvig's AI: A Modern Approach book
        while True:
            # Create deepcopy of map so you can update it
            old_map = {}
            for x in M:
                old_map[x] = M[x]

            delta = 0
            for i in range(width):
                for j in range(height):
                    if (i, j) not in walls:

                        # Bellman's Equation:
                        M[(i, j)] = self.Reward[(i, j)] + self.gamma*(self.MEU(i, j, old_map))

                        # Store the largest difference between successive iterations
                        delta = max(delta,(abs(M[(i, j)] - old_map[(i, j)])))

            # Once the largest change in utility between any coordinates is less than this threshold,
            # Convergence is achieved & algorithm halts
            if delta < 0.01 * (1 - self.gamma)/self.gamma:
                break


    # Using this newly updated utility map, calculate expected utility
    # of every possible move for (x,y) and return the move with the MEU.
    def getMove(self, x, y, iteratedmap):

        # Your newly updated utility map
        self.IM = iteratedmap

        self.x = x
        self.y = y

        # Initialise dictionary for storing utility of all possible moves
        self.utils = {api.Directions.NORTH : 0.0, api.Directions.SOUTH : 0.0, api.Directions.EAST : 0.0, api.Directions.WEST : 0.0}

        # Calculate expected utility of every move
        for a in [api.Directions.NORTH, api.Directions.SOUTH, api.Directions.EAST, api.Directions.WEST]:
            self.utils[a] = self.expectedUtility(self.x, self.y, a, self.IM)

        # Return move with maximum expected utility
        return max(self.utils, key=self.utils.get)

    # Where all of the functions come together to form an MDP solver.
    def getAction(self, state):
        corners = api.corners(state)
        pacman = api.whereAmI(state)

        # The agent checks the size of the map and creates the suitable
        # Initial utility map & assigns gamma value
        if self.getLayoutHeight(corners)<10 or self.getLayoutWidth(corners)<10:
            u_map = self.smallrewardmap(state)
            self.gamma = 0.6
        else:
            u_map = self.rewardmap(state)
            self.gamma = 0.7

        # Value iterate initial u_map to update it
        self.ValueIteration(state,M=u_map)

        # Now decide action based on the now iterated map
        response = self.getMove(pacman[0], pacman[1], iteratedmap=u_map)

        legal = api.legalActions(state)

        return api.makeMove(response, legal)

