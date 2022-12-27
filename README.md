<p align="center">
  <a href="" rel="noopener">
 <img width=450px src="https://constellationpolitical.com/images/facebook-form-header.png" alt="Project logo"></a>
</p>

<h3 align="center">Colorado Voter Registration Timeseries</h3>

---

<p align="center"> A Google Cloud Run job to periodically download the Colorado voter registration totals and add them to a timeseries in Google BigQuery.
    <br> 
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)


## About <a name = "about"></a>

The Colorado Secreatry of State's office publishes a monthly report on the voter registration totals for different districts within the state.

This repository creates a Google Cloud Run job that can be run on a schedule or on demand to retrieve the Secretary of State data and upload it your Google BigQuery instance as an entry in a continuous timeseries.


## Getting Started <a name = "getting_started"></a>

These instructions will get your copy of the project up and running on your local machine for development and testing purposes.

This repository depends on certain user defined variables that need to be configured in two places: `config.py` & `.env`

`config.py` will generally contain the latest values that I am using to run this repository. A careful read and update to your own values should be all that's needed to update this file. The variables contained here are mostly file and project names.

This repository includes a template for `.env` as the file `.env.template`. If you are attempting to run this repository locally and not as a Google Cloud Run job you will need to modify `.env.template` to contain your secret variables such as the strings for your Google Service Account credentials. Once you have done so, save  `.env.template` as `.env`


### Prerequisites

This repository is meant to be run as a Google Cloud Run job. That means you will need your own Google Cloud login and several Google Cloud services enabled.

1.  Google Cloud Run
2.  Google Big Query
3.  Google Cloud Scheduler

This repository uploads this information to our Google BigQuery. If you do not have your own BigQuery instance it won't work.


### Installing

1. Clone this repository to your local machine.
```
git clone https://github.com/bengen343/co-registration-timeseries.git
```

2. Update variables within `config.py` to name your outputs and correctly reference file origins/destinations. 

3. Update `.env.template` with values for each of the variables requested. Note that the variable `BQ_ACCOUNT_CREDS` should be the entire output of the json credential file associated with the Google service account you're using for this project. Save this file as `.env` when you've added all your values.

4. Create a virtual environment for the repository, probably by running `python3 -m venv .venv` in the terminal from the local directory. 

5. Activate the virtual environment, probably by running `.venv\Scripts\activate.bat` on Windows or `source .venv/bin/activate` on Mac.

6. Install the required dependencies by running `pip install -r requirements.txt`


## Built Using <a name = "built_using"></a>

- [Google BigQuery](https://cloud.google.com/bigquery)
- [Google Cloud Run](https://cloud.google.com/run)


## Authors <a name = "authors"></a>

- [@bengen343](https://github.com/bengen343)

