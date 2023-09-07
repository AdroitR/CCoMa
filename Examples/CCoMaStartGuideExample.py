#Luca Ciampaglia
#SME Soft Robotics Lab
#Case Western Reserve University

#CCoMa Start Guide Example

import pybullet as p
import time
import pybullet_data
from CCoMa import Cable, CableSet, ContinuumManipulator, generateURDF


'''
In order to use the CCoMa package, a suitable URDF file must be used or generated.
This only has to be called once in the project directory, but for demonstration 
purposes it is called at the start of this script.
'''

# The inputs for generateURDF() are:
# generateURDF(fileName, robotname, manipulator radius, number of links, length, mass, automatic segments, custom link inertia (optional), joint damping (optional))
# The length and mass inputs can be used for to define individual link length/mass or overall manipulator length/mass. This is controlled by the automatic segments boolean
# The damping value should be determined experimentally based on the manipulator size and number of links
generateURDF('start_guide_example_manipulator', 'examplebot',0.05,10,1,1,True,damping=0.05)




'''
The following code is required by Pybullet to set up the simulation environment.
'''

# Set up the simulation
physicsClient = p.connect(p.GUI) # or p.DIRECT for non-graphical version
p.setAdditionalSearchPath(pybullet_data.getDataPath()) # optionally

# Create the physical environment 
p.setGravity(0,0,-9.81) # creates gravity (not enabled by default)
planeId = p.loadURDF("plane.urdf") # loads the surface plane (not by default)

# Configure the GUI Windows

#p.configureDebugVisualizer(p.COV_ENABLE_GUI,0) # hides the interface panels, useful but also disables sliders
p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW,0) # hide rgb buffer window
p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW,0) # hide depth buffer window
p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW,0) # hide segmentation mark window


'''
The generated URDF must be loaded using the Pybullet internal loadURDF() function. 
This requires a start position and orientation, which are given in a [xyz] vector 
and [xyzw] quaternion respectively.

If custom link inertias were specified in generateURDF(), then loadURDF() can use
the flag p.URDF_USE_INERTIA_FROM_FILE. 
The flag p.URDF_USE_SELF_COLLISION can be used if you want self collision
'''

startPos = [0,0,2] # Set a start position for the manipulator [xyz]
startOrientation = p.getQuaternionFromEuler([0,0,0]) # Set a start orientation for the manipulator [xyzw]
bot = p.loadURDF("start_guide_example_manipulator.urdf",startPos, startOrientation, 0, 1) 


# Finds the number of joints in the manipulator
numJoints = p.getNumJoints(bot)


'''
The next step is to generate a set of cables for controlling the manipulator.
These can be created individually by creating a number of Cable objects or 
automatically generated by a CableSet object.
'''


# Generates a set of Cables using a CableSet
# The CableSet requires the inputs (startLink, endLink, number of cables, list of cables, segment color)
# The list of Cable objects can be None if the function generateCables() is called
cables = CableSet(-1,numJoints,3,None,[0.5,0.0,0.7,0.6])

# generateCables(placement radius, angular offset, link length, twist offset)
# the radius is the distance of the x/y position to the link center, the angular offset is the initial angle of the coordinate, and the twist offset is the angle between links
cables.generateCables(0.04,0.0,1.0/11.0,0.0)

# The user debug sliders can be automatically generated for testing (requires a maximum tension parameter)
cables.generateDebugSliders(400)


'''
The final step is to create the ContinuumManipulator object using the loaded URDF robot, CableSet(s), and various required parameters
In this case, an additional slider is generated for getting user input for a spring constant slider.
'''

# Initializes the loaded URDF as a ContinuumManipulator object with the two sets of cables
# ContinuumManipulator(loadedURDF robot, list of all CableSets, initial spring constant, link length, self collision boolean, maximum link velocity, twist force scaling factor)
manip = ContinuumManipulator(bot,[cables],10.0,1.0/11,False,5,5.0)

# Set up GUI slider for spring constant
spring = p.addUserDebugParameter("Spring", 1.0, 200.0, 50.0)

# Adjust the visuals of the manipulator
manip.showSegmentColors() # Uses the CableSet defined segment colors for links
manip.showCables() # Draws the cables on the screen

# Run the simulation
for i in range (1000000): # runs the simulation for 1000000 steps
    
    manip.setSpringConstant(p.readUserDebugParameter(spring)) # Updates the spring parameter of the manipulator from the slider value
    cables.readDebugSliders() # Updates the cable tensions using the sliders
    manip.stepSimulation() # Updates all forces in the manipulator

    p.stepSimulation() # Moves sim one step forward
    time.sleep(1/240.) # Rest 1/240th seconds


p.disconnect()
