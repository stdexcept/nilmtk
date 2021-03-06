from __future__ import print_function
from nilmtk.dataset import DataSet
from nilmtk.cross_validation import train_test_split
from nilmtk.disaggregate.fhmm_exact import FHMM
from nilmtk.metrics import rms_error_power
from nilmtk.metrics import mean_normalized_error_power
from nilmtk.sensors.electricity import Measurement
from nilmtk.stats.electricity.building import top_k_appliances
from nilmtk.preprocessing.electricity.building import filter_top_k_appliances
import time
import pandas as pd
import matplotlib.pyplot as plt
import resource


PATH = '/home/nipun/Desktop/AMPds/'
EXPORT_PATH = '/home/nipun/Desktop/temp/ampds/'
DISAGG_FEATURE = Measurement('power', 'active')

# Setting the limits to 5 GB RAM usage
megs = 5000
resource.setrlimit(resource.RLIMIT_AS, (megs * 1048576L, -1L))

# Loading data from HDF5 store
dataset = DataSet()
t1 = time.time()
dataset.load_hdf5(EXPORT_PATH)
t2 = time.time()
print("Runtime to import from HDF5 = {:.2f}".format(t2 - t1))

# Experiment on first (and only) building
b = dataset.buildings[1]

# Filtering to include only top 8 appliances
b = filter_top_k_appliances(b, 3)

# Dividing the data into train and test
train, test = train_test_split(b)

# Again subdivide data into train, test for testing on even smaller data
#train, test = train_test_split(train, test_size=.5)


# Initializing FHMM Disaggregator
disaggregator = FHMM()
train_mains = train.utility.electric.mains[
    train.utility.electric.mains.keys()[0]][DISAGG_FEATURE]

# Get appliances data
app = train.utility.electric.appliances
train_appliances = pd.DataFrame({appliance: app[appliance][DISAGG_FEATURE] for appliance in app if DISAGG_FEATURE in app[appliance]})


# Train
t1 = time.time()
disaggregator.train(train, disagg_features=[DISAGG_FEATURE])
t2 = time.time()
print("Runtime to train = {:.2f} seconds".format(t2 - t1))


# Disaggregate
t1 = time.time()
disaggregator.disaggregate(test)
t2 = time.time()
print("Runtime to disaggregate = {:.2f} seconds".format(t2 - t1))


# Metrics

predicted_power = disaggregator.predictions
app_ground = test.utility.electric.appliances
ground_truth_power = pd.DataFrame({appliance: app_ground[appliance][DISAGG_FEATURE] for appliance in app_ground})

# RMS Error
re = rms_error_power(predicted_power, ground_truth_power)

# Mean Normalized Error
mne = mean_normalized_error_power(predicted_power, ground_truth_power)

# Plot results
for appliance in predicted_power:
    fig, axes = plt.subplots(nrows=2, sharex=True)
    predicted_power[appliance].plot(ax=axes[0])
    axes[0].set_title("Predicted power for %s instance %d" %
                      (appliance.name, appliance.instance))
    ground_truth_power[appliance].plot(ax=axes[1])
    axes[1].set_title("Ground truth power for %s instance %d" %
                      (appliance.name, appliance.instance))
