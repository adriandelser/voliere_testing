from gflow.cases import Cases
from gflow.utils.simulation_utils import run_simulation, set_new_attribute
from gflow.utils.plot_utils import PlotTrajectories 
from gflow.plotting.main_plot import SimulationVisualizer
from scenebuilder.gui_sim import InteractivePlot

#scenebuilder part
p = InteractivePlot()
p.draw_scene() 

#gflow part
file_name = "scenebuilder.json"
case_name="scenebuilder"
case = Cases.get_case(file_name, case_name)
# set_new_attribute(case, "ARRIVAL_DISTANCE", new_attribute_value=1e-6)
set_new_attribute(case, "sink_strength", new_attribute_value=1)
set_new_attribute(case, "source_strength", new_attribute_value=1)
set_new_attribute(case, "turn_radius", new_attribute_value=0.1)

case.mode = 'radius'
result = run_simulation(
    case,
    t=2000,
    update_every=1,
    stop_at_collision=False
    )

# create ouput json
case.to_dict(file_path="example_output.json")

trajectory_plot = PlotTrajectories(case, update_every=1)
# trajectory_plot.BUILDING_EDGE_COLOUR
LIMS = (-5,5)
# XLIMS = (575600,576000)
# YLIMS = (6275100,6275700)
trajectory_plot.ax.set_xlim(LIMS)
trajectory_plot.ax.set_ylim(LIMS)
trajectory_plot.show()

# visualisation part
visualizer = SimulationVisualizer('example_output.json')
visualizer.show_plot()