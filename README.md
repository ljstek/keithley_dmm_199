# Keithley model 199 digital multimeter
Python 3 class for adressing the Keithley model 199 DMM over GPIB

This class is meant to be used using the GPIB-to-USB Arduino code from Rudi's Wiki: <http://www.rudiswiki.de/wiki9/GPIBtoUSB_Nano3>

It implements most of the M199 GPIB functionality needed to perform measurements, also see the manual, found here: <https://doc.xdevs.com/doc/Keithley/199/199_901_01D.pdf>

# Requirements
* Python 3
* `numpy`, `time`, `pyserial`

# How to use

1. Import the class
```python
import dmm199
```
2. Initialize the class with the name of the serial connection to the Arduino and the baud rate (`115200`) 
```python
dmm = dmm199.keithley_m199('/dev/ttyACM0', '115200')
```
3. Set some basic measurement settings, such as Ohms and auto range selection
```python
dmm.func('OHM')
dmm.range('auto')
```
4. Perform a measurement, in this case, let's use the DMM's internal memory and interval to do 10 measurement at an interval of 175 ms (the default) and get the results in a single request
```python
data = dmm.read_buffered(10)
print(data)
```
which should output a numpy array containing your measurement results
```
[ 100.3123  100.3125  100.3124  100.3124  100.3128  100.3132  100.3132
  100.3135  100.3141  100.3139]
```

### Todo:
* Make some examples
* Implement some less used GPIB commands for the DMM
* Documentation (read the source code for now)
