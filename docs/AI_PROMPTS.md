# Team AI prompt record

This historical prompt record is preserved from the repository. Its original
introduction attributed the prompts to the team; this audit did not independently
verify that attribution. Names and assignments were confirmed in the current user
request. Prompts are not evidence that the requested work was completed. Original
tools/models, dates of use and any additional prompts remain unverified.

## Person 1 — Kareem

Hi, I'm working on a Data Engineering project about housing growth and road safety in New York City. My part is cleaning and exploring the housing dataset.

I'm using the Affordable Housing Production by Building dataset (hg8x-zxpr) and working with Python and pandas.

I need help with these steps:

1. Load the housing data into `df_housing_raw` and do EDA to understand the data.
2. Check for missing values, duplicates, outliers, wrong data types, and inconsistent values.
3. Clean the data and make sure `zip_code`, `borough`, and `year` have consistent formats.
4. Make sure housing buildings, projects, and affordable housing units are counted correctly.
5. Save the cleaned data as `df_housing_clean`.

I also need to answer two research questions using our final merged dataset `df_integrated`:

- Do ZIP codes with more affordable housing units also have more serious crashes? I need a scatter plot.
- Which boroughs have the highest affordable housing production and serious crash counts? I need a grouped bar chart.

Please give me simple Python code using pandas and Plotly or matplotlib. Add comments so I can understand what each part does. Also explain why we clean certain values and how I can check that the results are correct. Keep the explanations short and easy to understand.

## Person 2 — Youssef

I'm doing the transportation part of our NYC housing and road safety project.

My dataset is Serious Injury Response, Tracking & Analysis Program (SIRTA), dataset ID xeqp-qz8h.

I want to use Python to explore and clean the transportation data. Can you help me write the code?

First, load the dataset as `df_transport_raw`. I want to check the columns, data types, missing data, duplicates, and unusual values.

After that, help me clean it. I need to fix the date formats, standardize ZIP codes and borough names, and create the `year` column. I also want to make sure injury counts are valid and that the same crash isn't counted twice. Use the crash ID when counting serious crashes.

The cleaned dataframe should be called `df_transport_clean`.

For the visualization part, I have these questions:

1. How have affordable housing production and serious crashes changed over time? Make a line chart.
2. Do ZIP codes with more housing projects also have more severe crash injuries? Make a scatter plot.

Both graphs should use `df_integrated` because they need housing and transportation data together.

Please use pandas and Plotly or matplotlib. Explain the code in a simple way and add useful comments. I also want to understand what the graphs show without making conclusions that the data doesn't support.

## Person 3 — Malak

Hey, I'm responsible for combining the two datasets in our Data Engineering project about housing and road safety in NYC.

We already have two cleaned dataframes called `df_housing_clean` and `df_transport_clean`.

I need to integrate them into one dataframe using pandas.

Can you help me do the following?

1. Check that both datasets have `zip_code` and `year` in the same format.
2. Aggregate both datasets by `zip_code` and `year` before merging them.
3. Make sure we don't double count housing buildings, projects, or serious crashes.
4. Merge the datasets and explain which type of join makes the most sense.
5. Check for unmatched records, duplicates, null values, and incorrect data types after merging.
6. Clean any remaining problems and save the result as `df_integrated`.

Please also explain why we aggregate first instead of directly merging the original rows.

I have two research questions:

- Which ZIP codes have both high affordable housing production and high serious crash activity? Use a scatter plot.
- Which ZIP codes have the highest serious crash counts compared to affordable housing production? Use a top-10 bar chart.

For the second graph, calculate crashes relative to affordable housing units and handle ZIP codes with zero affordable units properly.

I want Python code with comments and short explanations for the merging and cleaning decisions. Also show me how to verify that the final dataframe is correct and ready for the rest of the team.

## Person 4 — Ahmed

I need help creating the website for our Data Engineering project. Our topic is Housing Growth and Road Safety in New York City.

We have already combined our datasets into `df_integrated`. It has columns like `zip_code`, `borough`, `year`, `affordable_units`, `housing_building_count`, `housing_project_count`, `serious_crash_count`, and `severe_injuries`.

I want to build an interactive website using Python Dash and Plotly.

The website should look clean and be easy to use. I need dropdown filters for borough, year, and ZIP code, along with filters for housing and transportation values.

I also want a search feature where users can search for an area or year, and a Generate Report button that updates the graphs based on the selected filters.

These are my two research questions:

