# **Stock Quick Predict**
> Easy UI and fast results for on-the-go prediction
> **NOTE: Work in progress!  This was once working, now broken due to a change in model structure.**

## What is included?
1. Multiple ML models for predicting the next timeframe (or current)
   a. Can be next 5 min, 15 min, 30 min, 1 hour, 4 hour, day, week, month 
2. Robust UI, Easy to click and select models
3. Multithreaded support
4. Real-time predictions
5. Easy to view analysis
6. *FAST*- total 8 predictions in sub 20 seconds!
## What model does this run?
Initially, this model was based on a basic linear regression with Leaky ReLU activation, with Adam Optimizer, but over time, attempts were made to improve the model.  There were multiple different variations recorded for testing in the commit history, but at this point, there is current work to implement a newer type of model, which is Long-Short Term Memory (LSTM).  If in broken state, the latest commit will reflect this.
## Required modules
- Tensorflow
- Keras
- Numpy
- Twitter API
- yfinance
- tkinter
- ttk
- PIL
- pandas
- pathlib
- pytz
- mysql
- pandas_datareader

## How to Execute?
Under the 'main' package, run 'launch_main.py' through your favorite IDE(tested through Eclipse)!  

## UI Quick Start
Overview
![image](https://user-images.githubusercontent.com/12478124/132107184-1b053c89-d19f-44d3-8e27-4c2d1ea5970a.png)


Stock entry input goes here:
![image](https://user-images.githubusercontent.com/12478124/132107203-578718d4-0da0-44a8-b1dd-a6804775b65a.png)


To Generate, press the 'Generate' Button:
![image](https://user-images.githubusercontent.com/12478124/132107209-d66d8ec1-8d73-4137-b06f-773dbd62d0f2.png)


Quick-generate a stock from a pre-defined list:
![image](https://user-images.githubusercontent.com/12478124/132107214-e8aefd9e-eec8-4c3e-b55c-0a11b6911ac9.png)


Compare prior day's results for accuracy:
![image](https://user-images.githubusercontent.com/12478124/132107222-59b4cb01-4036-4406-89cd-98c43515706b.png)


Force regeneration of current model values(or next day)
![image](https://user-images.githubusercontent.com/12478124/132107225-c6dd38ba-c185-4ba7-8014-4f8cef5e07d3.png)


Predict an extra day out:
![image](https://user-images.githubusercontent.com/12478124/132107227-bc089354-2828-4ac5-bd19-f69b46a612fd.png)

Press Right Arrow to go into 'Analysis' Mode(Only Predict a chart:
![image](https://user-images.githubusercontent.com/12478124/132107247-ac016026-60f4-46fd-a409-5131fd229673.png)


## What does each chart represent?

- Top left is a graph to show current fib levels and keltner belt with next day predicted values:

![image](https://user-images.githubusercontent.com/12478124/132107282-a4138cef-a086-4fa9-ae60-2941a81084a3.png)

- Top right and bottom left are 2 sets of different ML models predicting outputs of 3 and 8 in size.  Only 2 outputs represented since that info is the most important...  Outputs represent Difference in Open from prior day, difference in close from prior day and predicted range

![image](https://user-images.githubusercontent.com/12478124/132107296-cedcd12d-46a9-4032-8dab-de43a413adc0.png)
![image](https://user-images.githubusercontent.com/12478124/132107300-f4c2331b-974f-4e9f-abfa-4fb466b5b9f8.png)

- Bottom right is still WIP, extra ML model to predict expected range...

![image](https://user-images.githubusercontent.com/12478124/132107310-23b10ae8-1e0b-4025-98c3-fa3d7aa54510.png)

