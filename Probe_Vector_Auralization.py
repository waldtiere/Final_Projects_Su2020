"""
Phobos Auralization Projet

Final Project for IS590PR
Programming for Data Analysis

Professor John Weible

Contributors:

Ryan Ingebritsen:  PhD Informatics.  UIUC.

Gabriel Meyers:  BS Computational Physics UIUC.




"""
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import wave, struct, math, random, matplotlib

def create_dict_from_file(filename, delimeters, first_char, column_names):
    """
    This function takes in a filename of an output file from the Horizons On-line
    Ephemeris System v4.70 (Solar System Dynamics Group Jet Propulsion Laboratory
    Pasadena, CA, USA) and creates a list of dictionaries from it with the relevant information
    needed to create arrays from each element in the file format. It prints relevant data to the
    console and then creates a nested dictionary with a Measurement Date as key and its existing
    dictionary as the value before returning it to the main.  This function is adapted from the
    hurdat2_create_dict_from_file() function originated by 590PR Summer 2020 students Grace Spiewak,
    Ryan Ingebitsen, David Mendoza and modifed for this project by Ryan Ingebritsen.

    >>> filetest = create_dict_from_file('sound/Parker Measurements 1cycle_1.wav', 'X =|Y =|Z =', 'X', ['X ', 'Y ', 'Z '])
    Input File Must Be a .txt File
    >>> filetest = create_dict_from_file('ParkerSolarProbe.txt', 'X |Y =|Z ', 'X', ['X ', 'Y', 'Z '])
    Please Check Syntax for Delimeters and colunm_names.
    >>> filetest = create_dict_from_file('ParkerSolarProbe.txt', 'X =|Y =|Z =', 'X', ['X ', 'Y ', 'Z '])
    >>> print(len(filetest))
    16801
    >>> print(filetest['2458343.500000000'])
    {'X ': -0.003126133124396237, 'Y ': -0.003561447762865196, 'Z ': -0.0006934630025140552}

    """

# This opens the
    measurement_output = open('measurement_output.txt', "w", encoding="utf8")
    # This creates and initializes a list to  serve as a dictionary container outside of the for-loop.
    measurements_file_container = {}

    # This opens the file and then splits it (preserving the commas because of the landfall count requirement).
    if not filename.endswith('.txt'):
        print('Input File Must Be a .txt File')
        return None
    elif delimeters != '{}=|{}=|{}='.format(column_names[0], column_names[1], column_names[2]):
        print('Please Check Syntax for Delimeters and colunm_names.')
        return None
    else:
        with open(filename, 'r') as infile:
            for line in infile:
                line = line.strip()
                # This checks to see if line begins with a numeric character; if so, it is a header for a new measurement.
                if line[0].isnumeric():
                    measurement_current_line = line.split()
                    # This initializes a new measurement dictionary
                    key = measurement_current_line[0]
                    new_measurement_dictionary = {
                        column_names[0]: '0',
                        column_names[1]: '0',
                        column_names[2]: '0',
                    }
                    #print(measurement_current_line)
                    # this determines if a line starts with 'X', splits it at the X =,Y =,Z = indicators
                    # to spit out a list containing only the 3 values and then updates the corresponding
                    # value in the dictionary
                if line[0] == first_char:
                    measurement_current_line = re.split(delimeters, line.strip(' '))
                    #print(measurement_current_line)
                    if len(measurement_current_line) == 4:
                        new_measurement_dictionary[column_names[0]] = float(measurement_current_line[1].strip())
                        new_measurement_dictionary[column_names[1]] = float(measurement_current_line[2].strip())
                        new_measurement_dictionary[column_names[2]] = float(measurement_current_line[3].strip())
                        measurements_file_container[key] = new_measurement_dictionary
                        #print(new_measurement_dictionary)
                    # this stops the processing when the end of data key '$$EOE' is reached
                elif line == '$$EOE':
                    break

            #print(measurements_file_container)
            return(measurements_file_container)


