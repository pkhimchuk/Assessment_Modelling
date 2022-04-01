# Assessment index modelling - solution

Class initialisation function contains general parameters used to calculate index:
 * path to file with market data
 * weights 
 * index starting value
Default values of these parameters are set to corresponding inputs of the exercise.
Empty DataFrame is also created to store index levels.

# Business logic
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