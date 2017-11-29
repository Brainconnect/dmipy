from os.path import join
import pkg_resources
import nibabel as nib
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
DATA_PATH = pkg_resources.resource_filename(
    'microstruktur', 'data/'
)


def wu_minn_hcp_coronal_slice():
    data_name = 'wu_minn_hcp_coronal_slice.nii.gz'
    return nib.load(join(DATA_PATH, data_name)).get_data()


def synthetic_camino_data_parallel():
    fractions_1_7 = np.loadtxt(DATA_PATH + 'fractions_camino_D1_7.txt')
    fractions_2_0 = np.loadtxt(DATA_PATH + 'fractions_camino_D2_0.txt')
    fractions_2_3 = np.loadtxt(DATA_PATH + 'fractions_camino_D2_3.txt')

    data_1_7 = np.loadtxt(join(DATA_PATH, 'data_camino_D1_7.txt'))
    data_2_0 = np.loadtxt(join(DATA_PATH, 'data_camino_D2_0.txt'))
    data_2_3 = np.loadtxt(join(DATA_PATH, 'data_camino_D2_3.txt'))

    fractions = np.r_[fractions_1_7, fractions_2_0, fractions_2_3]
    data = np.r_[data_1_7, data_2_0, data_2_3]
    diffusivity = np.r_[np.tile(1.7e-9, len(fractions_1_7)),
                        np.tile(2e-9, len(fractions_2_0)),
                        np.tile(2.3e-9, len(fractions_2_3))]

    class CaminoData:
        def __init__(self):
            self.fractions = fractions
            self.diffusivities = diffusivity
            self.signal_attenuation = data
    return CaminoData()


def synthetic_camino_data_dispersed():
    data_1_7_dispersed = np.loadtxt(
        join(DATA_PATH, 'data_camino_dispersed_D1_7.txt'))
    data_2_0_dispersed = np.loadtxt(
        join(DATA_PATH, 'data_camino_dispersed_D2_0.txt'))
    data_2_3_dispersed = np.loadtxt(
        join(DATA_PATH, 'data_camino_dispersed_D2_3.txt'))
    data = np.r_[
        data_1_7_dispersed, data_2_0_dispersed, data_2_3_dispersed]

    parameters_1_7_dispersed = np.loadtxt(
        join(DATA_PATH, 'parameters_camino_dispersed_D1_7.txt'))
    parameters_2_0_dispersed = np.loadtxt(
        join(DATA_PATH, 'parameters_camino_dispersed_D2_0.txt'))
    parameters_2_3_dispersed = np.loadtxt(
        join(DATA_PATH, 'parameters_camino_dispersed_D2_3.txt'))

    fractions = np.r_[
        parameters_1_7_dispersed[:, 0],
        parameters_2_0_dispersed[:, 0],
        parameters_2_3_dispersed[:, 0]
    ]

    kappas = np.r_[
        parameters_1_7_dispersed[:, 1],
        parameters_2_0_dispersed[:, 1],
        parameters_2_3_dispersed[:, 1]
    ]

    betas = np.r_[
        parameters_1_7_dispersed[:, 2],
        parameters_2_0_dispersed[:, 2],
        parameters_2_3_dispersed[:, 2]
    ]

    diffusivity = np.r_[np.tile(1.7e-9, len(parameters_1_7_dispersed)),
                        np.tile(2e-9, len(parameters_2_0_dispersed)),
                        np.tile(2.3e-9, len(parameters_2_3_dispersed))]

    class DispersedCaminoData:
        def __init__(self):
            self.fractions = fractions
            self.diffusivities = diffusivity
            self.signal_attenuation = data
            self.kappa = kappas
            self.beta = betas
    return DispersedCaminoData()


def visualize_correlation_camino_and_estimated_fractions(
        estim_fractions_parallel, estim_fractions_dispersed):

    data_parallel = synthetic_camino_data_parallel()
    data_dispersed = synthetic_camino_data_dispersed()

    mask_par_17 = data_parallel.diffusivities == 1.7e-9
    mask_disp_17 = data_dispersed.diffusivities == 1.7e-9

    fractions_par_17 = data_parallel.fractions[mask_par_17]
    fractions_disp_17 = data_dispersed.fractions[mask_disp_17]

    estim_fractions_par_17 = estim_fractions_parallel[mask_par_17]
    estim_fractions_disp_17 = estim_fractions_dispersed[mask_disp_17]

    pr = pearsonr(estim_fractions_par_17, fractions_par_17)
    pr_dispersed = pearsonr(estim_fractions_disp_17, fractions_disp_17)
    pr_multidif = pearsonr(estim_fractions_parallel, data_parallel.fractions)
    pr_multidif_dispersed = pearsonr(
        estim_fractions_dispersed, data_dispersed.fractions)

    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
        2, 2, sharex='col', sharey='row')
    ax1.scatter(fractions_par_17, estim_fractions_par_17)
    ax2.scatter(data_parallel.fractions, estim_fractions_parallel)
    ax3.scatter(fractions_disp_17, estim_fractions_disp_17)
    ax4.scatter(data_dispersed.fractions, estim_fractions_dispersed)

    ax1.text(.216, .817, 'pearsonR= ' +
             str(np.round(pr[0], 3)), fontsize=10, bbox=dict(facecolor='white', alpha=1))
    ax2.text(.216, .817, 'pearsonR= ' +
             str(np.round(pr_multidif[0], 3)), fontsize=10, bbox=dict(facecolor='white', alpha=1))
    ax3.text(.216, .817, 'pearsonR= ' +
             str(np.round(pr_dispersed[0], 3)), fontsize=10, bbox=dict(facecolor='white', alpha=1))
    ax4.text(.216, .817, 'pearsonR= ' + str(np.round(
        pr_multidif_dispersed[0], 3)), fontsize=10, bbox=dict(facecolor='white', alpha=1))

    ax1.set_title('Static Diffusivity')
    ax3.set_xlabel('Ground Truth')
    ax2.set_title('Varying Diffusivity')
    ax1.set_ylabel('Estimated intra-vf')
    ax4.set_xlabel('Ground Truth')
    ax3.set_ylabel('Estimated intra-vf')

    ax1.plot([0, 1], [0, 1], ls='--', c='k', lw=3)
    ax2.plot([0, 1], [0, 1], ls='--', c='k', lw=3)
    ax3.plot([0, 1], [0, 1], ls='--', c='k', lw=3)
    ax4.plot([0, 1], [0, 1], ls='--', c='k', lw=3)
    ax1.set_ylim(0.2, .9)
    ax1.set_xlim(0.2, .8)
    ax4.set_ylim(0.2, .9)
    ax4.set_xlim(0.2, .8)