# This ruins converts the dictionary resulting from "create dict from filename" into a
# pd.DataFrame with the time ID for each measurement as the Index and the values of X, Y,
# and Z as each column respectively
def convert_measuerment_dict_to_DataFrame(measurement_dict):
    """
    simple conversion of dictionary to dataframe

    :param measurement_dict:
    :return: dataframe form measurement dictionary

    >>> filetest = create_dict_from_file('ParkerSolarProbe.txt', 'X =|Y =|Z =', 'X', ['X ', 'Y ', 'Z '])
    >>> dataframe_test = convert_measuerment_dict_to_DataFrame(filetest)
    >>> print(len(dataframe_test))
    16801
    >>> print(dataframe_test.dtypes)
    X     float64
    Y     float64
    Z     float64
    dtype: object
    """
    df = pd.DataFrame.from_dict(measurement_dict, orient='index')
    return(df)


def convert_coordinates_to_amplitude(measurement_DataFrame):
    """
    this defines the minimum and maximum range of each column by subtracing the max from
    the min.  This will later be used to scale the value to a value from -32767 to 32767
    :param measurement_DataFrame:
    :return: measurement_DataFrame transformed into amplitude data for .wav file
    >>> list = [1.5, 2.1, 3.3, 2.2, 3.4, 3.1, 1.45, 0.8]
    >>> df_test = pd.DataFrame(list,columns=['X'])
    >>> amp_df = convert_coordinates_to_amplitude(df_test)
    >>> print(amp_df)
           X
    0 -15123
    1      0
    2  30246
    3   2520
    4  32766
    5  25205
    6 -16383
    7 -32767

    """
    for c in measurement_DataFrame:
        range = abs(measurement_DataFrame[c].max() - measurement_DataFrame[c].min())
        data_offset = -((measurement_DataFrame[c].max() + measurement_DataFrame[c].min())/2)
        func = lambda x: int((65534 / range) * (x + data_offset))
        measurement_DataFrame[c] = measurement_DataFrame[c].apply(func)
    return measurement_DataFrame


def get_mean_wav(DataFrame):
    """
    :param DataFrame: A Dataframe with multiple colunms of amplitude numbers
    :return: a single colunm dataframe with the mean of all the columns for each row
    """

    data_mean = pd.DataFrame(DataFrame.mean(axis=1))
    return data_mean



def get_correlation(df):
    """
    This function takes three arguments, of the DataFrame and the two columns to compare.
    It returns the correlation between the two columns.
    :param df: DataFrame to use, c1: First Column to compare, c2: Second Column to Compare
    :return: corrlation between two columns in the Dataframe

    >>> df = pd.DataFrame({'one':   {'one': 1, 'two': 2, 'three': 3}, 'two':   {'one':1, 'two':2, 'three':3}, 'three': {'one':1, 'two':2, 'three':3}})
    >>> get_correlation(df)
           one  two  three
    one    1.0  1.0    1.0
    two    1.0  1.0    1.0
    three  1.0  1.0    1.0
    """
    frame_correlation = df.corr()
    return frame_correlation


def plot_data(DataFrame, title, ps, pe, columns: list):
    """
    This plots a line plot of the columns of a dataframe with up to 4 columns.  You can indicate exactly which colums you want to plot
    as well as the start and end points of each plot in the case you want to show a smaller slice of the dataframe.

    :param DataFrame: The dataFrame to plot
    :param title: Title of the Plot
    :param ps: Point Start (the first point of a slice)
    :param pe: Point End (the last point of a slice)
    :param columns: a list of which columns you want to plot as strings.
    :return: Displays the desired Output Plot
    """

    ax = plt.gca()
    idx = 0
    colors = ['blue', 'red', 'green', 'black']
    plot_titles = title.split('/')
    plot_title = plot_titles[1]

    for c in columns:
            DataFrame[ps:pe].plot(kind='line',y=c, color=colors[idx], ax=ax, fontsize=4, title=plot_title)
            idx+=1


    plt.savefig('{}.jpg'.format(title))
    plt.show()


def plot_single_data(DataFrame, title, ps, pe, columns: list, color):
    """
    This plots a line plot of the columns of a dataframe with up to 4 columns.  You can indicate exactly which colums you want to plot
    as well as the start and end points of each plot in the case you want to show a smaller slice of the dataframe.

    :param DataFrame: The dataFrame to plot
    :param title: Title of the Plot
    :param ps: Point Start (the first point of a slice)
    :param pe: Point End (the last point of a slice)
    :param columns: a list of which columns you want to plot as strings.
    :return: Displays the desired Output Plot
    """

    ax = plt.gca()
    plot_titles = title.split('/')
    plot_title = plot_titles[1]
    DataFrame[ps:pe].plot(kind='line',y=columns[0], color=color, ax=ax, fontsize=4, title=plot_title)



    plt.savefig('{}.jpg'.format(title))
    plt.show()


