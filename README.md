# _NEM_Project
A project to collect NEM data, gain insights into the data, understand the Tesla big battery's operation, optimize its performance and create a battery controller.

First thingss first, A HUGE shoutout and thanks to the legends at OpenNem (https://opennem.org.au/energy/nem) for providing opensource access to their data.

The NEM (National Electricity Market) is the largest wholesale electricity market in Australia and representes approximately 200TWh of electricity generation and consumption and over 75% of Australia's electricity usage. The NEM is broken into regions (Tas, SA, Vic, NSW, Qld) each with their own wholesale electricity market. The market has many different types of generators that feed into it, from large brown and black coal-fired power stations, to combined cycle and open cycle gas generators, to variable wind and solar generators, to large and small hydro powered generators, to small rooftop solar and diesel generators, and more. The NEM has several loads that buy energy from the wholesale market and store it to be used later, these loads are mostly in the form of pumped-hydro storage, however, large commercial-scale batteries are rapidly being introduced. Lastly, the NEM allows inter-market trading through interconnectors that facilitiate energy transmission between markets, these interconnectors act as market participants in a sense, sometimes behavinbg as loads, and sometimes as generators.

This project is intended to help me better understand the operation of generators and demand in the market, the data that the market is powered by and new technology that is being introduced into the NEM, such as batteries and variable renewable energy generators.

The data used in this project comes from OpenNem, as mention above, who provide access to 5 minute and 30 minute resolved data from each of the NEM's regional markets dataing back to 2005. The data includes:
- demand (MW)
- generation/load by fuel type (MW)
- electricity spot price($/MWh)
- temperature (degrees Celsius)
The data will be collected using the opennempy web_api module (https://github.com/opennem/opennempy) made available by the legends at OpenNEM.

# This project is to be carried out in 5 stages:
1. Data collection, processing, verification and checking
2. Data insights and analysis
3. Big battery analysis and insights
4. Big battery optimization
5. Big battery controller

## Data collection, processing, verification and checking
In this section of the project I will write a class object that has the following capabilities:
- Uses opennempy (https://github.com/opennem/opennempy) to collect NEM data
- Performs checks on the data to ensure quality
- Organises and stores the data locallly as CSVs
- Opens data from local storage
- Generates a basic plot of the data
- Replaces null values using multiple methods
- Prints general statistics on each field of the data

## Data insights and analysis
In this section I will take a dataset from a region within a given date range and perform some analysis including:
- Determine average 30 minutely, daily, weekly, seasonally price, demand and generation profiles and present the graphically
- Determine price/demand spikes/drops and present them graphically
- Determine the distributions of demand/price/generation per daily/weekly time interval
- Determine average cost of generation per generator source per daily/weekly time interval
- Probably more when I get to it!

## Big battery analysis and insights
In this section I will use the data to investigate the operation of the Tesla big battery in South Australia, specifically I would like to find:
- The operating properties of the battery:
- - Maximum battery capacity
- - Maximum battery charge/discharge rates
- Battery charge/discharge distribution per daily/weekly time interval
- Battery charge/discharge rate per electricity spot price
- Average battery capacity per daily/weekly time interval
- Battery capacity distribution per spot price
- Profitibility per day
- Ratio of charge to discharge time

## Big battery optimization
More on this later after I have done more study

## Big battery controller
Use a regression model and/or neural net to learn from the optimized charge/discharge profile and create a battery controller that takes the price, temperature, generation mix as inputs and determines the battery charge/discharge operation.
