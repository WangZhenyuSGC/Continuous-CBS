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
    for agent in log_element.findall('agent'):
        agent_info = {'number': int(agent.get('number')), 'path': []}
        path_element = agent.find('path')
        for section in path_element.findall('section'):
            section_info = {
                'start_i': int(section.get('start_i')),
                'start_j': int(section.get('start_j')),
                'goal_i': int(section.get('goal_i')),
                'goal_j': int(section.get('goal_j')),
                'duration': float(section.get('duration'))
            }
            agent_info['path'].append(section_info)
        agents.append(agent_info)
    
    return grid, agents

# Function to draw the grid
def draw_grid(ax, grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            rect = patches.Rectangle((j, len(grid) - 1 - i), 1, 1, linewidth=1, edgecolor='black', facecolor='white')
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
            start = (section['start_j'] + 0.5, len(grid) - 1 - section['start_i'] + 0.5)
            goal = (section['goal_j'] + 0.5, len(grid) - 1 - section['goal_i'] + 0.5)
            ax.plot([start[0], goal[0]], [start[1], goal[1]], color=color, linestyle='-')  # Draw entire path with solid line
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
                last_section['goal_j'] + 0.5,
                len(grid) - 1 - last_section['goal_i'] + 0.5
            )
    
    # Draw all agents at their current positions
    for agent_number, position in agent_positions.items():
        ax.plot(position[0], position[1], color=colors[agent_number], marker='o')
    
    ax.set_aspect('equal')
    plt.xlim(0, len(grid[0]))
    plt.ylim(0, len(grid))
    plt.gca().invert_yaxis()

# Main function
def main():
    log_path = '/home/0000410764/oss/Continuous-CBS/Examples/grid_task_log.xml'  # Replace with your XML file path
    map_path = '/home/0000410764/oss/Continuous-CBS/Examples/grid_map.xml'  # Replace with your XML file path
    grid, agents = parse_xml(map_path, log_path)
    
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
    
    ani = animation.FuncAnimation(fig, update_paths, frames=int(total_duration * 10), fargs=(ax, grid, agents, agent_positions, agent_colors), interval=200, repeat=True)
    plt.show()

if __name__ == '__main__':
    main()