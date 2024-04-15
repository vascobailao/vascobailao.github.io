# Data science portfolio by Vasco Fernandes

This portfolio is a compilation of notebooks which I created for data analysis or for exploration of machine learning algorithms.


---

## Prioritize Lockers

[Github](https://github.com/vascobailao/prioritize-lockers)
[nbviewer](https://github.com/vascobailao/prioritize-lockers/blob/main/solution.ipynb)

Network of parcel lockers. These parcel lockers are used by users to ship items.

The standard shipment flow for our parcel lockers is as follows:

- Seller of a pre-loved item drops off their parcel at a locker;
- Driver picks up the parcel from the origin locker & brings it to a warehouse;
- Parcels are sorted in the warehouse;
- Driver picks up the parcel from the warehouse & drops it off at the destination locker;
- Buyer of a pre-loved item picks up the parcel from the destination locker.
  
Every day, we must decide which lockers to visit. This decision involves a **trade-off between conflicting business objectives**. Visiting more lockers increases delivery speed, but it also increases delivery costs.

---

## Rossmann Uplift Model

[Github](https://github.com/vascobailao/rossmann-uplift)
[nbviewer](https://nbviewer.org/github/vascobailao/rossmann-uplift/blob/main/solution.ipynb)

Uplift model approach using 2 different models - My hypothesis is Sales can be optimized (maximized) if certain promotions in certain segments of products (Assortments) are launched in specific days and holidays. The ultimate goal would be to automate promotions and eventually stocks.

Rossmann Store Sales Challenge - Forecast sales using store, promotion, and competitor data - [link](https://www.kaggle.com/c/rossmann-store-sales)

Rossmann is challenging you to predict 6 weeks of daily sales for 1,115 stores located across Germany. Reliable sales forecasts enable store managers to create effective staff schedules that increase productivity and motivation. By helping Rossmann create a robust prediction model, you will help store managers stay focused on what’s most important to them: their customers and their teams! 

---

## Offer Optimization

[Github](https://github.com/vascobailao/offer-optimization)
[nbviewer](https://nbviewer.org/github/vascobailao/offer-optimization/blob/main/solution.ipynb)

Content optimisation: We currently have a very large library of voices and sounds. Sounds are grouped in “Theme packs” (Like Xmas, Video Games, movie titles etc). Each week each user gets one pack for free. You are told to maximize the usage of the weekly packs. What would you do? What data would you need?

Churn reduction: Subscription business model where optimizing churn is a key factor. Using telco client churn sample data. The analysis is focus on different offers and the impact of selecting these offers. In this challenge I used the [econml library](https://econml.azurewebsites.net/_autosummary/econml.dr.DRLearner.html).

Telco Customer Churn Challenge - Focused customer retention programs - [link](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)

---

## Customer Lifetime Value

[Github](https://github.com/vascobailao/ltv-prediction)
[nbviewer](https://nbviewer.org/github/vascobailao/ltv-prediction/blob/main/soution.ipynb)

The business model is subscription based. They have different insurance products and we have a wide variety of features available per user, some of which can change over time.

The task is to create a model that predicts the customer lifetime value (aka **LTV**) of a customer for the next 12 months. This metric is the sum of the monthly commission we collect from a customer during the first 12 months since they join us, plus the one time commission from additional products they might purchase (cross sell). The customers can cancel their subscription at any time.

---

## Churn predictions

[Github](https://github.com/vascobailao/ltv-prediction)
[nbviewer](https://nbviewer.org/github/vascobailao/churn-prediction/blob/main/solution.ipynb)

As a social network platform, one of our major concerns is user churn. The ability to identify potential user churn and proactively respond to retain those users is a valuable asset.

- Design a solution to identify users at risk of churning. This solution should include your approach to data analysis, choice of model(s), feature selection, and strategies for user retention.
- Implement a proof of concept of your solution design. This includes data preprocessing, a basic prediction model for user churn, and evaluation of the model's performance.

---

## Price Elasticity of Demand

[Github](https://github.com/vascobailao/price-elasticity)
[nbviewer](https://nbviewer.org/github/vascobailao/price-elasticity/blob/main/elasticity.ipynb)

Price elasticity of demand (**PED**) is a measure representing the quantity demanded to the change in the price of a product or service. To simplify, it is the ratio of percentage change in quantity demanded of a product in response to the percent change in its price.

---

## Credit Decision Model

[Github](https://github.com/vascobailao/credit-decision-model)
[nbviewer](https://nbviewer.org/github/vascobailao/credit-decision-model/blob/main/solution.ipynb)

Build a credit model to predict future unpayments.

The training dataset contains the history of loan requests (orders) of a set of customers, as well as when they paid. The test dataset, contains the details of the last transaction requested by some of these users. The goal is to estimate the likelihood of the customers not paying it. 

---

## Keystroke Dynamics

[Github](https://github.com/vascobailao/keystroke-dynamics)
[nbviewer](https://nbviewer.org/github/vascobailao/keystroke-dynamics/blob/main/exploration.ipynb)

[Kaggle challenge](https://www.kaggle.com/competitions/keystroke-dynamics-challenge-1/overview) - Identify users based on the way they type

- `press_1` - timestamp when the 1st key was pressed
- `release_1` - timestamp when the 1st key was released

---- 

## Device Activations Challenge

[Github](https://github.com/vascobailao/device-activations)
[nbviewer](https://nbviewer.org/github/vascobailao/device-activations/blob/main/solution.ipynb)

Kaggle challenge

The data consists on timestamps, device and device_activated, the number of times each device was activated.
The objective of the challenge is to predict the next 24 hours individually, a predictions for 9:00 AM, 10:00 AM, and so on until 23:00PM the last timestamp of each day.

---- 

## Conversion Improvements

[Github](https://github.com/vascobailao/conversion-improvements)
[nbviewer-1st](https://nbviewer.org/github/vascobailao/conversion-improvements/blob/main/problem1.ipynb)
[nbviewer-2nd](https://nbviewer.org/github/vascobailao/conversion-improvements/blob/main/problem2.ipynb)

The goal is to optimise conversion funnel by applying your data science skills to uncover user behaviour patterns in the data. The deliverable of this problem is to provide one or more recommendations on how we can improve conversion.

---- 
