import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from matplotlib.colors import hsv_to_rgb

# Function to parse the XML file
def parse_xml(map_file_path, log_file_path):
    # Parse the map file
    map_tree = ET.parse(map_file_path)
    map_root = map_tree.getroot()
    
    grid = []
    map_element = map_root.find('map')
    grid_element = map_element.find('grid')
    for row in grid_element.findall('row'):
        grid.append([int(x) for x in row.text.split()])
    
    # Parse the log file
    log_tree = ET.parse(log_file_path)
    log_root = log_tree.getroot()
    
    agents = []
    log_element = log_root.find('log')
    root_agents = log_root.findall('agent')  # Get agents from the root element
    
    # Create a mapping of agent numbers to root agents based on start positions
    root_agent_map = {}
    for i, agent in enumerate(root_agents):
        start_i = float(agent.get('start_i'))
        start_j = float(agent.get('start_j'))
        root_agent_map[(start_i, start_j)] = agent
    
    for agent in log_element.findall('agent'):
        agent_number = int(agent.get('number'))
        agent_info = {'number': agent_number, 'path': []}
        path_element = agent.find('path')
        
        if path_element is not None and path_element.findall('section'):
            for section in path_element.findall('section'):
                section_info = {
                    'start_i': float(section.get('start_i')),
                    'start_j': float(section.get('start_j')),
                    'goal_i': float(section.get('goal_i')),
                    'goal_j': float(section.get('goal_j')),
                    'duration': float(section.get('duration'))
                }
                agent_info['path'].append(section_info)
        else:
            # Use the start position from the root element if no path sections are found
            root_agent = None
            for agent in root_agents:
                if agent_number == root_agents.index(agent):
                    root_agent = agent
                    break
            if root_agent is not None:
                start_i = float(root_agent.get('start_i'))
                start_j = float(root_agent.get('start_j'))
                goal_i = float(root_agent.get('goal_i'))
                goal_j = float(root_agent.get('goal_j'))
                agent_info['path'].append({
                    'start_i': start_i,
                    'start_j': start_j,
                    'goal_i': goal_i,
                    'goal_j': goal_j,
                    'duration': 0  # No duration since there's no movement
                })
        
        agents.append(agent_info)
    
    return grid, agents

# Function to draw the grid
def draw_grid(ax, grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 1:
                facecolor = 'black'
            else:
                facecolor = 'white'
            rect = patches.Rectangle((i - 0.5, j - 0.5), 1, 1, linewidth=1, edgecolor='black', facecolor=facecolor)
            ax.add_patch(rect)

# Function to update the paths
def update_paths(frame, ax, grid, agents, agent_positions, colors):
    ax.clear()
    draw_grid(ax, grid)
    
    for agent in agents:
        path = agent['path']
        color = colors[agent['number']]
        elapsed_time = 0
        for section in path:
            start = (section['start_i'] , section['start_j'] )
            goal = (section['goal_i'] , section['goal_j'] )
            ax.plot([start[0], goal[0]], [start[1], goal[1]], color=color, linestyle='-')  # Draw entire path with solid line
            ax.plot(start[0], start[1], color=color, marker='o')  # Draw start point
            ax.plot(goal[0], goal[1], color=color, marker='o')  # Draw goal point
            if elapsed_time <= frame < elapsed_time + section['duration']:
                progress = (frame - elapsed_time) / section['duration']
                current_position = (
                    start[0] + (goal[0] - start[0]) * progress,
                    start[1] + (goal[1] - start[1]) * progress
                )
                agent_positions[agent['number']] = current_position
                break
            elapsed_time += section['duration']
        else:
            # If the agent has reached the end of its path, keep it at the last goal position
            last_section = path[-1]
            agent_positions[agent['number']] = (
                last_section['goal_i'] ,
                last_section['goal_j'] 
            )
    
    # Draw all agents at their current positions
    for agent_number, position in agent_positions.items():
        ax.plot(position[0], position[1], color=colors[agent_number], marker='o', markersize=10)
        ax.text(position[0], position[1], str(agent_number + 1), color='white', ha='center', va='center') 
    
    ax.set_aspect('equal')
    plt.xlim(-0.5, len(grid[0]) - 6)
    plt.ylim(-0.5, len(grid[1]))  # Invert the Y-axis by setting limits in reverse order

# Main function
def main():
    log_path = '/home/0000410764/oss/Python-RVO2/simulator/grid_task_log.xml'  # Replace with your XML file path
    map_path = '/home/0000410764/oss/Python-RVO2/simulator/grid_map.xml'  # Replace with your XML file path
    grid, agents = parse_xml(map_path, log_path)
    # print(agents)
    fig, ax = plt.subplots()
    draw_grid(ax, grid)
    
    # Calculate total duration
    total_duration = max(sum(section['duration'] for section in agent['path']) for agent in agents)
    
    # Initialize agent positions
    agent_positions = {}
    
    # Generate unique colors for each agent
    num_agents = len(agents)
    colors = [hsv_to_rgb((i / num_agents, 1, 1)) for i in range(num_agents)]
    agent_colors = {agent['number']: colors[i] for i, agent in enumerate(agents)}
    
    ani = animation.FuncAnimation(fig, update_paths, frames=int(total_duration * 30), fargs=(ax, grid, agents, agent_positions, agent_colors), interval=300, repeat=True)
    plt.show()

if __name__ == '__main__':
    main()