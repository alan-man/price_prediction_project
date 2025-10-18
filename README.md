# price_prediction_project
DALAS project


Pre-requisites:

python 3.10 or newer
pip install pyairbnb
pip install pandas numpy matplotlib seaborn


run DataScraper.py with the coordinates of any city, you can change the search parameters
it will save the data in a file search_from_url.json (i think there is a hardcoded limit of 280 listings per search)

then you can run VisualizationAndParser to create visuals of the statistics, and a file airbnb_analysis.csv that has the data parsed

it's not clean, a lot of stuff is hardcoded especially the prints, and there seems to be missing parts of the data, and weird looking prices sometimes, but it seems to be reliable enough, we can take some of its data and complement with a database.
