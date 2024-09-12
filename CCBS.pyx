# distutils: language = c++
from libcpp.vector cimport vector
from libcpp cimport bool

cdef extern from "config.h":
    cdef cppclass Config:
        Config() except +
        void getConfig(const char* fileName)
        int     connectdness;
        double  agent_size;

cdef extern from "structs.h":
    cdef cppclass sNode:
        int id;
        double g;
    cdef cppclass sPath:
        vector[sNode] nodes;
        int agentID;
        double cost;
    cdef cppclass Solution:
        bool found;
        vector[sPath] paths;

cdef extern from "map.h":
    cdef cppclass Map:
        bool get_map(const char* FileName);
        int  get_width() const;
        Map(double size, int k); 
        double get_i (int id) const;
        double get_j (int id) const;

cdef extern from "task.h":
    cdef cppclass Task:
        bool get_task(const char* FileName, int k);
        void make_ids(int width);
        Task();

cdef extern from "cbs.h":
    cdef cppclass CBS:
        CBS();
        Solution find_solution(const Map &map, const Task &task, const Config &cfg);
        
cdef class PyCCBS:
    cdef CBS *thisptr
    cdef Config *configptr
    cdef Map *mapptr
    cdef Task *taskptr
    cdef Solution *solutionptr

    def __cinit__(self, map_name, task_name, config_name):
        self.configptr = new Config()
        self.configptr.getConfig(config_name)

        self.mapptr = new Map(self.configptr.agent_size, self.configptr.connectdness)
        self.mapptr.get_map(map_name)

        self.taskptr = new Task()
        self.taskptr.get_task(task_name, -1)
        self.taskptr.make_ids(self.mapptr.get_width())

        self.thisptr = new CBS()
        
    def find_solution(self):
        solution = self.thisptr.find_solution(self.mapptr[0], self.taskptr[0], self.configptr[0])
        paths = []
        for path in solution.paths:
            nodes = []
            for i in range(path.nodes.size()):
                if i == 0:
                    continue
                node = path.nodes[i]
                prev_node = path.nodes[i - 1]
                nodes.append({
                    "section_number": i - 1,
                    "start_i": self.mapptr.get_i(prev_node.id),
                    "start_j": self.mapptr.get_j(prev_node.id),
                    "goal_i": self.mapptr.get_i(node.id),
                    "goal_j": self.mapptr.get_j(node.id),
                    "duration": node.g - prev_node.g
                })
            paths.append({
                "agentID": path.agentID,
                "duration": path.cost,
                "sections": nodes
            })
        result = {
            "found": solution.found,
            "paths": paths
        }
        return result
        