1. Is a higher number of housing buildings associated with more severe injuries? Show this using a scatter plot.
2. Which boroughs have the highest number of serious crashes per housing project? Make a bar chart and handle division by zero.

The website should also display the other team members' graphs and have a section for the main findings.

Can you give me the Dash code and explain how to connect it to `df_integrated`? Please organize the code into simple parts, add comments, and show me how to run and test the website. I want something that works well but isn't too complicated.

## Person 5 — Kenzy

Our group is making a project about affordable housing and serious road crashes in NYC, and my job is to work on the visualizations and help put the final results together.

We are using `df_integrated`, which has housing and crash information for different ZIP codes and years.

I want the charts to be easy to read and look consistent, so I need help choosing suitable colors, titles, labels, and legends.

I also have two questions I need to visualize.

My first question is: Where in NYC do high affordable housing production and high serious crash levels overlap?

I want to make an interactive map that shows this using real NYC ZIP code locations or boundaries. Please explain how to create the map and how we can decide which areas count as high.

My second question is: Do years with higher affordable housing production also have higher or lower severe injuries?

For this, help me make a scatter plot or line chart comparing `affordable_units` and `severe_injuries` over the years.

After making the graphs, I also need to help write the story of our project. This should include what we're investigating, the important findings, limitations, and why our results might be useful.

Please use pandas and Plotly. Keep everything simple and add comments to the code. For the findings, explain how I can write them based on our actual graphs instead of assuming the results beforehand. Also make sure we don't confuse correlation with causation.

## Person 6 — Lama

Hi, I'm working on the final part of our Data Engineering group project. We're studying the relationship between affordable housing and road safety in New York City.

Our project uses two NYC Open Data datasets, and we have a merged dataframe called `df_integrated`. We also have a Jupyter notebook and a Dash website.

I need help making sure everything is organized and working before submission.

Can you guide me through these tasks?

- Organize our GitHub repository so the notebooks, datasets, website files, and documentation are easy to find.
- Write a simple README with the project idea, datasets, setup instructions, and what each of the six team members did.
- Make sure our notebook runs correctly and the cleaning and merging steps are explained.
- Check that `df_integrated` has no duplicate ZIP-code/year combinations or unexpected data problems.
- Test the website filters, search, Generate Report button, and visualizations.
- Help me deploy our Dash website using Render and check that the link works.

I also need to create two graphs using our integrated dataset:

1. Which ZIP codes have high housing growth but poor road safety? I want a heatmap or categorized scatter plot.
2. Does the relationship between affordable housing production and serious crashes differ across boroughs? I need a scatter plot with different colors for each borough.

Please use Python, pandas, and Plotly for the graphs. Give me simple code and clear instructions for testing and deployment. Explain what I should check at every step, and don't assume something works until we've actually tested it.

### Person 6 assistance (November 8, 2026)

Lama used Claude (Anthropic) with the prompt above, plus the team's task breakdown and
the course project description. Claude reviewed the repository, ran the tests, wrote
`app/charts/rq11_rq12.py`, `Person6_Research_Questions.ipynb`, the RQ11/RQ12 tests and
story text, `render.yaml`, and the README deployment section, and ran browser
end-to-end checks of the dashboard. The per-year averaging decision came from checking
how summed totals relate to the number of matched years.

## Integration repair assistance

The prior repository record states that additional requests asked Codex to inspect the repository,
repair available work for persons 1–4, identify missing teammate deliverables,
and push the fixes. Codex implemented website RQ1–RQ4, added the RQ3–RQ4
analysis notebook, adjusted notebook portability and scope documentation, and
added regression and notebook execution checks. See `PROJECT_REVIEW.md` for
verified checks and remaining gaps. This paragraph summarizes the repair requests;
it is not a transcript of earlier prompts used by individual members.

## November 7, 2026 audit assistance

The current user asked Codex to analyze the repository and supplied files, verify
Persons 1–5 against the shared NYC datasets, dataframe names, aggregate-before-merge
rule and assigned research questions, fix errors and update the README and files.
They identified Person 3 as Malak and supplied the six member names. Codex recovered
official raw snapshots, reconstructed the missing transportation cleaning workflow,
added shared cleaning/integration code and audit exports, corrected misleading
claims and chart edge cases, and expanded verification. These are audit additions;
they do not establish individual authorship of historical work. See PROJECT_REVIEW.md
and VERIFICATION.md for scope, results and remaining Person 6 deliverables.
