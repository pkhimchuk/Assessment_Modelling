# Assessment index modelling - solution
This script calculates levels of index with constituents limited to 3 stocks weights 50%,  25%, 25% according to their market cap. Index is rebalanced at the beginning of every month. Results are exported to csv file.

# Business logic

Class initialisation function contains general parameters used to calculate index:
 * path to file with the market data;
 * weights; 
 * index starting value.
Default values of these parameters are set to corresponding inputs of the exercise.
Empty DataFrame is created to store index levels.


Index levels calculation function contains all the business logic of the exercise. Steps of the calculation:
 * import and check the data;
 * get rebalancing dates;
 * filter data according to dates;
 * get rebalancing prices;
 * get ranks and corresponding weights;
 * calculation of stocks MTD returns;
 * calculation of index levels;
 * writing results to empty DataFrame created at initialisation step.

# Output
Results are exported to csv file. 