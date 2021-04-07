# ThroughLineLP
PLEASE READ THIS AS A "HOW TO USE" FOR THE REPOSITORY

ThroughLineLP is a code base for projects related to generating StreamTables. Here, I will do through each file and what its purpose is.

3x3 Work
  - This is a folder which contains early work on small examples. This folder and all files inside of it can be irgnored

EHLooped.py
  - This file iteratively applies the post-height error hill climbing heuristic. 
  - The iteration will end when either the time limit expires or no excess area was removed compared to the previous iteration
  - this file reads in the table information from mosek_LP.csv and outputs an updated mosek_LP.csv, as well as for line_tab.csv
  - parameters:
      - epislon (306)- this is the minimum amount of intersect between rectanlges from the same column. An epsilon of 0 means the rectanlges will at a minimum touch 'corner-to-corner'. It is recommended to keep this parameter at 0
      - time_limit (307)- the maximum amount, in seconds, for which the ErrorHeuristic will run
      - top_to_bottom (308)- if true, the heuristic will be aplied in raster order. If false, it will be applied in reverse raster order
    
ErrorHeuristic.py
  - this file performs one iteration of the hill climbing heuristic.
  - this file is out of date and is not recommended for use
  
GeneticLP.py
  - This files uses a genetic algorithm to generate strong inital height values for our linear programming solution.
  - the genetic algotihm will run until either time runs out or an optimal solution is found
  - this file direclty imports NxMLP.py, which is what creates the LP solutions. For this reason, mosek must be installed on your computer to use GeneticLP.py
  - The heights, once calculated are used to create a linear programming solution with them, which are written to mosek_LP.csv and line_tab.csv
  -NOTE: be sure to set "mode=None" on line 206 of NxMLP.py beofre using the genetic algorithm
  - parameters:
      - popsize (7)- this defines the population size for one generation
      - time_limit (9)- sets a time limit for how long the genetic algorithm can run. Note that if the time limit is reached while creating the next generation, it may take a little extra time beofre the algorithm terminates.
         
GurobiOpt.py
  - This file applies a non-linear programming solution to an input table, which is of a form of a list of lists (see example tables at start of file)
  - TO USE THIS FILE GUROBI MUST BE INSTALLED (and the respective liscense)
  - gurobipy is a third-party software tool and can be attained from their main website
  - the output of GurobiOpt.py is written to mosek_LP.csv and line_tab.csv
  - parameters:
      - epsilon (239)- this is the minimum amount of intersect between rectanlges from the same column. An epsilon of 0 means the rectanlges will at a minimum touch 'corner-to-corner'. It is recommended to keep this parameter at 0
      - time_limit (241)- the maximum amount, in seconds, for which GurobiOpt will run
      - table = olympic_read(0.025) (240)- uncomment this line if you wish to use data taken from winter-olympic-medal-win.csv. The number of countires sampled can be changed on line 37 by ajusting the size of the slice (max of 15). If this line is commented, you must deinfe your own list of lists called 'table' beofre line 240

line_tab.csv
  - This file stores the data of a streamtable as a series of line segments, split into x and y coordinates. The area between each pair of lines represents a stream.
  - This file is used to visualise the StreamTable with aesthetic smoothing in conjunction with OlympicVis.html
  - NOTE: This file should only be considered legitimate if the StreamTable has 15 columns or less

mosek_LP.csv
  - This file stores the data of the streamtable, where reach row represents one rectangle in the StreamTable
  - This file is used to visualise the StreamTable with no aesthetic smoothing in conjunction with Visualise.html
  - this file is also used as input to EHLooped.py 

  

