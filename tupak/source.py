from __future__ import division, print_function

import logging
import numpy as np

try:
    import lalsimulation as lalsim
except ImportError:
    logging.warning("You do not have lalsuite installed currently. You will not be able to use some of the "
                        "prebuilt functions.")

from . import utils


def lal_binary_black_hole(
        frequency_array, mass_1, mass_2, luminosity_distance, a_1, tilt_1, phi_12, a_2, tilt_2, phi_jl,
        iota, phase, waveform_approximant, reference_frequency, ra, dec, geocent_time, psi):
    """ A Binary Black Hole waveform model using lalsimulation """
    if mass_2 > mass_1:
        return None

    luminosity_distance = luminosity_distance * 1e6 * utils.parsec
    mass_1 = mass_1 * utils.solar_mass
    mass_2 = mass_2 * utils.solar_mass

    iota, spin_1x, spin_1y, spin_1z, spin_2x, spin_2y, spin_2z = \
        lalsim.SimInspiralTransformPrecessingNewInitialConditions(iota, phi_jl, tilt_1, tilt_2, phi_12, a_1, a_2,
                                                                  mass_1, mass_2, reference_frequency, phase)

    longitude_ascending_nodes = 0.0
    eccentricity = 0.0
    mean_per_ano = 0.0

    waveform_dictionary = None

    approximant = lalsim.GetApproximantFromString(waveform_approximant)

    frequency_minimum = 20
    frequency_maximum = frequency_array[-1]
    delta_frequency = frequency_array[1] - frequency_array[0]

    hplus, hcross = lalsim.SimInspiralChooseFDWaveform(
        mass_1, mass_2, spin_1x, spin_1y, spin_1z, spin_2x, spin_2y,
        spin_2z, luminosity_distance, iota, phase,
        longitude_ascending_nodes, eccentricity, mean_per_ano, delta_frequency,
        frequency_minimum, frequency_maximum, reference_frequency,
        waveform_dictionary, approximant)

    h_plus = hplus.data.data
    h_cross = hcross.data.data

    return {'plus': h_plus, 'cross': h_cross}

def sinegaussian(frequency_array, hrss, Q, frequency, ra, dec, geocent_time, psi):

    pi = 3.14159 
    tau  = Q / (np.sqrt(2.0)*np.pi*frequency)
    temp = Q / (4.0*np.sqrt(np.pi)*frequency)
    t = geocent_time
    fm = frequency_array - frequency
    fp = frequency_array + frequency

    h_plus = (hrss / np.sqrt(temp * (1+np.exp(-Q**2)))) * ((np.sqrt(np.pi)*tau)/2.0) * (np.exp(-fm**2 * np.pi**2 * tau**2) + np.exp(-fp**2 * pi**2 * tau**2))
    
    h_cross = -1j*(hrss / np.sqrt(temp * (1-np.exp(-Q**2)))) * ((np.sqrt(pi)*tau)/2.0) * (np.exp(-fm**2 * pi**2 * tau**2) - np.exp(-fp**2 * pi**2 * tau**2))

    return{'plus': h_plus, 'cross': h_cross}

def supernova(frequency_array, file_path, luminosity_distance, ra, dec, geocent_time, psi):
    """ A supernova NR simulation for injections """

#    realhplus, imaghplus = np.loadtxt(file_path , usecols = (0,1), unpack=True)
    realhplus, imaghplus, realhcross, imaghcross = np.loadtxt('MuellerL15_example_inj.txt', usecols = (0,1,2,3), unpack=True)
  
    # waveform in file at 10kpc
    scaling = 10.0 / luminosity_distance  

    h_plus = scaling * (realhplus + 1.0j*imaghplus)
    h_cross = scaling * (realhcross + 1.0j*imaghcross)
    return {'plus': h_plus, 'cross': h_cross}

def supernova_pca_model(frequency_array, coeff1, coeff2, coeff3, coeff4, coeff5, luminosity_distance, ra, dec, geocent_time, psi):
    """ Supernova signal model """

    # this is slow reading in the file every time
    realpc1, realpc2, realpc3, realpc4, realpc5 = np.loadtxt('SupernovaRealPCs.txt', usecols = (0,1,2,3,4), unpack=True)
    imagpc1, imagpc2, imagpc3, imagpc4, imagpc5 = np.loadtxt('SupernovaImagPCs.txt', usecols = (0,1,2,3,4), unpack=True)

    pc1 = realpc1 + 1.0j*imagpc1
    pc2 = realpc2 + 1.0j*imagpc2
    pc3 = realpc3 + 1.0j*imagpc3
    pc4 = realpc4 + 1.0j*imagpc4
    pc5 = realpc5 + 1.0j*imagpc5

    # file at 10kpc
    scaling = 1e-22 * (10.0 / luminosity_distance)  

    h_plus = scaling * (coeff1*pc1 + coeff2*pc2 + coeff3*pc3 + coeff4*pc4 + coeff5*pc5)
    h_cross = scaling * (coeff1*pc1 + coeff2*pc2 + coeff3*pc3 + coeff4*pc4 + coeff5*pc5)

    return {'plus': h_plus, 'cross': h_cross}



#class BinaryNeutronStarMergerNumericalRelativity:
#    """Loads in NR simulations of BNS merger
#    takes parameters mean_mass, mass_ratio and equation_of_state, directory_path
#    returns time,hplus,hcross,freq,Hplus(freq),Hcross(freq)
#    """
#    def model(self, parameters):
#        mean_mass_string = '{:.0f}'.format(parameters['mean_mass'] * 1000)
#        eos_string = parameters['equation_of_state']
#        mass_ratio_string = '{:.0f}'.format(parameters['mass_ratio'] * 10)
#        directory_path = parameters['directory_path']
#        file_name = '{}-q{}-M{}.csv'.format(eos_string, mass_ratio_string, mean_mass_string)
#        full_filename = '{}/{}'.format(directory_path, file_name)
#        if not os.path.isfile(full_filename):
#            print('{} does not exist'.format(full_filename))  # add exception
#            return (-1)
#        else:  # ok file exists
#            strain_table = Table.read(full_filename)
#            Hplus, _ = utils.nfft(strain_table["hplus"], utils.get_sampling_frequency(strain_table['time']))
#            Hcross, frequency = utils.nfft(strain_table["hcross"], utils.get_sampling_frequency(strain_table['time']))
#            return (strain_table['time'], strain_table["hplus"], strain_table["hcross"], frequency, Hplus, Hcross)