def make_waves(wave_array, filename: str, num_cycle=1):
    """
    This function takes a column from "amp_position" and "amp_velocity" dataframes
    and uses the datapoints to write a .wav file

    :param wave_array: list of datapoints scaled from -32767 to 32767
    :param filename: desired name for output .wav file
    :param num_cycle: optional arguent for number of times to iterate through the cycle, default=1
    :return: output .wav file
    """
    sampleRate = 44100.0  # hertz
    duration = 1.0  # seconds
    frequency = 440.0  # hertz
    obj = wave.open(filename, 'w')
    obj.setnchannels(1)  # mono
    obj.setsampwidth(2)
    obj.setframerate(sampleRate)
    waves = list(wave_array)
    for w in range(num_cycle):
        for i in waves:
            value = i
            data = struct.pack('<h', int(value))
            obj.writeframesraw(data)
    obj.close()


def find_zero_points(DataSeries, column):
    """
    Takes a single column of a DataFrame and finds the row of any column whose value
    is zero and returns its index into a list:

    :param DataSeries: the data series to analize
    :column to look for zero point
    :return: list of numbers that represent the first two zero points in the dataset
    >>> filetest = create_dict_from_file('ParkerSolarProbe.txt', 'X =|Y =|Z =', 'X', ['X ', 'Y ', 'Z '])
    >>> dataframe_test = convert_measuerment_dict_to_DataFrame(filetest)
    >>> amp_test = convert_coordinates_to_amplitude(dataframe_test)
    >>> find_zero_points(amp_test, 'X ')
    [2985, 11184]
    >>> filetest = create_dict_from_file('Phobos2018-Jan-02.txt', 'X =|Y =|Z =', 'X', ['X ', 'Y ', 'Z '])
    >>> dataframe_test = convert_measuerment_dict_to_DataFrame(filetest)
    >>> amp_test = convert_coordinates_to_amplitude(dataframe_test)
    >>> find_zero_points(amp_test, 'X ')
    Single Wave Cycle Not Found
    [0, -1]
    """

    wave_list = np.array(DataSeries[column])
    zero_indexes = np.where(abs(wave_list[:-1] - wave_list[1:]) > abs(wave_list[:-1]))[0]
    #print(zero_indexes)
    odd_zero_indexes = np.where((zero_indexes[:-1] + 1) != zero_indexes[1:])[0]
    if len(odd_zero_indexes) < 3:
        print('Single Wave Cycle Not Found')
        return [0, -1]
    odd_zero_indexes = zero_indexes[odd_zero_indexes]
    #print(odd_zero_indexes)
    if odd_zero_indexes[2] - odd_zero_indexes[0] > 900:
        indexes = [odd_zero_indexes[0], odd_zero_indexes[2]]
    elif odd_zero_indexes[4] - odd_zero_indexes[2] > 900:
        indexes = [odd_zero_indexes[2], odd_zero_indexes[4]]
    else:
        indexes = [odd_zero_indexes[0], odd_zero_indexes[4]]
    #print(indexes)
    return indexes




# This function calls all other functions given a specific waveform.

