# ThroughLineLP
PLEASE READ THIS AS A "HOW TO USE" FOR THE REPOSITORY

ThroughLineLP is a code base for projects related to generating StreamTables. Here, I will do through each file and what its purpose is.

3x3 Work
  - This is a folder which contains early work on small examples. This folder and all files inside of it can be irgnored

EHLooped.py
  - This file iteratively applies the post-height error hill climbing heuristic
  - The iteration will end when either the time limit expires or no excess area was removed compared to the previous iteration
  - This file reads in the table information from mosek_LP.csv and outputs an updated mosek_LP.csv, as well as for line_tab.csv
  - parameters:
      - epislon (308)- this is the minimum amount of intersect between rectanlges from the same column. An epsilon of 0 means the rectanlges will at a minimum touch 'corner-to-corner'. It is recommended to keep this parameter at 0
      - time_limit (309)- the maximum amount, in seconds, for which the ErrorHeuristic will run
      - top_to_bottom (310)- if true, the heuristic will be aplied in raster order. If false, it will be applied in reverse raster order
    
ErrorHeuristic.py
  - This file performs one iteration of the hill climbing heuristic.
  - This file is out of date and is not recommended for use
  
GeneticLP.py
  - This files uses a genetic algorithm to generate strong inital height values for our linear programming solution
  - The genetic algotihm will run until either time runs out or an optimal solution is found
  - This file direclty imports NxMLP.py, which is what creates the LP solutions. For this reason, mosek must be installed on your computer to use GeneticLP.py
  - The heights, once calculated are used to create a linear programming solution with them, which are written to mosek_LP.csv and line_tab.csv
  -NOTE: be sure to set "mode=None" on line 206 of NxMLP.py beofre using the genetic algorithm
  - parameters:
      - popsize (7)- this defines the population size for one generation
      - time_limit (9)- sets a time limit for how long the genetic algorithm can run. Note that if the time limit is reached while creating the next generation, it may take a little extra time beofre the algorithm terminates
         
GurobiOpt.py
  - This file applies a non-linear programming solution to an input table, which is of a form of a list of lists (see example tables at start of file)
  - TO USE THIS FILE GUROBI MUST BE INSTALLED (and the respective license)
  - gurobipy is a third-party module and can be attained from their main website
  - The output of GurobiOpt.py is written to mosek_LP.csv and line_tab.csv
  - parameters:
      - epsilon (239)- this is the minimum amount of intersect between rectanlges from the same column. An epsilon of 0 means the rectanlges will at a minimum touch 'corner-to-corner'. It is recommended to keep this parameter at 0
      - time_limit (241)- the maximum amount, in seconds, for which GurobiOpt will run
      - table = olympic_read(0.025) (240)- uncomment this line if you wish to use data taken from winter-olympic-medal-win.csv. The number of countires sampled can be changed on line 37 by ajusting the size of the slice (max of 15). If this line is commented, you must deinfe your own list of lists called 'table' beofre line 240

line_tab.csv
  - This file stores the data of a streamtable as a series of line segments, split into x and y coordinates. The area between each pair of lines represents a stream
  - This file is used to visualise the StreamTable with aesthetic smoothing in conjunction with OlympicVis.html
  - NOTE: This file should only be considered legitimate if the StreamTable has 15 columns or less

mosek_LP.csv
  - This file stores the data of the streamtable, where reach row represents one rectangle in the StreamTable
  - This file is used to visualise the StreamTable with no aesthetic smoothing in conjunction with Visualise.html
  - This file is also used as input to EHLooped.py 

NxMLP.py
  - This file uses a linear-programming solution with fixed heights and a table as input, and outputs the data for a StreamTable in the files mosek_LP.csv and line_tab.csv
  - TO USE THIS FILE MOSEK MUST BE INSTALLED (and the respective license)
  - mosek is a third-party module and can be attained from their main website
  - parameters:
      - mode (206) the argument passed to 'mode' determines how the fixed heights are obtained. Use 'mode=None' for random heights, mode='Uniform' for uniform row heights and mode='Scale' for row heights proportional to sum of data in that row. Use mode='Scale' for most optimal results
      - table (374)- comment or uncomment this line if you wish to use data from winter-olympic-medal-win.csv. The number of countires sampled can be changed on line 37 by ajusting the size of the slice (max of 15). If this line is commented, you must deinfe your own list of lists called 'table' beofre line 375

OlympicLeg.html
  - This file is used to generate a legend for the StreamTbale if olympic data is used
  - This file is out out of date and should not be used

OlympicVis.html
  - This file visualises the output of line_tab.csv as an aesthetically smoothed StreamTable
  - As this is an html file, be sure to open and run it in your browser properly (and make sure the .csv file can be found by it)
  - Note that the StreamTable should have 15 columns or less
  - Note for exceptionally wide tables the visualization may not all be visible

Visualize.html
  - This file visualises the output of the mosek_LP.csv as a StreamTable
  - As this is an html file, be sure to open and run it in your browser properly (and make sure the .csv file can be found by it)
  - Note for exceptionally wide tables the visualization may not all be visible

winter-olympic-mdeal-win.csv
  - This file is used as the source of the real world olympic datasets
