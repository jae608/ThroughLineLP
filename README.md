# ThroughLineLP
PLEASE READ THIS AS A "HOW TO USE" FOR THE REPOSITORY

ThroughLineLP is a code base for projects related to generating StreamTables. Here, I will do through each file and what its purpose is.

3x3 Work
  - This is a folder which contains early work on small examples. This folder and all files inside of it can be irgnored

EHLooped.py
  - This file iteratively applies the post-height error hill climbing heuristic. 
  - The iteration will end when either the time limit expires or no excess area was removed compared to the previous iteration
  - this file reads in the table information from mosek_LP.csv and outputs an updated mosek_LP.csv, as well as for line_tab.csv
  - There are 3 adjustable parameters:
      - epislon (306)- this is the minimum amount of intersect between rectanlges from the same column. An epsilon of 0 means the rectanlges will at a minimum touch 'corner-to-corner'. It is recommended to keep this parameter at 0
      - time_limit (307)- the maximum amount, in seconds, for which the ErrorHeuristic will run
      - top_to_bottom (308)- if true, the heuristic will be aplied in raster order. If false, it will be applied in reverse raster order
    
ErrorHeuristic.py
  - this file performs one iteration of the hill climbing heuristic.
  - this file is out of date and is not recommended for use
  
GeneticLP.py
  - This files uses a genetic algorithm to generate strong inital height values for our linear programming solution.
  - the genetic algotihm will run until either time runs out or an optimal solution is found
  - this file direclty importas NxMLP.py, which is what creates the LP solutions. For this reason, mosek must be installed on your computer to use GeneticLP.py
  - The heights, once calculated are used to create a linear programming solution with them, which are written to mosek_LP.csv and line_tab.csv
  -NOTE: be sure to set "mode=None" on line 206 of NxMLP.py beofre using the genetic algorithm
  - There are 2 adjustable parameters:
      - popsize (7)- this defines the population size for one generation
      - time_limit (9)- sets a time limit for how long the genetic algorithm can run. Note that if the time limit is reached while creating the next generation, it may take a little extra time beofre the algorithm terminates.
         
GurobiOpt.py
  - 
  

