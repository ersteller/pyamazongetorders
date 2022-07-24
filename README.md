# pyamazongetorders
This project uses selenium to gather all orders of a selected year from amazon webfrontend. 

# Get and unzip selenium driver 
select your according to your installed chrome version from drivers: https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/
```bash
curl https://chromedriver.storage.googleapis.com/100.0.4896.60/chromedriver_linux64.zip > chromedriver_linux64.zip && unzip chromedriver_linux64.zip
```
# get selenium python module
`pip3 install selenium`

# Preparation
you may need to adjust the string cookies the script is using according to you language settings of your amazon profile. 
# Usage 
The process is semi automatic. To start the process launch a new python process in the terminal: 
```
python3 pyamazon.py
```
It will open the chrome driver for you and loads the amazon signin page. after you have signed in you can select the year you want to get the orders from and hit enter in the terminal.
