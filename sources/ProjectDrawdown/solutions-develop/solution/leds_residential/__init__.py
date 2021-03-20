"""Residential LED Lighting solution model.
   Excel filename: Drawdown-Residential LED Lighting_RRS_v1.1_19Nov2018_PUBLIC.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import dd
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import s_curve
from model import unitadoption
from model import vma
from model import tam
from solution import rrs

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = {
  'Current Adoption': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
      use_weight=False),
  'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_First_Cost_per_Implementation_Unit.csv"),
      use_weight=True),
  'SOLUTION First Cost per Implementation Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
      use_weight=False),
  'CONVENTIONAL Lifetime Capacity': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
      use_weight=True),
  'SOLUTION Lifetime Capacity': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
      use_weight=False),
  'CONVENTIONAL Average Annual Use': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
      use_weight=False),
  'SOLUTION Average Annual Use': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
      use_weight=False),
  'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
      use_weight=True),
  'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
      use_weight=False),
  'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Total_Energy_Used_per_Functional_Unit.csv"),
      use_weight=True),
  'SOLUTION Energy Efficiency Factor': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Total_Energy_Used_per_Functional_Unit.csv"),
      use_weight=False),
  'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Fuel Efficiency Factor': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Indirect_CO2_Emissions_per_Unit.csv"),
      use_weight=True),
  'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
      use_weight=False),
  'CH4-CO2eq Tons Reduced': vma.VMA(
      filename=None, use_weight=False),
  'N2O-CO2eq Tons Reduced': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Revenue per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'Future estimates of First cost - LED': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Future_estimates_of_First_cost_LED.csv"),
      use_weight=False),
  'LED Lamp Efficacy': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "LED_Lamp_Efficacy.csv"),
      use_weight=False),
  'Luminous Flux - Incandescent Lamp': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Luminous_Flux_Incandescent_Lamp.csv"),
      use_weight=False),
  'Luminous Flux - Halogen Lamp': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Luminous_Flux_Halogen_Lamp.csv"),
      use_weight=False),
  'Luminous Flux - LFL (Linear Fluorescent)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Luminous_Flux_LFL_Linear_Fluorescent.csv"),
      use_weight=False),
  'Luminous Flux - CFL (Compact Fluorescent)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Luminous_Flux_CFL_Compact_Fluorescent.csv"),
      use_weight=False),
  'Luminous Efficacy - Incandescent Lamp': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Luminous_Efficacy_Incandescent_Lamp.csv"),
      use_weight=False),
  'Luminous Efficacy - Halogen Lamp': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Luminous_Efficacy_Halogen_Lamp.csv"),
      use_weight=False),
  'Luminous Efficacy - LFL (Linear Fluorescent)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Luminous_Efficacy_LFL_Linear_Fluorescent.csv"),
      use_weight=False),
  'Luminous Efficacy - CFL (Compact Fluorescent)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Luminous_Efficacy_CFL_Compact_Fluorescent.csv"),
      use_weight=False),
  'LED Luminous Flux': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "LED_Luminous_Flux.csv"),
      use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
  "implementation unit": "Petalumens (Plm)",
  "functional unit": "Petalumen hours (Plmh)",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'Residential LED Lighting'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)


class Scenario:
  name = name
  units = units
  vmas = VMAs
  solution_category = solution_category

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = list(scenarios.keys())[0]
    self.scenario = scenario
    self.ac = scenarios[scenario]

    # TAM
    tamconfig_list = [
      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
      ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
      ['trend', '2nd Poly', '2nd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')
    tam_ref_data_sources = {
      'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': THISDIR.joinpath('tam', 'tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'Calculations on the basis of floor space (m2, Urge-Vorsats et al. 2013 data), average illuminance (lm/m2) and annual operating time (constant 1000 h/a)': THISDIR.joinpath('tam', 'tam_Calculations_on_the_basis_of_floor_space_m2_UrgeVorsats_et_al__2013_data_average_illumin_66d3beb0.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
      },
      'Region: China': {
        'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': THISDIR.joinpath('tam', 'tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'Calculations on the basis of floor space (m2, Hong et al. 2014 data), average illuminance (lm/m2) and annual operating time (constant 1000 h/a)': THISDIR.joinpath('tam', 'tam_Calculations_on_the_basis_of_floor_space_m2_Hong_et_al__2014_data_average_illuminance_lm_d069a17b.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          'VITO 2015 Task 7, corrected': THISDIR.joinpath('tam', 'tam_VITO_2015_Task_7_corrected.csv'),
          'Calculations, see sheet "IEA 2006 TAM" for details': THISDIR.joinpath('tam', 'tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'Navigant Consulting 2010 http://apps1.eere.energy.gov/buildings/publications/pdfs/ssl/ssl_energy-savings-report_10-30.pdf, growth rate 1.31% in http://apps1.eere.energy.gov/buildings/publications/pdfs/ssl/energysavingsforecast14.pdf': THISDIR.joinpath('tam', 'tam_Navigant_Consulting_2010_httpapps1_eere_energy_govbuildingspublicationspdfssslssl_energy_95d1ca30.csv'),
          'US DOE 2014 Energy saving forecast (total Tlmh lighting in Figure 3.2) & US DOE 2012 (2010 US Lighting Market) for 8% residential lighting, assumed to be constant': THISDIR.joinpath('tam', 'tam_US_DOE_2014_Energy_saving_forecast_total_Tlmh_lighting_in_Figure_3_2_US_DOE_2012_2010_US_0abbe87d.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Conservative Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': THISDIR.joinpath('tam', 'tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
        },
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      tam_pds_data_sources=tam_ref_data_sources)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    adconfig_list = [
      ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['trend', self.ac.soln_pds_adoption_prognostication_trend, '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'Medium',
       'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0], dtype=np.object).set_index('param')
    ad_data_sources = {
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    ref_adoption_data_per_region = None

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      pds_adoption_data_per_region = self.ad.adoption_data_per_region()
      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
      pds_adoption_is_single_source = self.ad.adoption_is_single_source()
    elif self.ac.soln_pds_adoption_basis == 'Linear':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = None
      pds_adoption_is_single_source = None

    ht_ref_adoption_initial = pd.Series(
      [0.6794492428871898, 0.3191954710617667, 0.10696600912194591, 0.14940816617982913, 0.05052731382746539,
       0.028682249324419262, 0.27338382605688477, 0.06226876414656746, 0.08601359398921465, 0.12076301805261236],
       index=dd.REGIONS)
    ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=pds_tam_per_region,
        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
        bug_cfunits_double_count=True)
    soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()
    soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()
    conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()
    soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()

    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
        ref_learning_increase_mult=2, conv_learning_increase_mult=2,
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
        conv_ref_tot_iunits=conv_ref_tot_iunits,
        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
        conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
        fc_convert_iunit_factor=1000000000000.0)

    self.oc = operatingcost.OperatingCost(ac=self.ac,
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
        conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),
        soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),
        soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),
        conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),
        single_iunit_purchase_year=2017,
        soln_pds_install_cost_per_iunit=self.fc.soln_pds_install_cost_per_iunit(),
        conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit(),
        conversion_factor=1000000000000.0)

    self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

    self.c2 = co2calcs.CO2Calcs(ac=self.ac,
        ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
        soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
        soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
        soln_pds_direct_co2_emissions_saved=self.ua.soln_pds_direct_co2_emissions_saved(),
        soln_pds_direct_ch4_co2_emissions_saved=self.ua.soln_pds_direct_ch4_co2_emissions_saved(),
        soln_pds_direct_n2o_co2_emissions_saved=self.ua.soln_pds_direct_n2o_co2_emissions_saved(),
        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
        conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
        conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
        conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        fuel_in_liters=False)

    self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],
        soln_avg_annual_use=self.ac.soln_avg_annual_use,
        conv_avg_annual_use=self.ac.conv_avg_annual_use)

