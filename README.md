# EU Migration Web API
**Repository:** `eu_migration_web_api`

## Overview

The Europe Migration Web API is a backend service developed using Flask. It provides prepared migration data related to immigration and emigration trends across the Europe. The API includes data from EU member states as well as additional reporting countries, and designed to serve as a data source for external applications, enabling easy access to migration statistics for analysis and visualization purposes.

## Features

- **Read Migration Data:** Processes and manages data related to immigration and emigration.
- **RESTful API Endpoints:** Provides clean and well-structured endpoints for data access.
- **Data-Ready Responses:** Returns data in JSON format, optimized for integration with data analysis tools like Plotly.

## Technologies Used

- **Python 3.12**
For the necessary libraries, please see `requirements.txt`. 

## Datasets

For this project Eurostat is used to access datasets. All used databases are listed below. 

| Dataset       | Source URL                                                                                     | File Name                   |
| ------------- | --------------------------------------------------------------------------------------------- | --------------------------- |
| Immigration   | [Eurostat - Immigration](https://ec.europa.eu/eurostat/databrowser/product/page/tps00176)     | `estat_tps00176_en.csv`     |
| Emigration    | [Eurostat - Emigration](https://ec.europa.eu/eurostat/databrowser/product/page/tps00177)      | `estat_tps00177_en.csv`     |

## API Endpoints

### Base URL

```sh
127.0.0.1:8080
```
### Example Endpoints

- ### Check apidocs 

```sh
127.0.0.1:8080/apidocs/
```

- ### Data analysis 

```sh
127.0.0.1:8080/analytics/dashboard
```

```sh
127.0.0.1:8080/analytics/map
```