def plots_and_waves(datafile, identifier, delimiters, first_char, column_names, data_inc=500):
    """
    This function takes a text file as output from NASA's Horizon Database and outpus a number of plots
    .wav files that auralize different aspets of the dataset as sound and plots it as a graph.
    :param datafile: textfile of data from the Nasa JPL Horizons Database
    :param identifier: identifier for all output wave and image files
    :param data_inc: smaller number creates a larger increment for samples
    :return: various plots and soundfiles
    """
    # create a separate dictionary with X,Y,Z postion data
    XYZ_measurements = create_dict_from_file(datafile, delimiters, first_char, column_names)
    data_length = len(XYZ_measurements)
    data_inc = data_length/data_inc
    print(data_length)


    #create dataframe out of XYZ data dictionary
    measurement_DataFrame = convert_measuerment_dict_to_DataFrame(XYZ_measurements)


    # Plot movement of the X,Y, and Z coordniates
    print('Raw Data \n', measurement_DataFrame, '\n')
    plot_data(measurement_DataFrame, 'image/{0} Raw'.format(identifier), 0, data_length, column_names)

    # convert the coordinate position data into amplitude data and plot
    amp = (convert_coordinates_to_amplitude(measurement_DataFrame))
    print(amp)
    plot_data(amp, 'image/{0} as Amplitude'.format(identifier), 0, data_length, column_names)

    # separate out the converted X,Y, and Z coordniate position
    # amplitude datasets and use to generate soundfiles
    amp_1 = amp[column_names[0]]
    amp_2 = amp[column_names[1]]
    amp_3 = amp[column_names[2]]
    make_waves(amp_1, "sound/{0}_1.wav".format(identifier))
    make_waves(amp_2, "sound/{0}_2.wav".format(identifier))
    make_waves(amp_3, "sound/{0}_3.wav".format(identifier))

    # calculate the mean of all 3 rows of the dataframe to create a new column for the mean
    # velocity and add it to the dataframe
    mean_wav = get_mean_wav(amp)
    amp['M'] = mean_wav
    print(column_names + ['M'])
    # plot the full DataFrame with X, Y, Z and Mean Velocities as well as 3 closer samples
    plot_data(amp, 'image/{0} Mean as Amplitude'.format(identifier), 0, data_length, (column_names + ['M']))
    plot_data(amp, 'image/{0} Mean as Amplitude Sample 1'.format(identifier), 0, int(data_length/data_inc), (column_names + ['M']))
    plot_data(amp, 'image/{0} Mean as Amplitude Sample 2'.format(identifier), int(data_length/3), int((data_length/3)+(data_length/data_inc)), (column_names + ['M']))
    plot_data(amp, 'image/{0} Mean as Amplitude Sample 3'.format(identifier), int((data_length/3)*2), int(((data_length/3)*2)+(data_length/data_inc)), (column_names + ['M']))

    # re-normalize amplitude values of amp and re-plot
    amp_M = convert_coordinates_to_amplitude(amp)
    plot_data(amp_M, 'image/{0}-Mean as Amplitude Normalized'.format(identifier), 0, data_length, (column_names + ['M']))

    # create sound from the "mean" wavefile
    make_waves(amp_M['M'], "sound/{0}_mean.wav".format(identifier))

    # sample out the first full wave cycle in order to create a waveform that begins and ends on a zero point
    # define zero points of all 4 X, Y, Z and Mean Velocities, using the the
    # first and 3rd to ientify one "cycle" of the wave from zero through positive
    # phase space, back through zero to negative phase space, and back to zero.
    zero_points_X = find_zero_points(amp_M, column_names[0])
    zpx1 = zero_points_X[0]
    zpx2 = zero_points_X[1]
    zero_points_Y = find_zero_points(amp_M, column_names[1])
    zpy1 = zero_points_Y[0]
    zpy2 = zero_points_Y[1]
    zero_points_Z = find_zero_points(amp_M, column_names[2])
    zpz1 = zero_points_Z[0]
    zpz2 = zero_points_Z[1]
    zero_points_M = find_zero_points(amp_M, 'M')
    zpm1 = zero_points_M[0]
    zpm2 = zero_points_M[1]

    # plot the four sampled out full waveforms
    plot_single_data(amp_M[column_names[0]][zpx1:zpx2], 'image/{0}-Mean as Amplitude Normalized One Cycle_1'.format(identifier),
              0, data_length, (column_names[0]),'Blue')
    plot_single_data(amp_M[column_names[1]][zpy1:zpy2], 'image/{0}-Mean as Amplitude Normalized One Cycle_2'.format(identifier),
              0, data_length, (column_names[1]),'Red')
    plot_single_data(amp_M[column_names[2]][zpz1:zpz2], 'image/{0}-Mean as Amplitude Normalized One Cycle_3'.format(identifier),
              0, data_length, (column_names[2]),'Green')
    plot_single_data(amp_M['M'][zpm1:zpm2], 'image/{0}-Mean as Amplitude Normalized One Cycle_mean'.format(identifier),
              0, data_length, 'M','Black')

    # create a continuous repeated tone out of each sampled wave
    make_waves(amp_M[column_names[0]][zpx1:zpx2], "sound/{0} 1cycle_1.wav".format(identifier), 50)
    make_waves(amp_M[column_names[1]][zpy1:zpy2], "sound/{0} 1cycle_2.wav".format(identifier), 50)
    make_waves(amp_M[column_names[2]][zpz1:zpz2], "sound/{0} 1cycle_3.wav".format(identifier), 50)
    make_waves(amp_M['M'][zpm1:zpm2], "sound/{0} 1cycle_mean.wav".format(identifier), 50)

    # create a continuous repeated tone out of each sampled wave with higher pitch
    make_waves(amp_M[column_names[0]][zpx1:zpx2:5], "sound/{0} 1cycle_1_higher.wav".format(identifier), 500)
    make_waves(amp_M[column_names[1]][zpy1:zpy2:5], "sound/{0} 1cycle_2_higher.wav".format(identifier), 500)
    make_waves(amp_M[column_names[2]][zpz1:zpz2:5], "sound/{0} 1cycle_3_higher.wav".format(identifier), 500)
    make_waves(amp_M['M'][zpm1:zpm2:5], "sound/{0} 1cycle_mean_higher.wav".format(identifier), 500)

    # create a continuous repeated tone out of each sampled wave with highest pitch
    make_waves(amp_M[column_names[0]][zpx1:zpx2:30], "sound/{0} 1cycle_1_highest.wav".format(identifier), 5000)
    make_waves(amp_M[column_names[1]][zpy1:zpy2:30], "sound/{0} 1cycle_2_highest.wav".format(identifier), 5000)
    make_waves(amp_M[column_names[2]][zpz1:zpz2:30], "sound/{0} 1cycle_3_highest.wav".format(identifier), 5000)
    make_waves(amp_M['M'][zpm1:zpm2:30], "sound/{0} 1cycle_mean_highest.wav".format(identifier), 5000)

# create a non-repeating single cyle wave for use by MAX/MSP
    make_waves(amp_M[column_names[0]][zpx1:zpx2], "sound/for_max/{0} 1cycle_1_single.wav".format(identifier))
    make_waves(amp_M[column_names[1]][zpy1:zpy2], "sound/for_max/{0} 1cycle_2_single.wav".format(identifier))
    make_waves(amp_M[column_names[2]][zpz1:zpz2], "sound/for_max/{0} 1cycle_3_single.wav".format(identifier))
    make_waves(amp_M['M'][zpm1:zpm2], "sound/for_max/{0} 1cycle_mean_single.wav".format(identifier))


# CALL THE MAIN FUNCTION BELOW.

if __name__ == '__main__':
    """
    How to call:  
    
    The proram can be called by simply replacing the default parameters below with your own parameters.  
    
    plots_and_waves(datafile, identifier, delimiters, first_char, column_names, data_inc=500):
     make sure to check the origial datafile you are using to make sure it is a JPL Horizons datafile.  Lines will be formatted like so:
    
    2458343.500000000 = A.D. 2018-Aug-13 00:00:00.0000 TDB 
     X =-3.126133124396237E-03 Y =-3.561447762865196E-03 Z =-6.934630025140552E-04
     VX=-4.618261087536135E-03 VY=-5.370670708376926E-03 VZ=-9.784335339083530E-04
     LT= 2.766075923986267E-05 RG= 4.789311998076623E-03 RR= 7.149914144709729E-03
    2458343.541666667 = A.D. 2018-Aug-13 01:00:00.0000 TDB 
     X =-3.318537227417918E-03 Y =-3.785200789771382E-03 Z =-7.342262242201711E-04
     VX=-4.617155482195074E-03 VY=-5.369496986640906E-03 VZ=-9.782056435918771E-04
     LT= 2.938117068112179E-05 RG= 5.087192005121990E-03 RR= 7.148354295757034E-03
    etc.............
    
    You may only extract the values from one row and must extract all 3 values from each row.  
    to exract the X,Y and Z positoin data in this example: 
    delimiter = 'X =|Y =|Z ='
    first_char = 'X'
    column_names = ['X ', 'Y ', 'Z ']
    
    do extract the VX, VY, and VZ velocity data:
    delimiter = 'VX=|VY=|VZ='
    first_char = 'V'
    column_names = ['VX', 'VY', 'VZ']
    
    note that each individual entry in "delimiter" and each string in the "colunm_name"
    list require two spaces wtih the second space left blank in the case of a single character
    item. 
    
    The last arguement "data_inc" only affects the size of the "samples" that are plotted.  
    """


    plots_and_waves('ParkerSolarProbe.txt', 'Parker Velocities', 'VX=|VY=|VZ=', 'V', ['VX', 'VY', 'VZ'], 2000)